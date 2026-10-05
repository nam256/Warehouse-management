from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models import (
    CCPStatus,
    CapaStatus,
    Disposition,
    MaterialType,
    MovementType,
    OrderStatus,
    OrderType,
    PurchaseRequestStatus,
    QualityStatus,
    ReservationStatus,
    UserRole,
)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class UserUpdateMe(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=1, max_length=100)
    role: UserRole


class UserAdminOut(UserOut):
    is_active: bool


class UserAdminUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class MaterialCreate(BaseModel):
    code: str
    name: str
    type: MaterialType
    unit: str = "kg"
    min_stock: float = 0
    image_url: str | None = None


class MaterialOut(MaterialCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class MaterialUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    min_stock: float | None = None
    image_url: str | None = None
    is_active: bool | None = None


class SupplierCreate(BaseModel):
    code: str
    name: str
    contact: str | None = None


class SupplierOut(SupplierCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class StockReceiptCreate(BaseModel):
    material_id: int
    supplier_id: int | None = None
    warehouse_id: int = 1
    quantity: float = Field(gt=0)
    batch_no: str | None = None
    ccp1_c14: float | None = None
    mfg_date: date | None = None
    expiry_date: date | None = None
    notes: str | None = None


class StockIssueCreate(BaseModel):
    batch_id: int
    quantity: float = Field(gt=0)
    notes: str | None = None
    production_order_id: int | None = None


class StockBatchOut(BaseModel):
    id: int
    batch_no: str
    material_id: int
    quantity: float
    ccp1_c14: float | None
    ccp1_status: CCPStatus
    quality_status: QualityStatus = QualityStatus.quarantine
    mfg_date: date | None = None
    expiry_date: date | None = None
    source_order_id: int | None = None
    reserved_qty: float = 0
    available_qty: float | None = None
    has_release_certificate: bool = False

    model_config = {"from_attributes": True}


class FefoAllocationOut(BaseModel):
    batch_id: int
    batch_no: str
    qty: float
    expiry_date: date | None
    on_hand_qty: float
    reserved_qty: float
    available_qty: float


class QualityTransitionCreate(BaseModel):
    to_status: QualityStatus
    reason_code: str | None = None
    note: str | None = None


class StockMovementOut(BaseModel):
    id: int
    movement_type: MovementType
    batch_id: int
    quantity: float
    reference_no: str
    notes: str | None
    production_order_id: int | None = None
    created_at: str

    model_config = {"from_attributes": True}


class IssueLedgerItem(BaseModel):
    id: int
    reference_no: str
    created_at: str
    created_at_vn: str
    batch_id: int
    batch_no: str
    material_code: str
    material_name: str
    quantity: float
    issue_kind: str
    order_no: str | None = None
    created_by_name: str | None = None
    notes: str | None = None


class PeriodInventoryItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    material_type: str
    unit: str
    opening: float
    inbound: float
    outbound: float
    adjustment: float
    closing: float


class PeriodInventoryReport(BaseModel):
    date_from: str
    date_to: str
    note: str
    items: list[PeriodInventoryItem]


class InventoryItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    material_type: MaterialType
    unit: str
    total_quantity: float
    reserved_quantity: float = 0
    available_quantity: float = 0
    nearest_expiry: date | None = None
    min_stock: float
    low_stock: bool
    image_url: str | None = None


class DashboardSummary(BaseModel):
    material_count: int
    batch_count: int
    total_stock_kg: float
    low_stock_items: int
    ccp_pending: int
    ccp_fail: int
    orders_running: int = 0
    orders_done: int = 0
    ccp2_fail: int = 0
    overdue_capa_count: int = 0


class AlertItem(BaseModel):
    id: str
    kind: str
    severity: str
    title: str
    detail: str
    href: str


class AlertFeed(BaseModel):
    items: list[AlertItem]
    count: int


class PurchaseRequestCreate(BaseModel):
    material_id: int
    requested_qty: float = Field(gt=0)
    reason: str | None = None


class PurchaseRequestOut(BaseModel):
    id: int
    material_id: int
    material_code: str
    material_name: str
    requested_qty: float
    reason: str | None
    status: PurchaseRequestStatus
    created_at: str

    model_config = {"from_attributes": True}


class ProductionOrderCreate(BaseModel):
    product_material_id: int
    planned_qty: float = Field(gt=0)
    order_type: OrderType = OrderType.normal


class MaterialAllocation(BaseModel):
    batch_id: int
    quantity: float = Field(gt=0)


class StartProduction(BaseModel):
    materials: list[MaterialAllocation] = []


class OperationRecordCreate(BaseModel):
    step: str
    temperature: float | None = None
    pressure: float | None = None
    t_top: float | None = None
    t_ca_percent: float | None = None
    notes: str | None = None


class CompleteProduction(BaseModel):
    actual_qty: float = Field(gt=0)


class ProductionOrderOut(BaseModel):
    id: int
    order_no: str
    product_material_id: int
    product_code: str
    product_name: str
    planned_qty: float
    actual_qty: float | None
    status: OrderStatus
    order_type: OrderType = OrderType.normal
    output_batch_no: str | None
    created_at: str

    model_config = {"from_attributes": True}


class OperationRecordOut(BaseModel):
    id: int
    order_id: int
    step: str
    temperature: float | None
    pressure: float | None
    t_top: float | None
    t_ca_percent: float | None
    ccp2_status: CCPStatus
    notes: str | None
    created_at: str

    model_config = {"from_attributes": True}


class LabTestCreate(BaseModel):
    order_id: int | None = None
    batch_id: int | None = None
    test_type: str = "GC"
    gc_data: str | None = None
    c14: float | None = None
    t_ca_percent: float | None = None


class LabTestOut(BaseModel):
    id: int
    order_id: int | None
    batch_id: int | None
    test_type: str
    gc_data: str | None
    c14: float | None
    t_ca_percent: float | None
    result_status: CCPStatus
    created_at: str

    model_config = {"from_attributes": True}


class TraceNode(BaseModel):
    batch_no: str
    material_code: str
    material_name: str
    quantity: float
    ccp_status: str | None = None


class TraceResult(BaseModel):
    batch_no: str
    direction: str
    input_batches: list[TraceNode] = []
    production_orders: list[dict] = []
    output_batches: list[TraceNode] = []


class BatchTraceSuggest(BaseModel):
    batch_no: str
    material_code: str
    material_name: str
    material_type: str
    quantity: float
    trace_hint: str


class BatchPassportOut(BaseModel):
    batch_no: str
    material_code: str
    material_name: str
    material_type: str
    supplier_name: str | None = None
    received_at: datetime
    mfg_date: date | None = None
    expiry_date: date | None = None
    quantity: float
    quality_status: str
    ccp_status: str
    ccp_results: list[dict] = []
    source_order: dict | None = None
    downstream_orders: list[dict] = []
    certificate_url: str | None = None


class RecallSimulationCreate(BaseModel):
    batch_no: str = Field(min_length=1, max_length=50)
    reason: str = Field(min_length=1, max_length=1000)


class RecallAffectedBatch(BaseModel):
    batch_id: int
    batch_no: str
    material: str
    order_no: str | None
    quantity: float
    quality_status: str
    depth: int


class RecallAffectedOrder(BaseModel):
    order_id: int
    order_no: str
    input_batch_no: str
    output_batch_no: str
    quantity: float
    depth: int


class RecallSimulationResultOut(BaseModel):
    id: int
    root_batch_no: str
    reason: str
    initiated_by_id: int
    initiated_at: datetime
    duration_ms: int
    affected_batches: list[RecallAffectedBatch]
    affected_orders: list[RecallAffectedOrder]


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity: str
    entity_id: str | None
    detail: str | None
    user_name: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


class AuditLogPage(BaseModel):
    items: list[AuditLogOut]
    total: int
    page: int
    page_size: int
    pages: int


class MaterialBalanceOut(BaseModel):
    order_no: str
    input_total: float
    output_qty: float
    loss_qty: float
    loss_percent: float
    inputs: list[dict]


class MixingReportCreate(BaseModel):
    order_id: int
    formula: str | None = None
    input_batches: str | None = None
    mixed_qty: float = Field(gt=0)
    notes: str | None = None


class MixingReportOut(BaseModel):
    id: int
    order_id: int
    order_no: str
    formula: str | None
    mixed_qty: float
    notes: str | None
    created_at: str

    model_config = {"from_attributes": True}


class CorrectiveActionCreate(BaseModel):
    entity_type: str
    entity_id: int
    reason: str
    title: str | None = None
    source_type: str | None = None
    source_id: int | None = None
    root_cause: str | None = None
    action_taken: str | None = None
    due_date: date | None = None
    disposition: Disposition | None = None
    verification_note: str | None = None
    status: CapaStatus = CapaStatus.open


class CorrectiveActionTransition(BaseModel):
    to_status: CapaStatus
    root_cause: str | None = None
    action_taken: str | None = None
    due_date: date | None = None
    disposition: Disposition | None = None
    verification_note: str | None = None


class CorrectiveActionOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    reason: str
    title: str | None = None
    source_type: str | None = None
    source_id: int | None = None
    root_cause: str | None = None
    action_taken: str | None
    due_date: date | None = None
    disposition: Disposition | None = None
    verification_note: str | None = None
    status: CapaStatus
    verified_by_id: int | None = None
    verified_at: datetime | None = None
    closed_by_id: int | None = None
    closed_at: datetime | None = None
    created_at: str

    model_config = {"from_attributes": True}


class BatchStatusHistoryOut(BaseModel):
    id: int
    batch_id: int
    from_status: QualityStatus | None
    to_status: QualityStatus
    reason: str | None
    note: str | None
    changed_by_id: int
    changed_at: datetime

    model_config = {"from_attributes": True}


class QualityApprovalOut(BaseModel):
    id: int
    batch_id: int
    submitted_by_id: int
    approved_by_id: int | None
    decision: str | None
    submitted_at: datetime
    signed_at: datetime | None

    model_config = {"from_attributes": True}


class MaterialReservationOut(BaseModel):
    id: int
    order_id: int
    batch_id: int
    batch_no: str = ""
    quantity: float
    status: ReservationStatus
    expiry_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecallSimulationOut(BaseModel):
    id: int
    batch_id: int
    reason: str
    initiated_by_id: int
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GcImportOut(BaseModel):
    id: int
    filename: str
    sha256: str
    row_count: int
    imported_by_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class GcImportResultOut(BaseModel):
    imported: int
    duplicate: bool
    sha256: str
    row_count: int


class SpcPointOut(BaseModel):
    value: float
    tested_at: datetime
    batch_no: str
    out_of_control: bool


class SpcResultOut(BaseModel):
    analyte: str
    status: str
    mean: float | None
    std_dev: float | None
    ucl: float | None
    lcl: float | None
    points: list[SpcPointOut]


class AssistantQueryLogOut(BaseModel):
    id: int
    user_id: int
    question: str
    tools_called: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssistantAsk(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class AssistantAnswer(BaseModel):
    answer: str
    tools_called: list[str]
    data: list[dict]


class AssistantStatus(BaseModel):
    enabled: bool
    available: bool
    provider: str
    message: str
