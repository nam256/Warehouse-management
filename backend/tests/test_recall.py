from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import (
    CCPStatus,
    Material,
    MaterialType,
    OrderStatus,
    ProductionMaterialUsage,
    ProductionOrder,
    QualityStatus,
    StockBatch,
    Warehouse,
)
from app.services.recall import simulate_recall


def test_recall_returns_all_downstream_batches_across_multiple_levels():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    try:
        raw_material = Material(code="RAW-RECALL", name="Nguyên liệu", type=MaterialType.NVL)
        intermediate_material = Material(code="BTP-RECALL", name="Bán thành phẩm", type=MaterialType.BTP)
        finished_material = Material(code="TP-RECALL", name="Thành phẩm", type=MaterialType.TP)
        warehouse = Warehouse(code="KHO-RECALL", name="Kho recall")
        db.add_all([raw_material, intermediate_material, finished_material, warehouse])
        db.flush()

        raw_batch = StockBatch(
            batch_no="RAW-001",
            material_id=raw_material.id,
            warehouse_id=warehouse.id,
            quantity=100,
            ccp1_status=CCPStatus.pass_,
            quality_status=QualityStatus.released,
        )
        intermediate_batch = StockBatch(
            batch_no="BTP-001",
            material_id=intermediate_material.id,
            warehouse_id=warehouse.id,
            quantity=60,
            ccp1_status=CCPStatus.pass_,
            quality_status=QualityStatus.released,
        )
        finished_batch = StockBatch(
            batch_no="TP-001",
            material_id=finished_material.id,
            warehouse_id=warehouse.id,
            quantity=50,
            ccp1_status=CCPStatus.pass_,
            quality_status=QualityStatus.awaiting_release,
        )
        db.add_all([raw_batch, intermediate_batch, finished_batch])
        db.flush()

        first_order = ProductionOrder(
            order_no="SX-RECALL-1",
            product_material_id=intermediate_material.id,
            planned_qty=60,
            actual_qty=60,
            status=OrderStatus.done,
            output_batch_id=intermediate_batch.id,
            created_by_id=1,
        )
        second_order = ProductionOrder(
            order_no="SX-RECALL-2",
            product_material_id=finished_material.id,
            planned_qty=50,
            actual_qty=50,
            status=OrderStatus.done,
            output_batch_id=finished_batch.id,
            created_by_id=1,
        )
        db.add_all([first_order, second_order])
        db.flush()
        db.add_all(
            [
                ProductionMaterialUsage(order_id=first_order.id, batch_id=raw_batch.id, quantity=70),
                ProductionMaterialUsage(
                    order_id=second_order.id,
                    batch_id=intermediate_batch.id,
                    quantity=55,
                ),
            ]
        )
        db.commit()

        result = simulate_recall(db, raw_batch.id)

        assert {item.batch_no for item in result.affected_batches} == {
            raw_batch.batch_no,
            intermediate_batch.batch_no,
            finished_batch.batch_no,
        }
        assert {item.order_no for item in result.affected_orders} == {
            first_order.order_no,
            second_order.order_no,
        }
        assert [item.depth for item in result.affected_batches] == [0, 1, 2]
        assert result.duration_ms >= 0
        assert db.get(StockBatch, raw_batch.id).quantity == 100
        assert db.get(StockBatch, finished_batch.id).quality_status == QualityStatus.awaiting_release
    finally:
        db.close()
