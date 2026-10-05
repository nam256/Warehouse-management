import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_sqlite_memory_profile_starts_application():
    if settings.database_url != "sqlite://":
        pytest.skip("requires the in-memory SQLite profile")

    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
