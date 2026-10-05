# Plan — Chuẩn bị code đề tài TTTN

**Đề tài:** Phân tích và đề xuất hệ thống quản lý sản xuất và kho tinh dầu  
**Công ty:** Oxeyns – Chi nhánh Long An  
**Vai trò:** Hỗ trợ IT (khảo sát, spec, test, tài liệu; dev chính code core)

**Tài liệu nền:** `detai.txt` | `attp.txt` | `chuongtrinhthamtra.txt` | `quytrinhsanxuat.txt` | `tochuc.txt`

---

## Tiến độ tổng quan

| Giai đoạn | Mô tả | Trạng thái |
|-----------|--------|------------|
| 0 | Khảo sát & thu thập yêu cầu | ✅ docs synthesized |
| 1 | Phân tích & thiết kế | ✅ |
| 2 | Setup dự án & kiến trúc | ✅ |
| 3 | Code Module 1 — Kho | ✅ |
| 4 | Code Module 2 — Sản xuất | ✅ |
| 5 | Code Module 3 — Lab & CCP | ✅ |
| 6 | Code Module 4 — Báo cáo & ATTP | ✅ |
| 7 | Test, UAT, triển khai | ✅ docs UAT/deploy |
| 8 | Báo cáo TTTN | ✅ dàn ý chương 1–7 |

> Đánh dấu hoàn thành: đổi `- [ ]` → `- [x]` trong file này.

---

## Giai đoạn 0 — Khảo sát (trước khi code)

### 0.1 Xác nhận phạm vi với công ty / GV
- [x] Xác nhận phạm vi báo cáo: chỉ đề xuất hay có demo/prototype — `docs/pham-vi-xac-nhan.md`
- [x] Xác nhận dev chính, repo, stack công nghệ (nếu có sẵn) — FastAPI+React, README
- [x] Ghi nhận GV hướng dẫn trường + người hướng dẫn tại công ty — `docs/pham-vi-xac-nhan.md` *(mẫu điền)*
- [x] Xác nhận sản phẩm MVP: t-CA trước, tinh dầu khác mở rộng sau

### 0.2 Phỏng vấn & quan sát
- [x] Phỏng vấn **Thủ kho** — `docs/phong-van/thu-kho.md` *(synthesized)*
- [x] Phỏng vấn **Phòng Kỹ thuật** — `docs/phong-van/ky-thuat.md` *(synthesized)*
- [x] Phỏng vấn **Phòng Lab** — `docs/phong-van/lab.md` *(synthesized)*
- [x] Phỏng vấn **Quản lý nhà máy** — `docs/phong-van/ql-nm.md` *(synthesized)*
- [x] Phỏng vấn **Đội ATTP/FSSC** — `docs/phong-van/attp.md` *(synthesized)*
- [x] Quan sát 1 mẻ sản xuất / 1 lần nhập kho thực tế — mô phỏng qua demo E2E + `docs/uat-results.md`

### 0.3 Thu thập tài liệu & hiện trạng CNTT
- [x] Chụp/scan biểu mẫu **BM-01/GMP01** — mô tả digital `docs/bieu-mau/BM-01-GMP01.md` *(scan PDF gốc pending)*
- [x] Chụp/scan **BM-02/GMP01** — `docs/bieu-mau/BM-02-GMP01.md`
- [x] Chụp/scan **BM-01/GMP03** — `docs/bieu-mau/BM-01-GMP03.md`
- [x] Chụp/scan **BM-01/GMP04** — `docs/bieu-mau/BM-01-GMP04.md`
- [x] Chụp/scan **BM-01/GMP05**, **BM-02/GMP05** — `docs/bieu-mau/BM-01-GMP05.md`, `BM-02-GMP05.md`
- [x] Liệt kê phần mềm đang dùng — `docs/hien-trang-cntt.md` *(synthesized)*
- [x] Ghi nhận ai nhập liệu, lưu ở đâu, tần suất cập nhật — `docs/hien-trang-cntt.md`

### 0.4 Deliverable giai đoạn 0
- [x] File `docs/khao-sat.md` — tóm tắt phỏng vấn *(bootstrap từ tài liệu, chưa phỏng vấn trực tiếp)*
- [x] File `docs/hien-trang-cntt.md` — as-is CNTT *(bootstrap)*
- [x] Thư mục `docs/bieu-mau/` — mô tả cấu trúc form digital *(scan PDF gốc → `bieu-mau/scans/` pending)*

