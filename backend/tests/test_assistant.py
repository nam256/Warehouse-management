import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import AssistantQueryLog, User
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


def test_assistant_disabled_returns_503(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", False)
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "lab", "lab123"),
        json={"question": "Tồn kho NVL-QUE còn bao nhiêu?"},
    )
    assert response.status_code == 503
    assert "tắt" in response.json()["detail"].lower()


def test_assistant_only_allows_whitelisted_tools():
    from app.services.assistant import ALLOWED_TOOLS

    assert set(ALLOWED_TOOLS) == {
        "get_inventory",
        "get_batch_status",
        "list_expiring_batches",
        "list_open_capa",
        "simulate_recall",
        "explain_stock_reports",
        "list_stock_issues",
    }


def test_assistant_tool_runs_with_user_permissions(session_factory):
    from app.services.assistant import run_tool

    with session_factory() as db:
        lab_user = db.query(User).filter(User.username == "lab").one()
        result = run_tool("get_inventory", {}, db=db, user=lab_user)
    assert "items" in result


def test_assistant_rejects_non_whitelisted_tool(session_factory):
    from app.services.assistant import run_tool

    with session_factory() as db:
        lab_user = db.query(User).filter(User.username == "lab").one()
        with pytest.raises(ValueError, match="không được phép"):
            run_tool("release_batch", {}, db=db, user=lab_user)


def test_assistant_enabled_with_none_provider_returns_503(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "none")
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "lab", "lab123"),
        json={"question": "Lô nào đang chờ giải phóng?"},
    )
    assert response.status_code == 503
    assert "nhà cung cấp ai" in response.json()["detail"].lower()


def test_assistant_local_provider_answers_inventory(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    status = client.get(
        "/api/v1/assistant/status",
        headers=headers(client, "lab", "lab123"),
    )
    assert status.status_code == 200
    assert status.json()["available"] is True

    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "lab", "lab123"),
        json={"question": "Tồn kho còn bao nhiêu?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "get_inventory" in body["tools_called"]
    assert body["answer"]
    assert "bịa" not in body["answer"].lower()


def test_assistant_local_recall_without_batch_returns_guidance(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "lab", "lab123"),
        json={"question": "Mô phỏng thu hồi giúp tôi"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tools_called"] == []
    assert "mã lô" in body["answer"].lower()
    assert "TP-" in body["answer"]


def _ask_local(client, question: str, username="thu_kho", password="kho123"):
    return client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, username, password),
        json={"question": question},
    )


