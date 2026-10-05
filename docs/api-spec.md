# API Spec — Digital QMS khóa kỹ thuật

Base URL: `http://localhost:8000/api/v1`

## Quy ước phạm vi

- Các endpoint Auth/Materials/Suppliers/Stock/Dashboard/Audit hiện có là **baseline TTTN**.
- Các endpoint ở phần “Digital QMS” là hợp đồng mới của luận văn. Chúng đang được đặc tả/triển khai tạm thời theo ủy quyền của người dùng; sign-off giảng viên/Gate G1 vẫn đang chờ.
- “Khóa kỹ thuật” không đồng nghĩa với giảng viên đã phê duyệt; đây là baseline hợp đồng để tránh đổi tên field, enum hoặc trạng thái tùy ý trong lúc code.
- JSON dùng tên field/enum tiếng Anh; UI và `detail` lỗi hướng người dùng dùng tiếng Việt.
- Tất cả endpoint yêu cầu JWT trừ khi ghi rõ khác. Backend luôn thực thi RBAC; việc ẩn nút trên UI không thay thế kiểm tra quyền.

## A. API baseline TTTN

### Auth

| Method | Path | Mô tả |
|--------|------|--------|
| POST | /auth/login | `{username, password}` → JWT |
| GET | /auth/me | User hiện tại |

### Materials

| GET | /materials | Danh sách (?type=NVL) |
| POST | /materials | Tạo |
| GET | /materials/{id} | Chi tiết |
| PUT | /materials/{id} | Sửa |
| DELETE | /materials/{id} | Xóa (soft nếu có tồn) |

### Suppliers

| GET/POST | /suppliers | CRUD |

### Warehouse — Stock

| POST | /stock/receipts | Nhập kho (+ CCP1) |
| POST | /stock/issues | Xuất kho |
| GET | /stock/inventory | Tồn theo material/batch |
| GET | /stock/batches/{batch_no}/trace | Truy xuất lô |

### Dashboard

| GET | /dashboard/summary | Tồn, cảnh báo, CCP gần đây |

### Audit

| GET | /audit-logs | (?entity, ?from, ?to) — admin/attp |

---

## B. API Digital QMS

### B.1 Kiểu và enum dùng chung

```text
QualityStatus = quarantine | sampling | under_test | awaiting_release |
                released | rejected | retest
CapaStatus = open | investigating | action_pending | verification | closed
Disposition = retest | rework | reject | use_as_is
ReservationStatus = active | consumed | released
CCPStatus API value = pending | pass | fail
```

Quy ước kiểu:

- `id`, `*_id`: integer dương.
- Số lượng: decimal > 0, truyền dưới dạng JSON number.
- Ngày: ISO `YYYY-MM-DD`; thời gian: ISO 8601 có timezone.
- `batch_no`: string không rỗng; khi nằm trên path phải URL-encode.
- Response lỗi: `{"detail": "Thông báo tiếng Việt thân thiện."}`. Lỗi validation dùng 422 chuẩn FastAPI nhưng UI phải chuyển thành thông báo dễ hiểu.
- 401: chưa đăng nhập/token hết hạn; 403: không đủ quyền; 404: không tìm thấy; 409: transition hoặc dữ liệu xung đột; 400: vi phạm luật nghiệp vụ như thiếu tồn.

### B.2 M1 — Quality Hold‑Release

#### `GET /quality/batches`

Role: mọi người dùng đã đăng nhập.

Query tùy chọn:

```text
quality_status: QualityStatus
material_id: integer
batch_no: string
page: integer >= 1 (default 1)
page_size: integer 1..100 (default 20)
```

Response `200`:

