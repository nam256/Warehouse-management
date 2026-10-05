from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    BatchStatusHistory,
    CCPStatus,
    QualityApproval,
    QualityStatus,
    StockBatch,
    User,
    UserRole,
)
from app.services.audit import log_action


ALLOWED_TRANSITIONS = {
    ("quarantine", "sampling"),
    ("sampling", "under_test"),
    ("under_test", "awaiting_release"),
    ("under_test", "rejected"),
    ("under_test", "retest"),
    ("retest", "under_test"),
    ("awaiting_release", "released"),
    ("awaiting_release", "rejected"),
}

_LAB_TRANSITIONS = {
    ("quarantine", "sampling"),
    ("sampling", "under_test"),
    ("under_test", "awaiting_release"),
    ("under_test", "rejected"),
    ("under_test", "retest"),
    ("retest", "under_test"),
}
_APPROVAL_TRANSITIONS = {
    ("awaiting_release", "released"),
    ("awaiting_release", "rejected"),
}


def transition_batch(
    db: Session,
    batch: StockBatch,
    to_status: QualityStatus,
    user: User,
    reason: str | None = None,
    note: str | None = None,
) -> StockBatch:
    current = batch.quality_status.value
    target = to_status.value
    transition = (current, target)
    if transition not in ALLOWED_TRANSITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển trạng thái từ {current} sang {target}",
        )

    if transition in _LAB_TRANSITIONS and user.role not in (UserRole.lab, UserRole.admin):
        raise HTTPException(status_code=403, detail="Chỉ Lab được thực hiện bước kiểm nghiệm này")
    if transition in _APPROVAL_TRANSITIONS and user.role not in (UserRole.attp, UserRole.admin):
        raise HTTPException(status_code=403, detail="Chỉ ATTP được phê duyệt giải phóng lô")
    if transition in _APPROVAL_TRANSITIONS and (not reason or not note or not note.strip()):
        raise HTTPException(
            status_code=400,
            detail="ATTP phải nhập lý do và xác nhận điện tử khi phê duyệt",
        )
    if target == QualityStatus.awaiting_release.value and batch.ccp1_status != CCPStatus.pass_:
        raise HTTPException(status_code=400, detail="Lô phải đạt CCP1 trước khi gửi phê duyệt")

    batch.quality_status = to_status
    history = BatchStatusHistory(
        batch_id=batch.id,
        from_status=QualityStatus(current),
        to_status=to_status,
        reason=reason,
        note=note,
        changed_by_id=user.id,
    )
    db.add(history)

    if to_status == QualityStatus.awaiting_release:
        db.add(QualityApproval(batch_id=batch.id, submitted_by_id=user.id))
    elif to_status in (QualityStatus.released, QualityStatus.rejected):
        approval = (
            db.query(QualityApproval)
            .filter(QualityApproval.batch_id == batch.id)
            .order_by(QualityApproval.submitted_at.desc())
            .first()
        )
        if approval:
            from app.core.timezone import utc_now

            approval.approved_by_id = user.id
            approval.decision = target
            approval.signed_at = utc_now().replace(tzinfo=None)

    log_action(
        db,
        user,
        "QUALITY_TRANSITION",
        "stock_batch",
        batch.batch_no,
        f"{current} → {target}" + (f" — {note}" if note else ""),
    )
    return batch


def get_release_approval(db: Session, batch_id: int) -> QualityApproval | None:
    """Return the signed ATTP release approval, if any."""
    return (
        db.query(QualityApproval)
        .filter(
            QualityApproval.batch_id == batch_id,
            QualityApproval.decision == QualityStatus.released.value,
            QualityApproval.approved_by_id.isnot(None),
            QualityApproval.signed_at.isnot(None),
        )
        .order_by(QualityApproval.signed_at.desc())
        .first()
    )


def can_download_release_certificate(db: Session, batch: StockBatch) -> bool:
    return (
        batch.quality_status == QualityStatus.released
        and get_release_approval(db, batch.id) is not None
    )
