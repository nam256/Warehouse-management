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


def _token(client, username="thu_kho", password="kho123"):
    r = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_me_includes_avatar_url(client):
    token = _token(client)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert "avatar_url" in body
    assert body["username"] == "thu_kho"


def test_patch_me_updates_full_name(client):
    token = _token(client)
    r = client.patch(
        "/api/v1/auth/me",
        json={"full_name": "Thủ kho cập nhật"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["full_name"] == "Thủ kho cập nhật"
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["full_name"] == "Thủ kho cập nhật"


def test_change_password_requires_current(client):
    token = _token(client)
    bad = client.post(
        "/api/v1/auth/me/password",
        json={"current_password": "sai", "new_password": "kho456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bad.status_code == 400

    ok = client.post(
        "/api/v1/auth/me/password",
        json={"current_password": "kho123", "new_password": "kho456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ok.status_code == 200

    login_old = client.post(
        "/api/v1/auth/login",
        data={"username": "thu_kho", "password": "kho123"},
    )
    assert login_old.status_code == 401

    login_new = client.post(
        "/api/v1/auth/login",
        data={"username": "thu_kho", "password": "kho456"},
    )
    assert login_new.status_code == 200


def test_no_public_register(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"username": "hacker", "password": "x", "full_name": "H"},
    )
    assert r.status_code in (404, 405)
