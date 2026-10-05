# BM-01/GMP04 — Material Balance / Cân đối vật tư (số hóa)

**Mục đích:** Đối chiếu đầu vào – đầu ra – hao hụt theo từng mẻ sản xuất t-CA.

---

## Header

| Trường | Kiểu |
|--------|------|
| Mã mẻ SX | lookup |
| Sản phẩm | readonly |
| Kỳ / ngày chốt | date |

---

## Đầu vào (từ Module Kho)

| Cột | Nguồn |
|-----|--------|
| Mã NVL | |
| Tên NVL | |
| Mã lô NVL | Phiếu xuất kho link PO |
| SL xuất kho | Auto từ stock movement |
| Đơn vị | |

> MVP: tự động lấy từ `ProductionMaterialUsage` + phiếu xuất; báo cáo UI giai đoạn 2.

---

## Đầu ra

| Cột | Mô tả |
|-----|--------|
| Loại | TP / BTP / Phế liệu |
| Mã lô TP/BTP | |
| SL thu được | |
| Đơn vị | |

---

## Cân đối

| Trường | Công thức |
|--------|-----------|
| Tổng đầu vào | Sum NVL |
| Tổng đầu ra | Sum TP + BTP + phế |
| Hao hụt | Đầu vào − Đầu ra |
| % hao hụt | Hao hụt / Đầu vào × 100 |
| Ngưỡng cảnh báo | Cấu hình theo QT nội bộ (optional) |

---

## Ghi chú nghiệp vụ

- Mẻ chưng cất 32–37h thường có hao hụt do cặn, BTP tái chưng
- Nhánh BTP → chưng cất lại ghi trên dòng riêng hoặc mẻ con (mở rộng)

---

## Mapping

- `GET /production/orders/{id}/material-balance` (draft API)
- Liên kết FR-008, `docs/requirements.md`