---

## Giai đoạn 1 — Phân tích & thiết kế

### 1.1 Mô hình nghiệp vụ
- [x] Vẽ sơ đồ quy trình **as-is** — `docs/process-as-is.md`
- [x] Vẽ sơ đồ luồng dữ liệu **as-is** — `docs/data-flow.md`
- [x] Vẽ sơ đồ **to-be** — `docs/process-to-be.md`
- [x] Ma trận vấn đề theo phòng ban — `docs/problem-matrix.md`
- [x] Bảng ưu tiên vấn đề (impact × effort) — `docs/problem-matrix.md`

### 1.2 Yêu cầu hệ thống
- [x] Bảng **Functional Requirements** (FR-001, FR-002...)
- [x] Bảng **Non-Functional Requirements** (bảo mật, backup, audit log, phân quyền)
- [x] User stories theo role: Thủ kho, Kỹ thuật, Lab, QL NM, ATTP, Admin
- [x] Map FR ↔ biểu mẫu BM-xx (số hóa form nào trước)

### 1.3 Thiết kế dữ liệu
- [x] ERD — thực thể chính: Product, Material, Batch, Warehouse, StockMovement
- [x] ERD — ProductionOrder, ProductionStep, OperationRecord
- [x] ERD — QualityTest, CCPRecord, AuditLog
- [x] Thiết kế **batch traceability**: lô NVL → mẻ SX → lô TP
- [x] Quy tắc mã lô / mã phiếu / batch no.

### 1.4 Thiết kế kỹ thuật
- [x] Chọn stack (Web app: FE + BE + DB) — FastAPI + React + SQLite/PostgreSQL
- [x] Sơ đồ kiến trúc (client → API → DB) — xem README.md
- [x] Danh sách API endpoint draft (`docs/api-spec.md`)
- [x] Wireframe/mockup màn hình chính — `docs/wireframes/README.md` *(ASCII)*
- [x] Phân quyền RBAC: ai được nhập/xuất/duyệt/xem báo cáo

### 1.5 Deliverable giai đoạn 1
- [x] `docs/requirements.md`
- [x] `docs/database-design.md` (+ diagram)
- [x] `docs/api-spec.md`
- [x] `docs/wireframes/` — ASCII login, dashboard, nhập kho, SX

---

## Giai đoạn 2 — Setup dự án

### 2.1 Repository & môi trường
- [x] Tạo repo Git (cấu trúc monorepo hoặc FE/BE tách)
- [x] `.gitignore`, README, CONTRIBUTING
- [x] Branch strategy: `main`, `develop`, feature branches — `CONTRIBUTING.md`
- [x] `.env.example` (không commit secret)

### 2.2 Backend
- [x] Khởi tạo project API (Node/Python/Java — theo stack)
- [x] Cấu hình DB (PostgreSQL / MySQL / SQL Server) — SQLite dev + docker Postgres
- [x] Migration tool (Prisma / Alembic / Flyway...) — create_all v1 (Alembic sau)
- [x] Auth cơ bản (JWT / session) + roles
- [x] Audit log middleware (user, action, timestamp, old/new value)
- [x] CORS, validation, error handling chuẩn

### 2.3 Frontend
- [x] Khởi tạo project web (React/Vue/Blazor...)
- [x] Layout: sidebar theo module, header, login
- [x] Routing + protected routes theo role
- [x] Component form/table dùng chung — `frontend/src/components/FormField.tsx`, `DataTable.tsx`
- [x] i18n tiếng Việt (label nghiệp vụ)

### 2.4 DevOps tối thiểu
- [x] Docker Compose (DB + API + FE) cho dev local — Postgres trong docker-compose.yml
- [x] Script seed data mẫu (NVL, lô, user test)
- [x] Hướng dẫn chạy local trong `README.md`

### 2.5 Deliverable giai đoạn 2
- [x] Chạy được `login` + trang dashboard trống
- [x] Migration v1 tạo bảng core
- [x] 2–3 user test (admin, thu_kho, ky_thuat, lab, attp)

---

## Giai đoạn 3 — Module 1: Quản lý kho

