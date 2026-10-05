from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import Base, is_sqlite
from app import models as _models  # noqa: F401 — đăng ký toàn bộ bảng vào metadata
from app.models import (
    CapaStatus,
    CorrectiveAction,
    Material,
    MaterialType,
    PurchaseRequest,
    PurchaseRequestStatus,
    Supplier,
    User,
    UserRole,
    Warehouse,
)

DEMO_PR_REASON = "Cảnh báo mẫu: kho trống cần mua"
DEMO_CAPA_TITLE = "Cảnh báo mẫu: hạn khắc phục"

# Họ tên hiển thị khớp nhãn vai trò trên giao diện (có dấu đầy đủ)
DEMO_USERS = [
    ("admin", "admin123", "Quản trị viên", UserRole.admin),
    ("thu_kho", "kho123", "Thủ kho", UserRole.thu_kho),
    ("ky_thuat", "kt123", "Nhân viên kỹ thuật", UserRole.ky_thuat),
    ("lab", "lab123", "Phòng kiểm nghiệm", UserRole.lab),
    ("attp", "attp123", "Bộ phận an toàn thực phẩm", UserRole.attp),
    ("ql_nm", "ql123", "Quản lý nhà máy", UserRole.ql_nm),
]

MASTER_MATERIALS = [
    ("NVL-QUE", "Tinh dầu quế", MaterialType.NVL, "kg", 100, "/uploads/materials/demo-nvl-que.png"),
    ("TP-TCA", "Thành phẩm aldehyde cinamic (TCA)", MaterialType.TP, "kg", 50, "/uploads/materials/demo-tp-tca.png"),
    ("BTP-THO", "Thành phẩm thô (BTP chưng cất lại)", MaterialType.BTP, "kg", 20, "/uploads/materials/demo-btp-tho.png"),
]

MASTER_MATERIAL_CODES = {code for code, *_ in MASTER_MATERIALS}


def _ensure_users(db: Session) -> None:
    by_username = {u.username: u for u in db.query(User).all()}
    for username, password, full_name, role in DEMO_USERS:
        user = by_username.get(username)
        if user is None:
            db.add(
                User(
                    username=username,
                    password_hash=hash_password(password),
                    full_name=full_name,
                    role=role,
                )
            )
        else:
            user.full_name = full_name
            user.role = role
            user.is_active = True


def _ensure_master_data(db: Session) -> None:
    wh = db.query(Warehouse).filter(Warehouse.code == "KHO-NVL").first()
    if wh is None:
        db.add(Warehouse(code="KHO-NVL", name="Kho nguyên liệu"))
    else:
        wh.name = "Kho nguyên liệu"

    supplier = db.query(Supplier).filter(Supplier.code == "NCC-001").first()
    if supplier is None:
        db.add(
            Supplier(
                code="NCC-001",
                name="Nhà cung cấp dầu quế mẫu",
                contact="demo@supplier.local",
            )
        )
    else:
        supplier.name = "Nhà cung cấp dầu quế mẫu"
        supplier.contact = "demo@supplier.local"

    by_code = {m.code: m for m in db.query(Material).all()}
    for code, name, mtype, unit, min_stock, image_url in MASTER_MATERIALS:
        material = by_code.get(code)
        if material is None:
            db.add(
                Material(
                    code=code,
                    name=name,
                    type=mtype,
                    unit=unit,
                    min_stock=min_stock,
                    image_url=image_url,
                )
            )
        else:
            material.name = name
            material.type = mtype
            material.unit = unit
            material.min_stock = min_stock
            if not material.image_url or material.image_url.endswith(".svg"):
                material.image_url = image_url


def _ensure_demo_alerts(db: Session) -> None:
    """Yêu cầu mua + CAPA sắp hạn — không thêm kg tồn kho."""
    material = db.query(Material).filter(Material.code == "NVL-QUE").first()
    thu_kho = db.query(User).filter(User.username == "thu_kho").first()
    attp = db.query(User).filter(User.username == "attp").first()
    if material and thu_kho:
        exists = db.query(PurchaseRequest).filter(PurchaseRequest.reason == DEMO_PR_REASON).first()
        if exists is None:
            db.add(
                PurchaseRequest(
                    material_id=material.id,
                    requested_qty=100,
                    reason=DEMO_PR_REASON,
                    status=PurchaseRequestStatus.pending,
                    created_by_id=thu_kho.id,
                )
            )
    if attp:
        exists = (
            db.query(CorrectiveAction).filter(CorrectiveAction.title == DEMO_CAPA_TITLE).first()
        )
        if exists is None:
            db.add(
                CorrectiveAction(
                    entity_type="inventory",
                    entity_id=0,
                    source_type="inventory",
                    source_id=None,
                    title=DEMO_CAPA_TITLE,
                    reason="Hạn khắc phục gần đến — kiểm tra chuông cảnh báo",
                    status=CapaStatus.open,
                    due_date=date.today() + timedelta(days=2),
                    created_by_id=attp.id,
                )
            )
        else:
            exists.entity_type = "inventory"
            exists.source_type = "inventory"
            exists.source_id = None


def _clear_all_app_tables(db: Session) -> None:
    """Xóa toàn bộ dữ liệu nghiệp vụ; giữ alembic_version."""
    tables = [t for t in reversed(Base.metadata.sorted_tables) if t.name != "alembic_version"]
    if is_sqlite:
        db.execute(text("PRAGMA foreign_keys=OFF"))
        try:
            for table in tables:
                db.execute(table.delete())
        finally:
            db.execute(text("PRAGMA foreign_keys=ON"))
        return

    names = ", ".join(f'"{t.name}"' for t in tables)
    if names:
        db.execute(text(f"TRUNCATE TABLE {names} RESTART IDENTITY CASCADE"))


def reset_database(db: Session) -> None:
    """Đưa DB về trạng thái ban đầu: chỉ master data, chưa có giao dịch."""
    _clear_all_app_tables(db)
    db.flush()
    _ensure_users(db)
    _ensure_master_data(db)
    db.flush()
    _ensure_demo_alerts(db)
    db.commit()


def seed_database(db: Session) -> None:
    """Bổ sung master data nếu thiếu (không xóa giao dịch hiện có)."""
    _ensure_users(db)
    _ensure_master_data(db)
    db.flush()
    _ensure_demo_alerts(db)
    db.commit()
