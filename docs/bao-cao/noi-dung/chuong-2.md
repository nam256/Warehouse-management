# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

Chương này trình bày cơ sở lý thuyết về quản lý thông tin trong sản xuất SME, an toàn thực phẩm (HACCP/FSSC) và nền tảng kỹ thuật đã dùng để xây dựng prototype **Oxeyns Kho & SX** tại Chi nhánh Long An.

---

## 2.1. Lý thuyết

### 2.1.1. Hệ thống thông tin quản lý (MIS) trong sản xuất quy mô SME

**Hệ thống thông tin quản lý (MIS)** là tập hợp con người, quy trình và công nghệ thu thập, xử lý, lưu trữ và phân phối thông tin phục vụ ra quyết định. Trong sản xuất, MIS thường được cụ thể hóa qua ERP (hoạch định nguồn lực), MES (thực thi tại xưởng) hoặc LIMS (phòng Lab).

Với doanh nghiệp quy mô nhỏ như Oxeyns (~6 nhân sự), triển khai ERP/MES đầy đủ thường **không khả thi** về chi phí, thời gian đào tạo và tùy biến. Hướng tiếp cận phù hợp là **ứng dụng web chuyên biệt**, module hóa theo nghiệp vụ thực tế:

| Nguyên tắc | Áp dụng tại Oxeyns |
|------------|-------------------|
| Single source of truth | Một CSDL lô hàng (`stock_batches`) và mẻ SX (`production_orders`) |
| Phân quyền theo vai trò | 6 role: admin, thu_kho, ky_thuat, lab, ql_nm, attp |
| Triển khai từng giai đoạn | MVP demo SQLite trước; go-live sau |
| Audit trail | Bảng `audit_logs` — phục vụ thẩm tra ATTP |

Prototype đề tài không thay thế ERP tập đoàn mà **minh chứng** hướng số hóa kho – SX – Lab – ATTP cho nhà máy Long An.

### 2.1.2. An toàn thực phẩm, HACCP Codex và FSSC 22000

**HACCP** (Hazard Analysis and Critical Control Points) là phương pháp hệ thống xác định, đánh giá và kiểm soát mối nguy quan trọng. Hai khái niệm then chốt:

- **Giới hạn tới hạn (critical limit)** — ranh giới đo lường được phân biệt chấp nhận / không chấp nhận.
- **Điểm kiểm soát tới hạn (CCP)** — bước có thể áp dụng kiểm soát và giám sát để ngăn, loại bỏ hoặc giảm mối nguy.

**FSSC 22000** tích hợp ISO 22000, chương trình tiên quyết (GMP) và yêu cầu bổ sung. Tại Oxeyns, khung FSSC + Kosher đòi hỏi lưu hồ sơ đầy đủ và thẩm tra định kỳ.

**Hai CCP tại Oxeyns Long An:**

| CCP | Vị trí trong quy trình | Giới hạn tới hạn | Hồ sơ liên quan |
|-----|------------------------|------------------|-----------------|
| **CCP1** | Tiếp nhận NVL (dầu quế) | C14: **13,02 – 14,39** dpm/gC | BM-01/GMP01, kết quả Lab |
| **CCP2** | Chưng cất chân không | Ttop: **107 – 110** °C; **% t-CA > 99%** | BM-01/GMP03, BM-02/GMP05 |

**Giám sát và hành động khắc phục:** Thẩm tra CCP **14 ngày/lần**; khi vượt giới hạn — cô lập lô, báo cáo, điều chỉnh vận hành hoặc trả hàng NCC (CCP1). Prototype mã hóa giới hạn trong `app/services/ccp.py` và lưu `corrective_actions` khi cần.

*[Hình 2.1 — Chuỗi NVL → mẻ SX → lô TP với hai điểm CCP]*

### 2.1.3. Truy xuất lô hàng (batch) và liên kết dữ liệu

**Truy xuất lô (batch traceability)** là khả năng theo dõi lịch sử và vị trí của một lô qua các giai đoạn:

