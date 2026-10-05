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
    return r.json()["access_token"]


def test_e2e_flow(client):
    tok = _token(client, "thu_kho", "kho123")
    mats = client.get("/api/v1/materials", headers={"Authorization": f"Bearer {tok}"}).json()
    nvl = next(m for m in mats if m["code"] == "NVL-QUE")
    tp = next(m for m in mats if m["code"] == "TP-TCA")
    batch = client.post(
        "/api/v1/stock/receipts",
        json={"material_id": nvl["id"], "quantity": 100, "ccp1_c14": 13.5, "warehouse_id": 1},
        headers={"Authorization": f"Bearer {tok}"},
    ).json()
    assert batch["quality_status"] == "quarantine"
    assert batch["ccp1_status"] == "pending"

    lab_token = _token(client, "lab", "lab123")
    lab_headers = {"Authorization": f"Bearer {lab_token}"}
    for status in ("sampling", "under_test"):
        transition = client.post(
            f"/api/v1/quality/batches/{batch['id']}/transition",
            json={"to_status": status, "reason_code": "LAB_PROCESS"},
            headers=lab_headers,
        )
        assert transition.status_code == 200
    lab_test = client.post(
        "/api/v1/lab/tests",
        json={"batch_id": batch["id"], "test_type": "C14", "c14": 13.5},
        headers=lab_headers,
    )
    assert lab_test.status_code == 201
    awaiting = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        json={"to_status": "awaiting_release", "reason_code": "CCP_PASS"},
        headers=lab_headers,
    )
    assert awaiting.status_code == 200

    attp_token = _token(client, "attp", "attp123")
    released = client.post(
        f"/api/v1/quality/batches/{batch['id']}/transition",
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Đạt"},
        headers={"Authorization": f"Bearer {attp_token}"},
    )
    assert released.status_code == 200

    tok2 = _token(client, "ky_thuat", "kt123")
    order = client.post(
        "/api/v1/production/orders",
        json={"product_material_id": tp["id"], "planned_qty": 50},
        headers={"Authorization": f"Bearer {tok2}"},
    ).json()
    tok3 = _token(client, "ql_nm", "ql123")
    client.post(
        f"/api/v1/production/orders/{order['id']}/approve",
        headers={"Authorization": f"Bearer {tok3}"},
    )
    client.post(
        f"/api/v1/production/orders/{order['id']}/start",
        json={"materials": [{"batch_id": batch["id"], "quantity": 30}]},
        headers={"Authorization": f"Bearer {tok2}"},
    )
    client.post(
        f"/api/v1/production/orders/{order['id']}/operations",
        json={"step": "chung_cat", "t_top": 108, "t_ca_percent": 99.5},
        headers={"Authorization": f"Bearer {tok2}"},
    )
    done = client.post(
        f"/api/v1/production/orders/{order['id']}/complete",
        json={"actual_qty": 25},
        headers={"Authorization": f"Bearer {tok2}"},
    ).json()
    assert done["output_batch_no"]
    batches = client.get(
        "/api/v1/quality/batches",
        headers={"Authorization": f"Bearer {tok2}"},
    ).json()
    output_batch = next(item for item in batches if item["batch_no"] == done["output_batch_no"])
    assert output_batch["quality_status"] == "awaiting_release"
    trace = client.get(
        f"/api/v1/reports/trace/{done['output_batch_no']}",
        headers={"Authorization": f"Bearer {tok2}"},
    ).json()
    assert len(trace["production_orders"]) >= 1
    assert any(b["batch_no"] == done["output_batch_no"] for b in trace["output_batches"])
