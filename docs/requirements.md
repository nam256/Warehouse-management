# Yêu cầu hệ thống — đặc tả Digital QMS khóa kỹ thuật

## Trạng thái và phân định phạm vi

- **Baseline TTTN:** các yêu cầu `FR-001..FR-013` và `NFR-001..NFR-004` bên dưới mô tả prototype kho–sản xuất–Lab đã có; đây là nền tái sử dụng, không phải đóng góp mới của luận văn.
- **Phạm vi mới của luận văn:** Digital QMS gồm bốn module lõi M1–M4, được đặc tả bằng các ID `FR-Q*`, `FR-C*`, `FR-F*`, `FR-R*` và `NFR-LV*`.
- **Phạm vi tùy chọn:** M5 GC Import/SPC và M6 trợ lý AI hỏi–đáp chỉ được xem xét độc lập sau khi Gate G4 đạt; không được làm chậm M1–M4.
- **Tình trạng khóa:** nội dung Digital QMS dưới đây là baseline kỹ thuật để triển khai Task 1.5 trở đi; mọi thay đổi phạm vi phải được ghi nhận rõ, không sửa ngầm khi code.
- **Tình trạng phê duyệt:** sinh viên đang triển khai đặc tả này **tạm thời theo ủy quyền của người dùng** để chuẩn bị kỹ thuật. Xác nhận chính thức của giảng viên hướng dẫn/Gate G1 vẫn đang chờ; tài liệu này không khẳng định giảng viên đã phê duyệt.

## A. Baseline TTTN — yêu cầu hiện có

### Functional Requirements

| ID | Mô tả | Module | Ưu tiên |
|----|--------|--------|---------|
| FR-001 | Đăng nhập, phân quyền theo role | Auth | P0 |
| FR-002 | CRUD nguyên liệu, BTP, TP | Kho | P0 |
| FR-003 | CRUD nhà cung cấp | Kho | P1 |
| FR-004 | Phiếu nhập kho theo lô + CCP1 | Kho | P0 |
| FR-005 | Phiếu xuất kho (link mẻ SX sau) | Kho | P0 |
| FR-006 | Báo cáo tồn kho realtime | Kho | P0 |
| FR-007 | Lệnh/mẻ sản xuất | SX | P1 |
| FR-008 | Operation record + CCP2 | SX | P1 |
| FR-009 | Nhập kết quả Lab / GC | Lab | P2 |
| FR-010 | Cảnh báo vượt giới hạn CCP | CCP | P1 |
| FR-011 | Dashboard tổng hợp | Báo cáo | P1 |
| FR-012 | Audit log thao tác | Hệ thống | P0 |
| FR-013 | Truy xuất lô 2 chiều | Kho/SX | P1 |

### Non-Functional

- NFR-001: Giao diện tiếng Việt
- NFR-002: JWT session, mật khẩu hash
- NFR-003: Audit log không sửa/xóa
- NFR-004: Chạy local (SQLite/PostgreSQL)

### Roles

`admin` | `thu_kho` | `ky_thuat` | `lab` | `ql_nm` | `attp`

## Map biểu mẫu

| BM | Chức năng hệ thống |
|----|-------------------|
| BM-01/GMP01 | Phiếu nhập NVL |
| BM-02/GMP01 | Báo cáo tồn tháng |
| BM-01/GMP03 | Operation record |
| BM-01/GMP04 | Material balance |
| BM-01/GMP05 | Mixing report |
| BM-02/GMP05 | GC data |

---

## B. Phạm vi luận văn Digital QMS

### Module và thứ tự triển khai đã khóa

1. **M1 Quality Hold‑Release:** board trạng thái và Release Certificate.
2. **M2 CAPA/NCR:** hồ sơ sai lệch và quy trình khắc phục/phòng ngừa điện tử.
3. **M3 FEFO/Reservation:** phân bổ theo hạn dùng và giữ chỗ nguyên liệu.
4. **M4 QR/Recall:** Batch Passport bằng QR và Recall Simulator.
5. **M5 GC Import/SPC:** tùy chọn, chỉ sau Gate G4.
6. **M6 trợ lý AI:** tùy chọn, chỉ sau Gate G4, chỉ đọc và có thể tắt khi demo offline.

Mỗi module phải bàn giao API và UI trong cùng task/gate, dùng design system chung. Không chấp nhận trạng thái “backend xong, UI làm sau”.

