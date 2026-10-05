import csv
import io
import json
from datetime import datetime, timedelta
from urllib.parse import quote

import qrcode

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import (
    AuditLog,
    CCPStatus,
    LabTest,
    Material,
    MaterialType,
    OperationRecord,
    ProductionMaterialUsage,
    ProductionOrder,
    RecallSimulation,
    StockBatch,
    User,
    UserRole,
)
from app.services.quality_release import can_download_release_certificate
from app.services.csv_export import inventory_csv_rows, issues_csv_rows, period_inventory_csv_rows
from app.schemas import (
    AuditLogOut,
    AuditLogPage,
    BatchPassportOut,
    BatchTraceSuggest,
    IssueLedgerItem,
    PeriodInventoryItem,
    PeriodInventoryReport,
    RecallSimulationCreate,
    RecallSimulationResultOut,
    TraceNode,
    TraceResult,
)
from app.services.audit import short_ref
from app.services.audit_display import enrich_audit_log, step_label
from app.core.timezone import to_iso_utc, to_vn_display
from app.services.inventory_report import (
    PERIOD_NOTE,
    list_issue_rows,
    period_inventory,
    receipt_inbound_qty,
    summarize_inventory,
    summarize_inventory_batches,
)
from app.services.pdf_export import (
    gc_pdf,
    haccp_audit_pdf,
    inventory_pdf,
    issue_ledger_pdf,
    issue_voucher_pdf,
    material_balance_pdf,
    mixing_pdf,
    operation_pdf,
    period_inventory_pdf,
    receipt_pdf,
)
from app.services.recall import simulate_recall

router = APIRouter(prefix="/reports", tags=["reports"])

_TYPE_HINT = {
    MaterialType.NVL: "Nguyên liệu",
    MaterialType.TP: "Thành phẩm",
    MaterialType.BTP: "Bán thành phẩm",
}


def _trace_hint(batch: StockBatch, material: Material) -> str:
    kind = _TYPE_HINT.get(material.type, material.type.value)
    qty = float(batch.quantity)
    if qty > 0:
        return f"{kind} — còn {qty:.1f} kg trong kho"
    if material.type == MaterialType.TP:
        return f"{kind} — đã nhập kho thành phẩm"
    return f"{kind} — đã xuất / hết tồn"


@router.get("/trace-suggestions", response_model=list[BatchTraceSuggest])
def trace_batch_suggestions(
    q: str | None = Query(None, description="Lọc theo mã lô hoặc mã/tên vật tư"),
    limit: int = Query(25, ge=1, le=80),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = (
        db.query(StockBatch, Material)
        .join(Material, StockBatch.material_id == Material.id)
        .order_by(StockBatch.created_at.desc())
    )
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                StockBatch.batch_no.ilike(term),
                Material.code.ilike(term),
                Material.name.ilike(term),
            )
        )
    rows = query.limit(limit).all()
    return [
        BatchTraceSuggest(
            batch_no=batch.batch_no,
            material_code=material.code,
            material_name=material.name,
            material_type=material.type.value,
            quantity=float(batch.quantity),
            trace_hint=_trace_hint(batch, material),
        )
        for batch, material in rows
    ]


