import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import CCPStatus, CapaStatus, CorrectiveAction, LabTest, User
from app.seed import seed_database


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    with factory() as db:
        seed_database(db)
    return factory


@pytest.fixture()
def client(session_factory):
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


def test_same_failure_creates_one_open_capa(session_factory):
    from app.services.capa import create_capa_for_failure

    with session_factory() as db:
        lab_user = db.query(User).filter(User.username == "lab").one()
        failed_test = LabTest(
            batch_id=1,
            test_type="C14",
            c14=11,
            result_status=CCPStatus.fail,
            created_by_id=lab_user.id,
        )
        db.add(failed_test)
        db.flush()

        first = create_capa_for_failure(db, "lab_test", failed_test.id)
        second = create_capa_for_failure(db, "lab_test", failed_test.id)
        db.commit()

        assert first.id == second.id
        assert (
            db.query(CorrectiveAction)
            .filter(
                CorrectiveAction.source_type == "lab_test",
                CorrectiveAction.source_id == failed_test.id,
                CorrectiveAction.status != CapaStatus.closed,
            )
            .count()
            == 1
        )


def test_capa_cannot_close_without_verification(client, session_factory):
    with session_factory() as db:
        lab_user = db.query(User).filter(User.username == "lab").one()
        capa = CorrectiveAction(
            entity_type="lab_test",
            entity_id=999,
            title="CCP không đạt",
            source_type="lab_test",
            source_id=999,
            reason="Kết quả CCP không đạt",
            root_cause="Sai lệch nguyên liệu",
            action_taken="Cô lập lô",
            disposition="reject",
            status=CapaStatus.verification,
            created_by_id=lab_user.id,
        )
        db.add(capa)
        db.commit()
        capa_id = capa.id

    response = client.post(
        f"/api/v1/quality/corrective-actions/{capa_id}/transition",
        headers=headers(client, "attp", "attp123"),
        json={"to_status": "closed", "disposition": "reject"},
    )

    assert response.status_code == 400
    assert "xác minh" in response.json()["detail"].lower()
