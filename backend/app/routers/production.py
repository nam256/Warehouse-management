from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models import (
    BatchStatusHistory,
    CCPStatus,
    Material,
    MaterialReservation,
    MaterialType,
    MovementType,
    MixingReport,
    OperationRecord,
    OrderStatus,
    OrderType,
    ProductionMaterialUsage,
    ProductionOrder,
    QualityApproval,
    QualityStatus,
    ReservationStatus,
    StockBatch,
    StockMovement,
    User,
    UserRole,
)
from app.schemas import (
    CompleteProduction,
    MaterialReservationOut,
    MaterialBalanceOut,
    MaterialAllocation,
    MixingReportCreate,
    MixingReportOut,
    OperationRecordCreate,
    OperationRecordOut,
    ProductionOrderCreate,
    ProductionOrderOut,
    StartProduction,
)
from app.services.audit import log_action, next_ref
from app.services.audit_display import step_label
from app.services.capa import create_capa_for_failure
from app.services.ccp import evaluate_ccp2
from app.services.fefo import suggest_fefo

router = APIRouter(prefix="/production", tags=["production"])


def _order_out(db: Session, order: ProductionOrder) -> ProductionOrderOut:
    product = db.query(Material).filter(Material.id == order.product_material_id).first()
    output_no = None
    if order.output_batch_id:
        ob = db.query(StockBatch).filter(StockBatch.id == order.output_batch_id).first()
        output_no = ob.batch_no if ob else None
    return ProductionOrderOut(
        id=order.id,
        order_no=order.order_no,
        product_material_id=order.product_material_id,
        product_code=product.code if product else "",
        product_name=product.name if product else "",
        planned_qty=float(order.planned_qty),
        actual_qty=float(order.actual_qty) if order.actual_qty else None,
        status=order.status,
        order_type=order.order_type,
        output_batch_no=output_no,
        created_at=order.created_at.isoformat(),
    )


@router.get("/orders", response_model=list[ProductionOrderOut])
def list_orders(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    orders = db.query(ProductionOrder).order_by(ProductionOrder.created_at.desc()).limit(100).all()
    return [_order_out(db, o) for o in orders]


@router.post("/orders", response_model=ProductionOrderOut, status_code=201)
def create_order(
    data: ProductionOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ky_thuat, UserRole.ql_nm)),
):
    product = db.query(Material).filter(Material.id == data.product_material_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    order_no = next_ref("SX", db, ProductionOrder, "order_no")
    order = ProductionOrder(
        order_no=order_no,
        product_material_id=data.product_material_id,
        planned_qty=data.planned_qty,
        order_type=data.order_type,
        status=OrderStatus.draft,
        created_by_id=user.id,
    )
    db.add(order)
    log_action(
        db,
        user,
        "CREATE",
        "production_order",
        order_no,
        f"Tạo mẻ — kế hoạch {float(data.planned_qty)} kg",
    )
    db.commit()
    db.refresh(order)
    return _order_out(db, order)


def _issue_for_production(
    db: Session, user: User, order: ProductionOrder, batch_id: int, quantity: float
) -> StockMovement:
    batch = db.query(StockBatch).filter(StockBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy lô {batch_id}")
    if float(batch.quantity) < quantity:
        raise HTTPException(status_code=400, detail=f"Lô {batch.batch_no} không đủ tồn")
    if batch.quality_status != QualityStatus.released:
        raise HTTPException(status_code=400, detail=f"Lô {batch.batch_no} chưa được ATTP giải phóng")
    if batch.ccp1_status != CCPStatus.pass_:
        raise HTTPException(status_code=400, detail=f"Lô {batch.batch_no} chưa đạt CCP1")
    if batch.expiry_date and batch.expiry_date < date.today():
        raise HTTPException(status_code=400, detail=f"Lô {batch.batch_no} đã hết hạn")

    batch.quantity = float(batch.quantity) - quantity
    ref = next_ref("PX", db, StockMovement)
    movement = StockMovement(
        movement_type=MovementType.OUT,
        batch_id=batch.id,
        quantity=quantity,
        reference_no=ref,
        production_order_id=order.id,
        notes=f"Xuất cho mẻ {order.order_no}",
        created_by_id=user.id,
    )
    db.add(movement)
    db.flush()
    db.add(
        ProductionMaterialUsage(
            order_id=order.id, batch_id=batch.id, quantity=quantity, movement_id=movement.id
        )
    )
    return movement


@router.post("/orders/{order_id}/approve", response_model=ProductionOrderOut)
def approve_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ql_nm)),
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    if order.status != OrderStatus.draft:
        raise HTTPException(status_code=400, detail="Chỉ duyệt mẻ ở trạng thái draft")

    input_material = (
        db.query(Material)
        .filter(Material.type == MaterialType.NVL, Material.is_active.is_(True))
        .order_by(Material.id.asc())
        .first()
    )
    if not input_material:
        raise HTTPException(status_code=400, detail="Chưa cấu hình nguyên liệu đầu vào")
    required_qty = float(order.planned_qty)
    allocations = suggest_fefo(db, input_material.id, warehouse_id=1, required_qty=required_qty)
    if sum(item.qty for item in allocations) + 1e-9 < required_qty:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ tồn khả dụng {input_material.code} để giữ chỗ cho mẻ",
        )
    for allocation in allocations:
        db.add(
            MaterialReservation(
                order_id=order.id,
                batch_id=allocation.batch_id,
                quantity=allocation.qty,
                status=ReservationStatus.active,
            )
        )
    order.status = OrderStatus.approved
    order.approved_by_id = user.id
    order.approved_at = datetime.utcnow()
    log_action(db, user, "APPROVE", "production_order", order.order_no, "Duyệt mẻ sản xuất")
    db.commit()
    db.refresh(order)
    return _order_out(db, order)


