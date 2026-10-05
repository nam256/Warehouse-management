# Kịch bản video demo Digital QMS — 5 phút

**Mục tiêu:** Minh họa luồng kiểm soát chất lượng từ nhập lô đến recall, không trình bày kết quả UAT/sign-off chưa có.  
**Thời lượng:** 05:00, quay 1920×1080/30 FPS.

## Chuẩn bị

- Chạy full stack, seed sẵn hai lô: một lô đạt và một lô fail.
- Chuẩn bị tài khoản `thu_kho`, `lab`, `attp`, `ky_thuat`; không để lộ mật khẩu.
- Chuẩn bị lệnh sản xuất đủ nguyên liệu, chuỗi NVL → BTP → TP và thư mục tải CSV.
- Kiểm tra certificate PDF, QR/passport và recall trước khi quay.
- Dùng dữ liệu demo; không nói UAT doanh nghiệp đã ký hoặc nêu số thời gian chưa đo.

## Storyboard và lời thoại

| Thời gian | Thao tác trên màn hình | Lời thoại gợi ý |
|---|---|---|
| 00:00–00:40 | Đăng nhập Thủ kho, tạo phiếu nhập/lô mới | “Thủ kho ghi nhận lô nguyên liệu. Digital QMS luôn đặt lô mới ở trạng thái quarantine, vì vậy lô chưa thể cấp cho sản xuất.” |
| 00:40–01:20 | Chuyển sang Lab, nhập kết quả đạt | “Lab nhập kết quả kiểm nghiệm. Kết quả đạt chỉ chuyển lô sang awaiting release; hệ thống không tự giải phóng để bảo đảm phân tách trách nhiệm.” |
| 01:20–02:00 | Đăng nhập ATTP, xem lịch sử, xác nhận điện tử, release và tải certificate | “ATTP kiểm tra hồ sơ, ghi chú xác nhận rồi mới release. Sau release, hệ thống cho tải chứng nhận PDF và lưu lịch sử chuyển trạng thái.” |
| 02:00–03:00 | Mở lô fail, cho thấy CAPA tự sinh; thử đóng thiếu xác minh rồi hoàn thiện xử lý/xác minh | “Một kết quả fail tự tạo CAPA nhưng không tạo bản ghi trùng khi sự kiện được gửi lại. CAPA không thể đóng nếu thiếu xác minh hiệu lực.” |
| 03:00–04:00 | Kỹ thuật duyệt lệnh sản xuất; xem FEFO reservation; minh họa lô hết hạn bị loại | “Khi duyệt lệnh, hệ thống giữ chỗ theo hạn dùng sớm nhất, loại lô hết hạn hoặc quarantine. Nếu thiếu tồn, toàn bộ thao tác bị rollback thay vì giữ chỗ một phần.” |
| 04:00–05:00 | Mở QR Batch Passport, chạy recall nhiều cấp, kiểm tra danh sách downstream và export CSV | “Batch Passport tập trung trạng thái và truy xuất lô. Recall Simulator đi qua nhiều cấp NVL–BTP–TP ở chế độ chỉ đọc; kết quả có thể xuất CSV phục vụ diễn tập.” |

## Điểm nhấn hình ảnh

1. Badge `quarantine` → `awaiting_release` → `released`.
2. Thông báo từ chối khi sai vai trò/thiếu xác nhận.
3. Một CAPA duy nhất cho cùng failure và cảnh báo thiếu verification.
4. Thứ tự FEFO và lượng `available` sau reservation.
5. Danh sách affected batches/orders, depth và nút export CSV.

## Câu kết

“Các module Digital QMS đã có bằng chứng kiểm thử tự động cho rule cốt lõi. UAT trực tiếp, phép đo thời gian và phê duyệt doanh nghiệp/giảng viên vẫn được ghi là pending cho đến khi có buổi đánh giá thực tế.”

## Checklist hậu kỳ

- [ ] Tổng thời lượng không quá 05:10; cắt thời gian chờ.
- [ ] Che mật khẩu, token và dữ liệu nhạy cảm.
- [ ] Phụ đề tiếng Việt khớp tên trạng thái.
- [ ] Không chèn tỷ lệ hoặc runtime chưa đo.
- [ ] Export H.264 và lưu link/bằng chứng vào hồ sơ UAT.
