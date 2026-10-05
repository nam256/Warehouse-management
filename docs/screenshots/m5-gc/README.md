# M5 — GC Import + SPC

Thư mục bằng chứng giao diện cho module M5.

## Kịch bản chụp

1. Đăng nhập bằng tài khoản `lab` hoặc `admin`, mở **Phòng kiểm nghiệm**.
2. Chọn tab **Import GC & SPC**.
3. Chọn `backend/tests/fixtures/gc_sample.csv` và chụp phần xem trước CSV.
4. Import tệp, sau đó chụp thông báo thành công, các chỉ số mean/σ/UCL/LCL và biểu đồ SPC.
5. Import lại cùng tệp để chụp thông báo chống trùng SHA-256.
6. Dùng một CSV có dòng sai để chụp lỗi tiếng Việt và xác nhận không dòng nào được lưu.

Ảnh thực tế nên được đặt tại đây với tên `01-preview.png`, `02-spc.png`,
`03-duplicate.png` và `04-atomic-error.png`.
