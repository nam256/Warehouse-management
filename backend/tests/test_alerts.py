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
    CapaStatus,
    CorrectiveAction,
    Material,
    OperationRecord,
    ProductionOrder,
    PurchaseRequest,
    PurchaseRequestStatus,
    QualityStatus,
    StockBatch,
    User,
    Warehouse,
)
from app.seed import seed_database


@pytest.fixture()
def env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    with Session() as db:
        seed_database(db)

    def override():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as client:
        yield client, Session
    app.dependency_overrides.clear()


def _headers(client: TestClient, username="thu_kho", password="kho123") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _kinds(client: TestClient, username="thu_kho", password="kho123") -> set[str]:
    response = client.get("/api/v1/dashboard/alerts", headers=_headers(client, username, password))
    assert response.status_code == 200
    return {item["kind"] for item in response.json()["items"]}


def test_seed_stock_empty_for_warehouse_not_lab(env):
    client, _ = env
    kho = _kinds(client, "thu_kho", "kho123")
    lab = _kinds(client, "lab", "lab123")
    assert "out_of_stock" in kho
    assert "out_of_stock" not in lab


def test_seed_includes_purchase_and_capa_alerts(env):
    client, _ = env
    kho = _kinds(client, "thu_kho", "kho123")
    ql = _kinds(client, "ql_nm", "ql123")
    assert "purchase_pending" in kho
    assert "capa_due_soon" in ql


def test_expired_and_expiring_batches_alert(env):
    client, Session = env
    with Session() as db:
        material = db.query(Material).filter(Material.code == "NVL-QUE").one()
        warehouse = db.query(Warehouse).first()
        db.add(
            StockBatch(
                batch_no="NVL-HSD-001",
                material_id=material.id,
                warehouse_id=warehouse.id,
                quantity=12,
                ccp1_status=CCPStatus.pass_,
                quality_status=QualityStatus.released,
                expiry_date=date.today() - timedelta(days=1),
            )
        )
        db.add(
            StockBatch(
                batch_no="NVL-HSD-002",
                material_id=material.id,
                warehouse_id=warehouse.id,
                quantity=8,
                ccp1_status=CCPStatus.pass_,
                quality_status=QualityStatus.released,
                expiry_date=date.today() + timedelta(days=5),
            )
        )
        db.commit()
    kinds = _kinds(client)
    assert "expired" in kinds
    assert "expiring_soon" in kinds


def test_awaiting_release_alert_for_attp(env):
    client, Session = env
    with Session() as db:
        material = db.query(Material).filter(Material.code == "NVL-QUE").one()
        warehouse = db.query(Warehouse).first()
        db.add(
            StockBatch(
                batch_no="NVL-CHO-001",
                material_id=material.id,
                warehouse_id=warehouse.id,
                quantity=40,
                ccp1_status=CCPStatus.pass_,
                quality_status=QualityStatus.awaiting_release,
            )
        )
        db.commit()
    attp = _kinds(client, "attp", "attp123")
    kho = _kinds(client, "thu_kho", "kho123")
    assert "awaiting_release" in attp
    assert "awaiting_release" not in kho


def test_purchase_and_capa_due_soon(env):
    client, Session = env
    with Session() as db:
        material = db.query(Material).filter(Material.code == "NVL-QUE").one()
        thu_kho = db.query(User).filter(User.username == "thu_kho").one()
        attp = db.query(User).filter(User.username == "attp").one()
        db.add(
            PurchaseRequest(
                material_id=material.id,
                requested_qty=50,
                reason="Bổ sung tồn thấp",
                status=PurchaseRequestStatus.pending,
                created_by_id=thu_kho.id,
            )
        )
        db.add(
            CorrectiveAction(
                entity_type="lab_test",
                entity_id=1,
                title="Sai lệch CCP1",
                reason="Hàm lượng ngoài ngưỡng",
                status=CapaStatus.open,
                due_date=date.today() + timedelta(days=2),
                created_by_id=attp.id,
            )
        )
        db.commit()
    kho = _kinds(client, "thu_kho", "kho123")
    ql = _kinds(client, "ql_nm", "ql123")
    assert "purchase_pending" in kho
    assert "capa_due_soon" in ql
    assert "capa_due_soon" not in kho


def test_ccp2_fail_alert(env):
    client, Session = env
    with Session() as db:
        material = db.query(Material).filter(Material.code == "TP-TCA").one()
        ky_thuat = db.query(User).filter(User.username == "ky_thuat").one()
        order = ProductionOrder(
            order_no="SX-099",
            product_material_id=material.id,
            planned_qty=10,
            created_by_id=ky_thuat.id,
        )
        db.add(order)
        db.flush()
        db.add(
            OperationRecord(
                order_id=order.id,
                step="chưng cất",
                ccp2_status=CCPStatus.fail,
                created_by_id=ky_thuat.id,
            )
        )
        db.commit()
    kinds = _kinds(client, "ky_thuat", "kt123")
    assert "ccp2_fail" in kinds