- **Truy xuất xuôi (forward):** từ lô NVL → biết dùng cho mẻ SX nào → lô TP nào.
- **Truy xuất ngược (backward):** từ lô TP → biết mẻ SX và lô NVL nguồn.

Trong prototype, mỗi lô có `batch_no` (quy tắc: `NVL-YYYYMMDD-###`, `TP-...`); bảng `production_material_usages` ghi phân bổ NVL theo mẻ; API `GET /api/v1/reports/trace` trả cây liên kết hai chiều. Gợi ý mã lô qua `trace-suggestions` hỗ trợ người dùng nhập nhanh trên màn Truy xuất.

### 2.1.4. Yêu cầu phần mềm giám sát CCP (FSSC mục 8.7 — validation)

FSSC 22000 mục **8.7** quy định: phần mềm tham gia giám sát ATTP (ghi CCP, cảnh báo vượt ngưỡng, chặn phát hành lô) phải được **xác nhận (validation)** trước khi đưa vào sử dụng, gồm:

| Giai đoạn | Nội dung | Áp dụng prototype |
|-----------|----------|-------------------|
| **IQ** (Installation Qualification) | Cài đặt đúng phiên bản, môi trường | Python, Node, dependency `requirements.txt` |
| **OQ** (Operational Qualification) | Chức năng hoạt động đúng spec | pytest rule CCP, chặn complete khi fail |
| **PQ** (Performance Qualification) | Đáp ứng nghiệp vụ thực tế | UAT 10 kịch bản, luồng E2E |

Đề tài soạn bản draft `docs/software-validation.md` — minh họa quy trình cho báo cáo TTTN; **chưa thay thế** hồ sơ validation chính thức có chữ ký ATTP trước go-live.

---

## 2.2. Kỹ thuật

### 2.2.1. Kiến trúc tương tác frontend – backend (REST API, JWT)

Prototype áp dụng kiến trúc **ba tầng** tách presentation – application – data:

```text
┌─────────────────────────────────────────┐
│  Tầng trình diễn                        │
│  React 19 + TypeScript + Vite (:5173)   │
│  fetch → /api/v1/* (proxy Vite)         │
└──────────────────┬──────────────────────┘
                   │ JSON / REST
┌──────────────────▼──────────────────────┐
│  Tầng ứng dụng                          │
│  FastAPI + uvicorn (:8000)              │
│  Routers: auth, stock, production, lab, │
│  reports, quality, materials            │
└──────────────────┬──────────────────────┘
                   │ SQLAlchemy 2 ORM
┌──────────────────▼──────────────────────┐
│  Tầng dữ liệu                             │
│  SQLite — backend/oxeyns.db (đang dùng)   │
└───────────────────────────────────────────┘
```

> **Ghi chú CSDL trong phạm vi đề tài:** Toàn bộ prototype TTTN (dev, UAT, pytest, demo bảo vệ) chạy trên **SQLite** — file `backend/oxeyns.db`, cấu hình mặc định `DATABASE_URL=sqlite:///./oxeyns.db` trong `config.py`. Repo có file `docker-compose.yml` (image `postgres:16-alpine`) và thư viện `psycopg2-binary` trong `requirements.txt` nhưng **chưa triển khai, chưa kết nối, chưa kiểm thử** với PostgreSQL trong kỳ thực tập. Đó chỉ là **hướng mở rộng** khi go-live: đổi `DATABASE_URL` sang PostgreSQL (xem `docs/deploy.md`).

**Luồng xác thực:**

1. User gửi `POST /api/v1/auth/login` (form username/password, chuẩn OAuth2).
2. Server xác minh bcrypt, trả JWT (HS256, hết hạn **480 phút**).
3. Frontend lưu token vào `localStorage` (`auth.ts`).
4. Mỗi request kèm `Authorization: Bearer <token>`.
5. Dependency `get_current_user` giải mã JWT; `require_roles(...)` kiểm tra RBAC → `401` / `403` nếu không hợp lệ.

