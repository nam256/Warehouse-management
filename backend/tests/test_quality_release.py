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
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    with session_factory() as db:
        seed_database(db)

    def override():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def receipt(client: TestClient) -> dict:
    warehouse = headers(client, "thu_kho", "kho123")
    materials = client.get("/api/v1/materials", headers=warehouse).json()
    raw_material = next(item for item in materials if item["code"] == "NVL-QUE")
    response = client.post(
        "/api/v1/stock/receipts",
        headers=warehouse,
        json={
            "material_id": raw_material["id"],
            "warehouse_id": 1,
            "quantity": 20,
            "ccp1_c14": 13.5,
        },
    )
    assert response.status_code == 201
    return response.json()


def awaiting_batch(client: TestClient) -> dict:
    batch = receipt(client)
    lab = headers(client, "lab", "lab123")
    for status in ("sampling", "under_test"):
        response = client.post(
            f"/api/v1/quality/batches/{batch['id']}/transition",
            headers=lab,
            json={"to_status": status, "reason_code": "LAB_PROCESS"},
        )
        assert response.status_code == 200
    test_response = client.post(
        "/api/v1/lab/tests",
        headers=lab,
        json={"batch_id": batch["id"], "test_type": "C14", "c14": 13.5},
    )
    assert test_response.status_code == 201
    response = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=lab,
        json={
            "to_status": "awaiting_release",
            "reason_code": "CCP_PASS",
            "note": "Lab gửi duyệt",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_receipt_is_always_quarantined_and_pending(client):
    batch = receipt(client)
    assert batch["quality_status"] == "quarantine"
    assert batch["ccp1_status"] == "pending"
    assert batch["ccp1_c14"] is None


def test_warehouse_cannot_release(client):
    batch = awaiting_batch(client)
    response = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=headers(client, "thu_kho", "kho123"),
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Không hợp lệ"},
    )
    assert response.status_code == 403


def test_attp_release_requires_electronic_confirmation_note(client):
    batch = awaiting_batch(client)
    response = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=headers(client, "attp", "attp123"),
        json={"to_status": "released", "reason_code": "CCP_PASS"},
    )
    assert response.status_code == 400


def test_attp_releases_awaiting_batch_and_history_is_recorded(client):
    batch = awaiting_batch(client)
    attp = headers(client, "attp", "attp123")
    response = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        headers=attp,
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Đạt"},
    )
    assert response.status_code == 200
    assert response.json()["quality_status"] == "released"

    history = client.get(
        f"/api/v1/quality/batches/{batch['id']}/history",
        headers=attp,
    )
    assert history.status_code == 200
    assert [item["to_status"] for item in history.json()] == [
        "sampling",
        "under_test",
        "awaiting_release",
        "released",
    ]


def test_quarantine_batch_cannot_be_issued(client):
    batch = receipt(client)
    response = client.post(
        "/api/v1/stock/issues",
        headers=headers(client, "thu_kho", "kho123"),
        json={"batch_id": batch["id"], "quantity": 1},
    )
    assert response.status_code == 400


def test_lab_pass_does_not_auto_release(client):
    batch = receipt(client)
    lab = headers(client, "lab", "lab123")
    response = client.post(
        "/api/v1/lab/tests",
        headers=lab,
        json={"batch_id": batch["id"], "test_type": "C14", "c14": 13.5},
    )
    assert response.status_code == 201
    listed = client.get("/api/v1/quality/batches", headers=lab)
    current = next(item for item in listed.json() if item["id"] == batch["id"])
    assert current["ccp1_status"] == "pass"
    assert current["quality_status"] == "quarantine"
