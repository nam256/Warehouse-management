from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import (
    BatchStatusHistory,
    CapaStatus,
    CorrectiveAction,
    QualityApproval,
    QualityStatus,
    StockBatch,
    User,
    UserRole,
)
from app.schemas import (
    BatchStatusHistoryOut,
    CorrectiveActionCreate,
    CorrectiveActionOut,
    CorrectiveActionTransition,
    QualityTransitionCreate,
    StockBatchOut,
)
from app.services.audit import log_action
from app.services.capa import create_capa_for_failure, transition_capa
from app.services.pdf_export import release_certificate_pdf
from app.services.quality_release import (
    can_download_release_certificate,
    get_release_approval,
    transition_batch,
)

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/batches", response_model=list[StockBatchOut])
def list_quality_batches(
    status: QualityStatus | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(StockBatch)
    if status:
        query = query.filter(StockBatch.quality_status == status)
    if q and q.strip():
        query = query.filter(StockBatch.batch_no.ilike(f"%{q.strip()}%"))
    batches = query.order_by(StockBatch.created_at.desc()).limit(200).all()
    return [
        StockBatchOut.model_validate(batch).model_copy(
            update={
                "has_release_certificate": can_download_release_certificate(db, batch),
            }
        )
        for batch in batches
    ]


@router.post("/batches/{batch_id}/transition", response_model=StockBatchOut)
def change_batch_status(
    batch_id: int,
    data: QualityTransitionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    batch = db.query(StockBatch).filter(StockBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    try:
        transition_batch(
            db,
            batch,
            data.to_status,
            user,
            reason=data.reason_code,
            note=data.note,
        )
        if data.to_status == QualityStatus.rejected:
            create_capa_for_failure(
                db,
                "stock_batch",
                batch.id,
                created_by_id=user.id,
                reason=data.note or "Lô bị ATTP từ chối giải phóng",
            )
        db.commit()
        db.refresh(batch)
        return StockBatchOut.model_validate(batch).model_copy(
            update={
                "has_release_certificate": can_download_release_certificate(db, batch),
            }
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Không thể cập nhật trạng thái lô") from exc


@router.get("/batches/{batch_id}/history", response_model=list[BatchStatusHistoryOut])
def batch_history(
    batch_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(StockBatch).filter(StockBatch.id == batch_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    return (
        db.query(BatchStatusHistory)
        .filter(BatchStatusHistory.batch_id == batch_id)
        .order_by(BatchStatusHistory.changed_at.asc(), BatchStatusHistory.id.asc())
        .all()
    )


@router.get("/batches/{batch_id}/certificate.pdf")
def batch_release_certificate(
    batch_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    batch = db.query(StockBatch).filter(StockBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    if batch.quality_status != QualityStatus.released:
        raise HTTPException(status_code=400, detail="Chỉ lô đã giải phóng mới có chứng nhận")
    approval = get_release_approval(db, batch.id)
    if not approval or not approval.approved_by or not approval.signed_at:
        raise HTTPException(
            status_code=400,
            detail=(
                "Lô này được đánh dấu released từ dữ liệu cũ nhưng chưa có chữ ký "
                "ATTP qua Hold-Release. Hãy giải phóng lại lô trên board chất lượng "
                "để tạo chứng nhận PDF."
            ),
        )
    content = release_certificate_pdf(
        batch.batch_no,
        batch.ccp1_status.value,
        approval.submitted_by.full_name,
        approval.approved_by.full_name,
        approval.signed_at,
    )
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="release-certificate-{batch.batch_no}.pdf"'
        },
    )


def _action_out(item: CorrectiveAction) -> CorrectiveActionOut:
    return CorrectiveActionOut(
        id=item.id,
        entity_type=item.entity_type,
        entity_id=item.entity_id,
        title=item.title,
        source_type=item.source_type,
        source_id=item.source_id,
        reason=item.reason,
        root_cause=item.root_cause,
        action_taken=item.action_taken,
        due_date=item.due_date,
        disposition=item.disposition,
        verification_note=item.verification_note,
        status=item.status,
        verified_by_id=item.verified_by_id,
        verified_at=item.verified_at,
        closed_by_id=item.closed_by_id,
        closed_at=item.closed_at,
        created_at=item.created_at.isoformat(),
    )


@router.get("/corrective-actions", response_model=list[CorrectiveActionOut])
def list_actions(
    scope: str | None = Query(None, pattern="^(open|overdue|closed)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(CorrectiveAction)
    if scope == "closed":
        query = query.filter(CorrectiveAction.status == CapaStatus.closed)
    elif scope == "overdue":
        query = query.filter(
            CorrectiveAction.status != CapaStatus.closed,
            CorrectiveAction.due_date < date.today(),
        )
    elif scope == "open":
        query = query.filter(CorrectiveAction.status != CapaStatus.closed)
    rows = query.order_by(CorrectiveAction.created_at.desc()).limit(200).all()
    return [_action_out(row) for row in rows]


@router.post("/corrective-actions", response_model=CorrectiveActionOut, status_code=201)
def create_action(
    data: CorrectiveActionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.attp, UserRole.lab)),
):
    item = CorrectiveAction(
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        title=data.title,
        source_type=data.source_type or data.entity_type,
        source_id=data.source_id or data.entity_id,
        reason=data.reason,
        root_cause=data.root_cause,
        action_taken=data.action_taken,
        due_date=data.due_date,
        disposition=data.disposition,
        verification_note=data.verification_note,
        status=CapaStatus.open,
        created_by_id=user.id,
    )
    db.add(item)
    log_action(db, user, "CORRECTIVE", data.entity_type, str(data.entity_id), data.reason[:80])
    db.commit()
    db.refresh(item)
    return _action_out(item)


@router.post(
    "/corrective-actions/{action_id}/transition",
    response_model=CorrectiveActionOut,
)
def change_action_status(
    action_id: int,
    data: CorrectiveActionTransition,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy CAPA")
    try:
        transition_capa(
            db,
            item,
            data.to_status,
            user,
            root_cause=data.root_cause,
            action_taken=data.action_taken,
            due_date=data.due_date,
            disposition=data.disposition,
            verification_note=data.verification_note,
        )
        db.commit()
        db.refresh(item)
        return _action_out(item)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Không thể cập nhật CAPA") from exc