**Bảng 2.1 — Phân quyền RBAC (tóm tắt)**

| Vai trò | Quyền chính trên prototype |
|---------|----------------------------|
| `admin` | Toàn quyền |
| `thu_kho` | Nhập/xuất kho, tồn, YCMH |
| `ky_thuat` | Sản xuất, operation record |
| `lab` | Kiểm nghiệm, nhập C14/% t-CA |
| `ql_nm` | Duyệt mẻ, dashboard, báo cáo |
| `attp` | Giám sát CCP, truy xuất, audit, export |

### 2.2.2. Công nghệ và công cụ đã sử dụng

**Bảng 2.2 — Stack kỹ thuật prototype**

| Tầng | Công nghệ | Phiên bản / ghi chú |
|------|-----------|---------------------|
| Frontend | React, TypeScript, Vite | React 19; Vite 6; port 5173 |
| Điều hướng | react-router-dom | v7 — 12 trang (Login + 11 menu) |
| Backend | Python, FastAPI, uvicorn | API prefix `/api/v1` |
| Validation dữ liệu | Pydantic v2, pydantic-settings | Schema request/response |
| ORM | SQLAlchemy 2 | 14 bảng trong `models.py` |
| CSDL (đã dùng) | **SQLite** | `sqlite:///./oxeyns.db` — dev, UAT, demo |
| CSDL (chưa dùng) | PostgreSQL 16 | Chỉ có `docker-compose.yml` mẫu; ngoài phạm vi TTTN |
| Auth | python-jose (JWT), bcrypt | `core/security.py` |
| Rule CCP | Python thuần | `services/ccp.py` |
| Xuất PDF | ReportLab + DejaVu Sans | `pdf_export.py`, `pdf_fonts.py` |
| Xuất CSV | UTF-8 BOM | `csv_export.py` |
| Kiểm thử | pytest, httpx TestClient | 17 test (CCP, roles, E2E) |

**Logic rule CCP trong code** (`ccp.py`):

- `evaluate_ccp1(c14)` → `pending` nếu chưa có giá trị; `pass` nếu 13,02 ≤ C14 ≤ 14,39; ngược lại `fail`.
- `evaluate_ccp2(t_top, t_ca_percent)` → `fail` nếu Ttop ngoài 107–110°C hoặc % t-CA ≤ 99%; `pass` khi đủ cả hai; `pending` nếu thiếu dữ liệu.

**Chạy môi trường demo:**

```powershell
cd backend
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

cd frontend
npm run dev
```

Vite proxy `/api` → `http://127.0.0.1:8000` (`vite.config.ts`). Khởi động backend tự `create_all` bảng, chạy migration SQLite và `seed_database` (user demo, NVL mẫu).

### 2.2.3. Xây dựng và đề xuất mô hình ứng dụng

Sau khi khảo sát quy trình t-CA tại Oxeyns Long An (Chương 1) và rà soát ma trận vấn đề P01–P12, em đề xuất mô hình ứng dụng **web module hóa** thay vì triển khai ERP/MES đầy đủ. Mô hình này bám sát luồng vật tư thực tế **Kho → Sản xuất → Lab → ATTP**, dùng **một cơ sở dữ liệu trung tâm** làm *single source of truth* và phân quyền theo sáu vai trò nghiệp vụ.

#### 2.2.3.1. Nguyên tắc thiết kế mô hình

