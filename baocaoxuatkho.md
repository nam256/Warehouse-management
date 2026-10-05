# Kế hoạch hoàn thiện báo cáo tồn kho và xuất kho

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện bộ báo cáo **tồn kho (BM-02/GMP01)** và **xuất kho (phiếu PX + sổ xuất)** đủ để demo bảo vệ: số liệu khớp màn hình, lọc được kỳ, in PDF/CSV tiếng Việt, phủ đủ tình huống làm việc thực tế tại Oxeyns Long An.

**Architecture:** Giữ React → FastAPI `/api/v1/reports/*` → ReportLab/CSV. Tồn kho lấy từ `stock_batches` + `material_reservations`; xuất kho lấy từ `stock_movements` (`movement_type=OUT`) gắn lô, vật tư, người lập, mẻ SX nếu có. Không viết logic tồn riêng cho báo cáo — cùng công thức với màn Tồn kho / Xuất kho.

**Tech Stack:** FastAPI, SQLAlchemy 2, ReportLab, CSV UTF-8 BOM, React/TypeScript, pytest.

## Global Constraints

- UI và file xuất tiếng Việt có dấu; mã API/enum tiếng Anh.
- Tồn **vật lý** = `stock_batches.quantity`; tồn **giữ chỗ** = reservation `active`; tồn **khả dụng** = max(vật lý − giữ chỗ, 0). Báo cáo phải ghi rõ loại số đang in.
- Chỉ xuất lô `quality_status=released`, `ccp1_status=pass`, còn hạn, còn khả dụng — báo cáo xuất không được “ngụy tạo” phiếu cho lô không đủ điều kiện.
- Cùng model chạy SQLite (dev/test) và PostgreSQL (demo).
- Mọi endpoint báo cáo yêu cầu JWT; quyền xem: thủ kho, QL NM, ATTP, admin; lập phiếu xuất: thủ kho / kỹ thuật / admin (giữ như `stock_issue` hiện tại).
- Không cam kết go-live / chữ ký giấy FSSC chính thức; prototype đủ in và đối chiếu.
- File mới/sửa chính: `backend/app/services/csv_export.py`, `pdf_export.py`, `backend/app/routers/reports.py`, `frontend/src/pages/Reports.tsx`, `frontend/src/api.ts`, `backend/tests/test_stock_reports.py`.

---

## 1. Hiện trạng (để hội đồng khỏi “bịa”)

| Việc | Đã có | Thiếu / lệch |
|------|--------|----------------|
| Tồn kho trên UI `/inventory` | Vật lý, giữ chỗ, khả dụng, HSD gần, tồn thấp, ảnh, CSV/PDF nhanh | CSV/PDF **không** có giữ chỗ / khả dụng / HSD / trạng thái chất lượng |
| Công thức tồn thấp trên UI | So **khả dụng** với `min_stock` | CSV so **tồn vật lý** với `min_stock` → hai số có thể khác nhau |
| BM-02/GMP01 đặc tả | Tồn đầu / nhập / xuất / tồn cuối theo kỳ | File hiện tại chỉ **snapshot hôm nay**, không có kỳ |
| Chi tiết theo lô | Màn tồn + lô trên kho | Báo cáo gộp theo mã vật tư, mất lô / CCP / Hold-Release |
| Phiếu nhập BM-01/GMP01 | PDF theo `batch_id` | Số trên phiếu = tồn **hiện tại**, không phải SL lúc nhập nếu đã xuất bớt |
| Phiếu xuất kho | API `POST /stock/issues` tạo `PX-…` | **Không có PDF/CSV phiếu xuất** trên trang Báo cáo |
| Sổ nhập–xuất | `GET /stock/movements` | Không lọc ngày, không xuất file, UI Xuất kho không liệt kê lịch sử phiếu |
| Xuất khi bắt đầu mẻ | Tự xuất lô đã giữ chỗ | Báo cáo không tách “xuất tay” vs “xuất cho mẻ SX” |
| Hủy mẻ | Movement đảo hoàn tồn | Báo cáo chưa phân biệt phiếu đảo / điều chỉnh |

