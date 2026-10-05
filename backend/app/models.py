import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    thu_kho = "thu_kho"
    ky_thuat = "ky_thuat"
    lab = "lab"
    ql_nm = "ql_nm"
    attp = "attp"


class MaterialType(str, enum.Enum):
    NVL = "NVL"
    BTP = "BTP"
    TP = "TP"


class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"


class CCPStatus(str, enum.Enum):
    pending = "pending"
    pass_ = "pass"
    fail = "fail"


class OrderStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    running = "running"
    done = "done"
    cancelled = "cancelled"


class OrderType(str, enum.Enum):
    normal = "normal"
    redistill = "redistill"


class PurchaseRequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    ordered = "ordered"
    cancelled = "cancelled"


class QualityStatus(str, enum.Enum):
    quarantine = "quarantine"
    sampling = "sampling"
    under_test = "under_test"
    awaiting_release = "awaiting_release"
    released = "released"
    rejected = "rejected"
    retest = "retest"


class CapaStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    action_pending = "action_pending"
    verification = "verification"
    closed = "closed"


class Disposition(str, enum.Enum):
    retest = "retest"
    rework = "rework"
    reject = "reject"
    use_as_is = "use_as_is"


class ReservationStatus(str, enum.Enum):
    active = "active"
    consumed = "consumed"
    released = "released"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[MaterialType] = mapped_column(Enum(MaterialType))
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    min_stock: Mapped[float] = mapped_column(Numeric(12, 3), default=0)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    contact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    product_material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    planned_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    actual_qty: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.draft)
    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType), default=OrderType.normal)
    output_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "stock_batches.id",
            use_alter=True,
            name="fk_production_orders_output_batch_id",
        ),
        nullable=True,
    )
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    product: Mapped["Material"] = relationship(foreign_keys=[product_material_id])
    output_batch: Mapped["StockBatch | None"] = relationship(foreign_keys=[output_batch_id])


class ProductionMaterialUsage(Base):
    __tablename__ = "production_material_usages"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"))
    batch_id: Mapped[int] = mapped_column(ForeignKey("stock_batches.id"))
    quantity: Mapped[float] = mapped_column(Numeric(12, 3))
    movement_id: Mapped[int | None] = mapped_column(ForeignKey("stock_movements.id"), nullable=True)

    order: Mapped["ProductionOrder"] = relationship()
    batch: Mapped["StockBatch"] = relationship()


class OperationRecord(Base):
    __tablename__ = "operation_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"))
    step: Mapped[str] = mapped_column(String(50))
    temperature: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    pressure: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    t_top: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    t_ca_percent: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    ccp2_status: Mapped[CCPStatus] = mapped_column(Enum(CCPStatus), default=CCPStatus.pending)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    order: Mapped["ProductionOrder"] = relationship()


class LabTest(Base):
    __tablename__ = "lab_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("production_orders.id"), nullable=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("stock_batches.id"), nullable=True)
    test_type: Mapped[str] = mapped_column(String(30))
    gc_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    c14: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    t_ca_percent: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    result_status: Mapped[CCPStatus] = mapped_column(Enum(CCPStatus), default=CCPStatus.pending)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    requested_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[PurchaseRequestStatus] = mapped_column(
        Enum(PurchaseRequestStatus), default=PurchaseRequestStatus.pending
    )
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    material: Mapped["Material"] = relationship()


class StockBatch(Base):
    __tablename__ = "stock_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    quantity: Mapped[float] = mapped_column(Numeric(12, 3), default=0)
    ccp1_c14: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    ccp1_status: Mapped[CCPStatus] = mapped_column(Enum(CCPStatus), default=CCPStatus.pending)
    quality_status: Mapped[QualityStatus] = mapped_column(
        Enum(QualityStatus, native_enum=False),
        default=QualityStatus.quarantine,
        server_default=QualityStatus.quarantine.value,
    )
    mfg_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_order_id: Mapped[int | None] = mapped_column(ForeignKey("production_orders.id"), nullable=True)
    receipt_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    material: Mapped["Material"] = relationship()
    supplier: Mapped["Supplier | None"] = relationship()
    warehouse: Mapped["Warehouse"] = relationship()


class BatchStatusHistory(Base):
    __tablename__ = "batch_status_histories"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("stock_batches.id"), index=True)
    from_status: Mapped[QualityStatus | None] = mapped_column(
        Enum(QualityStatus, native_enum=False), nullable=True
    )
    to_status: Mapped[QualityStatus] = mapped_column(Enum(QualityStatus, native_enum=False))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    batch: Mapped["StockBatch"] = relationship()
    changed_by: Mapped["User"] = relationship()


class QualityApproval(Base):
    __tablename__ = "quality_approvals"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("stock_batches.id"), index=True)
    submitted_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(30), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    batch: Mapped["StockBatch"] = relationship()
    submitted_by: Mapped["User"] = relationship(foreign_keys=[submitted_by_id])
    approved_by: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])


class MaterialReservation(Base):
    __tablename__ = "material_reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"), index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("stock_batches.id"), index=True)
    quantity: Mapped[float] = mapped_column(Numeric(12, 3))
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, native_enum=False), default=ReservationStatus.active
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    order: Mapped["ProductionOrder"] = relationship()
    batch: Mapped["StockBatch"] = relationship()


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType))
    batch_id: Mapped[int] = mapped_column(ForeignKey("stock_batches.id"))
    quantity: Mapped[float] = mapped_column(Numeric(12, 3))
    reference_no: Mapped[str] = mapped_column(String(50), index=True)
    production_order_id: Mapped[int | None] = mapped_column(ForeignKey("production_orders.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    batch: Mapped["StockBatch"] = relationship()
    created_by: Mapped["User"] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50))
    entity: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MixingReport(Base):
    __tablename__ = "mixing_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"))
    formula: Mapped[str | None] = mapped_column(String(200), nullable=True)
    input_batches: Mapped[str | None] = mapped_column(Text, nullable=True)
    mixed_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    order: Mapped["ProductionOrder"] = relationship()


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column()
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    reason: Mapped[str] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    disposition: Mapped[Disposition | None] = mapped_column(
        Enum(Disposition, native_enum=False), nullable=True
    )
    verification_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CapaStatus] = mapped_column(String(30), default=CapaStatus.open)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    verified_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    verified_by: Mapped["User | None"] = relationship(foreign_keys=[verified_by_id])
    closed_by: Mapped["User | None"] = relationship(foreign_keys=[closed_by_id])


class RecallSimulation(Base):
    __tablename__ = "recall_simulations"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("stock_batches.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    initiated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    batch: Mapped["StockBatch"] = relationship()
    initiated_by: Mapped["User"] = relationship()


class GcImport(Base):
    __tablename__ = "gc_imports"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    row_count: Mapped[int] = mapped_column(default=0)
    imported_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    imported_by: Mapped["User"] = relationship()


class AssistantQueryLog(Base):
    __tablename__ = "assistant_query_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    tools_called: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
