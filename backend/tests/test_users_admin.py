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


def test_non_admin_cannot_list_users(client):
    token = _token(client, "thu_kho", "kho123")
    r = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_lists_and_creates_user(client):
    token = _token(client, "admin", "admin123")
    listed = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert isinstance(listed.json(), list)
    assert any(u["username"] == "admin" for u in listed.json())

    created = client.post(
        "/api/v1/users",
        json={
            "username": "nhanvien1",
            "password": "nv123456",
            "full_name": "Nhân viên 1",
            "role": "thu_kho",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["username"] == "nhanvien1"
    assert body["role"] == "thu_kho"
    assert body["is_active"] is True

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "nhanvien1", "password": "nv123456"},
    )
    assert login.status_code == 200


def test_admin_can_deactivate_user(client):
    token = _token(client, "admin", "admin123")
    created = client.post(
        "/api/v1/users",
        json={
            "username": "tamkhoa",
            "password": "tk123456",
            "full_name": "Tạm khóa",
            "role": "lab",
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    patched = client.patch(
        f"/api/v1/users/{created['id']}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patched.status_code == 200
    assert patched.json()["is_active"] is False

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "tamkhoa", "password": "tk123456"},
    )
    assert login.status_code == 403


def test_material_image_url_update(client):
    admin = _token(client, "admin", "admin123")
    mats = client.get("/api/v1/materials", headers={"Authorization": f"Bearer {admin}"}).json()
    assert mats
    mid = mats[0]["id"]
    assert "image_url" in mats[0]

    updated = client.patch(
        f"/api/v1/materials/{mid}",
        json={"image_url": "https://example.com/mat.png"},
        headers={"Authorization": f"Bearer {admin}"},
    )
    assert updated.status_code == 200
    assert updated.json()["image_url"] == "https://example.com/mat.png"

    inv = client.get("/api/v1/stock/inventory", headers={"Authorization": f"Bearer {admin}"})
    assert inv.status_code == 200
    row = next(item for item in inv.json() if item["material_id"] == mid)
    assert row["image_url"] == "https://example.com/mat.png"


def test_material_image_delete(client):
    admin = _token(client, "admin", "admin123")
    mats = client.get("/api/v1/materials", headers={"Authorization": f"Bearer {admin}"}).json()
    mid = mats[0]["id"]
    client.patch(
        f"/api/v1/materials/{mid}",
        json={"image_url": "/uploads/materials/demo.png"},
        headers={"Authorization": f"Bearer {admin}"},
    )
    deleted = client.delete(
        f"/api/v1/materials/{mid}/image",
        headers={"Authorization": f"Bearer {admin}"},
    )
    assert deleted.status_code == 200
    assert deleted.json()["image_url"] is None
