import re

from sqlalchemy.orm import Session

from app.core.timezone import utc_now
from app.models import AuditLog, User

_REF_SUFFIX = re.compile(r"-(\d+)$")
_DATE_PART = re.compile(r"^\d{8}$")


def log_action(
    db: Session,
    user: User | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    detail: str | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user.id if user else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            detail=detail,
            created_at=utc_now(),
        )
    )


def short_ref(code: str | None) -> str:
    """SX-20260718-001 → SX-001; mã đã ngắn giữ nguyên."""
    if not code:
        return "—"
    parts = code.split("-")
    if len(parts) >= 3 and _DATE_PART.match(parts[1]):
        return f"{parts[0]}-{parts[-1]}"
    return code


def ref_seq(code: str | None) -> int:
    if not code:
        return 0
    match = _REF_SUFFIX.search(code)
    return int(match.group(1)) if match else 0


def next_ref(prefix: str, db: Session, model, field_name: str = "reference_no") -> str:
    column = getattr(model, field_name)
    values = [
        str(row[0])
        for row in db.query(column).filter(column.like(f"{prefix}-%")).all()
        if row[0]
    ]
    max_n = max((ref_seq(value) for value in values), default=0)
    return f"{prefix}-{max_n + 1:03d}"
