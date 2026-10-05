from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import (
    CCPStatus,
    CapaStatus,
    CorrectiveAction,
    Material,
    MaterialReservation,
    MovementType,
    OperationRecord,
    OrderStatus,
    ProductionOrder,
    PurchaseRequest,
    PurchaseRequestStatus,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    StockMovement,
    Supplier,
    User,
    UserRole,
    Warehouse,
)
from app.schemas import (
    AlertFeed,
    DashboardSummary,
    FefoAllocationOut,
    InventoryItem,
    PurchaseRequestCreate,
    PurchaseRequestOut,
    StockBatchOut,
    StockIssueCreate,
    StockMovementOut,
    StockReceiptCreate,
    SupplierCreate,
    SupplierOut,
)
from app.services.alerts import build_alert_feed
from app.services.audit import log_action, next_ref
from app.services.fefo import active_reserved_subquery, suggest_fefo
from app.services.inventory_report import summarize_inventory

router = APIRouter(prefix="/stock", tags=["stock"])
suppliers_router = APIRouter(prefix="/suppliers", tags=["suppliers"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@suppliers_router.get("", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Supplier).filter(Supplier.is_active.is_(True)).all()


@suppliers_router.post("", response_model=SupplierOut, status_code=201)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho)),
):
    if db.query(Supplier).filter(Supplier.code == data.code).first():
        raise HTTPException(status_code=400, detail="Mã NCC đã tồn tại")
    item = Supplier(**data.model_dump())
    db.add(item)
    log_action(db, user, "CREATE", "supplier", detail=data.code)
    db.commit()
    db.refresh(item)
    return item


