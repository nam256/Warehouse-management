# Kịch bản UAT — Digital QMS

**Phiên bản:** Task 10  
**Ngày lập:** 18/07/2026  
**Phạm vi:** M1–M6; M1–M4 là lõi, M5–M6 là mở rộng đã triển khai  
**Nguyên tắc:** UAT trực tiếp phải do người dùng nghiệp vụ thao tác và ký xác nhận. Test tự động chỉ là bằng chứng kỹ thuật, không thay thế UAT con người.

## 1. Môi trường và dữ liệu chuẩn bị

- Backend và frontend chạy theo `docs/deploy.md`; ưu tiên PostgreSQL cho buổi UAT.
- Tài khoản tối thiểu: `thu_kho`, `lab`, `attp`, `ky_thuat`, `ql_nm`.
- Có lô ở các trạng thái `quarantine`, `awaiting_release`, `released`, một lô hết hạn và một lệnh sản xuất đủ/thiếu nguyên liệu.
- Có chuỗi truy xuất NVL → BTP → TP; file GC hợp lệ 10 dòng và file có một dòng sai.
- Ghi người thực hiện, thời điểm, DB/browser, dữ liệu đầu vào và bằng chứng ảnh/video vào `docs/uat-results.md`.

## 2. Danh sách 20 trường hợp

