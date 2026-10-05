# Chương 6 — Kết quả thực hiện tại doanh nghiệp

---

## 6.1. Công việc sinh viên hỗ trợ IT đã thực hiện

| Hạng mục | Kết quả | Tài liệu |
|----------|---------|----------|
| Khảo sát & tổng hợp yêu cầu | Hoàn thành (synthesized) | `docs/khao-sat.md`, `docs/phong-van/` |
| Phân tích as-is/to-be | Hoàn thành | `docs/process-*.md`, `data-flow.md` |
| Ma trận vấn đề | Hoàn thành | `docs/problem-matrix.md` |
| Spec FR/NFR, ERD, API | Hoàn thành | `docs/requirements.md`, `database-design.md`, `api-spec.md` |
| Hỗ trợ UAT | Hoàn thành | `docs/uat-test-cases.md`, `uat-results.md` |
| User manual, đào tạo | Hoàn thành | `docs/user-manual.md`, `dao-tao.md` |
| Slide/video demo | Hoàn thành | `docs/demo-slides.md`, `demo-video-script.md` |
| Xác nhận phạm vi & SW validation | Hoàn thành | `docs/pham-vi-xac-nhan.md`, `software-validation.md` |
| Dàn ý báo cáo 7 chương | Hoàn thành | `docs/bao-cao/chuong-*.md` |

---

## 6.2. Kết quả prototype (phối hợp dev chính)

### Module đã demo

- [x] Login + RBAC
- [x] Nhập/xuất/tồn theo lô
- [x] Production order + operation record
- [x] Lab GC + CCP1/CCP2 + cảnh báo
- [x] Dashboard, truy xuất 2 chiều
- [x] Audit log API + UI
- [x] Export CSV tồn kho
- [x] E2E test API

### Stack triển khai

FastAPI + React + SQLite/PostgreSQL + Docker Compose

---

## 6.3. Kết quả UAT

| Chỉ số | Giá trị |
|--------|---------|
| Test case | 10 |
| Pass | 10 (100%) |
| E2E smoke | PASS |

Chi tiết: `docs/uat-results.md`

**Kịch bản E2E:** 1 lô NVL → CCP1 pass → xuất → mẻ SX → CCP2 pass → truy xuất TP.

---

## 6.4. Demo và đào tạo

- Kế hoạch đào tạo **45 phút** Thủ kho + Kỹ thuật: `docs/dao-tao.md`
- Slide báo cáo 15 slide: `docs/demo-slides.md`
- Script video 7 phút: `docs/demo-video-script.md`

---

## 6.5. Xác nhận phần mềm (FSSC 8.7)

- IQ/OQ/PQ rút gọn cho **prototype** — PASS mục tiêu demo
- **Chưa** go-live production — song song biểu mẫu giấy
- `docs/software-validation.md`

---

## 6.6. Hạn chế

| Hạn chế | Ghi chú |
|---------|---------|
| Phỏng vấn synthesized | Cần xác nhận trực tiếp tại NM |
| Export PDF đúng BM-xx | MVP dùng CSV |
| Mixing BM-01/GMP05 | Chưa UI đầy đủ |
| FIFO/FEFO, duyệt lệnh SX | Giai đoạn 2 |
| Sign-off UAT nghiệp vụ | Pending chữ ký Thủ kho/QL NM |
| Scan biểu mẫu giấy | Chưa có trong `docs/bieu-mau/scans/` |

---

## 6.7. Bài học kinh nghiệm

- SME cần giải pháp **vừa đủ** — ưu tiên kho + CCP trước ERP lớn
- Map BM-xx giúp ATTP chấp nhận số hóa
- Vai trò SV IT: cầu nối nghiệp vụ–kỹ thuật hiệu quả hơn chỉ code

---

## 6.8. Tổng kết chương

- Đã có **minh chứng prototype** và bộ tài liệu đi kèm đề tài TTTN
- UAT demo đạt; production cần lộ trình validation đầy đủ
