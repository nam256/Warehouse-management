# Khảo sát (bootstrap + phỏng vấn synthesized)

> **Trạng thái:** Tóm tắt từ Sổ tay ATTP, HACCP, quy trình SX + **`docs/phong-van/`** (synthesized).  
> Cần bổ sung biên bản phỏng vấn trực tiếp khi có buổi tại nhà máy.

## Quy trình sản xuất (t-CA)

1. Tiếp nhận dầu quế → 2. Bảo quản → 3. Chưng cất chân không → 4. Chiết rót, bơm Nito → 5. Phối trộn → 6. Đóng can, dán nhãn

## Luồng dữ liệu hiện tại (giả định)

| Bộ phận | Ghi chép | Tần suất |
|---------|----------|----------|
| Thủ kho | BM-01/GMP01, BM-02/GMP01 | Mỗi lô nhập, báo cáo tuần |
| Kỹ thuật | BM-01/GMP03, BM-01/GMP04 | Mỗi mẻ SX |
| Lab | BM-02/GMP05, GC | Theo mẫu |
| ATTP | Thẩm tra CCP 14 ngày/lần | Định kỳ |

## CCP

- **CCP1:** C14 = 13.02–14.39 dpm/gC (mỗi lô NVL)
- **CCP2:** Ttop 107–110°C, % t-CA > 99% (mỗi mẻ chưng cất)

## Tài liệu phỏng vấn (synthesized)

- [x] Thủ kho — `docs/phong-van/thu-kho.md`
- [x] Kỹ thuật — `docs/phong-van/ky-thuat.md`
- [x] Lab — `docs/phong-van/lab.md`
- [x] QL NM — `docs/phong-van/ql-nm.md`
- [x] ATTP — `docs/phong-van/attp.md`

## Câu hỏi cần xác nhận trực tiếp (TODO)

- [ ] Tên phần mềm kế toán cụ thể tại Oxeyns?
- [ ] Xác nhận pain point #1 với Thủ kho/QL NM?
- [ ] Có yêu cầu bắt buộc duyệt phiếu nhập/xuất không?