| Nguyên tắc | Nội dung đề xuất | Lý do tại Oxeyns |
|------------|------------------|------------------|
| **Modular theo nghiệp vụ** | Tách 4 khối chức năng + Auth + Dashboard | ~6 nhân sự, mỗi bộ phận một nhóm màn hình riêng |
| **Kiến trúc 3 tầng** | React (presentation) — FastAPI (application) — SQLite (data) | Tách giao diện và logic; dễ mở rộng API |
| **REST + JSON** | Mọi thao tác qua `/api/v1/*` | Chuẩn hóa tích hợp; frontend/backend phát triển song song |
| **RBAC** | Kiểm tra quyền ở API (`require_roles`) và UI (`roles.ts`) | Phân tách Thủ kho, KT, Lab, QL NM, ATTP |
| **Rule CCP tập trung** | `services/ccp.py` — một nơi đánh giá CCP1/CCP2 | Tránh mỗi màn hình tự tính giới hạn khác nhau |
| **Audit append-only** | `audit_logs` ghi mọi thao tác quan trọng | Phục vụ thẩm tra FSSC, không cho sửa qua UI |
| **Triển khai từng giai đoạn** | MVP SQLite trước; PostgreSQL khi go-live | Phù hợp phạm vi TTTN, chi phí thấp |

#### 2.2.3.2. Mô hình tổng thể đề xuất

Ứng dụng **Oxeyns Kho & SX** được tổ chức theo mô hình **client–server** với frontend SPA (Single Page Application) và backend API độc lập:

```text
                    ┌─────────────────────────────────────┐
                    │     NGƯỜI DÙNG (6 vai trò)          │
                    │  Thủ kho │ KT │ Lab │ QL NM │ ATTP  │
                    └──────────────────┬──────────────────┘
                                       │ HTTPS (production)
                    ┌──────────────────▼──────────────────┐
                    │  TẦNG TRÌNH DIỄN (Frontend)         │
                    │  React 19 + TypeScript + Vite       │
                    │  12 trang: Login + 11 menu sidebar  │
                    │  api.ts → fetch + JWT Bearer        │
                    └──────────────────┬──────────────────┘
                                       │ REST JSON /api/v1
                    ┌──────────────────▼──────────────────┐
                    │  TẦNG ỨNG DỤNG (Backend)            │
                    │  FastAPI + uvicorn                  │
                    │  Routers │ Schemas (Pydantic)       │
                    │  Services: ccp, audit, pdf, csv     │
                    └──────────────────┬──────────────────┘
                                       │ SQLAlchemy ORM
                    ┌──────────────────▼──────────────────┐
                    │  TẦNG DỮ LIỆU                       │
                    │  SQLite — oxeyns.db (14 bảng)       │
                    └─────────────────────────────────────┘
```

*[Hình 2.2 — Mô hình kiến trúc 3 tầng prototype Oxeyns Kho & SX]*

**Đóng gói mã nguồn** theo mô hình trên:

| Thành phần | Thư mục | Trách nhiệm |
|------------|---------|-------------|
| Giao diện | `frontend/src/pages/` | Mỗi menu một trang React (`StockIn.tsx`, `Production.tsx`, …) |
| Gọi API | `frontend/src/api.ts`, `auth.ts` | Đăng nhập, gắn token, xử lý hết hạn phiên |
| Phân quyền UI | `frontend/src/roles.ts` | Ẩn/hiện nút ghi theo role |
| API endpoint | `backend/app/routers/` | `auth`, `stock`, `materials`, `production`, `lab`, `reports`, `quality` |
| Nghiệp vụ dùng chung | `backend/app/services/` | Rule CCP, audit, xuất PDF/CSV |
| Dữ liệu | `backend/app/models.py` | 14 bảng ORM; quan hệ lô — mẻ — kiểm nghiệm |

#### 2.2.3.3. Mô hình 4 module nghiệp vụ

Em đề xuất chia ứng dụng thành **bốn module nghiệp vụ** xoay quanh chuỗi sản xuất t-CA, cộng **Auth** (xác thực) và **Dashboard** (tổng hợp):

