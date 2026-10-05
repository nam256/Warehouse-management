from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    CCPStatus,
    CapaStatus,
    CorrectiveAction,
    Disposition,
    LabTest,
    OperationRecord,
    QualityStatus,
    StockBatch,
    User,
    UserRole,
)
from app.core.timezone import utc_now
from app.services.audit import log_action


ALLOWED_TRANSITIONS = {
    CapaStatus.open: CapaStatus.investigating,
    CapaStatus.investigating: CapaStatus.action_pending,
    CapaStatus.action_pending: CapaStatus.verification,
    CapaStatus.verification: CapaStatus.closed,
}


def _status_value(status: CapaStatus | str) -> CapaStatus:
    return status if isinstance(status, CapaStatus) else CapaStatus(status)


def _source_details(
    db: Session,
    source_type: str,
    source_id: int,
) -> tuple[str, str, int | None]:
    if source_type == "lab_test":
        source = db.query(LabTest).filter(LabTest.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Không tìm thấy kết quả kiểm nghiệm")
        if source.result_status != CCPStatus.fail:
            raise HTTPException(status_code=400, detail="Chỉ kết quả kiểm nghiệm không đạt mới tạo CAPA")
        return (
            f"CAPA kiểm nghiệm #{source.id}",
            f"Kết quả {source.test_type} không đạt yêu cầu CCP",
            source.created_by_id,
        )
    if source_type == "operation_record":
        source = db.query(OperationRecord).filter(OperationRecord.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi vận hành")
        if source.ccp2_status != CCPStatus.fail:
            raise HTTPException(status_code=400, detail="Chỉ bản ghi CCP2 không đạt mới tạo CAPA")
        return (
            f"CAPA CCP2 mẻ #{source.order_id}",
            f"Bản ghi vận hành #{source.id} không đạt CCP2",
            source.created_by_id,
        )
    if source_type == "stock_batch":
        source = db.query(StockBatch).filter(StockBatch.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Không tìm thấy lô")
        if source.quality_status != QualityStatus.rejected:
            raise HTTPException(status_code=400, detail="Chỉ lô bị ATTP từ chối mới tạo CAPA")
        return (
            f"CAPA lô {source.batch_no}",
            f"Lô {source.batch_no} bị ATTP từ chối giải phóng",
            None,
        )
    raise HTTPException(status_code=400, detail="Nguồn CAPA không hợp lệ")


def create_capa_for_failure(
    db: Session,
    source_type: str,
    source_id: int,
    *,
    created_by_id: int | None = None,
    reason: str | None = None,
) -> CorrectiveAction:
    existing = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.source_type == source_type,
            CorrectiveAction.source_id == source_id,
            CorrectiveAction.status != CapaStatus.closed,
        )
        .order_by(CorrectiveAction.id.asc())
        .first()
    )
    if existing:
        return existing

    title, default_reason, source_user_id = _source_details(db, source_type, source_id)
    actor_id = created_by_id or source_user_id
    if actor_id is None:
        raise HTTPException(status_code=400, detail="CAPA cần người khởi tạo")

    capa = CorrectiveAction(
        entity_type=source_type,
        entity_id=source_id,
        title=title,
        source_type=source_type,
        source_id=source_id,
        reason=reason or default_reason,
        due_date=date.today() + timedelta(days=14),
        status=CapaStatus.open,
        created_by_id=actor_id,
    )
    db.add(capa)
    db.flush()
    return capa


def transition_capa(
    db: Session,
    capa: CorrectiveAction,
    to_status: CapaStatus,
    user: User,
    *,
    root_cause: str | None = None,
    action_taken: str | None = None,
    due_date: date | None = None,
    disposition: Disposition | None = None,
    verification_note: str | None = None,
) -> CorrectiveAction:
    current = _status_value(capa.status)
    if ALLOWED_TRANSITIONS.get(current) != to_status:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển CAPA từ {current.value} sang {to_status.value}",
        )

    if current in (CapaStatus.open, CapaStatus.investigating):
        if user.role not in (UserRole.lab, UserRole.ky_thuat, UserRole.admin):
            raise HTTPException(status_code=403, detail="Chỉ Lab hoặc Kỹ thuật được cập nhật CAPA")
    else:
        if user.role not in (UserRole.attp, UserRole.admin):
            raise HTTPException(status_code=403, detail="Chỉ ATTP được xác minh và đóng CAPA")

    if root_cause is not None:
        capa.root_cause = root_cause.strip() or None
    if action_taken is not None:
        capa.action_taken = action_taken.strip() or None
    if due_date is not None:
        capa.due_date = due_date
    if disposition is not None:
        capa.disposition = disposition
    if verification_note is not None:
        capa.verification_note = verification_note.strip() or None

    now = utc_now().replace(tzinfo=None)
    if to_status == CapaStatus.verification:
        if not capa.root_cause or not capa.action_taken:
            raise HTTPException(
                status_code=400,
                detail="Cần nguyên nhân gốc và hành động khắc phục trước khi xác minh",
            )
        if not capa.verification_note:
            raise HTTPException(status_code=400, detail="ATTP phải nhập nội dung xác minh")
        capa.verified_by_id = user.id
        capa.verified_at = now

    if to_status == CapaStatus.closed:
        if not all(
            (
                capa.root_cause,
                capa.action_taken,
                capa.disposition,
                capa.verification_note,
                capa.verified_by_id,
                capa.verified_at,
            )
        ):
            raise HTTPException(
                status_code=400,
                detail="Không thể đóng CAPA khi thiếu nguyên nhân, hành động, disposition hoặc xác minh",
            )
        if capa.disposition == Disposition.use_as_is:
            if user.role != UserRole.attp or not capa.verification_note.strip():
                raise HTTPException(
                    status_code=400,
                    detail="use_as_is yêu cầu ATTP ghi rõ justification",
                )
        capa.closed_by_id = user.id
        capa.closed_at = now

    capa.status = to_status
    log_action(
        db,
        user,
        "CAPA_TRANSITION",
        "corrective_action",
        str(capa.id),
        f"{current.value} → {to_status.value}",
    )
    return capa