**Câu trả lời ngắn khi hỏi “em xuất file gì?”**

> Tồn kho: CSV/PDF BM-02/GMP01 snapshot. Nhập kho: PDF phiếu theo lô. Xuất kho: hệ thống đã ghi phiếu `PX-…` và audit, **chưa có bản in phiếu xuất** — đó là hạng mục hoàn thiện của kế hoạch này.

---

## 2. Mục tiêu sản phẩm sau khi làm xong

Ba loại hồ sơ, in được, đối chiếu được với UI:

1. **Báo cáo tồn kho** — theo kỳ (từ ngày → đến ngày) + snapshot “tại thời điểm in”.
2. **Sổ xuất kho** — danh sách mọi phiếu `OUT` trong kỳ (tay + sản xuất).
3. **Phiếu xuất kho từng lần** — PDF một `reference_no` (PX-…).

Mỗi file có: tên công ty Oxeyns Long An, mã biểu mẫu, ngày giờ VN, người xuất file, chú thích công thức số.

---

## 3. Ma trận tình huống làm việc (phải phủ hết)

### 3.1. Tồn kho — số liệu

| Mã | Tình huống | Báo cáo phải thể hiện | Nếu sai, hội đồng bắt |
|----|------------|------------------------|------------------------|
| T01 | Kho trống (sau `reset_db`) | 3 vật tư seed, tồn 0, không cảnh báo ảo | “Sao có 10 kg?” |
| T02 | Vừa nhập, chưa Lab | Lô **cách ly**, tồn vật lý tăng, **khả dụng = 0** (chưa released) | Xuất/SX dùng lô chưa giải phóng |
| T03 | Lab đạt, ATTP chưa giải phóng | Vật lý > 0, khả dụng = 0, trạng thái chờ phê duyệt | Nhầm “có hàng” với “được dùng” |
| T04 | Đã giải phóng, chưa giữ chỗ | Vật lý = khả dụng | OK baseline |
| T05 | QL NM đã duyệt mẻ (FEFO giữ chỗ) | Vật lý **không** giảm; giữ chỗ tăng; khả dụng giảm | CSV hiện tại gộp nhầm vào “Tồn (kg)” |
| T06 | Đã bắt đầu SX (consume) | Vật lý giảm đúng SL xuất; giữ chỗ hết; phiếu OUT gắn `production_order_id` | Không truy được mẻ |
| T07 | Hai lô cùng NVL, HSD khác | Dòng theo lô: HSD gần / xa; gộp mã hàng = tổng | FEFO không chứng minh được trên file |
| T08 | Lô hết hạn còn kg | Có cột/cảnh báo hết hạn; không đưa vào khả dụng xuất | Xuất lô HSD quá |
| T09 | Lô CCP1 fail / rejected | Không khả dụng; vẫn thấy trên tồn vật lý nếu chưa trả NCC | “Hàng hỏng biến mất” |
| T10 | Tồn thấp | Cảnh báo khi **khả dụng** < min_stock (đúng UI) | CSV đang so vật lý |
| T11 | BTP / TP | Tách loại NVL–BTP–TP; TP chờ release giống NVL | Gộp một cột |
| T12 | Lọc kỳ tháng | Tồn đầu + nhập + xuất + tồn cuối = khớp ledger | BM-02/GMP01 chưa làm |
| T13 | Vật tư không còn lô | Vẫn hiện dòng 0 (master data) | Mất mã hàng trên báo cáo tháng |
| T14 | In lúc đang có reservation | Chú thích “số in lúc … giờ VN” | Tranh cãi số với màn hình |

### 3.2. Xuất kho — thao tác và phiếu

