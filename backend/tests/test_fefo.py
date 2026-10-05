from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (
    CCPStatus,
    Material,
    MaterialReservation,
    MaterialType,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    Warehouse,
)
from app.seed import seed_database
from app.services.fefo import suggest_fefo


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _master_data(db):
    material = Material(code="NVL-TEST", name="Nguyên liệu thử", type=MaterialType.NVL)
    warehouse = Warehouse(code="KHO-TEST", name="Kho thử")
    db.add_all([material, warehouse])
    db.flush()
    return material, warehouse


def _batch(db, material, warehouse, batch_no, qty, expiry, *, released=True):
    batch = StockBatch(
        batch_no=batch_no,
        material_id=material.id,
        warehouse_id=warehouse.id,
        quantity=qty,
        ccp1_status=CCPStatus.pass_,
        quality_status=QualityStatus.released if released else QualityStatus.quarantine,
        expiry_date=expiry,
    )
    db.add(batch)
    db.flush()
    return batch


def test_fefo_allocates_earliest_expiry_first(db):
    material, warehouse = _master_data(db)
    later = _batch(db, material, warehouse, "LATER", 10, date.today() + timedelta(days=20))
    earliest = _batch(db, material, warehouse, "EARLIEST", 5, date.today() + timedelta(days=5))
    no_expiry = _batch(db, material, warehouse, "NO-EXPIRY", 20, None)

    allocations = suggest_fefo(db, material.id, warehouse.id, 12)

    assert [item.batch_id for item in allocations] == [earliest.id, later.id]
    assert [item.qty for item in allocations] == [5, 7]
    assert no_expiry.id not in {item.batch_id for item in allocations}


def test_expired_or_quarantine_batch_is_excluded(db):
    material, warehouse = _master_data(db)
    expired = _batch(db, material, warehouse, "EXPIRED", 10, date.today() - timedelta(days=1))
    quarantine = _batch(
        db,
        material,
        warehouse,
        "QUARANTINE",
        10,
        date.today() + timedelta(days=1),
        released=False,
    )
    valid = _batch(db, material, warehouse, "VALID", 10, date.today() + timedelta(days=10))

    allocations = suggest_fefo(db, material.id, warehouse.id, 1)

    assert [item.batch_id for item in allocations] == [valid.id]
    assert expired.id not in {item.batch_id for item in allocations}
    assert quarantine.id not in {item.batch_id for item in allocations}


def test_fefo_uses_on_hand_minus_active_reservations(db):
    material, warehouse = _master_data(db)
    batch = _batch(db, material, warehouse, "RESERVED", 10, date.today() + timedelta(days=5))
    db.add(
        MaterialReservation(
            order_id=1,
            batch_id=batch.id,
            quantity=7,
            status=ReservationStatus.active,
        )
    )
    db.flush()

    allocations = suggest_fefo(db, material.id, warehouse.id, 5)

    assert len(allocations) == 1
    assert allocations[0].qty == 3
    assert allocations[0].reserved_qty == 7
    assert allocations[0].available_qty == 3


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    with session_factory() as session:
        seed_database(session)

    def override():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _headers(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _released_batch(client, quantity=40):
    warehouse_headers = _headers(client, "thu_kho", "kho123")
    materials = client.get("/api/v1/materials", headers=warehouse_headers).json()
    raw = next(item for item in materials if item["code"] == "NVL-QUE")
    batch = client.post(
        "/api/v1/stock/receipts",
        headers=warehouse_headers,
        json={
            "material_id": raw["id"],
            "warehouse_id": 1,
            "quantity": quantity,
            "expiry_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    ).json()
    lab_headers = _headers(client, "lab", "lab123")
    for status in ("sampling", "under_test"):
        response = client.post(
            f"/api/v1/quality/batches/{batch['id']}/transition",
            headers=lab_headers,
            json={"to_status": status, "reason_code": "LAB_PROCESS"},
        )
        assert response.status_code == 200
    assert client.post(
        "/api/v1/lab/tests",
        headers=lab_headers,
        json={"batch_id": batch["id"], "test_type": "C14", "c14": 13.5},
    ).status_code == 201
    assert client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=lab_headers,
        json={"to_status": "awaiting_release", "reason_code": "CCP_PASS"},
    ).status_code == 200
    assert client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=_headers(client, "attp", "attp123"),
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Đạt"},
    ).status_code == 200
    return batch, materials


def test_cancel_running_order_restores_stock(client):
    batch, materials = _released_batch(client)
    product = next(item for item in materials if item["code"] == "TP-TCA")
    technical_headers = _headers(client, "ky_thuat", "kt123")
    order = client.post(
        "/api/v1/production/orders",
        headers=technical_headers,
        json={"product_material_id": product["id"], "planned_qty": 30},
    ).json()
    manager_headers = _headers(client, "ql_nm", "ql123")

    approved = client.post(
        f"/api/v1/production/orders/{order['id']}/approve",
        headers=manager_headers,
    )
    assert approved.status_code == 200
    reservations = client.get(
        f"/api/v1/production/orders/{order['id']}/reservations",
        headers=technical_headers,
    ).json()
    assert sum(item["quantity"] for item in reservations) == 30

    started = client.post(
        f"/api/v1/production/orders/{order['id']}/start",
        headers=technical_headers,
        json={"materials": []},
    )
    assert started.status_code == 200
    batches_after_start = client.get("/api/v1/stock/batches", headers=technical_headers).json()
    assert next(item for item in batches_after_start if item["id"] == batch["id"])["quantity"] == 10

    cancelled = client.post(
        f"/api/v1/production/orders/{order['id']}/cancel",
        headers=manager_headers,
    )
    assert cancelled.status_code == 200
    batches_after_cancel = client.get("/api/v1/stock/batches", headers=technical_headers).json()
    assert next(item for item in batches_after_cancel if item["id"] == batch["id"])["quantity"] == 40


def test_approve_with_insufficient_stock_creates_no_partial_reservation(client):
    _, materials = _released_batch(client, quantity=20)
    product = next(item for item in materials if item["code"] == "TP-TCA")
    technical_headers = _headers(client, "ky_thuat", "kt123")
    order = client.post(
        "/api/v1/production/orders",
        headers=technical_headers,
        json={"product_material_id": product["id"], "planned_qty": 30},
    ).json()

    response = client.post(
        f"/api/v1/production/orders/{order['id']}/approve",
        headers=_headers(client, "ql_nm", "ql123"),
    )

    assert response.status_code == 400
    reservations = client.get(
        f"/api/v1/production/orders/{order['id']}/reservations",
        headers=technical_headers,
    )
    assert reservations.status_code == 200
    assert reservations.json() == []
