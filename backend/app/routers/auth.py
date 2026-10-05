from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import PasswordChange, Token, UserOut, UserUpdateMe
from app.services.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_BYTES = 1_000_000


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return Token(access_token=create_access_token(user.username))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdateMe,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    payload = data.model_dump(exclude_unset=True)
    if "full_name" in payload and payload["full_name"] is not None:
        name = payload["full_name"].strip()
        if not name:
            raise HTTPException(status_code=400, detail="Họ tên không được để trống")
        user.full_name = name
    if "avatar_url" in payload:
        user.avatar_url = payload["avatar_url"]
    log_action(db, user, "UPDATE", "user", entity_id=user.username, detail="Người dùng tự cập nhật họ tên trên hồ sơ")
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/password")
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
    user.password_hash = hash_password(data.new_password)
    log_action(db, user, "UPDATE", "user", entity_id=user.username, detail="Người dùng tự đổi mật khẩu")
    db.commit()
    return {"ok": True, "detail": "Đã đổi mật khẩu"}


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận ảnh JPG, PNG hoặc WebP")
    content = await file.read()
    if len(content) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=400, detail="Ảnh đại diện tối đa 1 MB")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
    upload_dir = Path(__file__).resolve().parents[2] / "uploads" / "avatars"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"user_{user.id}{ext}"
    path.write_bytes(content)
    user.avatar_url = f"/uploads/avatars/{path.name}"
    log_action(db, user, "UPDATE", "user", entity_id=user.username, detail="Người dùng tự cập nhật ảnh đại diện")
    db.commit()
    db.refresh(user)
    return user
