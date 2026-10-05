# M3 — FEFO và giữ chỗ nguyên liệu

Thư mục lưu bằng chứng giao diện cho Gate G3:

- `inventory.png`: tồn vật lý, đã giữ chỗ, khả dụng và hạn dùng gần nhất.
- `stock-out.png`: nút **Gợi ý FEFO** và danh sách phân bổ theo hạn dùng.
- `production.png`: các lô nguyên liệu được giữ chỗ theo từng mẻ sản xuất.

Ảnh cần được chụp từ môi trường demo có ít nhất hai lô đã giải phóng với hạn dùng khác nhau. README này không tuyên bố UAT đã đạt khi chưa có ảnh và biên bản chạy thực tế.

PostgreSQL concurrency chưa được xác nhận trong Task 6 nếu máy chưa có dịch vụ PostgreSQL test. SQLite chỉ xác nhận quy tắc tuần tự; kiểm tra chống cấp giữ chỗ vượt tồn phải chạy trong profile PostgreSQL ở Gate G4.
