# Chương 7 — Kết luận và hướng phát triển

---

## 7.1. Kết luận chung

Đề tài đã **phân tích hiện trạng** quản lý kho và sản xuất tinh dầu tại Công ty TNHH Oxeyns – Chi nhánh Long An, xác định các vấn đề trọng tâm: dữ liệu phân tán, khó truy xuất lô, thiếu cảnh báo CCP tự động, và báo cáo tốn thời gian.

Trên cơ sở ma trận vấn đề và yêu cầu FR/NFR, đề tài **đề xuất hệ thống web 4 module** (Kho – Sản xuất – Lab/CCP – Báo cáo & ATTP) với kiến trúc FastAPI + React + PostgreSQL, phù hợp quy mô doanh nghiệp nhỏ và yêu cầu FSSC/HACCP.

**Prototype MVP** đã chứng minh khả thi luồng E2E: nhập lô NVL → CCP1 → xuất → mẻ SX → CCP2 → truy xuất lô TP, với UAT 100% pass trên phạm vi demo.

---

## 7.2. Kết luận theo mục tiêu

| Mục tiêu | Kết quả |
|----------|---------|
| Mô tả quy trình SX & luồng NVL/TP | Đạt — Chương 3, tài liệu HACCP |
| Khảo sát ghi chép & CNTT | Đạt (synthesized) — cần bổ sung phỏng vấn trực tiếp |
| Xác định điểm nghẽn | Đạt — ma trận P01–P12 |
| Đề xuất giải pháp & lộ trình | Đạt — Chương 5 |
| Hỗ trợ triển khai/demo | Đạt — UAT, manual, validation draft |

---

## 7.3. Ý nghĩa thực tiễn

- Gợi ý mô hình số hóa BM-xx cho DN SX hương liệu quy mô nhỏ
- Cách tiếp cận **validation phần mềm CCP** (FSSC 8.7) ở mức prototype
- Quy trình phối hợp **sinh viên IT – dev chính – nghiệp vụ** trong TTTN

---

## 7.4. Hạn chế của đề tài

- Phỏng vấn và một số giả định CNTT chưa xác nhận trực tiếp tại nhà máy
- Prototype chưa thay thế hoàn toàn biểu mẫu giấy và Excel
- Chưa triển khai production; chưa tích hợp GC/máy đo tự động
- Sản phẩm khác ngoài t-CA chưa khảo sát sâu

---

## 7.5. Hướng phát triển

### Ngắn hạn (3–6 tháng)

1. Hoàn thiện export **PDF** đúng template BM-xx
2. UI **material balance** và mixing report
3. **Sign-off UAT** nghiệp vụ có chữ ký
4. Thu thập scan biểu mẫu gốc vào `docs/bieu-mau/scans/`
5. Triển khai **staging** nội bộ 24/7

### Trung hạn (6–12 tháng)

1. Validation phần mềm **đầy đủ** (IQ/OQ/PQ) cho go-live CCP
2. FIFO/FEFO xuất kho; workflow duyệt lệnh SX
3. Import CSV từ máy GC
4. Mở rộng master data cho tinh dầu sả, cam, bạc hà…

### Dài hạn

1. Module **TT-TVTH** thu hồi/triệu hồi
2. Tích hợp kế toán / mua hàng
3. Mobile cho Thủ kho quét mã lô (barcode/QR)

---

## 7.6. Kiến nghị

**Đối với Oxeyns:**

- Duy trì song song giấy và hệ thống trong giai đoạn pilot
- Chỉ định owner nghiệp vụ (Thủ kho + ATTP) cho change control phần mềm
- Backup DB định kỳ theo `docs/backup-rollback.md`

**Đối với nhà trường:**

- Khuyến khích TTTN kết hợp **deliverable tài liệu + demo** cho DN SME

---

## 7.7. Lời cảm ơn (mẫu)

Em xin chân thành cảm ơn Công ty TNHH Oxeyns – Chi nhánh Long An, quý thầy cô và người hướng dẫn tại doanh nghiệp đã tạo điều kiện thực tập và cung cấp tài liệu ATTP, HACCP phục vụ đề tài.

---

*Báo cáo hoàn chỉnh kèm phụ lục: `docs/phu-luc.md`*