@router.get("/trace/{batch_no}", response_model=TraceResult)
def trace_batch(batch_no: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    batch = db.query(StockBatch).filter(StockBatch.batch_no == batch_no).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")

    material = db.query(Material).filter(Material.id == batch.material_id).first()
    node = TraceNode(
        batch_no=batch.batch_no,
        material_code=material.code if material else "",
        material_name=material.name if material else "",
        quantity=float(batch.quantity),
        ccp_status=batch.ccp1_status.value if batch.ccp1_status else None,
    )

    input_batches: list[TraceNode] = []
    production_orders: list[dict] = []
    output_batches: list[TraceNode] = []

    if batch.source_order_id:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == batch.source_order_id).first()
        if order:
            production_orders.append(
                {
                    "order_no": order.order_no,
                    "status": order.status.value,
                    "planned_qty": float(order.planned_qty),
                    "actual_qty": float(order.actual_qty) if order.actual_qty else None,
                }
            )
            usages = db.query(ProductionMaterialUsage).filter(ProductionMaterialUsage.order_id == order.id).all()
            for u in usages:
                ub = db.query(StockBatch).filter(StockBatch.id == u.batch_id).first()
                um = db.query(Material).filter(Material.id == ub.material_id).first() if ub else None
                if ub:
                    input_batches.append(
                        TraceNode(
                            batch_no=ub.batch_no,
                            material_code=um.code if um else "",
                            material_name=um.name if um else "",
                            quantity=float(u.quantity),
                            ccp_status=ub.ccp1_status.value if ub.ccp1_status else None,
                        )
                    )

    as_output = db.query(ProductionOrder).filter(ProductionOrder.output_batch_id == batch.id).first()
    if as_output:
        production_orders.append(
            {
                "order_no": as_output.order_no,
                "status": as_output.status.value,
                "planned_qty": float(as_output.planned_qty),
                "actual_qty": float(as_output.actual_qty) if as_output.actual_qty else None,
            }
        )
        usages = db.query(ProductionMaterialUsage).filter(ProductionMaterialUsage.order_id == as_output.id).all()
        for u in usages:
            if u.batch_id == batch.id:
                continue
            ub = db.query(StockBatch).filter(StockBatch.id == u.batch_id).first()
            um = db.query(Material).filter(Material.id == ub.material_id).first() if ub else None
            if ub:
                input_batches.append(
                    TraceNode(
                        batch_no=ub.batch_no,
                        material_code=um.code if um else "",
                        material_name=um.name if um else "",
                        quantity=float(u.quantity),
                        ccp_status=ub.ccp1_status.value if ub.ccp1_status else None,
                    )
                )

    as_input = db.query(ProductionMaterialUsage).filter(ProductionMaterialUsage.batch_id == batch.id).all()
    for u in as_input:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == u.order_id).first()
        if order and not any(p["order_no"] == order.order_no for p in production_orders):
            production_orders.append(
                {
                    "order_no": order.order_no,
                    "status": order.status.value,
                    "planned_qty": float(order.planned_qty),
                    "actual_qty": float(order.actual_qty) if order.actual_qty else None,
                }
            )
        if order and order.output_batch_id:
            ob = db.query(StockBatch).filter(StockBatch.id == order.output_batch_id).first()
            om = db.query(Material).filter(Material.id == ob.material_id).first() if ob else None
            if ob:
                output_batches.append(
                    TraceNode(
                        batch_no=ob.batch_no,
                        material_code=om.code if om else "",
                        material_name=om.name if om else "",
                        quantity=float(ob.quantity),
                        ccp_status=ob.ccp1_status.value if ob.ccp1_status else None,
                    )
                )

    direction = "TP" if material and material.type.value == "TP" else "NVL"
    if as_input:
        direction = "NVL"
    elif batch.source_order_id or as_output:
        direction = "TP"

    # Lô thành phẩm (TP) là đầu ra của mẻ SX — hiển thị chính lô đang tra cứu
    if (batch.source_order_id or as_output) and not any(o.batch_no == node.batch_no for o in output_batches):
        output_batches.insert(0, node)

    return TraceResult(
        batch_no=batch_no,
        direction=direction,
        input_batches=input_batches,
        production_orders=production_orders,
        output_batches=output_batches,
    )


