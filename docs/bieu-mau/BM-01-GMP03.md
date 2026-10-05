# BM-01/GMP03 — Operation Record (số hóa)

**Công đoạn GMP3:** Chưng cất | **CCP2:** Nhiệt độ đỉnh cột & hàm lượng

---

## Liên kết mẻ sản xuất

| Trường | Kiểu | Bắt buộc |
|--------|------|----------|
| Mã lệnh SX | lookup | ✓ | PO-YYYYMMDD-xxx |
| Mã batch SX | text | ✓ |
| Sản phẩm | lookup | ✓ | t-CA |
| SL kế hoạch | decimal | ✓ |
| Ngày bắt đầu / kết thúc | datetime | ✓ |

---

## Bảng công đoạn (multi-row)

Mỗi dòng = một bước vận hành (có thể lặp trong mẻ dài 32–37h).

| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| STT | int | |
| Tên công đoạn | enum/text | chưng cất, chiết rót, phối trộn, đóng phuy… |
| Thời gian bắt đầu | datetime | |
| Thời gian kết thúc | datetime | |
| Nhiệt độ T (°C) | decimal | |
| Áp suất P (MPa) | decimal | Chân không âm |
| Ttop TI103 (°C) | decimal | **CCP2:** 107–110 |
| Người vận hành | user | ky_thuat |
| Ghi chú | textarea | |

---

## CCP2 trên Operation Record

| Trường | Rule |
|--------|------|
| Ttop | 107 ≤ Ttop ≤ 110 → pass |
| % t-CA | > 99 (thường từ Lab/GC) → pass |
| Trạng thái CCP2 | pending / pass / fail |

**Corrective action (fail):** ghi nhận, lấy mẫu khảo sát — form bổ sung giai đoạn 2.

---

## Thiết bị & SSOP (tham chiếu)

- Thiết bị đo theo QT-KSTB (TI103 nhiệt độ đỉnh cột)
- Không thay thế checklist SSOP — chỉ số hóa số liệu vận hành

---

## Mapping API

- `POST /production/orders` — tạo mẻ
- `POST /production/orders/{id}/steps` — ghi operation step
- `POST /quality/ccp2/{order_id}` — đồng bộ % t-CA từ Lab

---

## Trạng thái mẻ

`draft` → `running` → `done` | `cancelled`  
Không chuyển `done` nếu CCP2 fail.