| Module | Router FastAPI | Thực thể dữ liệu chính | Menu UI | Vai trò sử dụng chính |
|--------|----------------|------------------------|---------|------------------------|
| **Auth** | `auth` | `users` | Đăng nhập | Tất cả |
| **Kho** | `stock`, `materials` | `materials`, `stock_batches`, `stock_movements`, `suppliers`, `purchase_requests` | Tồn kho, Nhập, Xuất, YCMH | `thu_kho`, `ql_nm` |
| **Sản xuất** | `production` | `production_orders`, `operation_records`, `production_material_usages` | Sản xuất | `ky_thuat`, `ql_nm` |
| **Lab** | `lab` | `lab_tests` | Kiểm nghiệm | `lab`, `attp` |
| **Báo cáo & ATTP** | `reports`, `quality` | `audit_logs`, `corrective_actions` | Truy xuất, Giám sát CCP, Nhật ký, Báo cáo | `attp`, `ql_nm` |
| **Tổng hợp** | `dashboard` (trong `stock`) | Tổng hợp từ nhiều bảng | Bảng tổng quan | `ql_nm`, `admin` |

**Bảng 2.3 — Phân rã module và phạm vi chức năng**

| Module | Chức năng đề xuất | Giải quyết vấn đề |
|--------|-------------------|-------------------|
| Kho | Nhập lô NVL + CCP1; xuất gắn mẻ SX; báo cáo tồn; YCMH | P01, P03 |
| Sản xuất | Tạo/duyệt mẻ; operation record; hoàn thành/hủy; chặn khi CCP fail | P04, P06 |
| Lab | Nhập C14, % t-CA, GC; cập nhật trạng thái CCP | P09, P06 |
| Báo cáo & ATTP | Truy xuất 2 chiều; giám sát CCP; audit; export PDF/CSV | P02, P07, P10 |
| Dashboard | Cảnh báo tồn thấp, mẻ đang chạy, CCP pending/fail | P08 |

#### 2.2.3.4. Luồng dữ liệu nghiệp vụ trong mô hình

Mô hình ứng dụng không chỉ liệt kê màn hình mà còn quy định **thứ tự luồng dữ liệu** giữa các module — đảm bảo truy xuất lô và giám sát CCP nhất quán:

```text
  [NCC] ──nhập kho──► stock_batches (lô NVL)
                            │
                     CCP1 ◄─┤ lab_tests (C14)
                            │
                     xuất kho ──► production_material_usages
                            │
                            ▼
                   production_orders (mẻ SX)
                            │
              operation_records (Ttop) ──► CCP2
                            │
                     lab_tests (% t-CA)
                            │
              hoàn thành mẻ ──► stock_batches (lô TP)
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
      GET /reports/trace          audit_logs + export PDF
      (truy xuất 2 chiều)         (thẩm tra ATTP)
```

**Quy tắc luồng quan trọng trong prototype:**

1. **Mỗi lô** (`stock_batches`) có `batch_no` duy nhất — nền tảng truy xuất.
2. **Xuất kho** phải liên kết `production_order_id` — đóng vấn đề phiếu xuất tách rời mẻ SX (P03).
3. **CCP1** đánh giá khi nhập NVL; **CCP2** khi có operation record và kết quả Lab.
4. **Hoàn thành mẻ** bị chặn nếu `ccp.py` trả `fail` — rule server-side, không phụ thuộc UI.
5. Mọi thao tác ghi quan trọng đều ghi `audit_logs` — phục vụ màn Nhật ký và thẩm tra.

*[Hình 2.3 — Luồng dữ liệu lô NVL → mẻ SX → lô TP và hai điểm CCP]*

#### 2.2.3.5. Ánh xạ vai trò — module — biểu mẫu

Mô hình ứng dụng gắn trực tiếp với tổ chức nhà máy (mục 1.1.2) và bộ biểu mẫu BM-xx đang dùng:

**Bảng 2.4 — Ánh xạ vai trò ↔ module**

