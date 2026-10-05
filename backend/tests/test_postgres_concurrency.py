"""PostgreSQL concurrency smoke for FEFO reservation locking."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models import (
    CCPStatus,
    Material,
    MaterialReservation,
    MaterialType,
    OrderStatus,
    ProductionOrder,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    User,
    Warehouse,
)
from app.services.fefo import suggest_fefo


pytestmark = [pytest.mark.integration, pytest.mark.postgres]

DATABASE_URL = os.getenv(
    "DATABASE_URL_POSTGRES",
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/oxeyns",
)


@pytest.fixture()
def pg_session_factory():
    engine = create_engine(DATABASE_URL)
    if engine.dialect.name != "postgresql":
        pytest.skip("Requires PostgreSQL")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    engine.dispose()


def _seed(factory) -> tuple[int, int, int, int, int]:
    with factory() as db:
        material = (
            db.query(Material)
            .filter(Material.code == "NVL-PG-CONCUR")
            .one_or_none()
        )
        if material is None:
            material = Material(
                code="NVL-PG-CONCUR",
                name="NVL concurrency test",
                type=MaterialType.NVL,
                unit="kg",
                is_active=True,
            )
            db.add(material)
            db.flush()

        product = (
            db.query(Material)
            .filter(Material.code == "TP-PG-CONCUR")
            .one_or_none()
        )
        if product is None:
            product = Material(
                code="TP-PG-CONCUR",
                name="TP concurrency test",
                type=MaterialType.TP,
                unit="kg",
                is_active=True,
            )
            db.add(product)
            db.flush()

        warehouse = db.query(Warehouse).first()
        if warehouse is None:
            warehouse = Warehouse(code="WH-PG", name="PG Warehouse")
            db.add(warehouse)
            db.flush()

        creator = db.query(User).order_by(User.id.asc()).first()
        if creator is None:
            pytest.skip("Need at least one user in PostgreSQL oxeyns DB")

        batch = (
            db.query(StockBatch)
            .filter(StockBatch.batch_no == "PG-CONCUR-001")
            .one_or_none()
        )
        if batch is None:
            batch = StockBatch(
                batch_no="PG-CONCUR-001",
                material_id=material.id,
                warehouse_id=warehouse.id,
                quantity=Decimal("10"),
                ccp1_status=CCPStatus.pass_,
                quality_status=QualityStatus.released,
                expiry_date=date.today() + timedelta(days=30),
            )
            db.add(batch)
            db.flush()
        else:
            batch.quantity = Decimal("10")
            batch.ccp1_status = CCPStatus.pass_
            batch.quality_status = QualityStatus.released

        order_ids: list[int] = []
        for order_no in ("SX-PG-CONCUR-1", "SX-PG-CONCUR-2"):
            order = (
                db.query(ProductionOrder)
                .filter(ProductionOrder.order_no == order_no)
                .one_or_none()
            )
            if order is None:
                order = ProductionOrder(
                    order_no=order_no,
                    product_material_id=product.id,
                    planned_qty=Decimal("8"),
                    status=OrderStatus.draft,
                    created_by_id=creator.id,
                )
                db.add(order)
                db.flush()
            order_ids.append(order.id)

        db.query(MaterialReservation).filter(
            MaterialReservation.order_id.in_(order_ids)
        ).delete(synchronize_session=False)
        db.commit()
        return material.id, warehouse.id, batch.id, order_ids[0], order_ids[1]


def test_postgres_reservation_lock_prevents_over_allocate(pg_session_factory):
    material_id, warehouse_id, batch_id, order_a, order_b = _seed(pg_session_factory)

    def try_reserve(order_id: int) -> str:
        with pg_session_factory() as db:
            try:
                allocations = suggest_fefo(db, material_id, warehouse_id, 8.0)
                total = sum(item.qty for item in allocations)
                if total < 8.0 - 1e-9:
                    db.rollback()
                    return "err:Insufficient"
                for item in allocations:
                    db.add(
                        MaterialReservation(
                            order_id=order_id,
                            batch_id=item.batch_id,
                            quantity=Decimal(str(item.qty)),
                            status=ReservationStatus.active,
                        )
                    )
                db.commit()
                return "ok"
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                return f"err:{type(exc).__name__}"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(try_reserve, [order_a, order_b]))

    # With SELECT FOR UPDATE, at most one reservation of 8 from qty 10 should succeed.
    assert results.count("ok") >= 1, results
    assert results.count("ok") <= 1 or any(r.startswith("err:") for r in results), results

    with pg_session_factory() as db:
        active_qty = (
            db.query(MaterialReservation)
            .filter(
                MaterialReservation.batch_id == batch_id,
                MaterialReservation.status == ReservationStatus.active,
                MaterialReservation.order_id.in_([order_a, order_b]),
            )
            .all()
        )
        reserved = sum(float(item.quantity) for item in active_qty)
        assert reserved <= 10.0 + 1e-9, reserved
        db.query(MaterialReservation).filter(
            MaterialReservation.order_id.in_([order_a, order_b])
        ).delete(synchronize_session=False)
        batch = db.get(StockBatch, batch_id)
        batch.quantity = Decimal("10")
        db.commit()