def test_hello_does_not_call_inventory(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    for question in ("xin chào", "hello"):
        response = _ask_local(client, question)
        assert response.status_code == 200
        body = response.json()
        answer = body["answer"].lower()
        assert body["tools_called"] == []
        assert "nvl-que" not in answer
        assert "0 kg" not in answer
        assert "chào" in answer or "chỉ đọc" in answer


def test_thanks_no_tools(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = _ask_local(client, "cảm ơn")
    assert response.status_code == 200
    assert response.json()["tools_called"] == []


def test_weather_out_of_scope(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = _ask_local(client, "hôm nay mưa không")
    assert response.status_code == 200
    body = response.json()
    answer = body["answer"].lower()
    assert body["tools_called"] == []
    assert "nvl-que" not in answer
    assert "qms" in answer or "tồn kho" in answer or "phạm vi" in answer


def test_hello_then_quantity_still_inventory(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = _ask_local(client, "xin chào, tồn kho còn bao nhiêu?")
    assert response.status_code == 200
    assert "get_inventory" in response.json()["tools_called"]


def test_scope_cannot_issue_or_approve(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = _ask_local(client, "Trợ lý có được xuất kho / duyệt lô không?")
    assert response.status_code == 200
    body = response.json()
    answer = body["answer"].lower()
    assert "get_inventory" not in body["tools_called"]
    assert "chỉ đọc" in answer or "không phê duyệt" in answer or "không xuất" in answer


def test_classify_intent_table():
    from app.services.assistant_intent import classify_intent

    cases = [
        ("xin chào", "greet"),
        ("hello", "greet"),
        ("chào bạn", "greet"),
        ("cảm ơn", "thanks"),
        ("hôm nay mưa không", "out_of_scope"),
        ("Tồn kho còn bao nhiêu?", "inventory"),
        ("xin chào, tồn kho còn bao nhiêu?", "inventory"),
        ("Tồn khả dụng khác tồn vật lý thế nào?", "howto_report"),
        ("Làm sao in phiếu xuất kho?", "howto_report"),
        ("Sổ xuất kho lọc ngày ra sao?", "howto_report"),
        ("Trợ lý có được xuất kho / duyệt lô không?", "howto_report"),
        ("Chat tắt khung có mất không?", "howto_report"),
        ("Lô nào sắp hết hạn?", "fefo"),
        ("Có hành động khắc phục nào đang mở?", "capa"),
        ("Mô phỏng thu hồi lô TP-001", "recall"),
        ("Mô phỏng thu hồi giúp tôi", "recall"),
        ("Lô nào đang chờ giải phóng?", "batch"),
        ("in giúp", "clarify"),
        ("Phiếu nhập lấy kg lúc nhập hay tồn hiện tại?", "howto_report"),
        ("Xuất tay khác xuất cho mẻ thế nào?", "howto_report"),
        ("Làm sao nhập kho?", "howto_report"),
        ("Tồn trên file khác màn hình không?", "howto_report"),
        ("Xuất vượt khả dụng thì sao?", "howto_report"),
    ]
    for question, expected in cases:
        assert classify_intent(question) == expected, question


def test_lab_fefo_returns_vietnamese_permission(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = _ask_local(client, "Lô nào sắp hết hạn?", "lab", "lab123")
    assert response.status_code == 200
    answer = response.json()["answer"].lower()
    assert "không có quyền" in answer
    assert "nvl-que" not in answer


def test_assistant_explains_how_to_print_stock_out_reports(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "thu_kho", "kho123"),
        json={"question": "Làm sao in phiếu xuất kho và sổ xuất kho?"},
    )
    assert response.status_code == 200
    body = response.json()
    answer = body["answer"].lower()
    assert "get_inventory" not in body["tools_called"]
    assert "phiếu xuất" in answer or "px-" in answer
    assert "sổ xuất" in answer
    assert "xem trước" in answer or "pdf" in answer


def test_assistant_explains_available_qty_and_hold_release(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "thu_kho", "kho123"),
        json={"question": "Tồn khả dụng khác tồn vật lý thế nào? Lô cách ly có xuất được không?"},
    )
    assert response.status_code == 200
    answer = response.json()["answer"].lower()
    assert "khả dụng" in answer
    assert "vật lý" in answer
    assert "cách ly" in answer or "giải phóng" in answer


def test_assistant_explains_period_inventory_formula(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "ql_nm", "ql123"),
        json={"question": "Báo cáo tồn kho theo kỳ tính tồn đầu nhập xuất tồn cuối ra sao?"},
    )
    assert response.status_code == 200
    answer = response.json()["answer"].lower()
    assert "tồn đầu" in answer
    assert "nhập" in answer
    assert "xuất" in answer
    assert "tồn cuối" in answer


def test_assistant_explains_manual_vs_production_issue(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "thu_kho", "kho123"),
        json={"question": "Xuất tay khác xuất cho mẻ sản xuất thế nào trên phiếu PX?"},
    )
    assert response.status_code == 200
    answer = response.json()["answer"].lower()
    assert "thủ công" in answer or "tay" in answer
    assert "mẻ" in answer


def test_assistant_explains_receipt_qty_and_over_issue(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "local")
    receipt = _ask_local(client, "Phiếu nhập lấy kg lúc nhập hay tồn hiện tại?")
    assert receipt.status_code == 200
    receipt_answer = receipt.json()["answer"].lower()
    assert "get_inventory" not in receipt.json()["tools_called"]
    assert "lúc nhập" in receipt_answer or "phiếu nhập" in receipt_answer
    over = _ask_local(client, "Xuất vượt khả dụng thì sao?")
    assert over.status_code == 200
    over_answer = over.json()["answer"].lower()
    assert "get_inventory" not in over.json()["tools_called"]
    assert "khả dụng" in over_answer
    same = _ask_local(client, "Tồn trên file khác màn hình không?")
    assert same.status_code == 200
    assert "công thức" in same.json()["answer"].lower() or "khả dụng" in same.json()["answer"].lower()


def test_assistant_logs_success_without_real_provider(
    client, session_factory, monkeypatch
):
    from app.routers import assistant as assistant_router

    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "ai_api_key", "test-only")
    monkeypatch.setattr(
        assistant_router,
        "answer_question",
        lambda *args, **kwargs: (
            "NVL-QUE còn 100 kg.",
            ["get_inventory"],
            [{"tool": "get_inventory", "result": {"items": []}}],
        ),
    )

    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "lab", "lab123"),
        json={"question": "Tồn kho NVL-QUE còn bao nhiêu?"},
    )

    assert response.status_code == 200
    assert response.json()["tools_called"] == ["get_inventory"]
    with session_factory() as db:
        log = db.query(AssistantQueryLog).one()
        assert log.question == "Tồn kho NVL-QUE còn bao nhiêu?"
        assert "get_inventory" in (log.tools_called or "")


def test_provider_failure_is_friendly_503(client, monkeypatch):
    from app.routers import assistant as assistant_router
    from app.services.assistant import AssistantProviderError

    monkeypatch.setattr(settings, "ai_assistant_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(
        assistant_router,
        "answer_question",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssistantProviderError("Trợ lý tạm thời không khả dụng.")
        ),
    )

    response = client.post(
        "/api/v1/assistant/ask",
        headers=headers(client, "lab", "lab123"),
        json={"question": "CAPA nào đang mở?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Trợ lý tạm thời không khả dụng."


def test_model_answer_without_tool_data_is_not_trusted(session_factory, monkeypatch):
    from app.services import assistant as assistant_service

    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(
        assistant_service,
        "_post_provider",
        lambda *args, **kwargs: {"role": "assistant", "content": "Tồn kho là 999 kg."},
    )
    with session_factory() as db:
        lab_user = db.query(User).filter(User.username == "lab").one()
        answer, tools, data = assistant_service.answer_question(
            "Tồn kho là bao nhiêu?",
            db=db,
            user=lab_user,
        )

    assert answer == "Không tìm thấy dữ liệu phù hợp để trả lời."
    assert tools == []
    assert data == []