@router.post("/receipts", response_model=StockBatchOut, status_code=201)
def stock_receipt(
    data: StockReceiptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho)),
):
    material = db.query(Material).filter(Material.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    warehouse = db.query(Warehouse).filter(Warehouse.id == data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Không tìm thấy kho")

    batch_no = data.batch_no or next_ref("NVL", db, StockBatch, "batch_no")
    if db.query(StockBatch).filter(StockBatch.batch_no == batch_no).first():
        raise HTTPException(status_code=400, detail="Mã lô đã tồn tại")

    batch = StockBatch(
        batch_no=batch_no,
        material_id=data.material_id,
        supplier_id=data.supplier_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        ccp1_c14=None,
        ccp1_status=CCPStatus.pending,
        quality_status=QualityStatus.quarantine,
        mfg_date=data.mfg_date,
        expiry_date=data.expiry_date,
        receipt_note=data.notes,
    )
    db.add(batch)
    db.flush()

    ref = next_ref("PN", db, StockMovement)
    movement = StockMovement(
        movement_type=MovementType.IN,
        batch_id=batch.id,
        quantity=data.quantity,
        reference_no=ref,
        notes=data.notes,
        created_by_id=user.id,
    )
    db.add(movement)
    log_action(
        db,
        user,
        "RECEIPT",
        "stock_batch",
        batch_no,
        f"Nhập {float(data.quantity)} kg — CCP1: {batch.ccp1_status.value}",
    )
    db.commit()
    db.refresh(batch)
    return batch


@router.post("/issues", response_model=StockMovementOut, status_code=201)
def stock_issue(
    data: StockIssueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ky_thuat)),
):
    batch = db.query(StockBatch).filter(StockBatch.id == data.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô")
    active_reserved = (
        db.query(MaterialReservation)
        .filter(
            MaterialReservation.batch_id == batch.id,
            MaterialReservation.status == ReservationStatus.active,
        )
        .all()
    )
    available = float(batch.quantity) - sum(float(item.quantity) for item in active_reserved)
    if available < data.quantity:
        raise HTTPException(status_code=400, detail="Tồn khả dụng của lô không đủ")
    if batch.quality_status != QualityStatus.released:
        raise HTTPException(status_code=400, detail="Lô chưa được ATTP giải phóng — không được xuất")
    if batch.ccp1_status != CCPStatus.pass_:
        raise HTTPException(status_code=400, detail="Lô chưa đạt CCP1 — không được xuất")
    if batch.expiry_date and batch.expiry_date < date.today():
        raise HTTPException(status_code=400, detail="Lô đã hết hạn — không được xuất")

    batch.quantity = float(batch.quantity) - data.quantity
    ref = next_ref("PX", db, StockMovement)
    movement = StockMovement(
        movement_type=MovementType.OUT,
        batch_id=batch.id,
        quantity=data.quantity,
        reference_no=ref,
        production_order_id=data.production_order_id,
        notes=data.notes,
        created_by_id=user.id,
    )
    db.add(movement)
    log_action(
        db,
        user,
        "ISSUE",
        "stock_batch",
        batch.batch_no,
        f"Xuất {float(data.quantity)} kg — phiếu {ref}",
    )
    db.commit()
    db.refresh(movement)
    return StockMovementOut(
        id=movement.id,
        movement_type=movement.movement_type,
        batch_id=movement.batch_id,
        quantity=float(movement.quantity),
        reference_no=movement.reference_no,
        notes=movement.notes,
        production_order_id=movement.production_order_id,
        created_at=movement.created_at.isoformat(),
    )


@router.get("/movements", response_model=list[StockMovementOut])
def list_movements(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(100).all()
    return [
        StockMovementOut(
            id=m.id,
            movement_type=m.movement_type,
            batch_id=m.batch_id,
            quantity=float(m.quantity),
            reference_no=m.reference_no,
            notes=m.notes,
            production_order_id=m.production_order_id,
            created_at=m.created_at.isoformat(),
        )
        for m in rows
    ]


@router.get("/purchase-requests", response_model=list[PurchaseRequestOut])
def list_purchase_requests(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(PurchaseRequest).order_by(PurchaseRequest.created_at.desc()).limit(100).all()
    result = []
    for r in rows:
        m = db.query(Material).filter(Material.id == r.material_id).first()
        result.append(
            PurchaseRequestOut(
                id=r.id,
                material_id=r.material_id,
                material_code=m.code if m else "",
                material_name=m.name if m else "",
                requested_qty=float(r.requested_qty),
                reason=r.reason,
                status=r.status,
                created_at=r.created_at.isoformat(),
            )
        )
    return result


@router.post("/purchase-requests", response_model=PurchaseRequestOut, status_code=201)
def create_purchase_request(
    data: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ql_nm)),
):
    material = db.query(Material).filter(Material.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    req = PurchaseRequest(
        material_id=data.material_id,
        requested_qty=data.requested_qty,
        reason=data.reason,
        status=PurchaseRequestStatus.pending,
        created_by_id=user.id,
    )
    db.add(req)
    db.flush()
    log_action(
        db,
        user,
        "PURCHASE_REQ",
        "purchase_request",
        str(req.id),
        f"{material.code} — yêu cầu {float(data.requested_qty)} kg",
    )
    db.commit()
    db.refresh(req)
    return PurchaseRequestOut(
        id=req.id,
        material_id=req.material_id,
        material_code=material.code,
        material_name=material.name,
        requested_qty=float(req.requested_qty),
        reason=req.reason,
        status=req.status,
        created_at=req.created_at.isoformat(),
    )


@router.get("/inventory", response_model=list[InventoryItem])
def inventory(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return [
        InventoryItem(
            material_id=row.material_id,
            material_code=row.material_code,
            material_name=row.material_name,
            material_type=row.material_type,
            unit=row.unit,
            total_quantity=row.on_hand,
            reserved_quantity=row.reserved,
            available_quantity=row.available,
            nearest_expiry=row.nearest_expiry,
            min_stock=row.min_stock,
            low_stock=row.low_stock,
            image_url=row.image_url,
        )
        for row in summarize_inventory(db)
    ]


@router.get("/batches", response_model=list[StockBatchOut])
def list_batches(
    fifo: bool = Query(False, description="FIFO: lô cũ trước"),
    material_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    reserved = active_reserved_subquery()
    q = db.query(StockBatch, reserved.label("reserved_qty")).filter(StockBatch.quantity > 0)
    if material_id:
        q = q.filter(StockBatch.material_id == material_id)
    q = q.order_by(StockBatch.created_at.asc() if fifo else StockBatch.created_at.desc())
    return [
        StockBatchOut(
            id=batch.id,
            batch_no=batch.batch_no,
            material_id=batch.material_id,
            quantity=float(batch.quantity),
            ccp1_c14=float(batch.ccp1_c14) if batch.ccp1_c14 is not None else None,
            ccp1_status=batch.ccp1_status,
            quality_status=batch.quality_status,
            mfg_date=batch.mfg_date,
            expiry_date=batch.expiry_date,
            source_order_id=batch.source_order_id,
            reserved_qty=float(reserved_qty or 0),
            available_qty=max(float(batch.quantity) - float(reserved_qty or 0), 0),
        )
        for batch, reserved_qty in q.limit(100).all()
    ]


@router.get("/fefo-suggest", response_model=list[FefoAllocationOut])
def fefo_suggest(
    material_id: int,
    qty: float = Query(gt=0),
    warehouse_id: int = 1,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(UserRole.admin, UserRole.thu_kho, UserRole.ky_thuat, UserRole.ql_nm)
    ),
):
    if not db.query(Material).filter(Material.id == material_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy vật tư")
    return suggest_fefo(db, material_id, warehouse_id, qty)


@dashboard_router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    materials_count = db.query(Material).filter(Material.is_active.is_(True)).count()
    batches = db.query(StockBatch).all()
    total = sum(float(b.quantity) for b in batches)
    low = 0
    for m in db.query(Material).filter(Material.is_active.is_(True)).all():
        mat_total = sum(float(b.quantity) for b in batches if b.material_id == m.id)
        if mat_total < float(m.min_stock):
            low += 1
    pending = db.query(StockBatch).filter(StockBatch.ccp1_status == CCPStatus.pending).count()
    fail = db.query(StockBatch).filter(StockBatch.ccp1_status == CCPStatus.fail).count()
    running = db.query(ProductionOrder).filter(ProductionOrder.status == OrderStatus.running).count()
    done = db.query(ProductionOrder).filter(ProductionOrder.status == OrderStatus.done).count()
    ccp2_fail = db.query(OperationRecord).filter(OperationRecord.ccp2_status == CCPStatus.fail).count()
    overdue_capa_count = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.status != CapaStatus.closed,
            CorrectiveAction.due_date < date.today(),
        )
        .count()
    )
    return DashboardSummary(
        material_count=materials_count,
        batch_count=len(batches),
        total_stock_kg=total,
        low_stock_items=low,
        ccp_pending=pending,
        ccp_fail=fail,
        orders_running=running,
        orders_done=done,
        ccp2_fail=ccp2_fail,
        overdue_capa_count=overdue_capa_count,
    )


@dashboard_router.get("/alerts", response_model=AlertFeed)
def dashboard_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Cảnh báo hiện tại theo vai trò — không lưu lịch sử, tự hết khi xử lý xong."""
    return build_alert_feed(db, user)
