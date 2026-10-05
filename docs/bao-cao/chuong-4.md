# Chương 4 — Phân tích vấn đề

---

## 4.1. Phương pháp phân tích

- Ma trận vấn đề theo phòng ban (Kho / SX / Lab / ATTP)
- Ma trận **Impact × Effort** — `docs/problem-matrix.md`
- Phân tích nguyên nhân (bảng 5M rút gọn)
- Xác định yêu cầu chức năng & phi chức năng — `docs/requirements.md`

---

## 4.2. Ma trận vấn đề theo phòng ban

| Phòng | Vấn đề | Mã |
|-------|--------|-----|
| **Kho** | Tồn cập nhật thủ công | P01 |
| | Khó truy xuất lô NVL→TP | P02 |
| | Phiếu không link mẻ SX | P03 |
| **SX** | Operation record giấy | P04 |
| | Material balance tính tay | P05 |
| **Lab** | GC tách file, nhập tay | P09 |
| | Không cảnh báo CCP | P06 |
| **ATTP** | Hồ sơ thẩm tra phân tán | P07 |
| **QL NM** | Thiếu dashboard | P08 |

---

## 4.3. Phân tích nguyên nhân (5M — ví dụ P01)

| Yếu tố | Nguyên nhân |
|--------|-------------|
| **Man** | Nhiều bộ phận nhập liệu, không quy trình một nguồn |
| **Machine** | Thiếu phần mềm tích hợp; chỉ Excel |
| **Material** | Nhiều lô, batch phức tạp — Excel khó quản |
| **Method** | BM giấy + Excel song song |
| **Measurement** | Không đối soát tự động tồn vs sổ kho |

---

## 4.4. Sơ đồ as-is và luồng dữ liệu

- Quy trình: `docs/process-as-is.md`
- Data flow: `docs/data-flow.md` (mục as-is)
- **Điểm nghẽn:** ghép thủ công Lab ↔ SX ↔ Kho

---

## 4.5. Rủi ro nếu không cải tiến

| Rủi ro | Hậu quả |
|--------|---------|
| CCP fail phát hiện muộn | Lô không đạt vào SX/TP |
| Truy xuất chậm | Không đáp ứng audit FSSC/khách |
| Tồn sai | Dừng mẻ, đặt NVL gấp |
| Thẩm tra tốn thời gian | Chi phí nhân sự, non-conformance |

---

## 4.6. Yêu cầu hệ thống (tóm tắt)

### Functional (FR)

- FR-001–013: auth, kho, SX, lab, CCP, dashboard, audit, truy xuất
- Chi tiết: `docs/requirements.md`

### Non-functional (NFR)

- Tiếng Việt, JWT, audit log bất biến, backup, RBAC
- Validation phần mềm CCP (FSSC 8.7)

### User stories theo role

| Role | Story ví dụ |
|------|-------------|
| thu_kho | Nhập phiếu BM-01/GMP01, xem tồn |
| ky_thuat | Tạo mẻ, ghi T/P/Ttop |
| lab | Nhập GC, cập nhật CCP |
| ql_nm | Dashboard, export tồn |
| attp | Audit, tra CCP 14 ngày |

---

## 4.7. Ưu tiên giải pháp (Impact × Effort)

**P0 — MVP:** P01, P02, P03, P06  
**P1:** P04, P07, P08, P09  
**P2+:** PDF BM, mixing, FIFO, tích hợp GC

Biểu đồ: `docs/problem-matrix.md`

---

## 4.8. Tổng kết chương

- Vấn đề cốt lõi: **phân tán dữ liệu + thiếu tự động hóa CCP + truy xuất lô**
- Giải pháp cần modular, phù hợp quy mô 6 NS
- Chương 5 trình bày kiến trúc và prototype