@router.post("/orders/{order_id}/cancel", response_model=ProductionOrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ql_nm, UserRole.ky_thuat)),
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    if order.status in (OrderStatus.done, OrderStatus.cancelled):
        raise HTTPException(status_code=400, detail="Không thể hủy mẻ đã hoàn thành")
    reservations = (
        db.query(MaterialReservation)
        .filter(MaterialReservation.order_id == order.id)
        .all()
    )
    for reservation in reservations:
        if reservation.status == ReservationStatus.active:
            reservation.status = ReservationStatus.released
            continue
        if reservation.status != ReservationStatus.consumed:
            continue
        batch = db.query(StockBatch).filter(StockBatch.id == reservation.batch_id).first()
        if not batch:
            raise HTTPException(status_code=400, detail="Không tìm thấy lô để hoàn tồn")
        usage = (
            db.query(ProductionMaterialUsage)
            .filter(
                ProductionMaterialUsage.order_id == order.id,
                ProductionMaterialUsage.batch_id == reservation.batch_id,
            )
            .first()
        )
        original = (
            db.query(StockMovement).filter(StockMovement.id == usage.movement_id).first()
            if usage and usage.movement_id
            else None
        )
        batch.quantity = float(batch.quantity) + float(reservation.quantity)
        db.add(
            StockMovement(
                movement_type=MovementType.IN,
                batch_id=batch.id,
                quantity=reservation.quantity,
                reference_no=next_ref("HT", db, StockMovement),
                production_order_id=order.id,
                notes=(
                    f"Hoàn tồn do hủy mẻ {order.order_no}; đảo phiếu "
                    f"{original.reference_no if original else 'OUT'}"
                ),
                created_by_id=user.id,
            )
        )
        reservation.status = ReservationStatus.released
    order.status = OrderStatus.cancelled
    log_action(db, user, "CANCEL", "production_order", order.order_no, "Hủy mẻ sản xuất")
    db.commit()
    db.refresh(order)
    return _order_out(db, order)


@router.post("/orders/{order_id}/start", response_model=ProductionOrderOut)
def start_order(
    order_id: int,
    data: StartProduction,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ky_thuat, UserRole.ql_nm)),
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    if order.status != OrderStatus.approved:
        raise HTTPException(status_code=400, detail="Mẻ SX phải được duyệt trước khi chạy")
    query = db.query(MaterialReservation).filter(
        MaterialReservation.order_id == order.id,
        MaterialReservation.status == ReservationStatus.active,
    )
    if db.get_bind().dialect.name == "postgresql":
        query = query.with_for_update()
    reservations = query.all()
    if not reservations:
        raise HTTPException(status_code=400, detail="Mẻ chưa có giữ chỗ nguyên liệu")

    for reservation in reservations:
        batch = db.query(StockBatch).filter(StockBatch.id == reservation.batch_id).first()
        movement = _issue_for_production(
            db, user, order, reservation.batch_id, float(reservation.quantity)
        )
        reservation.status = ReservationStatus.consumed
        if batch:
            log_action(
                db,
                user,
                "ISSUE",
                "stock_batch",
                batch.batch_no,
                f"Xuất {float(reservation.quantity)} kg cho mẻ {order.order_no} "
                f"từ giữ chỗ #{reservation.id}; phiếu {movement.reference_no}",
            )

    order.status = OrderStatus.running
    order.started_at = datetime.utcnow()
    log_action(db, user, "START", "production_order", order.order_no, "Bắt đầu sản xuất")
    db.commit()
    db.refresh(order)
    return _order_out(db, order)