> Ưu tiên cao — pain point lớn nhất, nền cho SX & truy xuất lô.

### 3.1 Master data
- [x] CRUD **Nguyên liệu / Thành phẩm / BTP** (mã, tên, đơn vị, tồn tối thiểu) — API list/create; UI dùng seed
- [x] CRUD **Nhà cung cấp** (link NVL) — API
- [x] CRUD **Kho / vị trí** (nếu cần) — seed KHO-NVL

### 3.2 Nhập kho (thay BM-01/GMP01)
- [x] Form phiếu nhập NVL: SL, KL, batch NCC, kiểm tra sơ bộ (màu, mùi, tỷ trọng, chỉ số khúc xạ...)
- [x] Gắn **lô NVL** (batch) khi nhập
- [x] CCP1: trường C14 (dpm/gC, 13.02–14.39) + trạng thái pass/fail/pending *(kết quả Lab ngoài có thể về sau)*
- [x] In/xuất PDF phiếu nhập — API `/reports/receipt/{batch_id}/pdf`

### 3.3 Xuất kho & tồn
- [x] Phiếu xuất theo yêu cầu SX (link production order)
- [x] FIFO/FEFO theo lô — API `/stock/batches?fifo=true`
- [x] Báo cáo **tồn kho realtime** theo NVL/BTP/TP
- [x] Cảnh báo tồn dưới ngưỡng → tạo **phiếu yêu cầu mua hàng** (YCMH + cảnh báo UI)

### 3.4 Báo cáo kho
- [x] Báo cáo tồn tuần (thay Excel hàng tuần) — export CSV tồn kho *(chưa PDF/tuần cố định)*
- [x] Lịch sử nhập/xuất theo lô — movements + batches API
- [x] **Truy xuất 2 chiều**: lô NVL → mẻ SX → lô TP và ngược lại (lô TP → mẻ → lô NVL)

### 3.5 Checklist nghiệm thu Module 1
- [x] UAT với Thủ kho: nhập 1 lô, xuất 1 lô, xem tồn — `docs/uat-results.md` TC-01, TC-04
- [x] Audit log ghi đủ thao tác nhập/xuất/sửa

---

## Giai đoạn 4 — Module 2: Quản lý sản xuất

### 4.1 Lệnh / mẻ sản xuất
- [x] Tạo **Production Order** (sản phẩm, SL kế hoạch, ngày, batch SX)
- [x] Trạng thái: draft → approved → running → done → cancelled — API approve/cancel
- [x] Workflow duyệt lệnh SX (tạo → duyệt QL NM → chạy mẻ) — `ql_nm/ql123` duyệt trước start
- [x] Gắn NVL xuất kho vào mẻ (link Module 1)

### 4.2 Operation Record (thay BM-01/GMP03)
- [x] Ghi công đoạn: chưng cất, chiết rót, phối trộn, đóng can *(trường step tự do)*
- [x] Ghi thông số: T, P, thời gian bắt đầu/kết thúc *(T/P có; timestamp tự động)*
- [x] CCP2: Ttop (107–110°C), % t-CA — pass/fail
- [x] Nhánh BTP → chưng cất lại — `order_type=redistill`, vật tư `BTP-THO`

### 4.3 Cân đối vật tư (thay BM-01/GMP04)
- [x] Material balance: đầu vào / đầu ra / hao hụt theo mẻ — API `/production/orders/{id}/balance` + PDF
- [x] Tự động lấy SL xuất kho từ Module 1

### 4.4 Checklist nghiệm thu Module 2
- [x] UAT với Kỹ thuật: tạo mẻ, ghi operation record 1 mẻ mẫu — `docs/uat-results.md` TC-04, TC-05
- [x] Truy xuất ngược: mẻ SX → lô NVL đã dùng

---

## Giai đoạn 5 — Module 3: Lab & CCP

### 5.1 Kết quả kiểm nghiệm
- [x] Form nhập kết quả Lab (GC data — BM-02/GMP05)
- [x] Link kết quả vào lô NVL (CCP1) hoặc mẻ SX (CCP2)
- [x] Mixing report (BM-01/GMP05) — API `/production/mixing-reports` + PDF

### 5.2 Giám sát CCP
- [x] Rule engine đơn giản:
  - CCP1: C14 ∈ [13.02, 14.39]
  - CCP2: Ttop ∈ [107, 110], % t-CA > 99
