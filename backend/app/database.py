from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

is_sqlite = settings.database_url.startswith("sqlite")
is_memory_sqlite = settings.database_url in {"sqlite://", "sqlite:///:memory:"}
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_options = {"poolclass": StaticPool} if is_memory_sqlite else {}
engine = create_engine(settings.database_url, connect_args=connect_args, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
