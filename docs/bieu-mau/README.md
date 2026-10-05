# Thư mục biểu mẫu BM-xx/GMPxx

Thư mục mô tả **cấu trúc số hóa** các biểu mẫu GMP đang dùng tại Oxeyns Long An, phục vụ thiết kế form trong hệ thống web và báo cáo TTTN.

---

## Trạng thái tài liệu

| Loại | Trạng thái |
|------|------------|
| Mô tả cấu trúc form (markdown) | ✅ Trong repo |
| Scan PDF/ảnh bản giấy gốc | ⬜ Chưa có — thay bằng mô tả synthesized từ Sổ tay ATTP |
| Export PDF từ hệ thống | 🟡 MVP — CSV/API; PDF theo `backend/app/services/pdf_export.py` (kế hoạch) |

> **Lưu ý:** Nội dung field dưới đây tổng hợp từ `chuongtrinhthamtra.txt` và quy trình nội bộ — **không thay thế bản BM-xx có kiểm soát tài liệu (QT-KSTL)** tại công ty.

---

## Danh mục biểu mẫu trong phạm vi MVP

| Mã | Tên | File mô tả | Module hệ thống |
|----|-----|------------|-----------------|
| BM-01/GMP01 | Phiếu nhập nguyên liệu | [BM-01-GMP01.md](./BM-01-GMP01.md) | Nhập kho, CCP1 |
| BM-02/GMP01 | Báo cáo tồn kho tháng | [BM-02-GMP01.md](./BM-02-GMP01.md) | Báo cáo / Tồn kho |
| BM-01/GMP03 | Operation Record | [BM-01-GMP03.md](./BM-01-GMP03.md) | Sản xuất, CCP2 |
| BM-01/GMP04 | Material Balance | [BM-01-GMP04.md](./BM-01-GMP04.md) | Sản xuất |
| BM-01/GMP05 | Mixing Report | [BM-01-GMP05.md](./BM-01-GMP05.md) | Sản xuất (giai đoạn 2) |
| BM-02/GMP05 | GC Data | [BM-02-GMP05.md](./BM-02-GMP05.md) | Lab |

---

## Nguyên tắc số hóa

1. **Giữ tên trường nghiệp vụ** gần với bản giấy để ATTP dễ đối chiếu khi thẩm tra.
2. **Mã lô (batch)** bắt buộc trên mọi phiếu liên quan truy xuất.
3. Trường CCP có **validation tự động** và trạng thái pass/fail/pending.
4. Mọi thao tác create/update ghi **audit log**.
5. PDF export dùng cùng layout logic với form web (template sau).

---

## Cấu trúc thư mục đề xuất (khi có scan)

```text
docs/bieu-mau/
├── README.md
├── BM-01-GMP01.md
├── ...
└── scans/              ← ảnh/PDF bản gốc (khi thu thập tại NM)
    ├── BM-01-GMP01.pdf
    └── ...
```

---

## Liên kết

- Map FR ↔ BM: `docs/requirements.md`
- Phỏng vấn synthesized: `docs/phong-van/`
- API: `docs/api-spec.md`