| Mã | Tình huống | Hệ thống / báo cáo |
|----|------------|---------------------|
| X01 | Chưa nhập số kg | Form trống; **Đã xuất = tổng phiếu OUT thật**, không hiện 10 kg ảo |
| X02 | Xuất tay một lô released | Tạo PX; tồn giảm; PDF phiếu; dòng sổ xuất |
| X03 | Gợi ý FEFO nhiều lô | Gợi ý đúng HSD sớm; **mỗi lần lưu vẫn một lô** (hạn chế hiện tại) — kế hoạch: xuất nhiều dòng / nhiều PX cùng lần hoặc một phiếu nhiều dòng |
| X04 | SL > khả dụng | 400, không ghi movement |
| X05 | Chọn lô quarantine / chưa pass CCP1 / hết hạn | Không chọn được / 400 |
| X06 | Thủ kho không được xuất (role khác) | 403 |
| X07 | Xuất gắn mẻ SX | `production_order_id` trên phiếu; in rõ “Xuất cho mẻ SX-…” |
| X08 | Xuất tay không gắn mẻ | Ghi “Xuất kho thủ công” |
| X09 | Hai phiếu cùng lô liên tiếp | Hai PX; tồn lũy kế đúng |
| X10 | Hủy mẻ đang chạy | Movement đảo (IN hoặc OUT âm — **chốt một kiểu**); sổ ghi “Hoàn tồn do hủy mẻ”, không xóa PX gốc |
| X11 | In lại phiếu cũ | Cùng `reference_no`, watermark “Bản in lại” + thời điểm in |
| X12 | Kỳ không có xuất | File vẫn ra, bảng trống, tổng 0 kg |
| X13 | Lọc từ ngày–đến ngày | Chỉ OUT trong khoảng (giờ VN) |
| X14 | Lọc theo vật tư / lô / mẻ | Query `material_id`, `batch_id`, `order_id` |
| X15 | Excel mở CSV | UTF-8 BOM, không lỗi font |
| X16 | PDF tiếng Việt | Font đã `register_pdf_fonts`, không mất dấu |
| X17 | Concurrent hai lệnh giữ cùng tồn | PostgreSQL row lock (đã có M3); báo cáo không đếm reservation hai lần |
| X18 | Phiếu xuất thành phẩm | Cùng pipeline OUT; ghi loại TP + Hold-Release TP |

### 3.3. Đối soát chéo (hay bị hỏi)

| Mã | Câu hỏi | Cách chứng minh |
|----|---------|-----------------|
| D01 | Tồn UI = file? | Cùng hàm `available = on_hand - reserved` |
| D02 | Tổng xuất kỳ = giảm tồn? | Sum OUT − hoàn tồn = delta vật lý (trừ nhập trong kỳ) |
| D03 | FEFO? | Sổ xuất + cột HSD lô; gợi ý UI khớp lô trên phiếu |
| D04 | Ai xuất? | `created_by` → họ tên tiếng Việt trên phiếu |
| D05 | Audit? | `ISSUE` trên nhật ký, mã PX |

---

## 4. Thiết kế báo cáo (chốt cột)

### 4.1. Tồn kho — bản snapshot (in ngay)

Cột bắt buộc:

`STT | Mã | Tên | Loại | Đơn vị | Tồn vật lý | Đang giữ chỗ | Khả dụng | HSD gần nhất | Trạng thái chất lượng (lô còn hàng) | Tồn tối thiểu | Cảnh báo`

Hai chế độ file:

- **Theo vật tư** (trang tổng): cộng dồn.
- **Theo lô** (phụ lục): mỗi `batch_no` một dòng — dùng khi hội đồng hỏi Hold-Release / FEFO.

### 4.2. Tồn kho — bản theo kỳ (BM-02/GMP01 đủ nghĩa)

`Tồn đầu kỳ | Nhập trong kỳ | Xuất trong kỳ | Hoàn tồn / điều chỉnh | Tồn cuối kỳ`