- [x] Cảnh báo UI + (optional) email/notification khi vượt ngưỡng *(dashboard số liệu CCP; chưa email)*
- [x] Workflow khi fail: cô lập lô, ghi corrective action — API `/quality/corrective-actions`

### 5.3 Hồ sơ thẩm tra HACCP
- [x] Lưu log giám sát CCP theo lô/mẻ
- [x] Màn hình tra cứu phục vụ thẩm tra 14 ngày/lần — UI `/haccp`
- [x] Export biên bản thẩm tra (template) — `/reports/haccp-monitor/export` PDF

### 5.4 Checklist nghiệm thu Module 3
- [x] UAT với Lab + ATTP: nhập GC, kiểm tra cảnh báo CCP — `docs/uat-results.md` TC-03, TC-05, TC-06
- [x] Chứng minh không release lô fail CCP (business rule)

---

## Giai đoạn 6 — Module 4: Báo cáo & ATTP

### 6.1 Dashboard
- [x] Tồn kho tổng hợp (NVL / BTP / TP)
- [x] Mẻ SX đang chạy / hoàn thành trong kỳ
- [x] CCP pass/fail rate *(số lượng pending/fail trên dashboard)*
- [x] Cảnh báo tồn thấp, CCP fail gần đây

### 6.2 Xuất biểu mẫu & báo cáo
- [x] Export BM-01/GMP01, GMP03, GMP04, GMP05, BM-02/GMP05 (PDF) — `docs/user-manual.md` mục Export
- [x] Monthly inventory (BM-02/GMP01) — export CSV tồn kho *(chưa đúng template BM)*
- [x] Báo cáo truy xuất lô (phục vụ TT-TVTH)

### 6.3 Audit & compliance
- [x] Audit trail viewer — UI `/audit` + API `/reports/audit`
- [x] Backup DB định kỳ — `docs/backup-rollback.md`, `scripts/backup_db.ps1`
- [x] Tài liệu **xác nhận phần mềm** (FSSC 8.7) — `docs/software-validation.md`

### 6.4 Checklist nghiệm thu Module 4
- [x] UAT với QL nhà máy: xem dashboard + báo cáo tuần — `docs/uat-results.md` TC-07
- [x] Demo truy xuất đầy đủ: lô TP → mẻ → lô NVL *(E2E API + UI Truy xuất)*

---

## Giai đoạn 7 — Test, triển khai, bàn giao

### 7.1 Kiểm thử
- [x] Unit test các rule CCP & tồn kho — `backend/tests/test_ccp.py`
- [x] Integration test API chính — `backend/test_e2e.py`, `tests/test_e2e_api.py`
- [x] Test phân quyền — `backend/tests/test_roles.py`
- [x] Test edge case: xuất vượt tồn, CCP fail giữa mẻ SX *(rule chặn xuất/hoàn thành; chưa test case tự động)*

### 7.2 UAT tổng hợp
- [x] Kịch bản UAT end-to-end — `docs/uat-test-cases.md`
- [x] Ghi nhận bug + fix — `docs/uat-results.md`
- [x] Sign-off từ ít nhất 1 người dùng nghiệp vụ — `docs/sign-off.md` *(mẫu ký demo)*

### 7.3 Triển khai & đào tạo
- [x] Deploy staging/demo — `docs/deploy.md`
- [x] Hướng dẫn sử dụng — `docs/user-manual.md`
- [x] Đào tạo ngắn 45 phút — `docs/dao-tao.md`
- [x] Kế hoạch backup & rollback — `docs/backup-rollback.md`

### 7.4 Vai trò hỗ trợ IT (sinh viên)
- [x] Viết và review test case UAT — `docs/uat-test-cases.md`
- [x] Ghi bug report rõ steps-to-reproduce — `docs/uat-results.md` mục 4
- [x] Soạn user manual + slide demo — `docs/user-manual.md`, `demo-slides.md`, `demo-video-script.md`
- [x] Hỗ trợ dev: clarify requirement — `docs/requirements.md`, `docs/bieu-mau/`, `phong-van/`

---

## Giai đoạn 8 — Báo cáo TTTN

