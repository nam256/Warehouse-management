from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user, hash_password, require_roles
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserAdminOut, UserAdminUpdate, UserCreate
from app.services.audit import log_action
from app.services.audit_display import describe_user_admin_change, role_label

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserAdminOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    return db.query(User).order_by(User.username).all()


@router.post("", response_model=UserAdminOut, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(UserRole.admin)),
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    user = User(
        username=data.username.strip(),
        password_hash=hash_password(data.password),
        full_name=data.full_name.strip(),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    log_action(
        db,
        actor,
        "CREATE",
        "user",
        entity_id=user.username,
        detail=f"Tạo tài khoản {user.full_name} ({user.username}) — vai trò {role_label(user.role.value)}.",
    )
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")

    payload = data.model_dump(exclude_unset=True)
    if "is_active" in payload and payload["is_active"] is False and user.id == actor.id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản của chính mình")

    if payload.get("is_active") is False and user.role == UserRole.admin:
        other_admins = (
            db.query(User)
            .filter(User.role == UserRole.admin, User.is_active.is_(True), User.id != user.id)
            .count()
        )
        if other_admins == 0:
            raise HTTPException(status_code=400, detail="Không thể khóa admin cuối cùng")

    old_active = user.is_active
    old_role = user.role.value
    old_name = user.full_name

    if "full_name" in payload and payload["full_name"] is not None:
        name = payload["full_name"].strip()
        if not name:
            raise HTTPException(status_code=400, detail="Họ tên không được để trống")
        user.full_name = name
    if "role" in payload and payload["role"] is not None:
        user.role = payload["role"]
    if "is_active" in payload and payload["is_active"] is not None:
        user.is_active = payload["is_active"]

    log_action(
        db,
        actor,
        "UPDATE",
        "user",
        entity_id=user.username,
        detail=describe_user_admin_change(
            username=user.username,
            full_name=user.full_name,
            old_active=old_active,
            new_active=user.is_active,
            old_role=old_role,
            new_role=user.role.value,
            old_name=old_name,
            new_name=user.full_name,
        ),
    )
    db.commit()
    db.refresh(user)
    return user