@router.get("/batch-passport/{batch_no}", response_model=BatchPassportOut)
def batch_passport(
    batch_no: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    batch = db.query(StockBatch).filter(StockBatch.batch_no == batch_no).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    material = db.get(Material, batch.material_id)
    supplier_name = batch.supplier.name if batch.supplier else None
    source_order = None
    source = (
        db.get(ProductionOrder, batch.source_order_id)
        if batch.source_order_id
        else db.query(ProductionOrder).filter(ProductionOrder.output_batch_id == batch.id).first()
    )
    if source:
        source_order = {
            "order_no": source.order_no,
            "status": source.status.value,
            "planned_qty": float(source.planned_qty),
            "actual_qty": float(source.actual_qty) if source.actual_qty is not None else None,
        }
    downstream_orders = []
    usages = (
        db.query(ProductionMaterialUsage)
        .filter(ProductionMaterialUsage.batch_id == batch.id)
        .all()
    )
    if usages:
        orders = (
            db.query(ProductionOrder)
            .filter(ProductionOrder.id.in_({usage.order_id for usage in usages}))
            .all()
        )
        downstream_orders = [
            {
                "order_no": order.order_no,
                "status": order.status.value,
                "output_batch_no": order.output_batch.batch_no if order.output_batch else None,
            }
            for order in orders
        ]
    tests = (
        db.query(LabTest)
        .filter(LabTest.batch_id == batch.id)
        .order_by(LabTest.created_at)
        .all()
    )
    ccp_results = [
        {
            "test_type": test.test_type,
            "status": test.result_status.value,
            "c14": float(test.c14) if test.c14 is not None else None,
            "t_ca_percent": (
                float(test.t_ca_percent) if test.t_ca_percent is not None else None
            ),
            "tested_at": to_iso_utc(test.created_at),
        }
        for test in tests
    ]
    return BatchPassportOut(
        batch_no=batch.batch_no,
        material_code=material.code if material else "",
        material_name=material.name if material else "",
        material_type=material.type.value if material else "",
        supplier_name=supplier_name,
        received_at=batch.created_at,
        mfg_date=batch.mfg_date,
        expiry_date=batch.expiry_date,
        quantity=float(batch.quantity),
        quality_status=batch.quality_status.value,
        ccp_status=batch.ccp1_status.value,
        ccp_results=ccp_results,
        source_order=source_order,
        downstream_orders=downstream_orders,
        certificate_url=(
            f"/api/v1/quality/batches/{batch.id}/certificate.pdf"
            if can_download_release_certificate(db, batch)
            else None
        ),
    )


@router.get("/batch-qr/{batch_no}")
def batch_qr(
    batch_no: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    exists = db.query(StockBatch.id).filter(StockBatch.batch_no == batch_no).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    image = qrcode.make(f"/trace?batch={quote(batch_no, safe='')}")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return Response(
        output.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="qr-{batch_no}.png"'},
    )


@router.post(
    "/recall-simulations",
    response_model=RecallSimulationResultOut,
    status_code=201,
)
def create_recall_simulation(
    payload: RecallSimulationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.attp, UserRole.ql_nm, UserRole.admin)),
):
    batch_no = payload.batch_no.strip()
    reason = payload.reason.strip()
    if not batch_no or not reason:
        raise HTTPException(status_code=422, detail="Mã lô và lý do là bắt buộc")
    batch = db.query(StockBatch).filter(StockBatch.batch_no == batch_no).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    result = simulate_recall(db, batch.id)
    simulation = RecallSimulation(
        batch_id=batch.id,
        reason=reason,
        initiated_by_id=user.id,
        duration_ms=result.duration_ms,
        result_json=json.dumps(result.to_dict(), ensure_ascii=False),
    )
    db.add(simulation)
    db.flush()
    db.add(
        AuditLog(
            user_id=user.id,
            action="simulate_recall",
            entity="recall_simulation",
            entity_id=str(simulation.id),
            detail=f"{batch.batch_no}: {reason}",
        )
    )
    db.commit()
    db.refresh(simulation)
    result_data = result.to_dict()
    return RecallSimulationResultOut(
        id=simulation.id,
        root_batch_no=result.root_batch_no,
        reason=simulation.reason,
        initiated_by_id=simulation.initiated_by_id,
        initiated_at=simulation.created_at,
        duration_ms=simulation.duration_ms or 0,
        affected_batches=result_data["affected_batches"],
        affected_orders=result_data["affected_orders"],
    )


