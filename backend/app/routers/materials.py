from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import Material, MaterialType, User, UserRole
from app.schemas import MaterialCreate, MaterialOut, MaterialUpdate
from app.services.audit import log_action

router = APIRouter(prefix="/materials", tags=["materials"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 1_000_000


@router.get("", response_model=list[MaterialOut])
def list_materials(
    type: MaterialType | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Material).filter(Material.is_active.is_(True))
    if type:
        q = q.filter(Material.type == type)
    return q.order_by(Material.code).all()


@router.post("", response_model=MaterialOut, status_code=201)
def create_material(
    data: MaterialCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ql_nm)),
):
    if db.query(Material).filter(Material.code == data.code).first():
        raise HTTPException(status_code=400, detail="Mã vật tư đã tồn tại")
    item = Material(**data.model_dump())
    db.add(item)
    log_action(db, user, "CREATE", "material", detail=data.code)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{material_id}", response_model=MaterialOut)
def get_material(material_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    return item


@router.patch("/{material_id}", response_model=MaterialOut)
def update_material(
    material_id: int,
    data: MaterialUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ql_nm)),
):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(item, key, value)
    log_action(db, user, "UPDATE", "material", entity_id=str(item.id), detail=item.code)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{material_id}/image", response_model=MaterialOut)
async def upload_material_image(
    material_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ql_nm)),
):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận ảnh JPG, PNG hoặc WebP")
    content = await file.read()
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Ảnh vật tư tối đa 1 MB")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
    upload_dir = Path(__file__).resolve().parents[2] / "uploads" / "materials"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"material_{item.id}{ext}"
    path.write_bytes(content)
    item.image_url = f"/uploads/materials/{path.name}?v={path.stat().st_mtime_ns}"
    log_action(db, user, "UPDATE", "material", entity_id=str(item.id), detail=f"{item.code} image")
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{material_id}/image", response_model=MaterialOut)
def delete_material_image(
    material_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ql_nm)),
):
    item = db.query(Material).filter(Material.id == material_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    if item.image_url:
        raw = item.image_url.split("?", 1)[0]
        if raw.startswith("/uploads/materials/"):
            name = Path(raw).name
            if name.startswith("material_"):
                path = Path(__file__).resolve().parents[2] / "uploads" / "materials" / name
                if path.is_file():
                    path.unlink()
    item.image_url = None
    log_action(db, user, "UPDATE", "material", entity_id=str(item.id), detail=f"{item.code} xóa ảnh")
    db.commit()
    db.refresh(item)
    return item