- Tồn đầu = vật lý tại 00:00 ngày `from` (replay movements hoặc snapshot; MVP: tính từ hiện tại lùi theo IN/OUT trong kỳ — **chốt thuật toán một chiều**: `cuối = đầu + nhập − xuất ± điều chỉnh`).
- Kỳ mặc định: đầu tháng → hôm nay (giờ VN).

### 4.3. Sổ xuất kho

`Số phiếu PX | Thời gian VN | Lô | Vật tư | SL (kg) | Loại (tay / mẻ SX) | Mã mẻ | Người lập | Ghi chú`

Tổng cuối trang.

### 4.4. Phiếu xuất một lần (PDF)

Header: Oxeyns Long An, BM phiếu xuất (đặt mã **BM-03/GMP01** nội bộ prototype nếu trường chưa cấp số — ghi rõ “biểu mẫu số hóa, không thay phiếu giấy pháp lý”).

Thân: số PX, ngày, lô, HSD, CCP1, quality_status, SL xuất, tồn còn lại sau xuất, mẻ SX (nếu có), người lập, chữ ký Thủ kho / QL NM (ô trống).

---

## 5. API đề xuất

| Method | Path | Việc |
|--------|------|------|
| GET | `/reports/inventory/export` | CSV snapshot; query `view=material\|batch`, `type=NVL\|…` |
| GET | `/reports/inventory/export/pdf` | PDF cùng cột snapshot |
| GET | `/reports/inventory/period` | JSON + CSV/PDF kỳ: `from`, `to` |
| GET | `/reports/issues` | JSON sổ xuất: `from`, `to`, `material_id`, `batch_id` |
| GET | `/reports/issues/export` | CSV sổ xuất |
| GET | `/reports/issues/export/pdf` | PDF sổ xuất |
| GET | `/reports/issues/{movement_id}/pdf` | PDF một phiếu PX |

Tái sử dụng `GET /stock/movements` nếu thêm filter; **không** trả 500 khi danh sách rỗng.

Quyền: JWT; `attp`/`ql_nm` xem; `thu_kho` xem + in; `lab`/`ky_thuat` xem sổ liên quan SX (không bắt buộc ẩn nếu JWT đã vào được reports hiện tại — **giữ mọi user đăng nhập được in như inventory CSV hiện nay**, trừ khi cần siết: thì chỉ `thu_kho`, `ql_nm`, `attp`, `admin`).

---

## 6. Việc UI

**`frontend/src/pages/Reports.tsx`**

- Khối 1: Tồn kho — nút CSV/PDF snapshot; chọn xem theo vật tư / theo lô; lọc loại.
- Khối 2: Tồn theo kỳ — date from/to, tải CSV/PDF.
- Khối 3: Sổ xuất kho — from/to, tải CSV/PDF.
- Khối 4: Phiếu xuất — chọn số PX (load từ `/reports/issues` hoặc movements OUT), tải PDF.
- Giữ các BM nhập / vận hành / cân bằng / lab hiện có.
- Empty state: “Chưa có phiếu xuất trong kỳ”.
- Loading/lỗi tiếng Việt (`try/catch` + `AlertBanner`).

**`frontend/src/pages/StockOut.tsx`**

- Sau khi lưu thành công: nút **In phiếu xuất** (gọi PDF vừa tạo).
- Khối lịch sử phiếu xuất gần đây (10 dòng) + in lại.

**`frontend/src/pages/Inventory.tsx`**

- Xuất CSV/PDF dùng **cùng API** với Reports (khả dụng + giữ chỗ), không gọi hàm cũ chỉ cộng `quantity`.

---

## 7. Việc triển khai (task)

**Gói đang code (bắt buộc):** Task 1 + 2 + 4. Task 3, 5, 6, 7, 8 để sau.