@router.get("/recall-simulations/{simulation_id}/csv")
def export_recall_simulation_csv(
    simulation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.attp, UserRole.ql_nm, UserRole.admin)),
):
    simulation = db.get(RecallSimulation, simulation_id)
    if not simulation or not simulation.result_json:
        raise HTTPException(status_code=404, detail="Không tìm thấy mô phỏng thu hồi")
    result = json.loads(simulation.result_json)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=["batch_no", "material", "order_no", "quantity", "quality_status"],
    )
    writer.writeheader()
    for item in result.get("affected_batches", []):
        writer.writerow(
            {
                "batch_no": item["batch_no"],
                "material": item["material"],
                "order_no": item.get("order_no") or "",
                "quantity": item["quantity"],
                "quality_status": item["quality_status"],
            }
        )
    content = ("\ufeff" + output.getvalue()).encode("utf-8")
    return Response(
        content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="recall-simulation-{simulation.id}.csv"'
            )
        },
    )


def _inventory_view(view: str) -> str:
    if view not in {"material", "batch"}:
        raise HTTPException(status_code=400, detail="view phải là material hoặc batch")
    return view


def _inventory_rows(db: Session, view: str, material_type: str | None):
    try:
        if view == "batch":
            return summarize_inventory_batches(db, material_type)
        return summarize_inventory(db, material_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _parse_day(value: str | None, *, end: bool = False) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Ngày phải dạng YYYY-MM-DD") from exc
    if end:
        return parsed.replace(hour=23, minute=59, second=59)
    return parsed


def _period_bounds(date_from: str | None, date_to: str | None) -> tuple[datetime, datetime, str, str]:
    today = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = _parse_day(date_from) or month_start
    end = _parse_day(date_to, end=True) or today
    if start > end:
        start, end = (
            end.replace(hour=0, minute=0, second=0, microsecond=0),
            start.replace(hour=23, minute=59, second=59, microsecond=0),
        )
    return start, end, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _day_pair(
    date_from: str | None,
    date_to: str | None,
    from_alias: str | None,
    to_alias: str | None,
) -> tuple[str | None, str | None]:
    return date_from or from_alias, date_to or to_alias


def _period_items(db: Session, date_from: str | None, date_to: str | None, material_type: str | None):
    start, end, from_label, to_label = _period_bounds(date_from, date_to)
    try:
        rows = period_inventory(db, start, end, material_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return rows, from_label, to_label


def _issue_items(rows) -> list[IssueLedgerItem]:
    return [
        IssueLedgerItem(
            id=row.id,
            reference_no=row.reference_no,
            created_at=to_iso_utc(row.created_at),
            created_at_vn=to_vn_display(row.created_at),
            batch_id=row.batch_id,
            batch_no=row.batch_no,
            material_code=row.material_code,
            material_name=row.material_name,
            quantity=row.quantity,
            issue_kind=row.issue_kind,
            order_no=row.order_no,
            created_by_name=row.created_by_name,
            notes=row.notes,
        )
        for row in rows
    ]


@router.get("/inventory/export")
def export_inventory_csv(
    view: str = Query("material"),
    type: str | None = Query(None, description="NVL | BTP | TP"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    view = _inventory_view(view)
    rows = _inventory_rows(db, view, type)
    content = inventory_csv_rows(rows, view=view)
    filename = f"ton-kho-{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/inventory/export/pdf")
def export_inventory_pdf(
    view: str = Query("material"),
    type: str | None = Query(None, description="NVL | BTP | TP"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    view = _inventory_view(view)
    rows = _inventory_rows(db, view, type)
    pdf = inventory_pdf(rows, view=view)
    filename = f"ton-kho-{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/inventory/period", response_model=PeriodInventoryReport)
def inventory_period(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    from_alias: str | None = Query(None, alias="from"),
    to_alias: str | None = Query(None, alias="to"),
    type: str | None = Query(None, description="NVL | BTP | TP"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    start, end = _day_pair(date_from, date_to, from_alias, to_alias)
    rows, from_label, to_label = _period_items(db, start, end, type)
    return PeriodInventoryReport(
        date_from=from_label,
        date_to=to_label,
        note=PERIOD_NOTE,
        items=[
            PeriodInventoryItem(
                material_id=row.material_id,
                material_code=row.material_code,
                material_name=row.material_name,
                material_type=row.material_type,
                unit=row.unit,
                opening=row.opening,
                inbound=row.inbound,
                outbound=row.outbound,
                adjustment=row.adjustment,
                closing=row.closing,
            )
            for row in rows
        ],
    )


@router.get("/inventory/period/export")
def export_inventory_period_csv(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    from_alias: str | None = Query(None, alias="from"),
    to_alias: str | None = Query(None, alias="to"),
    type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    start, end = _day_pair(date_from, date_to, from_alias, to_alias)
    rows, from_label, to_label = _period_items(db, start, end, type)
    content = period_inventory_csv_rows(rows, date_from=from_label, date_to=to_label)
    filename = f"ton-kho-ky-{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/inventory/period/export/pdf")
def export_inventory_period_pdf(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    from_alias: str | None = Query(None, alias="from"),
    to_alias: str | None = Query(None, alias="to"),
    type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    start, end = _day_pair(date_from, date_to, from_alias, to_alias)
    rows, from_label, to_label = _period_items(db, start, end, type)
    pdf = period_inventory_pdf(rows, date_from=from_label, date_to=to_label)
    filename = f"ton-kho-ky-{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/issues", response_model=list[IssueLedgerItem])
def list_issues(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    from_alias: str | None = Query(None, alias="from", description="YYYY-MM-DD"),
    to_alias: str | None = Query(None, alias="to", description="YYYY-MM-DD"),
    material_id: int | None = None,
    batch_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    start, end = _day_pair(date_from, date_to, from_alias, to_alias)
    rows = list_issue_rows(
        db,
        date_from=_parse_day(start),
        date_to=_parse_day(end, end=True),
        material_id=material_id,
        batch_id=batch_id,
    )
    return _issue_items(rows)


@router.get("/issues/export")
def export_issues_csv(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    from_alias: str | None = Query(None, alias="from"),
    to_alias: str | None = Query(None, alias="to"),
    material_id: int | None = None,
    batch_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    start, end = _day_pair(date_from, date_to, from_alias, to_alias)
    rows = list_issue_rows(
        db,
        date_from=_parse_day(start),
        date_to=_parse_day(end, end=True),
        material_id=material_id,
        batch_id=batch_id,
    )
    content = issues_csv_rows(rows)
    filename = f"so-xuat-kho-{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/issues/export/pdf")
def export_issues_pdf(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    from_alias: str | None = Query(None, alias="from"),
    to_alias: str | None = Query(None, alias="to"),
    material_id: int | None = None,
    batch_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    start, end = _day_pair(date_from, date_to, from_alias, to_alias)
    rows = list_issue_rows(
        db,
        date_from=_parse_day(start),
        date_to=_parse_day(end, end=True),
        material_id=material_id,
        batch_id=batch_id,
    )
    pdf = issue_ledger_pdf(rows)
    filename = f"so-xuat-kho-{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/issues/{movement_id}/pdf")
def export_issue_voucher_pdf(
    movement_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows = list_issue_rows(db, movement_id=movement_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu xuất")
    pdf = issue_voucher_pdf(rows[0])
    filename = f"{short_ref(rows[0].reference_no)}.pdf"
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/audit", response_model=AuditLogPage)
def audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    limit: int | None = Query(None, ge=1, le=300, description="Tương thích cũ — bỏ dần"),
    entity: str | None = None,
    action: str | None = None,
    since: str | None = Query(None, description="YYYY-MM-DD — lọc từ ngày (giờ VN)"),
    until: str | None = Query(None, description="YYYY-MM-DD — lọc đến ngày (giờ VN)"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.attp)),
):
    q = db.query(AuditLog, User).outerjoin(User, AuditLog.user_id == User.id).order_by(AuditLog.created_at.desc())
    if entity:
        q = q.filter(AuditLog.entity == entity)
    if action:
        q = q.filter(AuditLog.action == action)
    if since:
        try:
            start = datetime.strptime(since, "%Y-%m-%d")
            q = q.filter(AuditLog.created_at >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="since phải dạng YYYY-MM-DD")
    if until:
        try:
            end = datetime.strptime(until, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            q = q.filter(AuditLog.created_at <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="until phải dạng YYYY-MM-DD")

    size = limit if limit is not None else page_size
    total = q.count()
    pages = max(1, (total + size - 1) // size) if total else 1
    current = min(page, pages)
    offset = (current - 1) * size
    rows = q.offset(offset).limit(size).all()
    items = []
    for log, user in rows:
        entity_id, detail = enrich_audit_log(db, log)
        items.append(
            AuditLogOut(
                id=log.id,
                action=log.action,
                entity=log.entity,
                entity_id=entity_id,
                detail=detail,
                user_name=user.full_name if user else None,
                created_at=to_iso_utc(log.created_at),
            )
        )
    return AuditLogPage(items=items, total=total, page=current, page_size=size, pages=pages)


@router.get("/haccp-monitor")
def haccp_monitor(
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    batches = (
        db.query(StockBatch)
        .join(Material, StockBatch.material_id == Material.id)
        .filter(StockBatch.created_at >= since, Material.type == MaterialType.NVL)
        .order_by(StockBatch.created_at.desc())
        .all()
    )
    ops = (
        db.query(OperationRecord, ProductionOrder)
        .join(ProductionOrder, OperationRecord.order_id == ProductionOrder.id)
        .filter(OperationRecord.created_at >= since)
        .order_by(OperationRecord.created_at.desc())
        .all()
    )
    tests = db.query(LabTest).filter(LabTest.created_at >= since).order_by(LabTest.created_at.desc()).all()
    return {
        "period_days": days,
        "ccp1_records": [
            {
                "batch_no": b.batch_no,
                "c14": float(b.ccp1_c14) if b.ccp1_c14 else None,
                "status": b.ccp1_status.value,
                "at": to_iso_utc(b.created_at),
            }
            for b in batches
        ],
        "ccp2_records": [
            {
                "order_no": order.order_no,
                "step": step_label(op.step),
                "t_top": float(op.t_top) if op.t_top else None,
                "t_ca_percent": float(op.t_ca_percent) if op.t_ca_percent else None,
                "status": op.ccp2_status.value,
                "at": to_iso_utc(op.created_at),
            }
            for op, order in ops
        ],
        "lab_tests": len(tests),
        "fail_count": sum(1 for b in batches if b.ccp1_status == CCPStatus.fail)
        + sum(1 for op, _ in ops if op.ccp2_status == CCPStatus.fail),
    }


@router.get("/haccp-monitor/export")
def export_haccp_pdf(days: int = Query(14, ge=1, le=90), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    since = datetime.utcnow() - timedelta(days=days)
    records: list[tuple[str, str, str, str]] = []
    for b in (
        db.query(StockBatch)
        .join(Material, StockBatch.material_id == Material.id)
        .filter(StockBatch.created_at >= since, Material.type == MaterialType.NVL)
        .order_by(StockBatch.created_at.desc())
        .all()
    ):
        c14 = f"{float(b.ccp1_c14)}" if b.ccp1_c14 else "—"
        records.append((to_vn_display(b.created_at), "CCP1", b.batch_no, f"{c14} / {b.ccp1_status.value}"))
    for op, order in (
        db.query(OperationRecord, ProductionOrder)
        .join(ProductionOrder, OperationRecord.order_id == ProductionOrder.id)
        .filter(OperationRecord.created_at >= since)
        .order_by(OperationRecord.created_at.desc())
        .all()
    ):
        detail = f"{order.order_no} — {step_label(op.step)}"
        if op.t_top is not None:
            detail += f" / {float(op.t_top)}°C"
        if op.t_ca_percent is not None:
            detail += f" / {float(op.t_ca_percent)}%"
        records.append((to_vn_display(op.created_at), "CCP2", detail, op.ccp2_status.value))
    pdf = haccp_audit_pdf(records[:200])
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="haccp-audit.pdf"'})


@router.get("/receipt/{batch_id}/pdf")
def export_receipt_pdf(batch_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    batch = db.query(StockBatch).filter(StockBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    mat = db.query(Material).filter(Material.id == batch.material_id).first()
    pdf = receipt_pdf(
        batch.batch_no,
        mat.name if mat else "",
        receipt_inbound_qty(db, batch.id, float(batch.quantity)),
        float(batch.ccp1_c14) if batch.ccp1_c14 else None,
        batch.ccp1_status.value,
    )
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{short_ref(batch.batch_no)}.pdf"'})


@router.get("/operation/{record_id}/pdf")
def export_operation_pdf(record_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rec = db.query(OperationRecord).filter(OperationRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Không tìm thấy biên bản vận hành")
    order = db.query(ProductionOrder).filter(ProductionOrder.id == rec.order_id).first()
    pdf = operation_pdf(
        order.order_no if order else str(rec.order_id),
        rec.step,
        float(rec.t_top) if rec.t_top else None,
        float(rec.t_ca_percent) if rec.t_ca_percent else None,
        rec.ccp2_status.value,
    )
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="op-{record_id}.pdf"'})


@router.get("/balance/{order_id}/pdf")
def export_balance_pdf(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ")
    usages = db.query(ProductionMaterialUsage).filter(ProductionMaterialUsage.order_id == order.id).all()
    inputs = []
    for u in usages:
        b = db.query(StockBatch).filter(StockBatch.id == u.batch_id).first()
        inputs.append((b.batch_no if b else "", float(u.quantity)))
    output = float(order.actual_qty) if order.actual_qty else 0.0
    loss = max(sum(q for _, q in inputs) - output, 0.0)
    pdf = material_balance_pdf(order.order_no, inputs, output, loss)
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="balance-{short_ref(order.order_no)}.pdf"'})


@router.get("/mixing/{order_id}/pdf")
def export_mixing_pdf(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models import MixingReport

    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ")
    report = db.query(MixingReport).filter(MixingReport.order_id == order_id).order_by(MixingReport.created_at.desc()).first()
    pdf = mixing_pdf(order.order_no, report.formula if report else None, float(report.mixed_qty) if report else 0.0)
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="mixing-{short_ref(order.order_no)}.pdf"'})


@router.get("/lab/{test_id}/pdf")
def export_gc_pdf(test_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả kiểm nghiệm")
    label = f"KQ-{test.id}"
    if test.batch_id:
        batch = db.query(StockBatch).filter(StockBatch.id == test.batch_id).first()
        if batch:
            label = short_ref(batch.batch_no)
    elif test.order_id:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == test.order_id).first()
        if order:
            label = short_ref(order.order_no)
    pdf = gc_pdf(
        label,
        float(test.c14) if test.c14 else None,
        float(test.t_ca_percent) if test.t_ca_percent else None,
        test.result_status.value,
    )
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="gc-{test_id}.pdf"'})


@router.get("/ccp-summary")
def ccp_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ccp1_pending = db.query(StockBatch).filter(StockBatch.ccp1_status == CCPStatus.pending).count()
    ccp1_fail = db.query(StockBatch).filter(StockBatch.ccp1_status == CCPStatus.fail).count()
    ccp2_fail = db.query(OperationRecord).filter(OperationRecord.ccp2_status == CCPStatus.fail).count()
    return {"ccp1_pending": ccp1_pending, "ccp1_fail": ccp1_fail, "ccp2_fail": ccp2_fail}