@router.get("/orders/{order_id}/reservations", response_model=list[MaterialReservationOut])
def list_reservations(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    rows = (
        db.query(MaterialReservation)
        .filter(MaterialReservation.order_id == order_id)
        .order_by(MaterialReservation.created_at.asc(), MaterialReservation.id.asc())
        .all()
    )
    result = []
    for reservation in rows:
        batch = db.query(StockBatch).filter(StockBatch.id == reservation.batch_id).first()
        result.append(
            MaterialReservationOut(
                id=reservation.id,
                order_id=reservation.order_id,
                batch_id=reservation.batch_id,
                batch_no=batch.batch_no if batch else "",
                quantity=float(reservation.quantity),
                status=reservation.status,
                expiry_date=batch.expiry_date if batch else None,
                created_at=reservation.created_at,
                updated_at=reservation.updated_at,
            )
        )
    return result


@router.post("/orders/{order_id}/operations", response_model=OperationRecordOut, status_code=201)
def add_operation(
    order_id: int,
    data: OperationRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ky_thuat, UserRole.lab)),
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    if order.status != OrderStatus.running:
        raise HTTPException(status_code=400, detail="Mẻ SX chưa chạy")

    ccp2 = CCPStatus(evaluate_ccp2(data.t_top, data.t_ca_percent))
    record = OperationRecord(
        order_id=order.id,
        step=data.step,
        temperature=data.temperature,
        pressure=data.pressure,
        t_top=data.t_top,
        t_ca_percent=data.t_ca_percent,
        ccp2_status=ccp2,
        notes=data.notes,
        created_by_id=user.id,
    )
    db.add(record)
    db.flush()
    if ccp2 == CCPStatus.fail:
        create_capa_for_failure(
            db,
            "operation_record",
            record.id,
            created_by_id=user.id,
        )
    ccp2_parts = []
    if data.t_top is not None:
        ccp2_parts.append(f"nhiệt độ đỉnh {data.t_top}°C")
    if data.t_ca_percent is not None:
        ccp2_parts.append(f"hàm lượng {data.t_ca_percent}%")
    step_part = f"Công đoạn {step_label(data.step)}"
    ccp_part = ", ".join(ccp2_parts) if ccp2_parts else "Ghi nhận vận hành"
    log_action(
        db,
        user,
        "OPERATION",
        "production_order",
        order.order_no,
        f"{step_part} — {ccp_part}",
    )
    db.commit()
    db.refresh(record)
    return OperationRecordOut(
        id=record.id,
        order_id=record.order_id,
        step=record.step,
        temperature=float(record.temperature) if record.temperature else None,
        pressure=float(record.pressure) if record.pressure else None,
        t_top=float(record.t_top) if record.t_top else None,
        t_ca_percent=float(record.t_ca_percent) if record.t_ca_percent else None,
        ccp2_status=record.ccp2_status,
        notes=record.notes,
        created_at=record.created_at.isoformat(),
    )