| ID | Module | Loại | Vai trò | Thao tác chính | Kết quả mong đợi | Bằng chứng tự động liên quan |
|---|---|---|---|---|---|---|
| UAT-M1-01 | M1 Hold-Release | Âm/RBAC | `thu_kho` | Mở lô chờ và thử giải phóng | API/UI từ chối; trạng thái không đổi | `tests/test_quality_release.py::test_warehouse_cannot_release` |
| UAT-M1-02 | M1 Hold-Release | Dương | `lab` | Nhập kết quả đạt cho lô quarantine | Lô chuyển `awaiting_release`, chưa tự release | `test_lab_pass_does_not_auto_release` |
| UAT-M1-03 | M1 Hold-Release | Âm/state | `attp` | Thử release trực tiếp lô quarantine | Bị chặn do sai chuyển trạng thái | `test_attp_releases_awaiting_batch_and_history_is_recorded` và `test_quarantine_batch_cannot_be_issued` |
| UAT-M1-04 | M1 Hold-Release | Dương/gate | `attp` | Xác nhận điện tử, ghi chú và release lô `awaiting_release` | Lô `released`, có lịch sử; nếu thiếu ghi chú thì bị chặn | `test_attp_release_requires_electronic_confirmation_note`, `test_attp_releases_awaiting_batch_and_history_is_recorded` |
| UAT-M1-05 | M1 Hold-Release | Dương/âm | `attp` | Tải certificate trước và sau release | Trước release bị chặn; sau release trả PDF | `tests/test_release_certificate.py` |
| UAT-M2-01 | M2 CAPA | Dương | `lab` | Ghi cùng một kết quả CCP fail | Một CAPA mở được tự sinh | `tests/test_capa.py::test_same_failure_creates_one_open_capa` |
| UAT-M2-02 | M2 CAPA | Âm/idempotent | `lab` | Gửi lại cùng failure nhiều lần | Không tạo CAPA mở trùng | `test_same_failure_creates_one_open_capa` |
| UAT-M2-03 | M2 CAPA | Dương | `attp`/`ql_nm` | Mở danh sách CAPA quá hạn | CAPA quá hạn được nhận diện/hiển thị đúng | Chưa có test tự động trực tiếp; cần UAT thực tế |
| UAT-M2-04 | M2 CAPA | Âm/validation | `attp` | Đóng CAPA khi chưa có xác minh hiệu lực | Bị chặn, CAPA vẫn mở | `test_capa_cannot_close_without_verification` |
| UAT-M3-01 | M3 FEFO | Dương | `ky_thuat` | Duyệt lệnh cần nhiều lô hợp lệ | Giữ chỗ theo hạn dùng sớm nhất | `tests/test_fefo.py::test_fefo_allocates_earliest_expiry_first` |
| UAT-M3-02 | M3 FEFO | Âm | `ky_thuat` | Duyệt khi có lô hết hạn/quarantine | Hai loại lô bị loại khỏi lựa chọn | `test_expired_or_quarantine_batch_is_excluded` |
| UAT-M3-03 | M3 FEFO | Âm/atomic | `ky_thuat` | Duyệt lệnh vượt tồn khả dụng | Báo thiếu tồn; không tạo reservation một phần | `test_approve_with_insufficient_stock_creates_no_partial_reservation` |
| UAT-M3-04 | M3 FEFO | Dương/rollback | `ky_thuat` | Hủy lệnh đang chạy có reservation | Reservation được hủy, tồn khả dụng phục hồi đúng | `test_cancel_running_order_restores_stock` |
| UAT-M4-01 | M4 Passport | Dương | Người có quyền xem | Mở QR/link batch passport | Hiển thị đúng mã lô, trạng thái chất lượng và dữ liệu truy xuất; không sửa dữ liệu | Chưa có test API trực tiếp; cần UAT thực tế |
| UAT-M4-02 | M4 Recall | Dương/multi-level | `attp` | Chạy recall từ lô NVL qua BTP tới TP | Trả đủ các lô/lệnh downstream theo đúng depth; không đổi dữ liệu | `tests/test_recall.py::test_recall_returns_all_downstream_batches_across_multiple_levels` |
| UAT-M4-03 | M4 Recall | Dương/export | `attp` | Export kết quả recall CSV | Tệp tải được, UTF-8, số dòng/mã lô khớp màn hình | Chưa có test export trực tiếp; cần UAT thực tế |
| UAT-M5-01 | M5 GC/SPC | Âm/atomic | `lab` | Import CSV có một batch không tồn tại | HTTP 422; không ghi bất kỳ dòng Lab nào | `tests/test_gc_import_spc.py::test_gc_import_is_atomic_on_invalid_row` |
| UAT-M5-02 | M5 GC/SPC | Dương/SPC | `lab` | Import 10 điểm rồi thêm điểm vượt UCL | Import idempotent; SPC đánh dấu điểm ngoài kiểm soát | `test_gc_import_is_idempotent_and_populates_spc`, `test_spc_flags_value_above_ucl` |
| UAT-M6-01 | M6 Assistant | Dương/grounded | Vai trò được phép | Hỏi tồn kho/trạng thái lô có dữ liệu | Chỉ dùng tool whitelist và trả lời dựa trên dữ liệu tool | `tests/test_assistant.py::test_assistant_only_allows_whitelisted_tools`, `test_assistant_tool_runs_with_user_permissions`, `test_assistant_logs_success_without_real_provider` |
| UAT-M6-02 | M6 Assistant | Âm/safety | Vai trò hạn chế | Yêu cầu release hoặc hỏi khi không có dữ liệu | Từ chối tool ngoài whitelist; không bịa số; có thể tắt để demo offline | `test_assistant_rejects_non_whitelisted_tool`, `test_model_answer_without_tool_data_is_not_trusted`, `test_assistant_disabled_returns_503` |

## 3. Cách thực hiện và tiêu chí

1. Thực hiện đúng vai trò và dữ liệu chuẩn bị; không dùng tài khoản admin để né RBAC.
2. Chụp bằng chứng trước/sau cho mọi trường hợp âm và xác nhận dữ liệu không đổi.
3. **Pass (human UAT)** chỉ khi key user trực tiếp thao tác, kết quả đúng và ghi tên/ngày.
4. **Pass (automated)** chỉ xác nhận rule kỹ thuật được test; không được cộng thành tỷ lệ UAT con người.
5. Trường hợp lỗi phải ghi mã lỗi, bước tái hiện và mức ảnh hưởng; không tự sửa kết quả.

## 4. Điều kiện hoàn tất Gate G5

- Có kết quả cho đủ 20 trường hợp và bằng chứng gắn với từng ID.
- Các trường hợp P0 âm của M1–M4 không được fail.
- Các chỉ số thời gian/tỷ lệ chỉ điền sau khi đo thực tế.
- Có sign-off nghiệp vụ và giảng viên nếu quy trình yêu cầu. Hiện các sign-off này chưa được giả định là đã có.