| Task | Phạm vi | Trạng thái |
|------|---------|------------|
| 1 | Hàm tồn chung + CSV/PDF snapshot | Xong |
| 2 | Báo cáo theo lô | Xong |
| 3 | Tồn theo kỳ | Xong |
| 4 | Sổ xuất + phiếu PX | Xong |
| 5 | Xuất nhiều lô FEFO | Cắt scope — UI ghi rõ mỗi lần một lô |
| 6 | Phiếu nhập đúng SL lúc nhập | Xong |
| 7 | Phân quyền / tiếng Việt / tên file | Xong |
| 8 | Tài liệu bảo vệ | Xong (ảnh chụp: checklist trong `testluanvan.md`) |

### Task 1: Một hàm tính tồn — nguồn sự thật

**Files:**

- Create: `backend/app/services/inventory_report.py`
- Modify: `backend/app/routers/stock.py` (inventory endpoint gọi service)
- Modify: `backend/app/services/csv_export.py`, `pdf_export.py`, `routers/reports.py`
- Test: `backend/tests/test_stock_reports.py`

**Produces:** `summarize_inventory(db) -> list[InventoryRow]` với `on_hand`, `reserved`, `available`, `low_stock` theo **available**.

- [x] Test: lô 100 kg, reservation 40 → on_hand 100, reserved 40, available 60, low_stock so 60.
- [x] Test: lô quarantine 100, reserved 0 → available 0 (không released thì không khả dụng).
- [x] CSV/PDF snapshot dùng đúng ba cột; không còn chỉ một cột “Tồn (kg)” mơ hồ.
- [x] pytest `backend/tests/test_stock_reports.py -v` xanh.

### Task 2: Báo cáo theo lô (phụ lục FEFO / Hold-Release)

**Files:** `inventory_report.py`, `csv_export.py`, `pdf_export.py`, `Reports.tsx`

- [x] Mỗi dòng: `batch_no`, HSD, CCP1, `quality_status` (nhãn Việt), on_hand, reserved, available.
- [x] Test: hai lô HSD khác nhau, sort HSD tăng dần khi `view=batch`.

### Task 3: Tồn theo kỳ (nhập / xuất / cuối)

**Files:** `inventory_report.py` hàm `period_inventory(db, start, end)`; endpoint `GET /reports/inventory/period`.

Thuật toán MVP (một chiều, dễ bảo vệ):

```
cuối_hiện_tại = on_hand hôm nay
xuất_kỳ = SUM(OUT trong [from, to])
nhập_kỳ = SUM(IN trong [from, to])
điều_chỉnh_kỳ = SUM(movement hoàn tồn trong kỳ)   # nếu đã tag
đầu_kỳ = cuối_hiện_tại - nhập_kỳ + xuất_kỳ  (± điều chỉnh cho đúng dấu)
```

Ghi chú trên file: “Tính ngược từ sổ movement; không phải snapshot kế toán đã khóa sổ.”

- [x] Test: nhập 200, xuất 10 → đầu 0, nhập 200, xuất 10, cuối 190 (trên lô released, không reservation).

### Task 4: Sổ xuất + phiếu PX PDF

**Files:**

- Create helpers in `pdf_export.py`: `issue_voucher_pdf(...)`, `issue_ledger_pdf(...)`
- Create `csv_export.py`: `issues_csv_rows(...)`
- Modify `reports.py`: 3 endpoint mục 5
- Modify `StockOut.tsx`, `Reports.tsx`, `api.ts`

- [x] Test: `POST /stock/issues` 5 kg → GET PDF 200, body chứa số PX và “5”.
- [x] Test: xuất lô chưa release → 400, không có PDF.
- [x] Test: kỳ rỗng → CSV vẫn 200, tổng 0.
- [x] UI: in ngay sau khi lưu phiếu.

### Task 5: Xuất nhiều lô FEFO một lần (nếu còn thời gian)

Hiện **một request một lô**. Hội đồng có thể hỏi xuất 120 kg khi lô HSD gần chỉ 80.

