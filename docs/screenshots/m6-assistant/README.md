# M6 — Trợ lý AI chỉ đọc

Thư mục bằng chứng giao diện cho module M6.

## Kịch bản chụp

1. Giữ `AI_ASSISTANT_ENABLED=false`, đăng nhập và chụp widget thu gọn cùng thông báo trợ lý đang tắt.
2. Bật trợ lý với provider đã cấu hình, hỏi về tồn kho và chụp câu trả lời kèm nguồn **Tồn kho**.
3. Hỏi trạng thái một mã lô và chụp câu trả lời có dữ liệu thực từ **Trạng thái lô**.
4. Đăng nhập vai trò `lab`, hỏi danh sách hết hạn/FEFO và chụp thông báo từ chối quyền.
5. Dừng provider AI rồi gửi lại câu hỏi để chụp thông báo tiếng Việt thân thiện.

Không đưa API key, token JWT hoặc dữ liệu nhạy cảm vào ảnh. Ảnh thực tế nên đặt
tại đây với tên `01-disabled.png`, `02-inventory.png`, `03-batch-status.png`,
`04-rbac-denied.png` và `05-provider-unavailable.png`.