### M1 — Quality Hold‑Release (`FR-Q01..FR-Q08`)

| ID | Yêu cầu có thể kiểm thử | Ưu tiên |
|---|---|---|
| FR-Q01 | Mỗi receipt nguyên liệu phải tạo lô với `ccp1_status="pending"` và `quality_status="quarantine"`; `thu_kho` không được tự đánh giá hoặc giải phóng CCP1. | P0 |
| FR-Q02 | Lab được chuyển lô theo `quarantine → sampling → under_test` và chỉ được gửi `awaiting_release` khi có LabTest CCP1 `pass`. | P0 |
| FR-Q03 | Hold‑Release là quy trình hai bước: Lab gửi duyệt; chỉ `attp` hoặc `admin` mới quyết định `awaiting_release → released|rejected`, kèm lý do và xác nhận điện tử. | P0 |
| FR-Q04 | Thành phẩm sau khi hoàn thành và CCP2 `pass` phải ở `quality_status="awaiting_release"`; hệ thống không được tự động chuyển thành `released`. | P0 |
| FR-Q05 | Issue/start sản xuất chỉ được dùng lô `quality_status="released"`, CCP tương ứng `pass`, chưa hết hạn và còn lượng khả dụng. | P0 |
| FR-Q06 | Mỗi transition phải ghi lịch sử bất biến gồm trạng thái trước/sau, lý do/ghi chú, người thực hiện, thời gian và AuditLog. | P0 |
| FR-Q07 | Lô đã release phải có Release Certificate PDF chứa mã lô, kết quả CCP, người Lab gửi, người ATTP/admin quyết định và thời gian ký. | P1 |
| FR-Q08 | UI `/quality` phải có board/bộ lọc/lịch sử, badge trạng thái và hành động theo RBAC; lỗi API phải hiện thông báo tiếng Việt thân thiện. | P0 |

Enum khóa: `quarantine`, `sampling`, `under_test`, `awaiting_release`, `released`, `rejected`, `retest`. Giữ giá trị API CCP đạt là `"pass"`.

### M2 — CAPA/NCR (`FR-C01..FR-C07`)

| ID | Yêu cầu có thể kiểm thử | Ưu tiên |
|---|---|---|
| FR-C01 | Tự tạo đúng một CAPA/NCR đang mở cho mỗi nguồn LabTest CCP1/CCP2 `fail`, OperationRecord CCP2 `fail`, hoặc quyết định reject lô; thao tác tạo phải idempotent. | P0 |
| FR-C02 | State machine phải là `open → investigating → action_pending → verification → closed`; không cho phép bỏ qua bước. | P0 |
| FR-C03 | Hồ sơ phải lưu `title`, `source_type`, `source_id`, `reason`, `root_cause`, `action_taken`, `due_date`, `disposition`, người xác minh/đóng và thời gian đóng. | P0 |
| FR-C04 | `lab|ky_thuat` chỉ được cập nhật điều tra/hành động phù hợp nguồn; mọi thay đổi phải được audit. | P0 |
| FR-C05 | Chỉ `attp|admin` được xác minh và đóng; cấm đóng khi thiếu root cause, action, disposition hoặc verification. | P0 |
| FR-C06 | `disposition="use_as_is"` chỉ hợp lệ với `attp|admin` và bắt buộc có justification. Các giá trị disposition còn lại là `retest|rework|reject`. | P0 |
| FR-C07 | UI `/capa` phải có danh sách/tab trạng thái, đánh dấu quá hạn màu đỏ, liên kết nguồn lỗi và cảnh báo quá hạn trên dashboard. | P1 |

### M3 — FEFO và Material Reservation (`FR-F01..FR-F06`)

| ID | Yêu cầu có thể kiểm thử | Ưu tiên |
|---|---|---|
| FR-F01 | Batch phải có `mfg_date`, `expiry_date`; hệ thống hiển thị `available_qty = on_hand_qty - active_reserved_qty`. | P0 |
| FR-F02 | FEFO chỉ xét đúng material/warehouse, lô `released`, CCP1 `pass`, chưa hết hạn, `available_qty > 0`; sort `expiry_date ASC` (null cuối), rồi `created_at ASC`. | P0 |
| FR-F03 | FEFO phải phân bổ được nhiều lô theo thứ tự đến khi đủ lượng yêu cầu và trả rõ phần phân bổ theo từng batch. | P0 |
| FR-F04 | Approve lệnh sản xuất phải tạo reservation atomic; nếu thiếu tổng lượng khả dụng thì trả lỗi 400 và rollback toàn bộ, không giữ chỗ một phần. Chống race condition được xác nhận trên PostgreSQL bằng row lock. | P0 |
| FR-F05 | Start lệnh phải chuyển reservation `active → consumed` và tạo OUT movement trong cùng transaction. | P0 |
| FR-F06 | Cancel trước start chuyển reservation `active → released`; cancel sau start tạo movement đảo chiều, giữ lịch sử và giải phóng phần còn lại. UI kho/xuất/sản xuất phải hiển thị gợi ý FEFO và reservation. | P0 |

