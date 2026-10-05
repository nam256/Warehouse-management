# Chỉ số đánh giá luận văn — Digital QMS

**Ngày cập nhật:** 18/07/2026  
**Quy tắc ghi nhận:** Không suy diễn thời gian hoặc tỷ lệ từ test tự động. Trường thời gian/tỷ lệ chưa được người dùng thực tế đo bằng đồng hồ được để trống và ghi “chưa đo thủ công — cần UAT thực tế”.

## 1. Bảng chỉ số chính

| Metric | Baseline | Digital QMS | Kết quả/nguồn bằng chứng |
|---|---:|---:|---|
| Lô chưa release bị chặn | 0/5 *(mục tiêu kế hoạch, chưa đo lại)* |  | **Rule được xác nhận tự động**: quarantine không được issue, Thủ kho không được release (`test_quality_release.py`). Tỷ lệ 5 mẫu chưa đo thủ công. |
| CCP fail có CAPA | 0/5 *(mục tiêu kế hoạch, chưa đo lại)* |  | **Cơ chế tự sinh và chống trùng được xác nhận tự động** (`test_capa.py::test_same_failure_creates_one_open_capa`). Tỷ lệ 5 mẫu chưa đo thủ công. |
| FEFO chọn đúng | thủ công |  | **Thuật toán chọn hạn sớm nhất được xác nhận tự động** (`test_fefo_allocates_earliest_expiry_first`). Tỷ lệ 10 lượt chưa đo thủ công. |
| Recall runtime | thủ công |  ms | **chưa đo thủ công — cần UAT thực tế**. Test chỉ xác nhận runtime không âm và trả đủ chuỗi nhiều cấp; không dùng thời gian pytest làm runtime nghiệp vụ. |
| Nhập 10 GC rows |  giây |  giây | **chưa đo thủ công — cần UAT thực tế**. Test xác nhận 10 dòng được import một lần và lần lặp idempotent. |
| Hủy lệnh phục hồi tồn khả dụng | chưa có đo baseline |  | **Rule được xác nhận tự động** (`test_cancel_running_order_restores_stock`); chưa đo tỷ lệ thao tác người dùng. |
| Thiếu tồn không tạo reservation một phần | chưa có đo baseline |  | **Rule atomic được xác nhận tự động** (`test_approve_with_insufficient_stock_creates_no_partial_reservation`). |
| CAPA không được đóng khi thiếu xác minh | chưa có đo baseline |  | **Rule được xác nhận tự động** (`test_capa_cannot_close_without_verification`). |
| Trợ lý không bịa khi thiếu dữ liệu | chưa có đo baseline |  | **Hành vi fallback được xác nhận tự động** (`test_model_answer_without_tool_data_is_not_trusted`); chất lượng câu trả lời thực tế chưa UAT. |

## 2. Kết quả kiểm thử hỗ trợ

| Chỉ số kỹ thuật | Giá trị đã quan sát | Giới hạn diễn giải |
|---|---|---|
| Backend SQLite profile | 46 passed, 1 skipped, 1 deselected | Chỉ phản ánh test tự động ngày 18/07/2026; không thay UAT |
| Frontend production build | Pass, 72 modules transformed | Xác nhận khả năng build; không xác nhận UI nghiệp vụ |
| PostgreSQL profile | Chưa chạy trong Task 10 | Không tuyên bố concurrency/Gate G4 từ lượt chạy này |
| Playwright smoke | Blocked do frontend không chạy tại `127.0.0.1:5173` | Không phải lỗi assertion nghiệp vụ, nhưng E2E chưa có bằng chứng xanh |

## 3. Phiếu đo thủ công

### 3.1. Hold-Release và CAPA

| Lượt | Người/role | Lô/failure | Baseline đúng? | Digital QMS đúng? | Thời gian | Ghi chú |
|---:|---|---|---|---|---:|---|
| 1 |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |

### 3.2. FEFO

| Lượt | Tập lô/hạn dùng | Lô kỳ vọng | Lô hệ thống chọn | Đúng/sai | Thời gian |
|---:|---|---|---|---|---:|
| 1–10 |  |  |  |  |  |

### 3.3. Recall và GC

| Phép đo | Bắt đầu | Kết thúc | Thời lượng | Dữ liệu | Người đo |
|---|---|---|---:|---|---|
| Recall lần 1 |  |  |  |  |  |
| Recall lần 2 |  |  |  |  |  |
| Recall lần 3 |  |  |  |  |  |
| Import 10 GC baseline |  |  |  |  |  |
| Import 10 GC Digital QMS |  |  |  |  |  |

## 4. Cách tính sau UAT

- Tỷ lệ chặn đúng = số lượt bị chặn đúng / tổng lượt âm đã chạy.
- Tỷ lệ CAPA tự sinh đúng = số failure tạo đúng một CAPA / tổng failure.
- Tỷ lệ FEFO đúng = số lượt chọn đúng hạn sớm nhất / 10.
- Recall runtime báo cáo tối thiểu median của 3 lượt cùng bộ dữ liệu và cùng môi trường.
- Thời gian GC tính từ lúc chọn file đến khi UI báo hoàn tất; ghi riêng thời gian nhập baseline thủ công.

Cho đến khi các phiếu trên được điền và có người đo, báo cáo chỉ được kết luận rằng **các rule nêu trên có bằng chứng test tự động**, không kết luận phần trăm cải thiện hay thời gian tiết kiệm.
