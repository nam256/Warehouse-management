# Tóm tắt phỏng vấn — Đội ATTP / FSSC

> **Nguồn:** Tổng hợp synthesized từ `chuongtrinhthamtra.txt`, `attp.txt`, `detai.txt`.  
> **Không phải biên bản phỏng vấn trực tiếp.**

---

## Thông tin buổi phỏng vấn (mô phỏng)

| Mục | Nội dung |
|-----|----------|
| Đối tượng | Đội trưởng/phó HACCP, nhân sự ATTP |
| Thời lượng | ~55 phút |
| Mục tiêu | CCP, thẩm tra, biểu mẫu, yêu cầu phần mềm (FSSC 8.7) |

---

## 1. Khung ATTP tại Oxeyns

- Tiêu chuẩn: **FSSC 22000**, HACCP Codex, Kosher
- Tài liệu: Sổ tay ATTP, QT-xx, SSOP, **BM-xx/GMPxx**
- **Thẩm tra CCP:** 14 ngày/lần — xem hồ sơ + đối chiếu thực tế
- **Thẩm tra nội bộ HACCP:** hàng năm hoặc khi thay đổi dây chuyền / khiếu nại

---

## 2. Hai CCP trọng yếu

### CCP1 — Tiếp nhận nguyên liệu

- **Giới hạn:** C14 = 13.02–14.39 dpm/gC
- **Hồ sơ:** BM-01/GMP01, BM-02/GMP01
- **Corrective action:** cô lập, báo cáo, khiếu nại NCC, trả hàng

### CCP2 — Chưng cất

- **Giới hạn:** Ttop 107–110°C; % t-CA > 99%
- **Hồ sơ:** BM-01/GMP03 (operation record), GC (BM-02/GMP05)
- **Corrective action:** nhận diện, lấy mẫu khảo sát, điều chỉnh vận hành

---

## 3. Pain point về ghi chép & CNTT

1. Hồ sơ **phân tán** giữa Kho, KT, Lab — thẩm tra mất thời gian ghép chứng từ
2. **Không có cảnh báo tự động** khi vượt giới hạn tới hạn
3. Audit trail thủ công — khó chứng minh **ai sửa gì khi nào**
4. Phần mềm mới (nếu dùng giám sát CCP) phải có **xác nhận phần mềm** theo **FSSC Chương VIII — mục 8.7**

---

## 4. Yêu cầu đối với hệ thống đề xuất

| Yêu cầu | Mô tả |
|---------|--------|
| Số hóa BM-xx | Giữ cấu trúc trường tương đương biểu mẫu giấy |
| Rule CCP | Hard validation C14, Ttop, % t-CA; trạng thái pass/fail/pending |
| Chặn release | Không xuất NVL fail CCP1; không hoàn thành mẻ fail CCP2 |
| Audit log | User, timestamp, action, old/new value — **không cho sửa/xóa log** |
| Tra cứu thẩm tra | Lọc CCP theo kỳ 14 ngày; export biên bản (kế hoạch) |
| Xác nhận phần mềm | Tài liệu `docs/software-validation.md` — phạm vi prototype |

---

## 5. Phân quyền role `attp`

- Xem toàn bộ module Kho, SX, Lab, CCP, Audit
- Không nhập phiếu kho hàng ngày (tránh xung đột segregation of duties)
- Export báo cáo phục vụ thẩm tra và chứng nhận

---

## 6. Biểu mẫu ưu tiên số hóa (theo ATTP)

1. BM-01/GMP01 — nhập NVL + CCP1  
2. BM-01/GMP03 — operation record + CCP2  
3. BM-02/GMP05 — GC data  
4. BM-02/GMP01 — monthly inventory  
5. BM-01/GMP04, BM-01/GMP05 — giai đoạn 2  

---

## 7. Trích dẫn (paraphrase synthesized)

> “Thẩm tra 14 ngày một lần, anh cần thấy **đủ chuỗi** từ phiếu nhập quế đến GC t-CA cùng một mẻ. Phần mềm nếu dùng chính thức phải có hồ sơ validation — prototype demo thì ghi rõ phạm vi trong báo cáo sinh viên.”

---

*Tham chiếu chi tiết validation: `docs/software-validation.md`.*