Trạng thái reservation khóa: `active`, `consumed`, `released`.

### M4 — QR Batch Passport và Recall Simulator (`FR-R01..FR-R05`)

| ID | Yêu cầu có thể kiểm thử | Ưu tiên |
|---|---|---|
| FR-R01 | Batch Passport phải tổng hợp batch/material/supplier, ngày nhập hoặc sản xuất, hạn dùng, trạng thái chất lượng, kết quả CCP, lệnh sản xuất liên quan và link certificate nếu đã release. | P0 |
| FR-R02 | Hệ thống tạo QR dẫn đến đúng passport theo `batch_no`; quét QR không được tự thực hiện thao tác ghi nghiệp vụ. | P1 |
| FR-R03 | Recall Simulator phải duyệt downstream nhiều tầng từ input batch qua usages, production orders đến output batches; dùng tập batch/order đã thăm để chống vòng lặp. | P0 |
| FR-R04 | Kết quả recall phải nêu batch/lệnh bị ảnh hưởng, số lượng liên quan, trạng thái release, lý do, người khởi tạo và `duration_ms`. Recall là **read-only đối với dữ liệu nghiệp vụ**: không đổi tồn, reservation, trạng thái lô hoặc CAPA. | P0 |
| FR-R05 | UI `/trace` phải hiển thị passport/QR/kết quả phân tầng và cho export CSV UTF‑8 BOM. | P1 |

### M5/M6 — phạm vi tùy chọn sau Gate G4

- **M5 GC Import/SPC:** import CSV atomic, chống trùng SHA‑256 và thống kê SPC; chỉ bắt đầu sau khi M1–M4 chạy ổn định trên SQLite và PostgreSQL.
- **M6 trợ lý AI:** chỉ gọi whitelist truy vấn đọc dưới JWT/RBAC của người dùng, trả lời từ dữ liệu API thật và trả “không tìm thấy” khi thiếu dữ liệu. M6 không được gọi endpoint ghi nghiệp vụ, release/reject lô, thay đổi reservation, hoặc xác minh/đóng CAPA. Nếu hỗ trợ hỏi phạm vi recall, M6 chỉ chạy preview bằng service duyệt đồ thị read-only, không tạo `RecallSimulation`. Ghi `AssistantQueryLog`/AuditLog tối thiểu là metadata tuân thủ duy nhất được phép và không được làm thay đổi trạng thái nghiệp vụ. Có `AI_ASSISTANT_ENABLED` để tắt hoàn toàn mà không ảnh hưởng M1–M5.

## C. Yêu cầu phi chức năng luận văn (`NFR-LV01..NFR-LV05`)

| ID | Yêu cầu có thể kiểm thử |
|---|---|
| NFR-LV01 | Cùng SQLAlchemy model/migration phải chạy trên SQLite cho dev/unit test và PostgreSQL 16 cho integration, concurrency và demo; không tách hai nhánh business logic. |
| NFR-LV02 | Mỗi module ship API + UI cùng gate, dùng design tokens/component shell chung; không CSS ad-hoc tạo giao diện thứ hai. |
| NFR-LV03 | Mọi async UI handler phải có `try/catch`, trạng thái loading/empty/error và thông báo tiếng Việt qua `AlertBanner`/`Toast`; không hiện stack trace, JSON thô hoặc chỉ log console. |
| NFR-LV04 | Mọi module mới phải có RBAC phía backend, AuditLog, test tự động và UAT. Không tuyên bố UAT/chỉ số đạt nếu chưa có bằng chứng chạy thật. |
| NFR-LV05 | Reservation concurrency chỉ được xác nhận trên PostgreSQL; Recall Simulator có mục tiêu hoàn thành không quá 3 giây trên bộ dữ liệu demo, đo và lưu kết quả thật trước khi báo cáo. |
