"""Một nguồn sự thật cho tồn kho và sổ xuất — dùng chung UI và file CSV/PDF."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import (
    CCPStatus,
    Material,
    MaterialReservation,
    MaterialType,
    MovementType,
    ProductionOrder,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    StockMovement,
    User,
)

from app.services.audit import ref_seq, short_ref

QUALITY_LABELS = {
    QualityStatus.quarantine: "Cách ly",
    QualityStatus.sampling: "Đang lấy mẫu",
    QualityStatus.under_test: "Đang kiểm nghiệm",
    QualityStatus.awaiting_release: "Chờ giải phóng",
    QualityStatus.released: "Đã giải phóng",
    QualityStatus.rejected: "Từ chối",
    QualityStatus.retest: "Kiểm nghiệm lại",
}

CCP_LABELS = {
    CCPStatus.pending: "Chờ kiểm tra",
    CCPStatus.pass_: "Đạt",
    CCPStatus.fail: "Không đạt",
}

TYPE_LABELS = {
    MaterialType.NVL: "Nguyên liệu",
    MaterialType.TP: "Thành phẩm",
    MaterialType.BTP: "Bán thành phẩm",
}

STOCK_FORMULA_NOTE = (
    "Tồn vật lý = tổng kg trên lô. Khả dụng = lô đã giải phóng, đạt CCP1, còn hạn, trừ giữ chỗ. "
    "Không phải báo cáo kế toán đã khóa sổ."
)

PERIOD_NOTE = "Tính ngược từ sổ movement; không phải snapshot kế toán đã khóa sổ."


def quality_label(status: QualityStatus | str | None) -> str:
    if status is None:
        return "—"
    if isinstance(status, QualityStatus):
        return QUALITY_LABELS.get(status, status.value)
    try:
        return QUALITY_LABELS.get(QualityStatus(status), status)
    except ValueError:
        return str(status)


def ccp_label(status: CCPStatus | str | None) -> str:
    if status is None:
        return "—"
    if isinstance(status, CCPStatus):
        return CCP_LABELS.get(status, status.value)
    try:
        key = CCPStatus.pass_ if status == "pass" else CCPStatus(status)
        return CCP_LABELS.get(key, status)
    except ValueError:
        return str(status)


def type_label(value: MaterialType | str) -> str:
    if isinstance(value, MaterialType):
        return TYPE_LABELS.get(value, value.value)
    try:
        return TYPE_LABELS.get(MaterialType(value), value)
    except ValueError:
        return str(value)


def is_issuable(batch: StockBatch, today: date | None = None) -> bool:
    today = today or date.today()
    if batch.quality_status != QualityStatus.released:
        return False
    if batch.ccp1_status != CCPStatus.pass_:
        return False
    if batch.expiry_date and batch.expiry_date < today:
        return False
    return True


@dataclass
class InventoryRow:
    material_id: int
    material_code: str
    material_name: str
    material_type: str
    material_type_label: str
    unit: str
    on_hand: float
    reserved: float
    available: float
    nearest_expiry: date | None
    min_stock: float
    low_stock: bool
    quality_label: str
    image_url: str | None = None

    @property
    def alert_label(self) -> str:
        return "Tồn thấp" if self.low_stock else "Bình thường"


@dataclass
class InventoryBatchRow:
    material_id: int
    material_code: str
    material_name: str
    material_type: str
    material_type_label: str
    unit: str
    batch_id: int
    batch_no: str
    on_hand: float
    reserved: float
    available: float
    expiry_date: date | None
    ccp1_status: str
    quality_status: str
    quality_label: str
    ccp1_label: str


@dataclass
class IssueRow:
    id: int
    reference_no: str
    created_at: datetime
    batch_id: int
    batch_no: str
    material_code: str
    material_name: str
    quantity: float
    remaining_qty: float
    expiry_date: date | None
    ccp1_status: str
    quality_status: str
    quality_label: str
    ccp1_label: str
    production_order_id: int | None
    order_no: str | None
    created_by_name: str | None
    notes: str | None

    @property
    def issue_kind(self) -> str:
        if self.order_no:
            return f"Xuất cho mẻ {short_ref(self.order_no)}"
        return "Xuất kho thủ công"


@dataclass
class PeriodInventoryRow:
    material_id: int
    material_code: str
    material_name: str
    material_type: str
    material_type_label: str
    unit: str
    opening: float
    inbound: float
    outbound: float
    adjustment: float
    closing: float


def _reserved_by_batch(db: Session, batch_ids: list[int]) -> dict[int, float]:
    reserved: dict[int, float] = {batch_id: 0.0 for batch_id in batch_ids}
    if not batch_ids:
        return reserved
    for item in (
        db.query(MaterialReservation)
        .filter(
            MaterialReservation.batch_id.in_(batch_ids),
            MaterialReservation.status == ReservationStatus.active,
        )
        .all()
    ):
        reserved[item.batch_id] = reserved.get(item.batch_id, 0.0) + float(item.quantity)
    return reserved


def _parse_material_type(value: str | None) -> MaterialType | None:
    if not value:
        return None
    try:
        return MaterialType(value)
    except ValueError as exc:
        raise ValueError("type phải là NVL, BTP hoặc TP") from exc


def summarize_inventory_batches(
    db: Session,
    material_type: str | None = None,
) -> list[InventoryBatchRow]:
    parsed = _parse_material_type(material_type)
    query = (
        db.query(StockBatch, Material)
        .join(Material, StockBatch.material_id == Material.id)
        .filter(Material.is_active.is_(True), StockBatch.quantity > 0)
    )
    if parsed is not None:
        query = query.filter(Material.type == parsed)
    pairs = query.all()
    reserved_map = _reserved_by_batch(db, [batch.id for batch, _ in pairs])
    today = date.today()
    rows: list[InventoryBatchRow] = []
    for batch, material in pairs:
        on_hand = float(batch.quantity)
        reserved = reserved_map.get(batch.id, 0.0)
        available = max(on_hand - reserved, 0.0) if is_issuable(batch, today) else 0.0
        rows.append(
            InventoryBatchRow(
                material_id=material.id,
                material_code=material.code,
                material_name=material.name,
                material_type=material.type.value,
                material_type_label=type_label(material.type),
                unit=material.unit,
                batch_id=batch.id,
                batch_no=batch.batch_no,
                on_hand=on_hand,
                reserved=reserved,
                available=available,
                expiry_date=batch.expiry_date,
                ccp1_status=batch.ccp1_status.value,
                quality_status=batch.quality_status.value,
                quality_label=quality_label(batch.quality_status),
                ccp1_label=ccp_label(batch.ccp1_status),
            )
        )
    rows.sort(
        key=lambda row: (
            row.material_code,
            row.expiry_date is None,
            row.expiry_date or date.max,
            ref_seq(row.batch_no),
            row.batch_id,
        )
    )
    return rows


def summarize_inventory(
    db: Session,
    material_type: str | None = None,
) -> list[InventoryRow]:
    parsed = _parse_material_type(material_type)
    query = db.query(Material).filter(Material.is_active.is_(True)).order_by(Material.code)
    if parsed is not None:
        query = query.filter(Material.type == parsed)
    materials = query.all()
    lots = summarize_inventory_batches(db, material_type)
    by_material: dict[int, list[InventoryBatchRow]] = {}
    for lot in lots:
        by_material.setdefault(lot.material_id, []).append(lot)

    result: list[InventoryRow] = []
    for material in materials:
        group = by_material.get(material.id, [])
        on_hand = sum(item.on_hand for item in group)
        reserved = sum(item.reserved for item in group)
        available = sum(item.available for item in group)
        expiries = [item.expiry_date for item in group if item.expiry_date and item.on_hand > 0]
        labels: list[str] = []
        for item in group:
            if item.on_hand > 0 and item.quality_label not in labels:
                labels.append(item.quality_label)
        min_stock = float(material.min_stock)
        result.append(
            InventoryRow(
                material_id=material.id,
                material_code=material.code,
                material_name=material.name,
                material_type=material.type.value,
                material_type_label=type_label(material.type),
                unit=material.unit,
                on_hand=on_hand,
                reserved=reserved,
                available=available,
                nearest_expiry=min(expiries) if expiries else None,
                min_stock=min_stock,
                low_stock=available < min_stock,
                quality_label="; ".join(labels) if labels else "Chưa có lô",
                image_url=material.image_url,
            )
        )
    return result


def list_issue_rows(
    db: Session,
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    material_id: int | None = None,
    batch_id: int | None = None,
    movement_id: int | None = None,
) -> list[IssueRow]:
    query = (
        db.query(StockMovement, StockBatch, Material, User, ProductionOrder)
        .join(StockBatch, StockMovement.batch_id == StockBatch.id)
        .join(Material, StockBatch.material_id == Material.id)
        .outerjoin(User, StockMovement.created_by_id == User.id)
        .outerjoin(ProductionOrder, StockMovement.production_order_id == ProductionOrder.id)
        .filter(StockMovement.movement_type == MovementType.OUT)
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
    )
    if date_from is not None:
        query = query.filter(StockMovement.created_at >= date_from)
    if date_to is not None:
        query = query.filter(StockMovement.created_at <= date_to)
    if material_id is not None:
        query = query.filter(StockBatch.material_id == material_id)
    if batch_id is not None:
        query = query.filter(StockMovement.batch_id == batch_id)
    if movement_id is not None:
        query = query.filter(StockMovement.id == movement_id)

    rows: list[IssueRow] = []
    for movement, batch, material, user, order in query.all():
        rows.append(
            IssueRow(
                id=movement.id,
                reference_no=movement.reference_no,
                created_at=movement.created_at,
                batch_id=batch.id,
                batch_no=batch.batch_no,
                material_code=material.code,
                material_name=material.name,
                quantity=float(movement.quantity),
                remaining_qty=float(batch.quantity),
                expiry_date=batch.expiry_date,
                ccp1_status=batch.ccp1_status.value,
                quality_status=batch.quality_status.value,
                quality_label=quality_label(batch.quality_status),
                ccp1_label=ccp_label(batch.ccp1_status),
                production_order_id=movement.production_order_id,
                order_no=order.order_no if order else None,
                created_by_name=user.full_name if user else None,
                notes=movement.notes,
            )
        )
    return rows


def _is_adjustment(movement: StockMovement) -> bool:
    ref = (movement.reference_no or "").upper()
    return ref.startswith("HT") or "hoàn tồn" in (movement.notes or "").lower()


def period_inventory(
    db: Session,
    date_from: datetime,
    date_to: datetime,
    material_type: str | None = None,
) -> list[PeriodInventoryRow]:
    snapshot = summarize_inventory(db, material_type)
    inbound: dict[int, float] = defaultdict(float)
    outbound: dict[int, float] = defaultdict(float)
    adjustment: dict[int, float] = defaultdict(float)
    movements = (
        db.query(StockMovement, StockBatch)
        .join(StockBatch, StockMovement.batch_id == StockBatch.id)
        .filter(StockMovement.created_at >= date_from, StockMovement.created_at <= date_to)
        .all()
    )
    for movement, batch in movements:
        qty = float(movement.quantity)
        if movement.movement_type == MovementType.OUT:
            outbound[batch.material_id] += qty
        elif _is_adjustment(movement):
            adjustment[batch.material_id] += qty
        else:
            inbound[batch.material_id] += qty

    rows: list[PeriodInventoryRow] = []
    for item in snapshot:
        inn = inbound.get(item.material_id, 0.0)
        out = outbound.get(item.material_id, 0.0)
        adj = adjustment.get(item.material_id, 0.0)
        closing = item.on_hand
        opening = closing - inn - adj + out
        rows.append(
            PeriodInventoryRow(
                material_id=item.material_id,
                material_code=item.material_code,
                material_name=item.material_name,
                material_type=item.material_type,
                material_type_label=item.material_type_label,
                unit=item.unit,
                opening=opening,
                inbound=inn,
                outbound=out,
                adjustment=adj,
                closing=closing,
            )
        )
    return rows


def receipt_inbound_qty(db: Session, batch_id: int, fallback: float) -> float:
    movements = (
        db.query(StockMovement)
        .filter(
            StockMovement.batch_id == batch_id,
            StockMovement.movement_type == MovementType.IN,
        )
        .order_by(StockMovement.created_at.asc(), StockMovement.id.asc())
        .all()
    )
    for movement in movements:
        if _is_adjustment(movement):
            continue
        return float(movement.quantity)
    return fallback
