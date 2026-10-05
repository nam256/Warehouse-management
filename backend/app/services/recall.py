from dataclasses import asdict, dataclass
from time import perf_counter

from sqlalchemy.orm import Session

from app.models import Material, ProductionMaterialUsage, ProductionOrder, StockBatch


@dataclass(frozen=True)
class AffectedBatch:
    batch_id: int
    batch_no: str
    material: str
    order_no: str | None
    quantity: float
    quality_status: str
    depth: int


@dataclass(frozen=True)
class AffectedOrder:
    order_id: int
    order_no: str
    input_batch_no: str
    output_batch_no: str
    quantity: float
    depth: int


@dataclass(frozen=True)
class RecallResult:
    root_batch_no: str
    affected_batches: list[AffectedBatch]
    affected_orders: list[AffectedOrder]
    duration_ms: int

    def to_dict(self) -> dict:
        return asdict(self)


def _batch_item(
    batch: StockBatch,
    material_name: str,
    *,
    depth: int,
    order_no: str | None = None,
    quantity: float | None = None,
) -> AffectedBatch:
    return AffectedBatch(
        batch_id=batch.id,
        batch_no=batch.batch_no,
        material=material_name,
        order_no=order_no,
        quantity=float(batch.quantity if quantity is None else quantity),
        quality_status=batch.quality_status.value,
        depth=depth,
    )


def simulate_recall(db: Session, root_batch_id: int) -> RecallResult:
    """Traverse every downstream production output without changing business data."""
    started = perf_counter()
    root = db.get(StockBatch, root_batch_id)
    if root is None:
        raise ValueError("Không tìm thấy lô")

    root_material = db.get(Material, root.material_id)
    affected_batches = [
        _batch_item(root, root_material.name if root_material else "", depth=0)
    ]
    affected_orders: list[AffectedOrder] = []
    visited_batch_ids = {root.id}
    visited_order_ids: set[int] = set()
    frontier = {root.id: root}
    depth = 0

    while frontier:
        usages = (
            db.query(ProductionMaterialUsage)
            .filter(ProductionMaterialUsage.batch_id.in_(frontier))
            .all()
        )
        usages_by_order: dict[int, list[ProductionMaterialUsage]] = {}
        for usage in usages:
            if usage.order_id not in visited_order_ids:
                usages_by_order.setdefault(usage.order_id, []).append(usage)
        if not usages_by_order:
            break

        orders = (
            db.query(ProductionOrder)
            .filter(ProductionOrder.id.in_(usages_by_order))
            .all()
        )
        output_ids = {
            order.output_batch_id
            for order in orders
            if order.output_batch_id is not None and order.output_batch_id not in visited_batch_ids
        }
        outputs = (
            db.query(StockBatch).filter(StockBatch.id.in_(output_ids)).all()
            if output_ids
            else []
        )
        output_by_id = {batch.id: batch for batch in outputs}
        material_ids = {batch.material_id for batch in outputs}
        materials = (
            db.query(Material).filter(Material.id.in_(material_ids)).all()
            if material_ids
            else []
        )
        material_name_by_id = {material.id: material.name for material in materials}
        next_frontier: dict[int, StockBatch] = {}

        for order in orders:
            visited_order_ids.add(order.id)
            output = output_by_id.get(order.output_batch_id)
            if output is None:
                continue
            matching_usage = usages_by_order[order.id][0]
            input_batch = frontier[matching_usage.batch_id]
            output_quantity = (
                float(order.actual_qty) if order.actual_qty is not None else float(output.quantity)
            )
            affected_orders.append(
                AffectedOrder(
                    order_id=order.id,
                    order_no=order.order_no,
                    input_batch_no=input_batch.batch_no,
                    output_batch_no=output.batch_no,
                    quantity=float(matching_usage.quantity),
                    depth=depth + 1,
                )
            )
            affected_batches.append(
                _batch_item(
                    output,
                    material_name_by_id.get(output.material_id, ""),
                    depth=depth + 1,
                    order_no=order.order_no,
                    quantity=output_quantity,
                )
            )
            visited_batch_ids.add(output.id)
            next_frontier[output.id] = output

        frontier = next_frontier
        depth += 1

    duration_ms = max(0, int((perf_counter() - started) * 1000))
    return RecallResult(
        root_batch_no=root.batch_no,
        affected_batches=affected_batches,
        affected_orders=affected_orders,
        duration_ms=duration_ms,
    )
