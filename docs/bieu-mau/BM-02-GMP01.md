# BM-02/GMP01 — Báo cáo tồn kho tháng (số hóa)

**Mục đích:** Tổng hợp tồn cuối kỳ theo NVL, BTP, TP — thay Excel monthly inventory.

---

## Tham số báo cáo

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| Tháng/năm | month | Kỳ báo cáo |
| Kho | lookup | Tất cả / từng kho |
| Loại hàng | enum | NVL / BTP / TP / Tất cả |

---

## Chi tiết dòng (grid)

| Cột | Nguồn dữ liệu |
|-----|---------------|
| Mã hàng | Master Product/Material |
| Tên hàng | |
| Đơn vị | |
| Tồn đầu kỳ | Tính từ movements (hoặc snapshot) |
| Nhập trong kỳ | Sum phiếu nhập |
| Xuất trong kỳ | Sum phiếu xuất |
| Tồn cuối kỳ | Realtime ledger |
| Ghi chú | |

---

## Tổng hợp theo lô (optional drill-down)

| Cột | Mô tả |
|-----|--------|
| Mã lô nội bộ | |
| SL tồn | Theo batch |
| Hạn / ngày nhập | FEFO (giai đoạn 2) |
| Trạng thái CCP1 | pass/fail/pending |

---

## Header báo cáo in

- Tên công ty, địa chỉ KCN Tân Kim
- Người lập (Thủ kho), Người xác nhận (QL NM)
- Ngày in

---

## Mapping hệ thống

- `GET /reports/inventory` — tồn realtime
- `GET /reports/inventory/export` — CSV (MVP)
- Dashboard → Báo cáo → “Tồn kho tháng”

---

## Khác biệt so với báo cáo tuần

| | Tuần | Tháng (BM-02/GMP01) |
|---|------|---------------------|
| Tần suất | Hàng tuần (pain point Thủ kho) | Cuối tháng, phục vụ ATTP/kế toán |
| Độ chi tiết | Thường theo mã hàng | Có thể kèm chi tiết lô |
