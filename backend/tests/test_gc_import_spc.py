import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import GcImport, LabTest, Material, StockBatch, Warehouse
from app.seed import seed_database
from app.services.spc import calculate_spc


@pytest.fixture()
def client_and_session():
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
    with TestClient(app) as client:
        yield client, session_factory
    app.dependency_overrides.clear()


def _headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_gc_import_is_atomic_on_invalid_row(client_and_session):
    client, session_factory = client_and_session
    invalid_gc_csv = (
        b"batch_no,analyte,value,unit,tested_at\n"
        b"NVL-UNKNOWN,C14,13.50,%,2026-07-01T08:00:00\n"
        b"NVL-UNKNOWN,C14,not-a-number,%,2026-07-01T08:01:00\n"
    )

    response = client.post(
        "/api/v1/lab/gc-import",
        headers=_headers(client, "lab", "lab123"),
        files={"file": ("gc.csv", invalid_gc_csv, "text/csv")},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["imported"] == 0
    with session_factory() as db:
        assert db.query(LabTest).count() == 0


def test_gc_import_is_idempotent_and_populates_spc(client_and_session):
    client, session_factory = client_and_session
    with session_factory() as db:
        material = db.query(Material).first()
        warehouse = db.query(Warehouse).first()
        db.add(
            StockBatch(
                batch_no="GC-BATCH-001",
                material_id=material.id,
                warehouse_id=warehouse.id,
                quantity=1,
            )
        )
        db.commit()
    content = (Path(__file__).parent / "fixtures" / "gc_sample.csv").read_bytes()
    lab_headers = _headers(client, "lab", "lab123")

    first = client.post(
        "/api/v1/lab/gc-import",
        headers=lab_headers,
        files={"file": ("gc_sample.csv", content, "text/csv")},
    )
    duplicate = client.post(
        "/api/v1/lab/gc-import",
        headers=lab_headers,
        files={"file": ("gc_sample.csv", content, "text/csv")},
    )
    spc = client.get("/api/v1/lab/spc?analyte=C14&limit=100", headers=lab_headers)

    assert first.status_code == 200
    assert first.json()["imported"] == 10
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate"] is True
    assert spc.status_code == 200
    assert spc.json()["status"] == "ok"
    assert len(spc.json()["points"]) == 10
    with session_factory() as db:
        assert db.query(LabTest).count() == 10
        assert db.query(GcImport).count() == 1


def test_spc_flags_value_above_ucl():
    values = [10.0, 10.1, 9.9, 10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 20.0]

    result = calculate_spc(values)

    assert result.status == "ok"
    assert result.points[-1].out_of_control is True
    assert result.points[-1].value > result.ucl


def test_spc_requires_ten_points():
    result = calculate_spc([10.0] * 9)

    assert result.status == "insufficient_data"
    assert len(result.points) == 9