- [ ] API: `POST /stock/issues/bulk` nhận `material_id + qty` → FEFO allocations, **một transaction**, nhiều OUT cùng nhóm `reference_no` hoặc PX-xxx-01, 02.
- [ ] Thiếu tồn → rollback toàn bộ (giống reservation).
- [ ] PDF phiếu nhiều dòng lô.
- [x] Nếu cắt scope: ghi rõ hạn chế trên UI và trong khóa luận: “xuất tay từng lô; SX đã FEFO lúc duyệt mẻ.”

### Task 6: Phiếu nhập đúng SL lúc nhập

**Files:** `reports.py` `export_receipt_pdf` — lấy SL từ movement `IN` của lô, không dùng `batch.quantity` hiện tại.

- [x] Test: nhập 200, xuất 10, in phiếu nhập vẫn 200 kg.

### Task 7: Phân quyền, lỗi, tiếng Việt, giờ VN

- [x] `detail` lỗi tiếng Việt.
- [x] Thời gian `to_vn_display`.
- [x] CSV BOM UTF-8.
- [x] Tên file: `ton-kho-YYYYMMDD.csv`, `so-xuat-kho-YYYYMMDD.pdf`, `PX-….pdf`.

### Task 8: Tài liệu bảo vệ

- [x] Cập nhật `docs/user-manual.md` mục Báo cáo.
- [x] Thêm checklist vào `testluanvan.md`: in tồn, in PX, đối chiếu số.
- [x] 4 screenshot: checklist chụp lúc demo trong `testluanvan.md` (tồn UI vs PDF; phiếu PX; sổ xuất kỳ; tồn thấp khả dụng).

---

## 8. Thứ tự làm (để kịp hỏi đáp)

1. Task 1 + 2 — **bắt buộc** (số không mâu thuẫn UI).  
2. Task 4 — **bắt buộc** (thiếu phiếu xuất trên trang Báo cáo).  
3. Task 6 — nên làm (phiếu nhập sai sau khi xuất).  
4. Task 3 — nên làm (đúng tên BM-02/GMP01).  
5. Task 5 — tùy thời gian.  
6. Task 7–8 — trước demo.

---

## 9. Gợi ý trả lời hội đồng

**“Báo cáo lấy số ở đâu?”**  
Cùng ledger lô và phiếu `stock_movements`, không nhập tay trên Excel.

**“Tồn trên file khác màn hình?”**  
Trước đây CSV chỉ cộng tồn vật lý. Sau Task 1 in đủ vật lý / giữ chỗ / khả dụng như `/inventory`.

**“Xuất kho in ở đâu?”**  
Trước: chỉ PDF nhập + tồn. Sau Task 4: sổ xuất + phiếu PX; Xuất kho có nút in sau khi lưu.

**“Hold-Release ảnh hưởng báo cáo thế nào?”**  
Lô cách ly vẫn có tồn vật lý, khả dụng 0, không có trên sổ xuất hợp lệ.

**“Đây có phải báo cáo kế toán?”**  
Không. Đây là hồ sơ vận hành / GMP số hóa cho nhà máy tinh dầu, phục vụ thẩm tra CCP và truy xuất lô.

---

## 10. Phạm vi không làm

- ERP tài chính, hóa đơn VAT, giá vốn.
- Kết nối cân / máy in tem công nghiệp.
- Khóa sổ kế toán bất biến (glitch).
- Chữ ký số pháp lý.
- App mobile native.

---

Kế hoạch đã lưu tại `baocaoxuatkho.md`. Có thể triển khai từng task trong file này, hoặc làm gói bắt buộc trước: **Task 1 + 2 + 4**.

**Xem trước phiếu:** Có. Trang Báo cáo và Xuất kho có nút **Xem trước** — mở PDF trong hộp thoại, kiểm tra số rồi mới **Tải xuống**.