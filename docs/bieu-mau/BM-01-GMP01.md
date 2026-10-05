# BM-01/GMP01 — Phiếu nhập nguyên liệu (số hóa)

**Công đoạn GMP1:** Tiếp nhận nguyên liệu | **CCP1:** Kiểm soát nguyên liệu đầu vào

---

## Mục đích

Ghi nhận mỗi lô nguyên liệu nhập kho: số lượng, chất lượng sơ bộ, mã lô NCC, kết quả C14 (CCP1).

---

## Header

| Trường | Kiểu | Bắt buộc | Ghi chú |
|--------|------|----------|---------|
| Số phiếu | text (auto) | ✓ | PN-YYYYMMDD-SEQ |
| Ngày nhập | date | ✓ | |
| Nhà cung cấp | lookup | ✓ | Master NCC |
| Mã NVL | lookup | ✓ | VD: NL-QUE-001 |
| Tên NVL | text (readonly) | ✓ | Tinh dầu quế |
| Mã lô NCC | text | ✓ | Batch supplier |
| Mã lô nội bộ | text (auto) | ✓ | LOT-YYYYMMDD-xxx |

---

## Chi tiết nhập

| Trường | Kiểu | Bắt buộc |
|--------|------|----------|
| Số lượng (SL) | decimal | ✓ |
| Khối lượng (KL) | decimal | ✓ |
| Đơn vị | enum | ✓ | kg, L, phuy |
| Kho / vị trí | lookup | ✓ | KHO-NVL |
| Số hóa đơn / COA NCC | text | | |

---

## Kiểm tra sơ bộ (GMP)

| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| Màu sắc | select | Đạt / Không đạt |
| Mùi | select | Đạt / Không đạt |
| Tỷ trọng | decimal | |
| Chỉ số khúc xạ | decimal | |
| Độ triền quang | text | |
| Ghi chú kiểm tra | textarea | |

---

## CCP1 — C14

| Trường | Kiểu | Rule |
|--------|------|------|
| C14 (dpm/gC) | decimal | 13.02 ≤ C14 ≤ 14.39 → pass |
| Trạng thái CCP1 | enum | pending / pass / fail |
| Số báo cáo Lab | text | Lab ngoài |
| Ngày có kết quả | date | |
| Hành động sửa chữa | textarea | Bắt buộc nếu fail |

**Business rule:** Lô `fail` → cô lập, không cho xuất SX.

---

## Chữ ký / phê duyệt (form giấy → digital)

| Trường | Role |
|--------|------|
| Người lập phiếu | thu_kho |
| Người kiểm tra | attp / ql_nm (optional) |
| Thời gian tạo/sửa | audit log |

---

## Mapping API (prototype)

- `POST /stock/in` — tạo phiếu nhập + batch
- `PATCH /quality/ccp1/{batch_id}` — cập nhật C14 từ Lab

---

## Export

- PDF/Excel layout theo BM gốc — MVP: CSV + màn hình in trình duyệt