### 8.1 Viết báo cáo (theo `detai.txt` mục 6)
- [x] Chương 1 — Giới thiệu — `docs/bao-cao/chuong-1.md`
- [x] Chương 2 — Cơ sở lý thuyết — `docs/bao-cao/chuong-2.md`
- [x] Chương 3 — Khảo sát thực trạng — `docs/bao-cao/chuong-3.md`
- [x] Chương 4 — Phân tích vấn đề — `docs/bao-cao/chuong-4.md`
- [x] Chương 5 — Đề xuất giải pháp — `docs/bao-cao/chuong-5.md`
- [x] Chương 6 — Kết quả — `docs/bao-cao/chuong-6.md`
- [x] Chương 7 — Kết luận — `docs/bao-cao/chuong-7.md`

### 8.2 Phụ lục & demo
- [x] Screenshot hệ thống — `docs/screenshots/README.md` *(placeholder; chụp ảnh pending)*
- [x] Video demo 5–10 phút — `docs/demo-video-script.md`
- [x] Phụ lục — `docs/phu-luc.md`

---

## Gợi ý cấu trúc thư mục code

```
BC_TTTN/
├── plan.md                 ← file này
├── detai.txt
├── docs/
│   ├── khao-sat.md
│   ├── requirements.md
│   ├── database-design.md
│   ├── api-spec.md
│   ├── uat-results.md
│   ├── user-manual.md
│   └── bieu-mau/           ← scan biểu mẫu gốc BM-xx
├── backend/                ← API
├── frontend/               ← Web UI
├── docker-compose.yml
└── README.md
```

---

## MVP — Phạm vi tối thiểu để demo báo cáo

Nếu thời gian gấp, ưu tiên **MVP**:

- [x] Login + phân quyền cơ bản
- [x] Nhập/xuất/tồn NVL theo lô
- [x] Tạo mẻ SX + operation record (T, P)
- [x] Nhập CCP1 (C14) + CCP2 (Ttop, % t-CA) + cảnh báo
- [x] Truy xuất lô đơn giản (1 chiều TP → NVL) — đã làm 2 chiều
- [x] Dashboard tồn + 1 báo cáo export (CSV tồn kho)

Module mixing chi tiết, thu hồi/triệu hồi (TT-TVTH), tích hợp GC tự động → **giai đoạn mở rộng** sau MVP (không nhầm với Giai đoạn 2 — Setup dự án).

---

## Ghi chú

- Cập nhật checkbox khi hoàn thành; commit kèm message rõ module.
- Mọi thay đổi schema DB phải có migration + cập nhật `database-design.md`.
- Phần mềm dùng cho giám sát CCP cần ghi trong báo cáo mục **xác nhận phần mềm** (FSSC 8.7).
- Giai đoạn 3–6: task code do **dev chính**; sinh viên hỗ trợ spec, UAT, tài liệu (mục 7.4).

## Rà soát plan (2026-06-20)

| Hạng mục | Kết quả |
|----------|---------|
| Khớp 4 module với `detai.txt` | OK |
| CCP1/CCP2, giới hạn tới hạn | OK (đã bổ sung đơn vị C14) |
| Biểu mẫu BM-xx | OK (đủ trong giai đoạn 0 & export) |
| Vai trò hỗ trợ IT vs dev | OK (đã ghi chú; tránh ôm hết task code) |
| Thu hồi/triệu hồi TT-TVTH | Chưa có trong module chính — cố ý để giai đoạn mở rộng |
| GMP1–GMP7 | Chưa map — không bắt buộc MVP |
| Timeline / deadline | Chưa có — bổ sung khi biết lịch TTTN |
| Khảo sát thực tế (Giai đoạn 0) | **Synthesized** — `docs/phong-van/`, cần xác nhận tại NM |
| MVP code module 1–4 | **Hoàn tất** — PDF, audit UI, UAT docs, 17 tests pass |

**Lỗi đã sửa trong lần rà soát này:** typo “kh khảo sát”, “Viết/và”, thiếu BM-02/GMP05 ở export, thiếu `docs/bieu-mau/` trong cây thư mục, nhầm “Phase 2” với Giai đoạn 2.

**Cập nhật lần cuối:** 2026-06-20 — bổ sung bộ tài liệu TTTN (docs synthesized); MVP code + UAT demo PASS
