# Kết quả UAT — Digital QMS

**Ngày cập nhật bằng chứng tự động:** 18/07/2026  
**UAT trực tiếp với người dùng nghiệp vụ:** **Chưa thực hiện / chưa ký**  
**Phạm vi:** 20 trường hợp trong `docs/uat-test-cases.md`

> “Pass (automated)” dưới đây chỉ xác nhận rule bằng test tự động. Đây không phải là kết quả UAT con người và không được diễn giải thành “100% UAT”.

## 1. Bằng chứng chạy tự động

| Hạng mục | Lệnh/nguồn | Kết quả thực tế |
|---|---|---|
| Backend SQLite profile | `backend\.venv\Scripts\python.exe -m pytest tests -q -m "not postgres"` | **46 passed, 1 skipped, 1 deselected**, exit 0 |
| Backend gọi toàn bộ `tests` không cấu hình profile | `pytest tests -q` | **46 passed, 1 failed, 1 skipped**; fail do `test_postgres_profile.py` nhận SQLite thay vì PostgreSQL |
| Frontend production build | `npm run build` | **Pass**, 72 modules transformed, exit 0 |
| Playwright smoke | `npx playwright test` | **Blocked**: `ERR_CONNECTION_REFUSED` tại `127.0.0.1:5173`; full stack chưa chạy trong lượt xác minh |
| PostgreSQL integration/concurrency | profile PostgreSQL theo `docs/deploy.md` | **Chưa chạy trong Task 10** |

Ghi chú môi trường: lần chạy đầu tiên bị lỗi collection vì virtual environment thiếu gói `qrcode`; đã cài đúng dependency `qrcode[pil]>=8.2` vốn đã khai báo trong `backend/requirements.txt`, sau đó SQLite profile chạy xanh. Không sửa mã nguồn ứng dụng.

## 2. Kết quả theo trường hợp

| ID | Trạng thái kỹ thuật | Bằng chứng | UAT con người |
|---|---|---|---|
| UAT-M1-01 | **Pass (automated)** | `test_quality_release.py::test_warehouse_cannot_release` | Pending |
| UAT-M1-02 | **Pass (automated)** | `test_lab_pass_does_not_auto_release` | Pending |
| UAT-M1-03 | **Pending** | Chưa có test trực tiếp cho ATTP release từ `quarantine` | Pending |
| UAT-M1-04 | **Pass (automated)** | `test_attp_release_requires_electronic_confirmation_note`; `test_attp_releases_awaiting_batch_and_history_is_recorded` | Pending |
| UAT-M1-05 | **Pass (automated)** | `tests/test_release_certificate.py` | Pending |
| UAT-M2-01 | **Pass (automated)** | `test_capa.py::test_same_failure_creates_one_open_capa` | Pending |
| UAT-M2-02 | **Pass (automated)** | `test_same_failure_creates_one_open_capa` kiểm tra idempotency | Pending |
| UAT-M2-03 | **Pending** | Chưa có test trực tiếp cho hiển thị overdue | Pending |
| UAT-M2-04 | **Pass (automated)** | `test_capa_cannot_close_without_verification` | Pending |
| UAT-M3-01 | **Pass (automated)** | `test_fefo_allocates_earliest_expiry_first` | Pending |
| UAT-M3-02 | **Pass (automated)** | `test_expired_or_quarantine_batch_is_excluded` | Pending |
| UAT-M3-03 | **Pass (automated)** | `test_approve_with_insufficient_stock_creates_no_partial_reservation` | Pending |
| UAT-M3-04 | **Pass (automated)** | `test_cancel_running_order_restores_stock` | Pending |
| UAT-M4-01 | **Pending** | Chưa có test API/UI passport trực tiếp | Pending |
| UAT-M4-02 | **Pass (automated)** | `test_recall_returns_all_downstream_batches_across_multiple_levels` | Pending |
| UAT-M4-03 | **Pending** | Chưa có test tải/đối chiếu CSV trực tiếp | Pending |
| UAT-M5-01 | **Pass (automated)** | `test_gc_import_is_atomic_on_invalid_row` | Pending |
| UAT-M5-02 | **Pass (automated)** | `test_gc_import_is_idempotent_and_populates_spc`; `test_spc_flags_value_above_ucl` | Pending |
| UAT-M6-01 | **Pass (automated)** | whitelist, quyền tool và query log trong `test_assistant.py` | Pending |
| UAT-M6-02 | **Pass (automated)** | từ chối tool ghi, không tin câu trả lời thiếu dữ liệu, feature flag trong `test_assistant.py` | Pending |

## 3. Tổng hợp trung thực

- 16/20 trường hợp có bằng chứng rule tự động trực tiếp.
- 4/20 trường hợp cần bổ sung kiểm tra trực tiếp: M1 invalid transition cụ thể, CAPA overdue UI, batch passport UI và Recall CSV.
- 20/20 trường hợp vẫn **pending UAT con người**; chưa tính pass rate UAT và chưa có chữ ký doanh nghiệp/giảng viên.
- Gate G5 mới có bằng chứng kỹ thuật một phần; chưa thể tuyên bố hoàn tất cho đến khi UAT trực tiếp, đo thủ công, Playwright/full stack và sign-off được thực hiện.

## 4. Biểu ghi UAT trực tiếp cần điền

| ID | Người thực hiện/vai trò | Ngày giờ | Browser/DB | Kết quả | Bằng chứng/issue |
|---|---|---|---|---|---|
| UAT-M1-01 … UAT-M6-02 |  |  |  | Pending |  |

## 5. Sign-off

| Vai trò | Họ tên | Kết quả | Ngày | Chữ ký |
|---|---|---|---|---|
| Thủ kho | *(pending)* |  |  |  |
| Lab | *(pending)* |  |  |  |
| ATTP | *(pending)* |  |  |  |
| Quản lý nhà máy | *(pending)* |  |  |  |
| Giảng viên hướng dẫn | *(pending)* |  |  |  |
