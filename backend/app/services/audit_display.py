"""Chuẩn hóa hiển thị nhật ký — bổ sung mã đọc được và mô tả tiếng Việt cho bản ghi cũ."""

import re
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import AuditLog, LabTest, OperationRecord, ProductionOrder, StockBatch, User

STEP_LABELS: dict[str, str] = {
    "chung_cat": "Chưng cất",
    "pha_tron": "Pha trộn",
    "dong_goi": "Đóng gói",
}

TEST_LABELS: dict[str, str] = {
    "GC": "Sắc ký khí (GC)",
    "gc": "Sắc ký khí (GC)",
    "C14": "Hàm lượng C14",
    "c14": "Hàm lượng C14",
}

ROLE_LABELS: dict[str, str] = {
    "admin": "Quản trị viên",
    "thu_kho": "Thủ kho",
    "ky_thuat": "Nhân viên kỹ thuật",
    "lab": "Phòng kiểm nghiệm",
    "attp": "Bộ phận an toàn thực phẩm",
    "ql_nm": "Quản lý nhà máy",
}

_OLD_USER_UPDATE = re.compile(r"^(\S+)\s+active=(True|False)\s+role=(\S+)$")
_OLD_USER_CREATE = re.compile(r"^(\S+)/(\S+)$")


def step_label(step: str | None) -> str:
    if not step:
        return "Vận hành"
    return STEP_LABELS.get(step, step.replace("_", " "))


def role_label(role: str | None) -> str:
    if not role:
        return "—"
    return ROLE_LABELS.get(role, role)


def describe_user_admin_change(
    *,
    username: str,
    full_name: str,
    old_active: bool,
    new_active: bool,
    old_role: str,
    new_role: str,
    old_name: str,
    new_name: str,
) -> str:
    who = f"{full_name} ({username})"
    parts: list[str] = []
    if new_active != old_active:
        parts.append("mở khóa tài khoản" if new_active else "khóa tài khoản")
    if new_role != old_role:
        parts.append(f"đổi vai trò từ {role_label(old_role)} sang {role_label(new_role)}")
    if new_name != old_name:
        parts.append(f"đổi họ tên thành «{new_name}»")
    if not parts:
        parts.append("cập nhật thông tin tài khoản")
    return f"{who}: {'; '.join(parts)}."


def _order_by_id(db: Session, oid: int) -> ProductionOrder | None:
    return db.query(ProductionOrder).filter(ProductionOrder.id == oid).first()


def _enrich_production(db: Session, log: AuditLog, entity_id: str | None, detail: str | None) -> tuple[str | None, str | None]:
    order: ProductionOrder | None = None
    if entity_id and entity_id.isdigit():
        order = _order_by_id(db, int(entity_id))
        if order:
            entity_id = order.order_no
    elif entity_id and entity_id.startswith("SX-"):
        order = db.query(ProductionOrder).filter(ProductionOrder.order_no == entity_id).first()

    if not order and detail:
        if detail.startswith("SX-"):
            order = db.query(ProductionOrder).filter(ProductionOrder.order_no == detail).first()
            if order and (not entity_id or entity_id.isdigit()):
                entity_id = order.order_no
        elif detail.startswith("TP-"):
            batch = db.query(StockBatch).filter(StockBatch.batch_no == detail).first()
            if batch and batch.source_order_id:
                order = _order_by_id(db, batch.source_order_id)
                if order:
                    entity_id = order.order_no

    if log.action == "COMPLETE" and detail and detail.startswith("TP-"):
        detail = f"Hoàn thành — lô thành phẩm {detail}"
    elif log.action == "APPROVE" and detail and detail.startswith("SX-"):
        detail = "Duyệt mẻ sản xuất"
    elif log.action == "START" and detail and detail.startswith("SX-"):
        detail = "Bắt đầu sản xuất — phân bổ nguyên liệu"

    if log.action == "OPERATION" and order:
        step_code = detail if detail in STEP_LABELS else None
        if step_code or (detail and not detail.startswith("Ghi")):
            op_q = db.query(OperationRecord).filter(OperationRecord.order_id == order.id)
            if log.created_at:
                window_start = log.created_at - timedelta(seconds=5)
                window_end = log.created_at + timedelta(seconds=5)
                op_q = op_q.filter(
                    OperationRecord.created_at >= window_start,
                    OperationRecord.created_at <= window_end,
                )
            op = op_q.order_by(OperationRecord.created_at.desc()).first()
            parts = [f"Công đoạn {step_label(step_code or (op.step if op else detail))}"]
            if op:
                if op.t_top is not None:
                    parts.append(f"nhiệt độ đỉnh {float(op.t_top)}°C")
                if op.t_ca_percent is not None:
                    parts.append(f"hàm lượng {float(op.t_ca_percent)}%")
            detail = " — ".join(parts)

    return entity_id, detail


def _enrich_lab(db: Session, log: AuditLog, entity_id: str | None, detail: str | None) -> tuple[str | None, str | None]:
    test: LabTest | None = None
    if entity_id and entity_id.isdigit():
        test = db.query(LabTest).filter(LabTest.id == int(entity_id)).first()

    if test:
        refs: list[str] = []
        if test.batch_id:
            batch = db.query(StockBatch).filter(StockBatch.id == test.batch_id).first()
            if batch:
                refs.append(batch.batch_no)
                if not entity_id or entity_id.isdigit():
                    entity_id = batch.batch_no
        if test.order_id:
            order = _order_by_id(db, test.order_id)
            if order:
                refs.append(order.order_no)
                if not entity_id or entity_id.isdigit():
                    entity_id = order.order_no
        test_name = TEST_LABELS.get(test.test_type, test.test_type)
        if detail in TEST_LABELS or detail in ("GC", "gc", "C14", "c14"):
            detail = f"{test_name}" + (f" — {', '.join(refs)}" if refs else "")
        elif refs:
            detail = f"{detail or test_name} — {', '.join(refs)}"

    elif detail in TEST_LABELS:
        detail = TEST_LABELS[detail]

    return entity_id, detail


def _enrich_user(db: Session, log: AuditLog, entity_id: str | None, detail: str | None) -> tuple[str | None, str | None]:
    if detail:
        matched = _OLD_USER_UPDATE.fullmatch(detail.strip())
        if matched:
            username, active, role = matched.groups()
            verb = "Mở khóa" if active == "True" else "Khóa"
            return username, f"{verb} tài khoản {username}. Vai trò: {role_label(role)}."
        if log.action == "CREATE":
            created = _OLD_USER_CREATE.fullmatch(detail.strip())
            if created:
                username, role = created.groups()
                return username, f"Tạo tài khoản {username} — vai trò {role_label(role)}."

    if entity_id and entity_id.isdigit():
        user = db.query(User).filter(User.id == int(entity_id)).first()
        if user:
            entity_id = user.username

    return entity_id, detail


def enrich_audit_log(db: Session, log: AuditLog) -> tuple[str | None, str | None]:
    entity_id = log.entity_id
    detail = log.detail

    if log.entity == "production_order":
        return _enrich_production(db, log, entity_id, detail)
    if log.entity == "lab_test":
        return _enrich_lab(db, log, entity_id, detail)
    if log.entity == "user":
        return _enrich_user(db, log, entity_id, detail)

    return entity_id, detail
