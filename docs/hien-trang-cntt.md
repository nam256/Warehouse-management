# Hiện trạng CNTT (as-is)

> Tổng hợp synthesized từ tài liệu nội bộ Oxeyns + giả định khảo sát — **xác nhận lại tại công ty** khi có phỏng vấn trực tiếp.

---

## Hệ thống hiện có

- Quản lý chất lượng: **giấy + Excel + tài liệu QT-xx, BM-xx/GMPxx**
- Chưa có **ERP/MES** tích hợp kho – SX – Lab trên một nền tảng
- FSSC 22000 yêu cầu truy xuất lô, audit trail, kiểm soát tài liệu (QT-KSTL)
- Thiết bị đo (nhiệt độ, áp suất) quản lý theo QT-KSTB — ghi số liệu thủ công lên operation record

---

## Danh sách phần mềm & công cụ (synthesized)

| STT | Phần mềm / công cụ | Mục đích sử dụng | Bộ phận sử dụng | Lưu trữ / Ghi chú |
|-----|-------------------|-----------------|-----------------|-------------------|
| 1 | **Microsoft Excel** | Báo cáo tồn kho tuần/tháng; tổng hợp NVL | Thủ kho, QL NM | PC Thủ kho — file local, backup USB |
| 2 | **Google Sheets** | Bản sao tồn kho chia sẻ QL NM / Kỹ thuật | QL NM, Kỹ thuật | Google Drive tài khoản công ty |
| 3 | **Microsoft Word / PDF** | In BM-xx, quy trình QT-xx, biên bản thẩm tra | ATTP, QL NM | Tủ tài liệu + PC ATTP |
| 4 | **Email (Outlook/Gmail)** | Trao đổi kết quả Lab, COA, đặt hàng NCC | Lab, Thủ kho, QL NM | Hộp thư cá nhân/phòng ban |
| 5 | **Zalo / điện thoại** | Trao đổi nhanh tiến độ mẻ, CCP pass/fail | Toàn NM | Không lưu tập trung |
| 6 | **Máy GC (Gas Chromatography)** | Phân tích % t-CA, thành phần | Lab / lab thuê ngoài | Xuất **file dữ liệu / PDF báo cáo** — nhập tay vào BM-02/GMP05 |
| 7 | **Lab bên ngoài (C14)** | Phân tích đồng vị C14 cho CCP1 | Thủ kho gửi mẫu | COA PDF/email — không tích hợp API |
| 8 | **Phần mềm kế toán** | *(Chưa xác nhận tên)* — hóa đơn, công nợ NCC | Kế toán (HO) | Tách biệt kho SX — **không sync tồn realtime** |
| 9 | **Windows Explorer / USB** | Lưu file GC, scan COA | Lab | Folder PC — backup thủ công |
| 10 | **Oxeyns Kho & SX (prototype)** | Demo TTTN — kho, SX, CCP, truy xuất | IT / demo | Local/Docker — **chưa production** |

---

## Ai nhập liệu, lưu ở đâu, tần suất

| Bộ phận | Dữ liệu | Công cụ | Tần suất | Nơi lưu |
|---------|---------|---------|----------|---------|
| Thủ kho | Phiếu nhập, xuất, tồn | Giấy BM-01/GMP01 + Excel | Mỗi lô nhập; tồn **hàng tuần** | PC kho + tủ hồ sơ |
| Kỹ thuật | Operation record, T/P | Giấy BM-01/GMP03 | Mỗi mẻ (32–37h) | Sổ xưởng → lưu file |
| Kỹ thuật | Material balance | BM-01/GMP04 | Cuối mẻ | Excel/giấy |
| Lab | GC data, C14 | BM-02/GMP05, file GC | Mỗi lô/mẫu | PC Lab |
| QL NM | Tồn tổng hợp | Excel/Sheets | Tuần + tháng (BM-02/GMP01) | Drive / email |
| ATTP | Thẩm tra CCP | Biên bản giấy | **14 ngày/lần** | Hồ sơ ATTP |

---

## Luồng dữ liệu hiện tại (tóm tắt)

```text
NCC → [Giấy phiếu giao hàng] → Thủ kho → BM-01/GMP01
                                      ↓
                               Gửi mẫu → Lab ngoài (C14) → Email COA → Thủ kho/ATTP
                                      ↓
                               Excel tồn ←── copy thủ công ──→ Google Sheets (QL NM)
                                      ↓
Kỹ thuật ← xuất NVL (giấy) ← Kho
     ↓
BM-01/GMP03 (T, P) + Lab GC (% t-CA) — ghép thủ công khi thẩm tra
```

Chi tiết sơ đồ: `docs/process-as-is.md`, `docs/data-flow.md`

---

## Hạn chế

- Dữ liệu **phân tán** giữa phòng ban — không single source of truth
- **Khó tra cứu batch** NVL → mẻ SX → TP theo yêu cầu FSSC/HACCP/TT-TVTH
- CCP **chưa có cảnh báo tự động** — phụ thuộc người đọc kết quả Lab
- **Không audit trail** tập trung trên phần mềm nghiệp vụ
- Tích hợp kế toán – kho – SX **không realtime**
- Rủi ro mất file Excel/local PC (backup không đồng bộ)

---

## Hướng cải tiến (to-be)

- Web app tích hợp 4 module — xem `docs/process-to-be.md`
- Giữ Excel/giấy song song trong giai đoạn pilot
- Backup DB khi triển khai staging — `docs/backup-rollback.md`

---

*Cập nhật lần cuối: 20/06/2026 — bổ sung mục danh sách phần mềm (synthesized).*
