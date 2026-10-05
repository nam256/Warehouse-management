import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import seed_database


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    seed_database(db)
    db.close()

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _token(client, username, password):
    r = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_thu_kho_cannot_view_audit(client):
    token = _token(client, "thu_kho", "kho123")
    r = client.get("/api/v1/reports/audit", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_attp_can_view_audit(client):
    token = _token(client, "attp", "attp123")
    r = client.get("/api/v1/reports/audit", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "total" in body
    assert body["page"] >= 1
    assert body["page_size"] >= 1


def test_issue_over_stock_blocked(client):
    token = _token(client, "thu_kho", "kho123")
    mats = client.get("/api/v1/materials", headers={"Authorization": f"Bearer {token}"}).json()
    nvl = next(m for m in mats if m["code"] == "NVL-QUE")
    batch = client.post(
        "/api/v1/stock/receipts",
        json={"material_id": nvl["id"], "quantity": 10, "ccp1_c14": 13.5, "warehouse_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    r = client.post(
        "/api/v1/stock/issues",
        json={"batch_id": batch["id"], "quantity": 999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400
