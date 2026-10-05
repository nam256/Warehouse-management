import { clearStoredToken, readStoredToken } from "./auth";

const API = "/api/v1";

export type User = {
  id: number;
  username: string;
  full_name: string;
  role: string;
  avatar_url?: string | null;
};

export type AdminUser = User & {
  is_active: boolean;
};

export type Material = {
  id: number;
  code: string;
  name: string;
  type?: string;
  unit?: string;
  min_stock?: number;
  image_url?: string | null;
  is_active?: boolean;
};

export type AssistantStatus = {
  enabled: boolean;
  available: boolean;
  provider: string;
  message: string;
};

export type AssistantAnswer = {
  answer: string;
  tools_called: string[];
  data: { tool: string; result: unknown }[];
};

export type QualityStatus =
  | "quarantine"
  | "sampling"
  | "under_test"
  | "awaiting_release"
  | "released"
  | "rejected"
  | "retest";

export type QualityBatch = {
  id: number;
  batch_no: string;
  material_id: number;
  quantity: number;
  ccp1_c14: number | null;
  ccp1_status: "pending" | "pass" | "fail";
  quality_status: QualityStatus;
  expiry_date: string | null;
  reserved_qty: number;
  available_qty: number;
  has_release_certificate?: boolean;
};

export type FefoAllocation = {
  batch_id: number;
  batch_no: string;
  qty: number;
  expiry_date: string | null;
  on_hand_qty: number;
  reserved_qty: number;
  available_qty: number;
};

export type MaterialReservation = {
  id: number;
  order_id: number;
  batch_id: number;
  batch_no: string;
  quantity: number;
  status: "active" | "consumed" | "released";
  expiry_date: string | null;
  created_at: string;
  updated_at: string;
};

export type BatchStatusHistory = {
  id: number;
  batch_id: number;
  from_status: QualityStatus | null;
  to_status: QualityStatus;
  reason: string | null;
  note: string | null;
  changed_by_id: number;
  changed_at: string;
};

export type CapaStatus = "open" | "investigating" | "action_pending" | "verification" | "closed";
export type CapaDisposition = "retest" | "rework" | "reject" | "use_as_is";
export type CapaScope = "open" | "overdue" | "closed";

export type CorrectiveAction = {
  id: number;
  entity_type: string;
  entity_id: number;
  title: string | null;
  source_type: string | null;
  source_id: number | null;
  reason: string;
  root_cause: string | null;
  action_taken: string | null;
  due_date: string | null;
  disposition: CapaDisposition | null;
  verification_note: string | null;
  status: CapaStatus;
  verified_by_id: number | null;
  verified_at: string | null;
  closed_by_id: number | null;
  closed_at: string | null;
  created_at: string;
};

export type CapaTransitionInput = {
  to_status: CapaStatus;
  root_cause?: string;
  action_taken?: string;
  due_date?: string;
  disposition?: CapaDisposition;
  verification_note?: string;
};

type RequestOptions = RequestInit & { silent401?: boolean };

