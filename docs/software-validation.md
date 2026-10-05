# Xác nhận phần mềm (FSSC 22000 — Mục 8.7)

**Tài liệu:** Software Validation Record (prototype)  
**Công ty:** Công ty TNHH Oxeyns – Chi nhánh Long An  
**Phần mềm:** Oxeyns Kho & SX (Web application)  
**Phiên bản:** v0.1-mvp-demo  
**Ngày:** 20/06/2026

---

## 1. Căn cứ

Theo Sổ tay ATTP / FSSC 22000 **Chương VIII — Quản lý hệ thống quản lý an toàn thực phẩm**, mục **8.7 Xác nhận phần mềm**:

> Phần mềm và/hoặc hệ thống CNTT được sử dụng trong khu vực giám sát ATTP phải được **xác nhận** trước khi đưa vào sử dụng.

Tài liệu này mô tả phạm vi xác nhận cho **prototype demo** phục vụ đề tài TTTN — **chưa thay thế** hồ sơ validation production đầy đủ của công ty.

---

## 2. Mô tả phần mềm

| Mục | Nội dung |
|-----|----------|
| Tên | Oxeyns Kho & SX |
| Loại | Web app (Browser) |
| Chức năng ATTP | Ghi nhận CCP1/CCP2, chặn release lô fail, audit trail |
| Module không ATTP | YCMH, dashboard thuần báo cáo |
| Stack | FastAPI, React, PostgreSQL/SQLite |
| Vị trí triển khai demo | Server nội bộ / localhost |

---

## 3. Phạm vi sử dụng (intended use)

| Trong phạm vi validation demo | Ngoài phạm vi |
|--------------------------------|---------------|
| Ghi phiếu nhập NVL + CCP1 | Điều khiển thiết bị chưng cất |
| Ghi operation record + Ttop CCP2 | Tích hợp trực tiếp PLC/SCADA |
| Nhập kết quả Lab GC | Thay thế lab LIMS đầy đủ |
| Cảnh báo & chặn xuất/hoàn thành khi CCP fail | Quyết định pháp lý thu hồi TP |
| Audit log thao tác người dùng | Kế toán tài chính |

---

## 4. Rủi ro phần mềm & biện pháp

| Rủi ro | Mức | Biện pháp |
|--------|-----|-----------|
| Nhập sai C14/% t-CA | Trung bình | Validation rule; role Lab; audit log |
| User vượt quyền | Trung bình | JWT + RBAC; test phân quyền |
| Mất dữ liệu | Cao | Backup DB — `docs/backup-rollback.md` |
| Bug chặn SX oan | Trung bình | UAT; override bằng quy trình giấy tạm nếu demo fail |
| Server không sẵn sàng | Thấp (demo) | Quy trình giấy backup as-is vẫn duy trì |

---

## 5. Kế hoạch xác nhận (IQ/OQ/PQ — rút gọn prototype)

### 5.1. IQ — Installation Qualification

| # | Kiểm tra | Kết quả |
|---|----------|---------|
| IQ-01 | Cài đặt theo `docs/deploy.md` | Pass (local/Docker) |
| IQ-02 | `.env` không commit secret | Pass |
| IQ-03 | DB tách riêng môi trường demo | Pass |

### 5.2. OQ — Operational Qualification

| # | Kiểm tra | Kết quả |
|---|----------|---------|
| OQ-01 | Rule CCP1: 13.02 ≤ C14 ≤ 14.39 | Pass (`test_ccp.py`) |
| OQ-02 | Rule CCP2: Ttop 107–110; % t-CA > 99 | Pass |
| OQ-03 | Chặn xuất lô fail CCP1 | Pass |
| OQ-04 | Chặn done mẻ fail CCP2 | Pass |
| OQ-05 | Audit log ghi create/update | Pass |
| OQ-06 | Phân quyền role | Pass (`test_roles.py`) |

### 5.3. PQ — Performance Qualification (UAT nghiệp vụ)