| Vai trò | Module truy cập chính | Thao tác ghi dữ liệu |
|---------|----------------------|----------------------|
| `thu_kho` | Kho | Nhập/xuất kho, YCMH |
| `ky_thuat` | Sản xuất, Xuất kho | Operation record, xuất NVL cho mẻ |
| `lab` | Lab | Nhập C14, % t-CA, GC |
| `ql_nm` | Dashboard, Sản xuất (duyệt), Báo cáo | Duyệt mẻ, xem tổng hợp |
| `attp` | Giám sát CCP, Truy xuất, Nhật ký | Giám sát, xuất hồ sơ thẩm tra |
| `admin` | Toàn bộ | Quản trị, kiểm thử |

**Bảng 2.5 — Ánh xạ biểu mẫu BM-xx ↔ module** (theo `requirements.md`)

| Biểu mẫu | Module | Chức năng hệ thống |
|----------|--------|-------------------|
| BM-01/GMP01 | Kho | Phiếu nhập NVL + CCP1 |
| BM-02/GMP01 | Dashboard / Kho | Báo cáo tồn; export CSV |
| BM-01/GMP03 | Sản xuất | Operation record + CCP2 |
| BM-01/GMP04 | Sản xuất | Lệnh/mẻ sản xuất |
| BM-01/GMP05 | Sản xuất | Mixing report (schema có, UI chưa đầy đủ) |
| BM-02/GMP05 | Lab | Kết quả GC / kiểm nghiệm |
| Biên bản thẩm tra CCP | Báo cáo & ATTP | Giám sát CCP + xuất PDF |

#### 2.2.3.6. Lộ trình xây dựng theo mô hình đề xuất

Mô hình trên được hiện thực hóa theo ba giai đoạn — phù hợp phạm vi TTTN:

| Giai đoạn | Nội dung | Kết quả |
|-----------|----------|---------|
| **G1 — Phân tích** | Ma trận P01–P12; FR/NFR; thiết kế ERD 14 bảng | Tài liệu yêu cầu, sơ đồ CSDL |
| **G2 — MVP** | 4 module + Auth + Dashboard; rule CCP; SQLite | Prototype chạy local, 17 pytest |
| **G3 — UAT & validation draft** | 10 kịch bản UAT; `software-validation.md` (IQ/OQ/PQ) | Minh chứng FSSC 8.7 cho báo cáo |

**Hướng mở rộng sau go-live** (ngoài phạm vi đề tài): chuyển PostgreSQL, HTTPS reverse proxy, tích hợp file GC tự động (P12), hoàn thiện UI pha trộn BM-01/GMP05.

### 2.2.4. Ma trận vấn đề và yêu cầu chức năng / phi chức năng (FR/NFR)

#### Ma trận vấn đề P01–P12

**Bảng 2.6 — Ma trận Impact × Effort (tóm tắt)**

| ID | Vấn đề | Impact | Effort | Ưu tiên |
|----|--------|--------|--------|---------|
| P01 | Tồn kho thủ công, dễ lệch | 5 | 3 | **P0** |
| P02 | Khó truy xuất lô NVL→TP | 5 | 3 | **P0** |
| P03 | Phiếu xuất không link mẻ SX | 4 | 2 | **P0** |
| P04 | Operation record giấy, tách GC | 4 | 3 | P1 |
| P05 | Material balance tính tay | 3 | 2 | P1 |
| P06 | Không cảnh báo CCP tự động | 5 | 2 | **P0** |
| P07 | Hồ sơ thẩm tra CCP phân tán | 4 | 3 | P1 |
| P08 | QL NM thiếu dashboard | 4 | 2 | P1 |
| P09 | Kết quả Lab chậm hiển thị | 3 | 2 | P1 |
| P10 | Export PDF đúng mẫu BM-xx | 3 | 4 | P2 |
| P11 | Workflow duyệt nhiều cấp | 2 | 3 | P2 |
| P12 | Tích hợp file GC tự động | 3 | 5 | P3 |

**Quick wins P0** (P01, P02, P03, P06) đã triển khai trong MVP prototype.

#### Yêu cầu chức năng (FR)

**Bảng 2.7 — Functional Requirements**

