# Slide demo báo cáo TTTN

> Nội dung 12–15 slide — trình bày 15–20 phút + Q&A. Copy vào PowerPoint/Google Slides.

---

## Slide 1 — Tiêu đề

**Phân tích và đề xuất hệ thống quản lý sản xuất và kho tinh dầu**

- Sinh viên: [Họ tên] — MSSV
- Công ty: Oxeyns Long An
- GV hướng dẫn: [Họ tên]
- Ngày: 2026

---

## Slide 2 — Bối cảnh

- SX hương liệu thiên nhiên: t-CA từ dầu quế
- Quy mô ~6 NS, FSSC 22000 / HACCP / Kosher
- Ghi chép: giấy BM-xx + Excel phân tán
- Vai trò SV: **hỗ trợ IT** — khảo sát, spec, UAT, tài liệu

---

## Slide 3 — Mục tiêu đề tài

1. Mô tả quy trình & hiện trạng CNTT
2. Phân tích vấn đề (kho, SX, Lab, ATTP)
3. Đề xuất hệ thống 4 module + prototype demo
4. UAT & hướng triển khai

---

## Slide 4 — Quy trình sản xuất t-CA

```text
Nhập dầu quế → Bảo quản → Chưng cất (32–37h)
→ Chiết rót/Nito → Phối trộn → Đóng phuy
```

- CCP1: C14 khi nhập NVL
- CCP2: Ttop 107–110°C, % t-CA > 99%

---

## Slide 5 — Hiện trạng (As-Is)

- Không ERP/MES tích hợp
- Pain point: tồn thủ công, truy xuất lô khó, CCP không cảnh báo
- Sơ đồ: `docs/process-as-is.md`

---

## Slide 6 — Ma trận vấn đề

| Impact cao | P01 Tồn thủ công, P02 Truy xuất, P06 CCP |
| Quick win | Số hóa kho + rule CCP |

*(Biểu đồ impact×effort — `docs/problem-matrix.md`)*

---

## Slide 7 — Giải pháp đề xuất (To-Be)

**4 module:** Kho → Sản xuất → Lab/CCP → Báo cáo & ATTP

- Web app: FastAPI + React + PostgreSQL
- Batch traceability, audit log, RBAC

---

## Slide 8 — Kiến trúc hệ thống

```text
React UI → REST API (FastAPI) → PostgreSQL
         ↘ Audit / CCP rules
```

Chi tiết: README, `docs/data-flow.md`

---

## Slide 9 — Demo: Nhập kho & CCP1

- Screenshot: form BM-01/GMP01
- Lô pending → Lab C14 pass/fail
- Chặn xuất nếu fail

---

## Slide 10 — Demo: Sản xuất & CCP2

- Production order + operation record
- Ttop + % t-CA
- Hoàn thành mẻ khi pass

---

## Slide 11 — Truy xuất & Dashboard

- Lô TP → mẻ → lô NVL (2 chiều)
- Dashboard: tồn, mẻ, cảnh báo
- Audit trail cho ATTP

---

## Slide 12 — Kết quả UAT

- 10/10 test case **PASS**
- E2E: 1 lô → 1 mẻ → truy xuất
- Hạn chế: PDF BM đầy đủ, mixing — giai đoạn 2

---

## Slide 13 — FSSC 8.7 (Xác nhận phần mềm)

- Prototype đã OQ/PQ rút gọn
- Chưa go-live production
- Song song biểu mẫu giấy

---

## Slide 14 — Lộ trình triển khai

| Giai đoạn | Nội dung |
|-----------|----------|
| 1 | Kho + CCP1 ✅ |
| 2 | SX + Lab + CCP2 ✅ |
| 3 | PDF, mixing, tích hợp GC |
| 4 | Go-live + validation đầy đủ |

---

## Slide 15 — Kết luận & Q&A

- Đã phân tích & đề xuất hệ thống phù hợp quy mô Oxeyns
- Prototype chứng minh khả thi kho–SX–CCP
- Hướng phát triển: mở rộng sản phẩm, TT-TVTH, ERP nhẹ

**Cảm ơn!**

---

*Kịch bản video: `docs/demo-video-script.md` | Screenshot: `docs/screenshots/`*
