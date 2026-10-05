# Chương 1 — Giới thiệu

> Dàn ý chi tiết cho báo cáo TTTN — nội dung tổng hợp từ `detai.txt`.

---

## 1.1. Lý do chọn đề tài

- Oxeyns Long An sản xuất tinh dầu và hương liệu thiên nhiên (t-CA từ dầu quế) trong bối cảnh yêu cầu **FSSC 22000**, **HACCP**, **Kosher**
- Quy mô nhỏ (~6 nhân sự) nhưng quy trình ghi chép phức tạp: kho – sản xuất – lab – ATTP
- Cơ hội ứng dụng kiến thức CNTT vào **số hóa biểu mẫu**, **truy xuất lô**, **giám sát CCP**
- Phù hợp vai trò sinh viên **hỗ trợ IT**: phân tích, đề xuất, UAT — không đơn thuần lập trình

---

## 1.2. Mục tiêu nghiên cứu

### Mục tiêu chung

Phân tích hiện trạng quản lý kho và sản xuất tinh dầu tại Oxeyns; đề xuất hướng xây dựng hệ thống quản lý tích hợp.

### Mục tiêu cụ thể

1. Mô tả quy trình SX t-CA và luồng NVL/TP
2. Khảo sát cách ghi chép, biểu mẫu BM-xx, hiện trạng CNTT
3. Xác định điểm nghẽn, rủi ro, nhu cầu số hóa
4. Đề xuất mô hình/chức năng và lộ trình triển khai
5. Hỗ trợ dev: spec, test, tài liệu; demo prototype nếu có

---

## 1.3. Phạm vi nghiên cứu

| Trong phạm vi | Ngoài phạm vi |
|---------------|---------------|
| SX t-CA, 4 module MVP | ERP toàn công ty |
| Prototype demo FastAPI+React | Go-live production đầy đủ |
| CCP1, CCP2 | Toàn bộ GMP1–7 chi tiết |
| Truy xuất lô cơ bản | TT-TVTH thu hồi đầy đủ |

Chi tiết: `docs/pham-vi-xac-nhan.md`

---

## 1.4. Phương pháp nghiên cứu

- **Khảo sát tài liệu:** Sổ tay ATTP, HACCP, quy trình SX
- **Phỏng vấn** (tổng hợp synthesized): Thủ kho, KT, Lab, QL NM, ATTP — `docs/phong-van/`
- **Phân tích:** as-is/to-be, ma trận vấn đề, yêu cầu FR/NFR
- **Thiết kế:** ERD, API, wireframe
- **Thực nghiệm:** Prototype + UAT — `docs/uat-results.md`

---

## 1.5. Ý nghĩa khoa học và thực tiễn

- Ứng dụng MIS/ERP quy mô SME vào SX thực phẩm/hương liệu
- Liên kết CNTT với yêu cầu **FSSC 8.7** (xác nhận phần mềm)
- Giải pháp tham khảo cho DN nhỏ cùng ngành

---

## 1.6. Cấu trúc báo cáo

- Chương 2: Cơ sở lý thuyết
- Chương 3: Khảo sát thực trạng
- Chương 4: Phân tích vấn đề
- Chương 5: Đề xuất giải pháp
- Chương 6: Kết quả thực hiện
- Chương 7: Kết luận & hướng phát triển

---

## 1.7. Tài liệu tham khảo (gợi ý)

- FSSC 22000, Codex HACCP
- Tài liệu nội bộ Oxeyns (attp, HACCP, quy trình SX)
- Tài liệu FastAPI, React (kỹ thuật prototype)
