from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, SessionLocal, engine, is_memory_sqlite
from app.routers import assistant, auth, lab, materials, production, quality, reports, stock, users
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    # An in-memory SQLite database cannot be migrated in a previous process.
    # Create its ephemeral schema here; file and PostgreSQL profiles use Alembic.
    if is_memory_sqlite:
        Base.metadata.create_all(bind=engine)
    upload_root = Path(__file__).resolve().parent.parent / "uploads"
    (upload_root / "avatars").mkdir(parents=True, exist_ok=True)
    (upload_root / "materials").mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(materials.router, prefix=prefix)
app.include_router(stock.router, prefix=prefix)
app.include_router(stock.suppliers_router, prefix=prefix)
app.include_router(stock.dashboard_router, prefix=prefix)
app.include_router(production.router, prefix=prefix)
app.include_router(lab.router, prefix=prefix)
app.include_router(reports.router, prefix=prefix)
app.include_router(quality.router, prefix=prefix)
app.include_router(assistant.router, prefix=prefix)

_upload_dir = Path(__file__).resolve().parent.parent / "uploads"
_upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_upload_dir)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}