function authHeader(): HeadersInit {
  const token = readStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function emitSessionExpired() {
  window.dispatchEvent(new CustomEvent("auth:expired"));
}

async function parseError(res: Response): Promise<string> {
  const err = await res.json().catch(() => ({}));
  if (typeof err.detail === "string") return err.detail;
  if (err.detail && typeof err.detail === "object") {
    const message = typeof err.detail.message === "string" ? err.detail.message : "Dữ liệu không hợp lệ.";
    const errors = Array.isArray(err.detail.errors)
      ? err.detail.errors.filter((item: unknown) => typeof item === "string")
      : [];
    return errors.length > 0 ? `${message} ${errors.join(" ")}` : message;
  }
  if (res.status === 403) return "Không có quyền thực hiện thao tác này";
  if (res.status === 401) return "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
  return "Lỗi API";
}

async function request<T = unknown>(path: string, init?: RequestOptions): Promise<T> {
  const { silent401, ...fetchInit } = init ?? {};
  const res = await fetch(`${API}${path}`, { ...fetchInit, headers: { ...authHeader(), ...fetchInit.headers } });
  if (!res.ok) {
    if (res.status === 401 && !silent401) {
      clearStoredToken();
      emitSessionExpired();
    }
    throw new Error(await parseError(res));
  }
  return res.json();
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Đăng nhập thất bại");
  return res.json() as Promise<{ access_token: string }>;
}

export async function getMe(): Promise<User> {
  return request("/auth/me", { silent401: true });
}

export async function updateMe(data: { full_name?: string; avatar_url?: string | null }): Promise<User> {
  return request("/auth/me", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function changePassword(current_password: string, new_password: string): Promise<{ ok: boolean }> {
  return request("/auth/me/password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ current_password, new_password }),
  });
}

export async function uploadAvatar(file: File): Promise<User> {
  const body = new FormData();
  body.append("file", file);
  return request("/auth/me/avatar", { method: "POST", body });
}

export async function getUsers(): Promise<AdminUser[]> {
  return request("/users");
}

export async function createUser(data: {
  username: string;
  password: string;
  full_name: string;
  role: string;
}): Promise<AdminUser> {
  return request("/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function updateUser(
  id: number,
  data: { full_name?: string; role?: string; is_active?: boolean },
): Promise<AdminUser> {
  return request(`/users/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function updateMaterial(
  id: number,
  data: { name?: string; unit?: string; min_stock?: number; image_url?: string | null; is_active?: boolean },
): Promise<Material> {
  return request(`/materials/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function uploadMaterialImage(id: number, file: File): Promise<Material> {
  const body = new FormData();
  body.append("file", file);
  return request(`/materials/${id}/image`, { method: "POST", body });
}

export async function deleteMaterialImage(id: number): Promise<Material> {
  return request(`/materials/${id}/image`, { method: "DELETE" });
}

export async function getAssistantStatus(): Promise<AssistantStatus> {
  return request("/assistant/status");
}

export async function askAssistant(
  question: string,
  init?: { signal?: AbortSignal },
): Promise<AssistantAnswer> {
  return request("/assistant/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal: init?.signal,
  });
}

export async function getInventory(): Promise<any[]> {
  return request("/stock/inventory");
}

export async function getDashboard(): Promise<Record<string, number>> {
  return request("/dashboard/summary");
}

export type AlertItem = {
  id: string;
  kind: string;
  severity: string;
  title: string;
  detail: string;
  href: string;
};

export type AlertFeed = {
  items: AlertItem[];
  count: number;
};

export async function getAlerts(): Promise<AlertFeed> {
  return request("/dashboard/alerts");
}

export async function getMaterials(): Promise<any[]> {
  return request("/materials");
}

export async function getBatches(): Promise<QualityBatch[]> {
  return request("/stock/batches");
}

export async function getQualityBatches(status = "", q = ""): Promise<QualityBatch[]> {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (q.trim()) params.set("q", q.trim());
  const query = params.toString();
  return request(`/quality/batches${query ? `?${query}` : ""}`);
}

export async function transitionQualityBatch(
  batchId: number,
  toStatus: QualityStatus,
  reasonCode: string,
  note = "",
): Promise<QualityBatch> {
  return request(`/quality/batches/${batchId}/transition`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to_status: toStatus, reason_code: reasonCode, note }),
  });
}

export async function getQualityBatchHistory(batchId: number): Promise<BatchStatusHistory[]> {
  return request(`/quality/batches/${batchId}/history`);
}

export async function getCorrectiveActions(scope: CapaScope): Promise<CorrectiveAction[]> {
  return request(`/quality/corrective-actions?scope=${scope}`);
}

export async function transitionCorrectiveAction(
  actionId: number,
  data: CapaTransitionInput,
): Promise<CorrectiveAction> {
  return request(`/quality/corrective-actions/${actionId}/transition`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function downloadReleaseCertificate(batchId: number, batchNo: string) {
  return downloadAuthenticated(
    `/quality/batches/${batchId}/certificate.pdf`,
    `chung-nhan-giai-phong-${batchNo}.pdf`,
  );
}

export async function getMovements(): Promise<any[]> {
  return request("/stock/movements");
}

export async function createReceipt(data: Record<string, unknown>): Promise<any> {
  return request("/stock/receipts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function createIssue(data: Record<string, unknown>): Promise<any> {
  return request("/stock/issues", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function suggestFefo(
  materialId: number,
  qty: number,
  warehouseId = 1,
): Promise<FefoAllocation[]> {
  const params = new URLSearchParams({
    material_id: String(materialId),
    qty: String(qty),
    warehouse_id: String(warehouseId),
  });
  return request(`/stock/fefo-suggest?${params.toString()}`);
}

export async function getProductionOrders(): Promise<any[]> {
  return request("/production/orders");
}

export async function createProductionOrder(data: Record<string, unknown>) {
  return request("/production/orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function startProductionOrder(orderId: number, materials: { batch_id: number; quantity: number }[]) {
  return request(`/production/orders/${orderId}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ materials }),
  });
}

export async function addOperation(orderId: number, data: Record<string, unknown>) {
  return request(`/production/orders/${orderId}/operations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function completeProductionOrder(orderId: number, actual_qty: number) {
  return request(`/production/orders/${orderId}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actual_qty }),
  });
}

export async function getLabTests(): Promise<any[]> {
  return request("/lab/tests");
}

export async function createLabTest(data: Record<string, unknown>) {
  return request("/lab/tests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export type GcImportResult = {
  imported: number;
  duplicate: boolean;
  sha256: string;
  row_count: number;
};

export type SpcPoint = {
  value: number;
  tested_at: string;
  batch_no: string;
  out_of_control: boolean;
};

export type SpcResult = {
  analyte: "C14" | "tCA";
  status: "ok" | "insufficient_data";
  mean: number | null;
  std_dev: number | null;
  ucl: number | null;
  lcl: number | null;
  points: SpcPoint[];
};

export async function importGcCsv(file: File): Promise<GcImportResult> {
  const body = new FormData();
  body.append("file", file);
  return request("/lab/gc-import", { method: "POST", body });
}

export async function getLabSpc(analyte: "C14" | "tCA", limit = 100): Promise<SpcResult> {
  const params = new URLSearchParams({ analyte, limit: String(limit) });
  return request(`/lab/spc?${params.toString()}`);
}

export async function traceBatch(batchNo: string): Promise<any> {
  return request(`/reports/trace/${encodeURIComponent(batchNo)}`);
}

export type BatchTraceSuggest = {
  batch_no: string;
  material_code: string;
  material_name: string;
  material_type: string;
  quantity: number;
  trace_hint: string;
};

export type BatchPassport = {
  batch_no: string;
  material_code: string;
  material_name: string;
  material_type: string;
  supplier_name: string | null;
  received_at: string;
  mfg_date: string | null;
  expiry_date: string | null;
  quantity: number;
  quality_status: string;
  ccp_status: string;
  ccp_results: {
    test_type: string;
    status: string;
    c14: number | null;
    t_ca_percent: number | null;
    tested_at: string;
  }[];
  source_order: {
    order_no: string;
    status: string;
    planned_qty: number;
    actual_qty: number | null;
  } | null;
  downstream_orders: {
    order_no: string;
    status: string;
    output_batch_no: string | null;
  }[];
  certificate_url: string | null;
};

export type RecallAffectedBatch = {
  batch_id: number;
  batch_no: string;
  material: string;
  order_no: string | null;
  quantity: number;
  quality_status: string;
  depth: number;
};

export type RecallSimulation = {
  id: number;
  root_batch_no: string;
  reason: string;
  initiated_by_id: number;
  initiated_at: string;
  duration_ms: number;
  affected_batches: RecallAffectedBatch[];
  affected_orders: {
    order_id: number;
    order_no: string;
    input_batch_no: string;
    output_batch_no: string;
    quantity: number;
    depth: number;
  }[];
};

export async function getTraceSuggestions(q = ""): Promise<BatchTraceSuggest[]> {
  const params = new URLSearchParams({ limit: "25" });
  if (q.trim()) params.set("q", q.trim());
  return request(`/reports/trace-suggestions?${params.toString()}`);
}

export async function getBatchPassport(batchNo: string): Promise<BatchPassport> {
  return request(`/reports/batch-passport/${encodeURIComponent(batchNo)}`);
}

export async function getBatchQr(batchNo: string): Promise<Blob> {
  const res = await fetch(`${API}/reports/batch-qr/${encodeURIComponent(batchNo)}`, {
    headers: authHeader(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.blob();
}

export async function createRecallSimulation(
  batchNo: string,
  reason: string,
): Promise<RecallSimulation> {
  return request("/reports/recall-simulations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ batch_no: batchNo, reason }),
  });
}

export async function downloadRecallCsv(simulationId: number) {
  return downloadAuthenticated(
    `/reports/recall-simulations/${simulationId}/csv`,
    `mo-phong-thu-hoi-${simulationId}.csv`,
  );
}

export async function getPurchaseRequests(): Promise<any[]> {
  return request("/stock/purchase-requests");
}

export async function createPurchaseRequest(data: Record<string, unknown>) {
  return request("/stock/purchase-requests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export type AuditLogPage = {
  items: any[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export async function getAuditLogs(query = ""): Promise<AuditLogPage> {
  return request(`/reports/audit${query}`);
}

export async function getHaccpMonitor(days = 14): Promise<any> {
  return request(`/reports/haccp-monitor?days=${days}`);
}

export async function approveProductionOrder(orderId: number) {
  return request(`/production/orders/${orderId}/approve`, { method: "POST" });
}

export async function cancelProductionOrder(orderId: number) {
  return request(`/production/orders/${orderId}/cancel`, { method: "POST" });
}

export async function getProductionReservations(orderId: number): Promise<MaterialReservation[]> {
  return request(`/production/orders/${orderId}/reservations`);
}

export async function getMaterialBalance(orderId: number): Promise<any> {
  return request(`/production/orders/${orderId}/balance`);
}

/** Tải file PDF/CSV — luôn gửi JWT, không dùng thẻ <a href> trực tiếp */
function dateRangeQuery(params?: { from?: string; to?: string }): string {
  let from = params?.from;
  let to = params?.to;
  if (from && to && from > to) {
    [from, to] = [to, from];
  }
  const query = new URLSearchParams();
  if (from) query.set("date_from", from);
  if (to) query.set("date_to", to);
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

export async function fetchAuthenticatedFile(path: string): Promise<Blob> {
  const token = readStoredToken();
  if (!token) {
    emitSessionExpired();
    throw new Error("Chưa đăng nhập. Vui lòng đăng nhập lại.");
  }

  const res = await fetch(`${API}${path}`, { headers: authHeader() });
  if (!res.ok) {
    if (res.status === 401) {
      clearStoredToken();
      emitSessionExpired();
    }
    throw new Error(await parseError(res));
  }

  return res.blob();
}

export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function downloadAuthenticated(path: string, filename: string) {
  const blob = await fetchAuthenticatedFile(path);
  saveBlob(blob, filename);
}

export async function downloadHaccpPdf() {
  return downloadAuthenticated("/reports/haccp-monitor/export?days=14", "bien-ban-giam-sat.pdf");
}

export async function downloadInventoryCsv(view: "material" | "batch" = "material") {
  return downloadAuthenticated(`/reports/inventory/export?view=${view}`, `ton-kho.csv`);
}

export async function downloadInventoryPdf(view: "material" | "batch" = "material") {
  return downloadAuthenticated(`/reports/inventory/export/pdf?view=${view}`, `ton-kho.pdf`);
}

export async function downloadInventoryPeriodCsv(params?: { from?: string; to?: string }) {
  return downloadAuthenticated(`/reports/inventory/period/export${dateRangeQuery(params)}`, "ton-kho-ky.csv");
}

export async function downloadInventoryPeriodPdf(params?: { from?: string; to?: string }) {
  return downloadAuthenticated(`/reports/inventory/period/export/pdf${dateRangeQuery(params)}`, "ton-kho-ky.pdf");
}

export type IssueLedgerItem = {
  id: number;
  reference_no: string;
  created_at: string;
  created_at_vn: string;
  batch_id: number;
  batch_no: string;
  material_code: string;
  material_name: string;
  quantity: number;
  issue_kind: string;
  order_no: string | null;
  created_by_name: string | null;
  notes: string | null;
};

export async function getIssueLedger(params?: { from?: string; to?: string }): Promise<IssueLedgerItem[]> {
  return request(`/reports/issues${dateRangeQuery(params)}`);
}

export async function downloadIssueLedgerCsv(params?: { from?: string; to?: string }) {
  return downloadAuthenticated(`/reports/issues/export${dateRangeQuery(params)}`, "so-xuat-kho.csv");
}

export async function downloadIssueLedgerPdf(params?: { from?: string; to?: string }) {
  return downloadAuthenticated(`/reports/issues/export/pdf${dateRangeQuery(params)}`, "so-xuat-kho.pdf");
}

export async function downloadIssueVoucherPdf(movementId: number, referenceNo: string) {
  return downloadAuthenticated(`/reports/issues/${movementId}/pdf`, `${referenceNo}.pdf`);
}

export async function downloadReceiptPdf(batchId: number, batchNo: string) {
  return downloadAuthenticated(`/reports/receipt/${batchId}/pdf`, `phieu-nhap-${batchNo}.pdf`);
}

export async function downloadOperationPdf(recordId: number) {
  return downloadAuthenticated(`/reports/operation/${recordId}/pdf`, `thong-so-van-hanh-${recordId}.pdf`);
}

export async function downloadBalancePdf(orderId: number, orderNo: string) {
  return downloadAuthenticated(`/reports/balance/${orderId}/pdf`, `can-bang-nguyen-lieu-${orderNo}.pdf`);
}

export async function downloadMixingPdf(orderId: number, orderNo: string) {
  return downloadAuthenticated(`/reports/mixing/${orderId}/pdf`, `phieu-pha-tron-${orderNo}.pdf`);
}

export async function downloadLabPdf(testId: number) {
  return downloadAuthenticated(`/reports/lab/${testId}/pdf`, `ket-qua-kiem-nghiem-${testId}.pdf`);
}

export async function getOrderOperations(orderId: number): Promise<any[]> {
  return request(`/production/orders/${orderId}/operations`);
}
