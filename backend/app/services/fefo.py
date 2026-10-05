from dataclasses import dataclass
from datetime import date

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models import (
    CCPStatus,
    MaterialReservation,
    QualityStatus,
    ReservationStatus,
    StockBatch,
)


@dataclass(frozen=True)
class FefoAllocation:
    batch_id: int
    batch_no: str
    qty: float
    expiry_date: date | None
    on_hand_qty: float
    reserved_qty: float
    available_qty: float


def active_reserved_subquery():
    return (
        func.coalesce(
            func.sum(
                case(
                    (
                        MaterialReservation.status == ReservationStatus.active,
                        MaterialReservation.quantity,
                    ),
                    else_=0,
                )
            ),
            0,
        )
        .select()
        .where(MaterialReservation.batch_id == StockBatch.id)
        .scalar_subquery()
    )


def suggest_fefo(
    db: Session,
    material_id: int,
    warehouse_id: int,
    required_qty: float,
) -> list[FefoAllocation]:
    if required_qty <= 0:
        return []

    reserved = active_reserved_subquery()
    available = StockBatch.quantity - reserved
    filters = (
        StockBatch.material_id == material_id,
        StockBatch.warehouse_id == warehouse_id,
        StockBatch.quality_status == QualityStatus.released,
        StockBatch.ccp1_status == CCPStatus.pass_,
        StockBatch.quantity > 0,
        (StockBatch.expiry_date.is_(None)) | (StockBatch.expiry_date >= date.today()),
    )
    expiry_order = (
        case((StockBatch.expiry_date.is_(None), 1), else_=0).asc(),
        StockBatch.expiry_date.asc(),
        StockBatch.created_at.asc(),
        StockBatch.id.asc(),
    )
    if db.get_bind().dialect.name == "postgresql":
        (
            db.query(StockBatch)
            .filter(*filters)
            .order_by(*expiry_order)
            .with_for_update(of=StockBatch)
            .all()
        )

    query = (
        db.query(StockBatch, reserved.label("reserved_qty"))
        .filter(
            *filters,
            available > 0,
        )
        .order_by(*expiry_order)
    )

    remaining = float(required_qty)
    allocations: list[FefoAllocation] = []
    for batch, reserved_qty in query.all():
        on_hand = float(batch.quantity)
        reserved_value = float(reserved_qty or 0)
        available_value = max(on_hand - reserved_value, 0)
        allocated = min(available_value, remaining)
        if allocated <= 0:
            continue
        allocations.append(
            FefoAllocation(
                batch_id=batch.id,
                batch_no=batch.batch_no,
                qty=allocated,
                expiry_date=batch.expiry_date,
                on_hand_qty=on_hand,
                reserved_qty=reserved_value,
                available_qty=available_value,
            )
        )
        remaining -= allocated
        if remaining <= 1e-9:
            break
    return allocations
