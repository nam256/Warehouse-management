# Chương 2 — Cơ sở lý thuyết

---

## 2.1. Hệ thống thông tin quản lý (MIS/ERP) trong sản xuất

### 2.1.1. Khái niệm ERP và phạm vi SME

- ERP (Enterprise Resource Planning): tích hợp kế hoạch, sản xuất, kho, chất lượng
- DN nhỏ: cần **modular**, triển khai từng bước — tránh over-engineering
- MIS: hỗ trợ ra quyết định qua báo cáo tập trung

### 2.1.2. MES và quản lý shop floor

- MES (Manufacturing Execution System): ghi nhận mẻ SX, thông số vận hành
- Operation record điện tử thay biểu mẫu giấy BM-01/GMP03
- Liên kết real-time với kho (xuất NVL theo lô)

### 2.1.3. Quản lý kho và truy xuất lô (batch traceability)

- Batch/lot: đơn vị truy xuất FSSC, TT-TVTH
- Chuỗi: **lô NVL → mẻ SX → lô TP**
- FIFO/FEFO: nguyên tắc xuất kho (giai đoạn mở rộng)

---

## 2.2. An toàn thực phẩm và HACCP

### 2.2.1. FSSC 22000

- Hệ thống quản lý ATTP dựa ISO 22000 + PRP (ISO/TS 22002-1)
- Yêu cầu tài liệu, truy xuất, kiểm soát thay đổi

### 2.2.2. HACCP Codex

- 7 nguyên tắc; phân tích mối nguy → xác định CCP
- Oxeyns: **CCP1** (C14 NVL), **CCP2** (Ttop + % t-CA chưng cất)

### 2.2.3. GMP và biểu mẫu ghi chép

- GMP1–GMP7 trên dây chuyền t-CA (`chuongtrinhthamtra.txt`)
- BM-xx/GMPxx: cầu nối giữa thực hành và bằng chứng thẩm tra

### 2.2.4. Thẩm tra CCP

- Tần suất 14 ngày/lần tại CCP
- Thẩm tra nội bộ hàng năm hoặc khi thay đổi quy trình

---

## 2.3. Yêu cầu phần mềm trong ATTP (FSSC 8.7)

- Phần mềm dùng giám sát CCP phải **validated**
- IQ/OQ/PQ; change control; audit trail
- Áp dụng cho prototype: `docs/software-validation.md`

---

## 2.4. Tích hợp dữ liệu Kho – Sản xuất – Kiểm nghiệm

- Single source of truth: một DB, nhiều module
- Luồng: nhập NVL → CCP1 → xuất → mẻ SX → CCP2 → TP
- Lab (GC) là nguồn số liệu định lượng cho CCP

---

## 2.5. Công nghệ web cho ứng dụng quản lý

### 2.5.1. Kiến trúc 3 tầng

- Presentation (React), Business (FastAPI), Data (PostgreSQL)

### 2.5.2. REST API và bảo mật

- JWT, RBAC, HTTPS (production)
- Validation server-side cho rule CCP

### 2.5.3. Audit log

- Append-only; user, timestamp, entity, old/new value

---

## 2.6. Tổng kết chương

- Lý thuyết ERP/MES/SME → cơ sở chọn 4 module Oxeyns
- HACCP/FSSC → cơ sở map CCP và BM-xx
- Web app + validation → cơ sở prototype kỹ thuật
