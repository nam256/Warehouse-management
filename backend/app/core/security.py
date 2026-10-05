import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expire}, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
    if not user:
        raise credentials_exception
    return user


def require_roles(*roles: UserRole):
    def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles and user.role != UserRole.admin:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")
        return user

    return checker
