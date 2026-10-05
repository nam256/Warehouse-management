# Tóm tắt phỏng vấn — Quản lý nhà máy

> **Nguồn:** Tổng hợp synthesized từ `detai.txt`, `chuongtrinhthamtra.txt`, `tochuc.txt`.  
> **Không phải biên bản phỏng vấn trực tiếp.**

---

## Thông tin buổi phỏng vấn (mô phỏng)

| Mục | Nội dung |
|-----|----------|
| Đối tượng | Quản lý nhà máy (QL NM) |
| Thời lượng | ~45 phút |
| Mục tiêu | Điều phối SX, báo cáo, tồn kho, pain point quản trị |

---

## 1. Vai trò và trách nhiệm

- Lập kế hoạch mẻ SX t-CA (~36 tấn/năm, mẻ 32–37h)
- Phối hợp **Thủ kho** (NVL), **Kỹ thuật** (vận hành), **Lab** (chất lượng)
- Theo dõi **tồn kho tuần** và **monthly inventory** (BM-02/GMP01)
- Báo cáo ban lãnh đạo / khách hàng khi cần COA, truy xuất lô
- Tham gia **thẩm tra nội bộ HACCP** hàng năm

---

## 2. Báo cáo hiện tại

| Báo cáo | Tần suất | Nguồn dữ liệu |
|---------|----------|---------------|
| Tồn kho tuần | Hàng tuần | Excel Thủ kho + xác nhận Kỹ thuật |
| Tồn tháng (BM-02/GMP01) | Hàng tháng | Tổng hợp thủ công |
| Tiến độ mẻ SX | Ad-hoc | Gọi điện / nhắn tin Kỹ thuật |
| CCP pass/fail | Khi có sự cố | Lab + ATTP |

**Không có dashboard tập trung** — QL NM mất thời gian hợp nhất.

---

## 3. Pain point

1. **Thiếu visibility realtime:** không biết mẻ đang ở công đoạn nào mà không xuống xưởng
2. **Rủi ro thiếu NVL:** đặt mẻ trước khi C14 pass hoặc tồn chưa cập nhật
3. **Truy xuất lô chậm:** khách hỏi lô TP → phải nhờ Kho + KT + Lab lục hồ sơ
4. **Quy mô ~6 người:** không đủ nhân sự để nhập liệu kép — cần hệ thống **đơn giản, một nguồn sự thật**

---

## 4. Kỳ vọng hệ thống

- **Dashboard:** tồn NVL/BTP/TP, mẻ đang chạy, CCP pending/fail, cảnh báo tồn thấp
- **Truy xuất 2 chiều** lô TP ↔ mẻ ↔ lô NVL (FSSC, TT-TVTH)
- Export báo cáo tuần/tháng (CSV/PDF)
- (Tùy chọn) Workflow **duyệt lệnh SX** trước khi chạy mẻ — chưa bắt buộc MVP
- Triển khai **từng bước**, không gián đoạn sản xuất

---

## 5. Tiêu chí chấp nhận demo (UAT)

- Xem dashboard phản ánh đúng sau 1 kịch bản E2E (nhập 1 lô → 1 mẻ → 1 lô TP)
- Tra cứu truy xuất < 2 phút thay vì lục hồ sơ giấy
- Báo cáo tồn export được từ hệ thống

---

## 6. Trích dẫn (paraphrase synthesized)

> “Nhà mình nhỏ nhưng khách FSSC/Kosher hỏi truy xuất rất gắt. Em cần một chỗ mở ra là thấy lô quế nào vào phuy nào — không cần ERP lớn, cần **đúng việc**.”

---

*QL NM là stakeholder ký xác nhận phạm vi demo — xem `docs/pham-vi-xac-nhan.md`.*
