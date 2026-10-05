# BM-01/GMP05 — Mixing Report / Báo cáo phối trộn (số hóa)

**Công đoạn GMP7:** Phối trộn, đóng phuy, dán nhãn, bảo quản

---

## Phạm vi MVP

Mô tả cấu trúc form — **UI nhập đầy đủ thuộc giai đoạn mở rộng** sau operation record & CCP2.

---

## Header

| Trường | Kiểu |
|--------|------|
| Mã mẻ SX | lookup |
| Mã lô TP sau phối trộn | text |
| Ngày phối trộn | date |
| Thời gian khuấy + Nito | duration | ~2h theo HACCP |

---

## Thành phần phối trộn

| Cột | Mô tả |
|-----|--------|
| Mã thành phần | TP thô, phụ gia (Benzaldehyde, Coumarin…) |
| Mã lô | |
| KL/SL theo công thức | |
| KL/SL thực tế | |
| Đơn vị | |

---

## Kiểm tra độ đồng nhất

| Trường | Kiểu |
|--------|------|
| Phương pháp | text |
| Kết quả | pass/fail |
| Người kiểm | lab / ky_thuat |

---

## Đóng gói

| Trường | Mô tả |
|--------|--------|
| Loại bao bì | Phuy 200 kg / theo KH |
| Số phuy | |
| Bơm Nito | 10 bar / 2 phút |
| Nhãn / mã lô in trên phuy | |

---

## Liên kết

- Sau phối trộn → nhập kho TP → truy xuất lô TP
- GC cuối (nếu có) → BM-02/GMP05
