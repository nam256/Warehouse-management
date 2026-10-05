# Tóm tắt phỏng vấn — Phòng Lab

> **Nguồn:** Tổng hợp synthesized từ `chuongtrinhthamtra.txt`, `detai.txt` (CCP1/CCP2, GC).  
> **Không phải biên bản phỏng vấn trực tiếp.**

---

## Thông tin buổi phỏng vấn (mô phỏng)

| Mục | Nội dung |
|-----|----------|
| Đối tượng | Phòng Lab / phối hợp lab phân tích bên ngoài |
| Thời lượng | ~40 phút |
| Mục tiêu | GC data, mẫu CCP, luồng kết quả về kho/SX |

---

## 1. Nhiệm vụ kiểm nghiệm

| Loại mẫu | Chỉ tiêu | Biểu mẫu / hồ sơ |
|----------|----------|------------------|
| NVL đầu vào | **C14** (13.02–14.39 dpm/gC) — CCP1 | BM-01/GMP01, kết quả lab ngoài |
| Sau chưng cất | **% t-CA** (> 99%) — CCP2 | BM-02/GMP05 (GC data) |
| Phối trộn | Độ đồng nhất (nếu có) | BM-01/GMP05 |

**Tần suất:** mỗi lô NVL (C14); mỗi mẻ/lô SX theo kế hoạch lấy mẫu (CCP2).

---

## 2. Quy trình hiện tại (as-is)

1. Thủ kho / Kỹ thuật gửi mẫu (giấy phiếu giao mẫu hoặc nhắn tin)
2. Lab nội bộ hoặc **lab bên ngoài** phân tích
3. Kết quả về dạng **file GC / báo cáo PDF** — lưu folder PC Lab
4. Nhập tay số vào Excel hoặc chép vào BM-02/GMP05 giấy
5. Báo pass/fail cho Thủ kho / Kỹ thuật (email, điện thoại)

**Máy GC:** xuất file dữ liệu; **chưa tích hợp API** vào hệ thống quản lý.

---

## 3. Pain point

1. **Độ trễ** giữa lấy mẫu và có kết quả — kho không thấy trạng thái “pending Lab” tập trung
2. GC data **không link** batch NVL/mẻ SX trong một DB
3. Thẩm tra CCP 14 ngày/lần: ATTP phải mở nhiều file rời
4. Không có **rule tự động** đánh dấu fail C14 hoặc % t-CA thấp

---

## 4. Kỳ vọng hệ thống

- Form nhập **GC data** (BM-02/GMP05): C14, % t-CA, ngày phân tích, số báo cáo lab
- Gắn kết quả vào **lô NVL** (CCP1) hoặc **mẻ SX** (CCP2)
- Trạng thái: pending / pass / fail — **chặn xuất kho / hoàn thành mẻ** khi fail
- Lưu log phục vụ màn hình tra cứu HACCP
- Giai đoạn sau: import file GC (CSV) — ngoài MVP

---

## 5. Phân quyền

- Role `lab`: nhập/sửa kết quả chưa duyệt; xem lịch sử mẫu
- `attp`: xem toàn bộ, không xóa audit
- `thu_kho`, `ky_thuat`: xem kết quả liên quan lô/mẻ của mình

---

## 6. Trích dẫn (paraphrase synthesized)

> “C14 mỗi lô phải chờ lab ngoài 3–5 ngày. Em ghi vào Excel riêng; Thủ kho gọi hỏi ‘lô X pass chưa’ — nếu có một màn hình chung thì đỡ phải nhắn tin.”

---

*Lab Oxeyns quy mô nhỏ; nhiều chỉ tiêu gửi lab thuê ngoài — hệ thống cần trường ‘lab ngoài / số COA’.*