| # | Kiểm tra | Kết quả |
|---|----------|---------|
| PQ-01 | E2E 1 lô → 1 mẻ → truy xuất | Pass — `docs/uat-results.md` |
| PQ-02 | Thủ kho nhập phiếu BM-01/GMP01 digital | Pass (demo) |
| PQ-03 | ATTP tra audit + CCP log | Pass (demo) |

---

## 6. Thay đổi phần mềm (change control)

Mọi thay đổi ảnh hưởng CCP hoặc audit:

1. Ghi trong CHANGELOG / PR
2. Chạy lại test CCP + E2E
3. ATTP review trước deploy staging
4. Backup DB trước deploy

---

## 7. Kết luận validation (prototype)

| Mục | Đánh giá |
|-----|----------|
| Phù hợp intended use demo | **Đạt** |
| Rule CCP đúng tài liệu HACCP | **Đạt** |
| Sẵn sàng go-live production | **Chưa** — cần validation đầy đủ + sign-off ATTP |

**Khuyến nghị:** Tiếp tục dùng **prototype** cho báo cáo TTTN và training; duy trì song song biểu mẫu giấy cho đến khi công ty phê duyệt go-live.

---

## 8. Phê duyệt (mẫu)

| Vai trò | Họ tên | Ngày | Chữ ký |
|---------|--------|------|--------|
| Đội trưởng HACCP | | | |
| QL nhà máy | | | |
| IT / Dev | | | |
| Sinh viên TTTN | | 20/06/2026 | |

---

*Tham chiếu: `chuongtrinhthamtra.txt` (CCP), `docs/uat-test-cases.md`*

## 9. Bổ sung phạm vi Digital QMS (Task 10)

Phạm vi validation draft được mở rộng từ baseline sang các module: **M1 Hold‑Release**, **M2 CAPA/NCR**, **M3 FEFO/Material Reservation**, **M4 QR Batch Passport/Recall Simulator**, cùng hai mở rộng **M5 GC Import/SPC** và **M6 trợ lý AI chỉ đọc**. Các kiểm soát cần xác nhận gồm:

| Module | Kiểm soát trọng yếu | Bằng chứng hiện có | Còn thiếu |
|---|---|---|---|
| M1 | Phân tách Lab–ATTP, state gate, certificate sau release | Test quality release/certificate | UAT key user và sign-off |
| M2 | Tự sinh CAPA, chống trùng, không đóng thiếu xác minh | `tests/test_capa.py` | UAT overdue và workflow đầy đủ |
| M3 | FEFO, loại lô hết hạn/quarantine, reservation atomic, cancel restore | `tests/test_fefo.py` | PostgreSQL concurrency và UAT UI |
| M4 | Passport read-only, recall nhiều cấp, CSV | `tests/test_recall.py` cho recall | UAT passport/CSV trực tiếp |
| M5 | Import atomic/idempotent, cảnh báo SPC | `tests/test_gc_import_spc.py` | Đo thời gian import thực tế |
| M6 | Tool whitelist, tôn trọng quyền, không bịa khi thiếu dữ liệu, feature flag | `tests/test_assistant.py` | UAT với provider/môi trường được phê duyệt |

Lần xác minh ngày 18/07/2026 ghi nhận SQLite profile **46 passed, 1 skipped, 1 deselected** và frontend build thành công. Playwright chưa chạy xanh vì full stack không hoạt động tại URL test; PostgreSQL profile chưa được chạy trong Task 10. Vì vậy trạng thái validation của Digital QMS vẫn là **draft/provisional**, không phải phê duyệt production.

## 10. PQ và phê duyệt còn mở

- Thực hiện đủ 20 trường hợp trong `docs/uat-test-cases.md` với người dùng đúng vai trò.
- Điền phép đo thật trong `docs/thesis-metrics.md`; không dùng thời gian chạy pytest thay cho thời gian nghiệp vụ.
- Chạy PostgreSQL integration/concurrency và Playwright trên full stack.
- Ghi deviation/issue và regression evidence nếu có lỗi.
- Chỉ đổi kết luận sang “đạt validation” sau khi Đội HACCP, Quản lý nhà máy và các bên có thẩm quyền ký. Hiện chưa có chữ ký đó.