| ID | Mô tả | Module | Ưu tiên |
|----|--------|--------|---------|
| FR-001 | Đăng nhập, phân quyền theo role | Auth | P0 |
| FR-002 | CRUD nguyên liệu, BTP, TP | Kho | P0 |
| FR-003 | CRUD nhà cung cấp | Kho | P1 |
| FR-004 | Phiếu nhập kho theo lô + CCP1 | Kho | P0 |
| FR-005 | Phiếu xuất kho (link mẻ SX) | Kho | P0 |
| FR-006 | Báo cáo tồn kho realtime | Kho | P0 |
| FR-007 | Lệnh/mẻ sản xuất | SX | P1 |
| FR-008 | Operation record + CCP2 | SX | P1 |
| FR-009 | Nhập kết quả Lab / GC | Lab | P2 |
| FR-010 | Cảnh báo / rule vượt giới hạn CCP | CCP | P1 |
| FR-011 | Dashboard tổng hợp | Báo cáo | P1 |
| FR-012 | Audit log thao tác | Hệ thống | P0 |
| FR-013 | Truy xuất lô 2 chiều | Kho/SX | P1 |

#### Ánh xạ vấn đề → giải pháp → FR

**Bảng 2.8 — Ma trận giải pháp**

| Vấn đề | Giải pháp trong prototype | FR |
|--------|---------------------------|-----|
| P01 | `stock_batches`, `stock_movements` | FR-006 |
| P02 | `/reports/trace`, `trace-suggestions` | FR-013 |
| P03 | `production_material_usages`, link movement | FR-005, FR-007 |
| P04 | `operation_records` trên màn Sản xuất | FR-008 |
| P06 | `ccp.py`, chặn complete khi fail | FR-010 |
| P07 | `audit_logs`, màn Giám sát CCP | FR-012 |
| P08 | Dashboard router | FR-011 |

#### Yêu cầu phi chức năng (NFR)

| ID | Mô tả | Cách đáp ứng |
|----|--------|--------------|
| NFR-001 | Giao diện tiếng Việt | Toàn bộ nhãn UI, thông báo lỗi |
| NFR-002 | JWT, mật khẩu hash | bcrypt + python-jose |
| NFR-003 | Audit log không sửa/xóa qua UI | Chỉ ghi append `audit_logs` |
| NFR-004 | Chạy local SQLite | `DATABASE_URL` mặc định trong `config.py`; PG là hướng sau |
| NFR-005 | PDF/CSV tiếng Việt | DejaVu font; CSV UTF-8 BOM |
| NFR-006 | Phân quyền menu theo role | `require_roles`, ẩn route frontend |

---

**Kết nối chương:** Cơ sở lý thuyết và stack trên là nền cho Chương 3 — thiết kế ERD 14 bảng, cài đặt prototype, kiểm thử pytest/UAT và mô tả 11 menu giao diện. Chi tiết đầy đủ FR/NFR và ma trận vấn đề: Phụ lục A và Phụ lục I.

## 2.8. Cơ sở kiểm soát cho Digital QMS

Phần mở rộng áp dụng các nguyên tắc: **Hold‑Release** tách bước kiểm nghiệm và quyết định giải phóng; **CAPA/NCR** liên kết sai lệch với hành động khắc phục, xác minh hiệu lực và chống hồ sơ trùng; **FEFO** ưu tiên hạn dùng sớm nhất trên tồn khả dụng sau reservation; **trace/recall** duyệt quan hệ lô nhiều cấp ở chế độ chỉ đọc; **SPC** đánh dấu điểm ngoài giới hạn kiểm soát. Trợ lý AI chỉ được gọi các công cụ đọc trong whitelist và phải trả fallback khi không có dữ liệu làm căn cứ.

Các nguyên tắc trên đã được hiện thực hóa trong M1–M6 và có test rule tương ứng. Tuy nhiên, test tự động không thay thế PQ/UAT với người sử dụng; trạng thái xác nhận cuối cùng vẫn provisional.