@router.get("/orders/{order_id}/operations", response_model=list[OperationRecordOut])
def list_operations(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    records = db.query(OperationRecord).filter(OperationRecord.order_id == order_id).all()
    return [
        OperationRecordOut(
            id=r.id,
            order_id=r.order_id,
            step=r.step,
            temperature=float(r.temperature) if r.temperature else None,
            pressure=float(r.pressure) if r.pressure else None,
            t_top=float(r.t_top) if r.t_top else None,
            t_ca_percent=float(r.t_ca_percent) if r.t_ca_percent else None,
            ccp2_status=r.ccp2_status,
            notes=r.notes,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]


@router.post("/orders/{order_id}/complete", response_model=ProductionOrderOut)
def complete_order(
    order_id: int,
    data: CompleteProduction,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ky_thuat, UserRole.ql_nm)),
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    if order.status != OrderStatus.running:
        raise HTTPException(status_code=400, detail="Mẻ SX chưa chạy")

    records = db.query(OperationRecord).filter(OperationRecord.order_id == order.id).all()
    if any(r.ccp2_status == CCPStatus.fail for r in records):
        raise HTTPException(status_code=400, detail="Có operation record fail CCP2 — không hoàn thành mẻ")
    if not any(r.ccp2_status == CCPStatus.pass_ for r in records):
        raise HTTPException(status_code=400, detail="Chưa có CCP2 pass")

    batch_no = next_ref("TP", db, StockBatch, "batch_no")
    output = StockBatch(
        batch_no=batch_no,
        material_id=order.product_material_id,
        warehouse_id=1,
        quantity=data.actual_qty,
        source_order_id=order.id,
        ccp1_status=CCPStatus.pass_,
        quality_status=QualityStatus.awaiting_release,
    )
    db.add(output)
    db.flush()
    db.add(
        BatchStatusHistory(
            batch_id=output.id,
            from_status=None,
            to_status=QualityStatus.awaiting_release,
            reason="CCP2_PASS",
            note=f"Thành phẩm hoàn tất từ mẻ {order.order_no}",
            changed_by_id=user.id,
        )
    )
    db.add(QualityApproval(batch_id=output.id, submitted_by_id=user.id))

    ref = next_ref("PN", db, StockMovement)
    db.add(
        StockMovement(
            movement_type=MovementType.IN,
            batch_id=output.id,
            quantity=data.actual_qty,
            reference_no=ref,
            production_order_id=order.id,
            notes=f"Thành phẩm mẻ {order.order_no}",
            created_by_id=user.id,
        )
    )

    order.actual_qty = data.actual_qty
    order.output_batch_id = output.id
    order.status = OrderStatus.done
    order.finished_at = datetime.utcnow()
    log_action(
        db,
        user,
        "COMPLETE",
        "production_order",
        order.order_no,
        f"Hoàn thành — lô thành phẩm {batch_no} ({float(data.actual_qty)} kg)",
    )
    db.commit()
    db.refresh(order)
    return _order_out(db, order)


@router.get("/orders/{order_id}/balance", response_model=MaterialBalanceOut)
def material_balance(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    usages = db.query(ProductionMaterialUsage).filter(ProductionMaterialUsage.order_id == order.id).all()
    inputs = []
    input_total = 0.0
    for u in usages:
        batch = db.query(StockBatch).filter(StockBatch.id == u.batch_id).first()
        mat = db.query(Material).filter(Material.id == batch.material_id).first() if batch else None
        qty = float(u.quantity)
        input_total += qty
        inputs.append({"batch_no": batch.batch_no if batch else "", "material": mat.code if mat else "", "qty": qty})
    output_qty = float(order.actual_qty) if order.actual_qty else 0.0
    loss = max(input_total - output_qty, 0.0)
    loss_pct = (loss / input_total * 100) if input_total else 0.0
    return MaterialBalanceOut(
        order_no=order.order_no,
        input_total=input_total,
        output_qty=output_qty,
        loss_qty=loss,
        loss_percent=round(loss_pct, 2),
        inputs=inputs,
    )


@router.post("/mixing-reports", response_model=MixingReportOut, status_code=201)
def create_mixing_report(
    data: MixingReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.ky_thuat)),
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẻ SX")
    report = MixingReport(
        order_id=order.id,
        formula=data.formula,
        input_batches=data.input_batches,
        mixed_qty=data.mixed_qty,
        notes=data.notes,
        created_by_id=user.id,
    )
    db.add(report)
    log_action(db, user, "MIXING", "production_order", order.order_no, f"Pha trộn {float(data.mixed_qty)} kg")
    db.commit()
    db.refresh(report)
    return MixingReportOut(
        id=report.id,
        order_id=report.order_id,
        order_no=order.order_no,
        formula=report.formula,
        mixed_qty=float(report.mixed_qty),
        notes=report.notes,
        created_at=report.created_at.isoformat(),
    )


@router.get("/mixing-reports", response_model=list[MixingReportOut])
def list_mixing_reports(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(MixingReport).order_by(MixingReport.created_at.desc()).limit(100).all()
    result = []
    for r in rows:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == r.order_id).first()
        result.append(
            MixingReportOut(
                id=r.id,
                order_id=r.order_id,
                order_no=order.order_no if order else "",
                formula=r.formula,
                mixed_qty=float(r.mixed_qty),
                notes=r.notes,
                created_at=r.created_at.isoformat(),
            )
        )
    return result
