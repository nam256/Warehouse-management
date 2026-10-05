# Tóm tắt phỏng vấn — Thủ kho

> **Nguồn:** Tổng hợp synthesized từ `chuongtrinhthamtra.txt`, `quytrinhsanxuat.txt`, `detai.txt`, Sổ tay ATTP.  
> **Không phải biên bản phỏng vấn trực tiếp.** Cần xác nhận lại khi có buổi phỏng vấn thực tế tại nhà máy.

---

## Thông tin buổi phỏng vấn (mô phỏng)

| Mục | Nội dung |
|-----|----------|
| Đối tượng | Thủ kho — bộ phận Kho NVL |
| Thời lượng | ~45 phút |
| Mục tiêu | Hiểu quy trình nhập/xuất/tồn, biểu mẫu, pain point số hóa |

---

## 1. Nhiệm vụ hàng ngày

- Tiếp nhận tinh dầu quế và NVL khác: đối chiếu **số lượng, khối lượng**, kiểm sơ bộ **màu, mùi, tỷ trọng, chỉ số khúc xạ**
- Ghi **BM-01/GMP01** (phiếu nhập nguyên liệu) cho **mỗi lô** — gắn mã lô NCC
- Bảo quản NVL **nhiệt độ phòng**, tránh nắng, không gian khô thoáng
- Xuất kho theo yêu cầu Phòng Kỹ thuật khi chạy mẻ SX
- Lập **báo cáo tồn kho hàng tuần** (phối hợp QL NM, Kỹ thuật); cuối tháng tổng hợp **BM-02/GMP01**

---

## 2. Biểu mẫu và công cụ hiện tại

| Biểu mẫu | Tần suất | Cách lưu (giả định khảo sát) |
|----------|----------|------------------------------|
| BM-01/GMP01 | Mỗi lô nhập | Bản giấy + file Excel trên PC kho |
| BM-02/GMP01 | Hàng tháng | Excel, gửi email QL NM |
| Phiếu xuất / YCMH | Theo nhu cầu | Giấy + Excel tồn |

**Phần mềm:** Excel, Google Sheets (bản sao tồn tuần); chưa có hệ thống tích hợp SX.

---

## 3. Liên kết CCP1

- Mỗi lô NVL gửi mẫu phân tích **C14 (13.02–14.39 dpm/gC)** — lab bên ngoài
- Thủ kho **chờ kết quả** trước khi cho xuất SX (quy trình ATTP)
- Khi fail: **cô lập lô**, báo ATTP và NCC — không nhập vào luồng SX

---

## 4. Pain point (ưu tiên số hóa)

1. **Tồn kho cập nhật thủ công** — dễ lệch giữa sổ giấy và Excel
2. **Khó tra cứu lô** — “lô này đã xuất cho mẻ nào?” phải lục nhiều file
3. **Báo cáo tuần tốn thời gian** — copy-paste từ nhiều nguồn
4. **Không cảnh báo tự động** khi dưới tồn tối thiểu — hay phát hiện muộn khi SX đặt lịch

---

## 5. Kỳ vọng với hệ thống đề xuất

- Form nhập kho điện tử thay BM-01/GMP01, in/export PDF khi cần
- Tồn realtime, lịch sử nhập/xuất theo lô
- Cảnh báo tồn thấp → tạo **phiếu yêu cầu mua hàng**
- Truy xuất: chọn lô NVL → xem mẻ SX đã dùng
- Vẫn giữ quy trình kiểm tra sơ bộ khi nhập — **không bỏ bước nghiệp vụ**

---

## 6. Phân quyền mong muốn

- Thủ kho: nhập/xuất, xem tồn, tạo YCMH
- Không được sửa phiếu đã khóa/đã duyệt (nếu có workflow duyệt sau này)
- QL NM và ATTP: xem báo cáo, không nhập liệu kho hàng ngày

---

## 7. Trích dẫn đại diện (paraphrase synthesized)

> “Mỗi tuần em phải cập nhật Excel tồn, trong khi phiếu nhập vẫn viết tay. Khi Lab báo C14 chậm, em giữ lô ở kho nhưng không có chỗ nào trên máy báo ‘đang chờ Lab’ cho cả nhà máy thấy.”

---

*Tài liệu phục vụ Chương 3–4 báo cáo TTTN. Cập nhật sau phỏng vấn thực tế: ghi rõ họ tên, ngày, biên bản có chữ ký.*
