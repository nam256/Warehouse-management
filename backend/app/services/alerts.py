"""Cảnh báo chuông — theo vai trò, tự hết khi xử lý xong."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import (
    CCPStatus,
    CapaStatus,
    CorrectiveAction,
    OperationRecord,
    ProductionOrder,
    PurchaseRequest,
    PurchaseRequestStatus,
    QualityStatus,
    User,
    UserRole,
)
from app.schemas import AlertFeed, AlertItem
from app.services.audit import short_ref
from app.services.inventory_report import summarize_inventory, summarize_inventory_batches

EXPIRY_SOON_DAYS = 30
CAPA_DUE_SOON_DAYS = 3


def _sees_stock(role: UserRole) -> bool:
    return role in {UserRole.admin, UserRole.thu_kho, UserRole.ql_nm, UserRole.ky_thuat}


def _sees_quality(role: UserRole) -> bool:
    return role in {UserRole.admin, UserRole.lab, UserRole.attp, UserRole.ql_nm}


def _sees_capa(role: UserRole) -> bool:
    return role in {UserRole.admin, UserRole.attp, UserRole.ql_nm}


def _sees_production(role: UserRole) -> bool:
    return role in {UserRole.admin, UserRole.ky_thuat, UserRole.ql_nm, UserRole.lab}


def _sees_purchase(role: UserRole) -> bool:
    return role in {UserRole.admin, UserRole.thu_kho, UserRole.ql_nm}


def build_alert_feed(db: Session, user: User) -> AlertFeed:
    items: list[AlertItem] = []
    today = date.today()

    if _sees_stock(user.role):
        for row in summarize_inventory(db):
            if row.available <= 0 and row.on_hand <= 0:
                items.append(
                    AlertItem(
                        id=f"stock-empty-{row.material_id}",
                        kind="out_of_stock",
                        severity="danger",
                        title=f"Hết hàng: {row.material_code}",
                        detail=f"{row.material_name} — tồn khả dụng 0 {row.unit}",
                        href="/inventory",
                    )
                )
            elif 0 < row.available < row.min_stock:
                items.append(
                    AlertItem(
                        id=f"stock-low-{row.material_id}",
                        kind="low_stock",
                        severity="warn",
                        title=f"Tồn thấp: {row.material_code}",
                        detail=(
                            f"{row.material_name} — còn {row.available:g} {row.unit}, "
                            f"tối thiểu {row.min_stock:g}"
                        ),
                        href="/inventory",
                    )
                )

        soon = today + timedelta(days=EXPIRY_SOON_DAYS)
        for lot in summarize_inventory_batches(db):
            if not lot.expiry_date or lot.on_hand <= 0:
                continue
            ref = short_ref(lot.batch_no)
            if lot.expiry_date < today:
                items.append(
                    AlertItem(
                        id=f"expiry-over-{lot.batch_id}",
                        kind="expired",
                        severity="danger",
                        title=f"Lô hết hạn: {ref}",
                        detail=f"{lot.material_code} — HSD {lot.expiry_date.isoformat()}, còn {lot.on_hand:g} {lot.unit}",
                        href="/inventory",
                    )
                )
            elif lot.expiry_date <= soon:
                items.append(
                    AlertItem(
                        id=f"expiry-soon-{lot.batch_id}",
                        kind="expiring_soon",
                        severity="warn",
                        title=f"Lô sắp hết hạn: {ref}",
                        detail=f"{lot.material_code} — HSD {lot.expiry_date.isoformat()} (trong {EXPIRY_SOON_DAYS} ngày)",
                        href="/inventory",
                    )
                )

    if _sees_quality(user.role):
        fail_lots = [
            lot
            for lot in summarize_inventory_batches(db)
            if lot.on_hand > 0
            and (
                lot.ccp1_status == CCPStatus.fail.value
                or lot.quality_status == QualityStatus.rejected.value
            )
        ]
        for lot in fail_lots[:20]:
            ref = short_ref(lot.batch_no)
            if lot.quality_status == QualityStatus.rejected.value:
                title = f"Lô bị từ chối: {ref}"
                detail = f"{lot.material_code} — chất lượng từ chối"
            else:
                title = f"Lô không đạt điểm kiểm soát 1: {ref}"
                detail = f"{lot.material_code} — CCP1 không đạt"
            items.append(
                AlertItem(
                    id=f"quality-{lot.batch_id}",
                    kind="quality_fail",
                    severity="danger",
                    title=title,
                    detail=detail,
                    href="/quality",
                )
            )

        waiting = [
            lot
            for lot in summarize_inventory_batches(db)
            if lot.on_hand > 0 and lot.quality_status == QualityStatus.awaiting_release.value
        ]
        for lot in waiting[:20]:
            items.append(
                AlertItem(
                    id=f"release-{lot.batch_id}",
                    kind="awaiting_release",
                    severity="warn",
                    title=f"Chờ giải phóng: {short_ref(lot.batch_no)}",
                    detail=f"{lot.material_code} — Lab xong, ATTP chưa giải phóng ({lot.on_hand:g} {lot.unit})",
                    href="/quality",
                )
            )

    if _sees_production(user.role):
        failures = (
            db.query(OperationRecord, ProductionOrder)
            .join(ProductionOrder, ProductionOrder.id == OperationRecord.order_id)
            .filter(OperationRecord.ccp2_status == CCPStatus.fail)
            .order_by(OperationRecord.id.desc())
            .limit(15)
            .all()
        )
        for record, order in failures:
            items.append(
                AlertItem(
                    id=f"ccp2-{record.id}",
                    kind="ccp2_fail",
                    severity="danger",
                    title=f"Điểm kiểm soát 2 không đạt: {short_ref(order.order_no)}",
                    detail=f"Bước {record.step} — mở Giám sát điểm kiểm soát",
                    href="/haccp",
                )
            )

    if _sees_capa(user.role):
        due_soon_until = today + timedelta(days=CAPA_DUE_SOON_DAYS)
        open_rows = (
            db.query(CorrectiveAction)
            .filter(
                CorrectiveAction.status != CapaStatus.closed,
                CorrectiveAction.due_date.isnot(None),
            )
            .order_by(CorrectiveAction.due_date.asc())
            .limit(40)
            .all()
        )
        for capa in open_rows:
            due = capa.due_date
            if due is None:
                continue
            label = str(capa.title or capa.reason or f"#{capa.id}")[:120]
            if due < today:
                items.append(
                    AlertItem(
                        id=f"capa-{capa.id}",
                        kind="capa_overdue",
                        severity="danger",
                        title=f"Khắc phục quá hạn #{capa.id}",
                        detail=label,
                        href="/capa",
                    )
                )
            elif due <= due_soon_until:
                items.append(
                    AlertItem(
                        id=f"capa-soon-{capa.id}",
                        kind="capa_due_soon",
                        severity="warn",
                        title=f"Khắc phục sắp đến hạn #{capa.id}",
                        detail=f"{label} — hạn {due.isoformat()}",
                        href="/capa",
                    )
                )

    if _sees_purchase(user.role):
        pending = (
            db.query(PurchaseRequest)
            .filter(PurchaseRequest.status == PurchaseRequestStatus.pending)
            .order_by(PurchaseRequest.created_at.desc())
            .limit(15)
            .all()
        )
        for req in pending:
            material = req.material
            code = material.code if material else f"#{req.material_id}"
            items.append(
                AlertItem(
                    id=f"purchase-{req.id}",
                    kind="purchase_pending",
                    severity="info",
                    title=f"Yêu cầu mua chờ duyệt: {code}",
                    detail=f"{float(req.requested_qty):g} {material.unit if material else 'kg'}",
                    href="/purchase",
                )
            )

    rank = {"danger": 0, "warn": 1, "info": 2}
    items.sort(key=lambda item: (rank.get(item.severity, 9), item.id))
    return AlertFeed(items=items, count=len(items))
