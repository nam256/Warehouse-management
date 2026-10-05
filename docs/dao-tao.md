# Đào tạo sử dụng hệ thống — 45 phút

**Đối tượng:** Thủ kho + Phòng Kỹ thuật (có thể mở rộng Lab/ATTP buổi 2)  
**Thời lượng:** 45 phút  
**Người đào tạo:** Sinh viên hỗ trợ IT  
**Tài liệu kèm:** `docs/user-manual.md`

---

## Mục tiêu buổi đào tạo

Sau 45 phút, học viên có thể:

1. Đăng nhập và điều hướng menu theo role
2. Thủ kho: tạo phiếu nhập NVL và hiểu trạng thái CCP1 pending
3. Kỹ thuật: tạo mẻ SX, ghi operation record, hiểu CCP2
4. Biết liên hệ ai khi CCP fail hoặc lỗi hệ thống

---

## Chuẩn bị

| Hạng mục | Chi tiết |
|----------|----------|
| Máy chiếu + laptop demo | URL hệ thống staging/local |
| Tài khoản | thu_kho, ky_thuat (in sẵn) |
| Phiếu hands-on | 1 kịch bản E2E rút gọn (dưới đây) |
| Phòng | Phòng họp NM hoặc văn phòng kho |

---

## Lịch trình chi tiết

### 0–5 phút — Mở đầu

- Giới thiệu mục đích: **prototype** hỗ trợ kho–SX–CCP, chưa thay giấy hoàn toàn
- Phạm vi: t-CA, 4 module chính
- Quy tắc: mọi thao tác có audit log; CCP fail phải báo ATTP

### 5–10 phút — Tổng quan & đăng nhập

- Sơ đồ to-be (1 slide): Kho → SX → Lab → Báo cáo
- Demo đăng nhập, sidebar, dashboard
- Giải thích role: ai làm gì

**Thảo luận nhanh:** “Pain point lớn nhất hiện tại là gì?” (1–2 ý)

### 10–20 phút — Module Kho (Thủ kho)

**Trình chiếu + live demo**

1. Nhập kho BM-01/GMP01 digital
2. Giải thích mã lô nội bộ vs lô NCC
3. CCP1 pending — chờ Lab
4. Xem tồn kho, cảnh báo tồn thấp → YCMH (giới thiệu ngắn)

**Hands-on Thủ kho (5 phút):** Mỗi người tạo 1 phiếu nhập demo (SL nhỏ)

### 20–32 phút — Module Sản xuất (Kỹ thuật)

1. Tạo mẻ SX t-CA
2. Xuất NVL cho mẻ (link lô đã CCP1 pass — trainer seed sẵn)
3. Ghi operation: T, P, **Ttop 107–110**
4. Giải thích: Lab nhập % t-CA → mới hoàn thành mẻ

**Hands-on Kỹ thuật (5 phút):** Ghi 1 bước operation trên mẻ demo

### 32–40 phút — Lab, CCP, Truy xuất (overview)

- Lab nhập GC (trainer demo) — C14 / % t-CA
- CCP fail → chặn xuất / không đóng mẻ
- Truy xuất lô 2 chiều — giá trị cho QL NM & ATTP
- Giới thiệu màn Audit (ATTP xem sau)

### 40–45 phút — Q&A & bước tiếp theo

- Thu feedback 3 câu:
  1. Màn hình nào cần đơn giản thêm?
  2. Thiếu trường nào so với BM giấy?
  3. Sẵn sàng UAT 1 tuần demo không?
- Phát `user-manual.md` (PDF/in)
- Lịch UAT / liên hệ IT

---

## Kịch bản hands-on (in cho học viên)

```text
Bước 1: Login thu_kho → Nhập 100 kg dầu quế, lô NCC TRAIN-001
Bước 2: (Trainer) Lab pass C14
Bước 3: Login ky_thuat → Tạo mẻ TRAIN-PO-01
Bước 4: Xuất 80 kg lô TRAIN-001 cho mẻ
Bước 5: Ghi operation Ttop = 109°C
Bước 6: (Trainer) Lab pass % t-CA → Hoàn thành mẻ
Bước 7: Truy xuất lô TP vừa tạo
```

---

## Buổi 2 (optional — 30 phút) — Lab + ATTP

- Nhập GC chi tiết
- Màn CCP / HACCP — chu kỳ 14 ngày
- Audit log phục vụ thẩm tra
- Export báo cáo CSV

---

## Đánh giá sau đào tạo

| Tiêu chí | Cách đo |
|----------|---------|
| Thủ kho tự nhập phiếu | Quan sát hands-on |
| KT tự ghi 1 operation | Quan sát hands-on |
| Hiểu CCP pending/fail | 2 câu hỏi miệng cuối buổi |

---

*Slide: `docs/demo-slides.md` | Video: `docs/demo-video-script.md`*