```json
{
  "items": [
    {
      "id": 101,
      "batch_no": "NVL-2026-001",
      "material_id": 12,
      "ccp1_status": "pass",
      "quality_status": "awaiting_release",
      "mfg_date": "2026-07-01",
      "expiry_date": "2027-07-01",
      "on_hand_qty": 100,
      "active_reserved_qty": 20,
      "available_qty": 80,
      "updated_at": "2026-07-18T08:00:00+07:00"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

#### `POST /quality/batches/{id}/transition`

Request:

```json
{
  "to_status": "awaiting_release",
  "reason": "Kết quả CCP1 đạt",
  "note": "Đã đối chiếu phiếu kiểm nghiệm",
  "electronic_confirmation": true
}
```

Quyền và luật:

- `lab`: `quarantine → sampling → under_test`, `under_test → awaiting_release`, `retest → under_test`.
- `attp|admin`: `awaiting_release → released|rejected`; quyết định bắt buộc `reason` và `electronic_confirmation=true`.
- `under_test → awaiting_release` yêu cầu LabTest CCP1 `pass`.
- Thành phẩm CCP2 `pass` được tạo ở `awaiting_release`, không tự chuyển `released`.

Response `200`: batch theo schema của endpoint danh sách. Mỗi lần thành công phải ghi `BatchStatusHistory` và `AuditLog`. Transition sai trả 409; thiếu điều kiện nghiệp vụ trả 400; sai role trả 403.

#### `GET /quality/batches/{id}/history`

Role: mọi người dùng đã đăng nhập. Response `200`:

```json
[
  {
    "id": 9001,
    "from_status": "under_test",
    "to_status": "awaiting_release",
    "reason": "Kết quả CCP1 đạt",
    "note": "Đã đối chiếu phiếu kiểm nghiệm",
    "changed_by_id": 7,
    "changed_at": "2026-07-18T08:00:00+07:00"
  }
]
```

#### `GET /quality/batches/{id}/certificate.pdf`

Role: mọi người dùng đã đăng nhập. Chỉ có khi batch `released`; trả `application/pdf` gồm mã lô, CCP, người Lab gửi, người ATTP/admin quyết định và thời gian ký. Batch chưa release trả 409.

### B.3 M2 — CAPA/NCR

#### `GET /quality/corrective-actions`

Role: mọi người dùng đã đăng nhập.

Query: `status: CapaStatus`, `source_type: lab_test|operation_record|quality_rejection`, `overdue: boolean`, `page`, `page_size`.

Response `200`:

```json
{
  "items": [
    {
      "id": 301,
      "title": "CCP1 không đạt",
      "source_type": "lab_test",
      "source_id": 88,
      "reason": "C14 ngoài giới hạn",
      "status": "investigating",
      "root_cause": null,
      "action_taken": null,
      "due_date": "2026-07-25",
      "disposition": null,
      "justification": null,
      "verified_by_id": null,
      "closed_by_id": null,
      "closed_at": null,
      "is_overdue": false
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

CAPA được service tự tạo idempotent từ LabTest CCP1/CCP2 `fail`, OperationRecord CCP2 `fail` hoặc reject lô. Không cung cấp endpoint công khai để tạo trùng thủ công cho cùng nguồn.

#### `POST /quality/corrective-actions/{id}/transition`

Request:

```json
{
  "to_status": "action_pending",
  "root_cause": "Sai lệch nhiệt độ đầu vào",
  "action_taken": "Hiệu chuẩn và kiểm tra lại",
  "due_date": "2026-07-25",
  "disposition": "retest",
  "justification": null,
  "verification_note": null,
  "electronic_confirmation": false
}
```

Luật:

- Chỉ cho `open → investigating → action_pending → verification → closed`.
- `lab|ky_thuat` cập nhật điều tra/hành động phù hợp nguồn.
- Chỉ `attp|admin` xác minh và đóng.
- Chuyển `closed` bắt buộc `root_cause`, `action_taken`, `disposition`, verification note, `electronic_confirmation=true`; server tự ghi `verified_by_id`, `closed_by_id`, `closed_at`.
- `use_as_is` chỉ do `attp|admin` thực hiện và bắt buộc `justification`.

Response `200`: CAPA đã cập nhật. Transition sai trả 409; thiếu dữ liệu trả 400; sai role trả 403.

### B.4 M3 — FEFO và Reservation

#### `GET /stock/fefo-suggest`

Role: `thu_kho|ky_thuat|ql_nm|admin`.

Query bắt buộc: `material_id: integer`, `warehouse_id: integer`, `required_qty: decimal > 0`.

Response `200`:

```json
{
  "material_id": 12,
  "warehouse_id": 1,
  "required_qty": 120,
  "total_allocated_qty": 120,
  "is_sufficient": true,
  "allocations": [
    {
      "batch_id": 101,
      "batch_no": "NVL-2026-001",
      "expiry_date": "2026-12-31",
      "available_qty": 80,
      "allocated_qty": 80
    },
    {
      "batch_id": 102,
      "batch_no": "NVL-2026-002",
      "expiry_date": "2027-01-31",
      "available_qty": 70,
      "allocated_qty": 40
    }
  ]
}
```

Chỉ chọn lô `released`, CCP1 `pass`, chưa hết hạn, available > 0; sort hạn dùng tăng dần (null cuối), sau đó `created_at`. Endpoint chỉ gợi ý, không ghi reservation.

#### Các endpoint vòng đời lệnh tích hợp reservation

| Method | Path | Role | Tác động bắt buộc |
|---|---|---|---|
| POST | `/production/orders/{id}/approve` | `ql_nm|admin` | Không có body; tính FEFO và tạo toàn bộ reservation `active` trong cùng transaction; trả ProductionOrder hiện có. |
| POST | `/production/orders/{id}/start` | `ky_thuat|ql_nm|admin` | Không nhận phân bổ batch thủ công; dùng reservation đã duyệt, chuyển `active → consumed` và tạo OUT movement trong cùng transaction. |
| POST | `/production/orders/{id}/cancel` | `ky_thuat|ql_nm|admin` | Không có body; trước start thì release reservation; sau start thì tạo movement đảo chiều và release phần còn lại. |

Approve thiếu tồn trả `400 {"detail":"Không đủ tồn khả dụng để giữ chỗ nguyên liệu."}` và rollback toàn bộ. Transition trạng thái lệnh không hợp lệ trả 409. PostgreSQL dùng row lock để kiểm tra concurrency; SQLite chỉ dùng cho logic tuần tự.

#### `GET /production/orders/{id}/reservations`

Role: mọi người dùng đã đăng nhập.

Response `200`:

```json
[
  {
    "id": 501,
    "order_id": 41,
    "batch_id": 101,
    "batch_no": "NVL-2026-001",
    "qty": 80,
    "status": "active",
    "created_at": "2026-07-18T08:00:00+07:00",
    "consumed_at": null,
    "released_at": null
  }
]
```

Start chuyển `active → consumed` và tạo OUT movement atomic. Cancel trước start chuyển `active → released`; cancel sau start tạo movement đảo chiều, không xóa lịch sử.

### B.5 M4 — Batch Passport, QR và Recall

#### `GET /reports/batch-passport/{batch_no}`

Role: mọi người dùng đã đăng nhập. Response `200`:

```json
{
  "batch": {
    "id": 201,
    "batch_no": "TP-2026-001",
    "material_id": 21,
    "supplier_id": null,
    "received_at": null,
    "mfg_date": "2026-07-10",
    "expiry_date": "2027-07-10",
    "quality_status": "released"
  },
  "ccp_results": [
    {"ccp": "CCP2", "status": "pass", "tested_at": "2026-07-10T15:00:00+07:00"}
  ],
  "source_order_ids": [41],
  "downstream_order_ids": [],
  "certificate_url": "/api/v1/quality/batches/201/certificate.pdf"
}
```

#### `GET /reports/batch-qr/{batch_no}`

Role: mọi người dùng đã đăng nhập. Trả ảnh `image/png` (hoặc SVG nếu `Accept: image/svg+xml`) mã hóa URL passport đúng `batch_no`. QR/passport không thực hiện ghi nghiệp vụ.

#### `POST /reports/recall-simulations`

Role: `attp|ql_nm|admin`.

Request:

```json
{
  "batch_no": "NVL-2026-001",
  "reason": "Diễn tập thu hồi định kỳ",
  "initiated_at": "2026-07-18T09:00:00+07:00"
}
```

Response `200`:

```json
{
  "id": 701,
  "source_batch_no": "NVL-2026-001",
  "reason": "Diễn tập thu hồi định kỳ",
  "initiated_by_id": 9,
  "initiated_at": "2026-07-18T09:00:00+07:00",
  "duration_ms": 42,
  "affected_batches": [
    {
      "batch_id": 201,
      "batch_no": "TP-2026-001",
      "related_qty": 80,
      "quality_status": "released",
      "depth": 1
    }
  ],
  "affected_orders": [{"order_id": 41, "depth": 1}]
}
```

POST được dùng vì request có input mô phỏng và hệ thống lưu metadata/audit của lần chạy. Đây vẫn là **read-only đối với nghiệp vụ**: tuyệt đối không đổi tồn, movement, reservation, trạng thái lô, quyết định release hoặc CAPA.

#### `GET /reports/recall-simulations/{id}/csv`

Role: `attp|ql_nm|admin`. Trả `text/csv; charset=utf-8` với UTF‑8 BOM, cùng dữ liệu phân tầng của simulation; không thay đổi nghiệp vụ.

### B.6 M5 — GC Import/SPC (tùy chọn, chỉ sau Gate G4)

| Method | Path | Role | Hợp đồng tóm tắt |
|---|---|---|---|
| POST | `/lab/gc-import` | `lab|admin` | `multipart/form-data`, field `file`; CSV tối đa 1 MB/1.000 dòng, header `batch_no,analyte,value,unit,tested_at`; validate toàn bộ rồi ghi atomic, SHA‑256 chống trùng. |
| GET | `/lab/spc` | `lab|attp|ql_nm|admin` | Query `analyte=C14|tCA`, `from`, `to`; tối thiểu 10 điểm, trả mean, sigma, UCL/LCL và điểm ngoài kiểm soát. |

### B.7 M6 — Trợ lý AI (tùy chọn, chỉ sau Gate G4)

#### `POST /assistant/ask`

Role: mọi người dùng đã đăng nhập; endpoint trả 404/503 thân thiện khi `AI_ASSISTANT_ENABLED=false`.

Request:

```json
{"question": "Lô NVL-2026-001 đang ở trạng thái nào?"}
```

Response `200`:

```json
{
  "answer": "Lô NVL-2026-001 đang chờ ATTP giải phóng.",
  "sources": [{"type": "batch", "ref": "NVL-2026-001"}],
  "tools_called": ["get_batch_status"]
}
```

M6 chỉ được gọi whitelist truy vấn đọc (`get_inventory`, `get_batch_status`, `list_expiring_batches`, `list_open_capa`, `simulate_recall_preview`) dưới JWT/RBAC của chính người dùng. `simulate_recall_preview` tái sử dụng service duyệt downstream nhưng không được gọi `POST /reports/recall-simulations`, không tạo `RecallSimulation` và không export một simulation chưa được người dùng có quyền tạo. `POST /assistant/ask` dùng POST để truyền câu hỏi, nhưng không phải lệnh ghi nghiệp vụ. M6 không sinh SQL, không gọi endpoint ghi nghiệp vụ, không release/reject lô, không thay đổi reservation và không xác minh/đóng CAPA. Nếu API không có dữ liệu, phải trả “không tìm thấy” thay vì suy đoán. Chỉ `AssistantQueryLog`/AuditLog tối thiểu về câu hỏi, tool và thời gian được phép ghi theo chính sách dữ liệu; metadata này không được thay đổi trạng thái nghiệp vụ.

## C. Ràng buộc triển khai API/UI

- SQLite dùng cho dev và unit test; PostgreSQL 16 dùng cho integration, migration, row-lock/concurrency và demo.
- Cùng model/schema/service phải chạy trên cả hai CSDL; không tạo hai nhánh business logic.
- Mỗi nhóm endpoint M1–M4 chỉ được xem là hoàn tất khi UI tương ứng cũng hoàn tất bằng design system chung.
- Mọi async UI call phải bọc `try/catch`, giữ input khi lỗi và hiện `AlertBanner`/`Toast` tiếng Việt; không đưa traceback/JSON thô ra màn hình.
