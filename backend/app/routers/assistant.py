import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import get_current_user
from app.database import get_db
from app.models import AssistantQueryLog, User
from app.schemas import AssistantAnswer, AssistantAsk, AssistantStatus
from app.services.assistant import AssistantProviderError, answer_question

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _status() -> AssistantStatus:
    provider = settings.ai_provider.lower().strip()
    enabled = settings.ai_assistant_enabled
    configured = provider == "local" or (
        provider in {"openai", "ollama"}
        and (provider != "openai" or bool(settings.ai_api_key))
    )
    if not enabled:
        message = "Trợ lý AI đang tắt."
    elif provider == "none":
        message = "Chưa cấu hình nhà cung cấp AI."
    elif not configured:
        message = "Cấu hình nhà cung cấp AI chưa đầy đủ."
    elif provider == "local":
        message = "Trợ lý local (chỉ đọc) đã sẵn sàng — không cần API key."
    else:
        message = "Trợ lý AI đã sẵn sàng."
    return AssistantStatus(
        enabled=enabled,
        available=enabled and configured,
        provider=provider,
        message=message,
    )


@router.get("/status", response_model=AssistantStatus)
def assistant_status(_: User = Depends(get_current_user)):
    return _status()


@router.post("/ask", response_model=AssistantAnswer)
def ask_assistant(
    data: AssistantAsk,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    status = _status()
    if not status.enabled:
        raise HTTPException(status_code=503, detail="Trợ lý AI đang tắt.")
    provider = settings.ai_provider.lower().strip()
    if provider == "none":
        raise HTTPException(status_code=503, detail="Chưa cấu hình nhà cung cấp AI.")
    if not status.available:
        raise HTTPException(status_code=503, detail=status.message)

    try:
        answer, tools_called, result_data = answer_question(
            data.question.strip(),
            db=db,
            user=user,
        )
        db.add(
            AssistantQueryLog(
                user_id=user.id,
                question=data.question.strip(),
                tools_called=json.dumps(tools_called, ensure_ascii=False),
            )
        )
        db.commit()
        return AssistantAnswer(
            answer=answer,
            tools_called=tools_called,
            data=result_data,
        )
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AssistantProviderError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Trợ lý tạm thời không khả dụng. Vui lòng thử lại sau.",
        ) from exc
