# BM-02/GMP05 — GC Data / Dữ liệu sắc ký khí (số hóa)

**Module Lab** — phục vụ CCP1 (C14) và CCP2 (% t-CA)

---

## Header

| Trường | Kiểu | Bắt buộc |
|--------|------|----------|
| Số phiếu GC | text | ✓ |
| Ngày phân tích | date | ✓ |
| Loại mẫu | enum | NVL / BTP / TP / Mẻ SX |
| Mã lô / Mã mẻ liên kết | lookup | ✓ |
| Lab thực hiện | text | Nội bộ / Lab ngoài |
| Số COA / báo cáo đính kèm | file (future) | |

---

## Kết quả chỉ tiêu

### CCP1 — Nguyên liệu

| Chỉ tiêu | Đơn vị | Giới hạn |
|----------|--------|----------|
| C14 | dpm/gC | 13.02 – 14.39 |

### CCP2 — Sau chưng cất

| Chỉ tiêu | Đơn vị | Giới hạn |
|----------|--------|----------|
| % t-CA | % | > 99 |

### Chỉ tiêu khác (optional)

| Chỉ tiêu | Ghi chú |
|----------|---------|
| Hàm lượng phụ | Theo COA |
| Ghi chú phương pháp | GC-MS… |

---

## Kết luận

| Trường | Kiểu |
|--------|------|
| Trạng thái | pass / fail / pending |
| CCP áp dụng | CCP1 / CCP2 / none |
| Hành động | textarea nếu fail |
| Người nhập | lab |
| Thời gian | audit |

---

## Business rules

- Cập nhật C14 → đồng bộ trạng thái batch NVL (CCP1)
- Cập nhật % t-CA → đồng bộ mẻ SX (CCP2)
- Fail → trigger cảnh báo dashboard + chặn release

---

## Mapping API

- `POST /lab/tests` — tạo bản ghi GC
- `GET /lab/tests?batch_id=` — tra cứu theo lô

---

## Tích hợp tương lai

- Import CSV từ máy GC
- Lưu file chromatogram PDF trong object storage
