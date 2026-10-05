# CHƯƠNG 4: KẾT LUẬN

Chương này tổng kết kết quả thực tập tại Công ty TNHH Oxeyns – Chi nhánh Long An: đánh giá mức độ hoàn thành mục tiêu, sản phẩm bàn giao, kinh nghiệm rút ra, hạn chế, hướng phát triển và kiến nghị.

---

## 4.1. Kết quả đạt được

### 4.1.1. Đánh giá kết quả theo mục tiêu đề tài

**Bảng 4.1 — Đánh giá mục tiêu cụ thể (Chương 1.3.2)**

| STT | Mục tiêu | Kết quả đạt được | Mức độ |
|-----|----------|------------------|--------|
| 1 | Mô tả quy trình t-CA, CCP, luồng NVL→SX→TP | Chương 1.2.2; Chương 3.1; tài liệu `quytrinhsanxuat.txt` | **Hoàn thành** |
| 2 | Khảo sát BM-xx, hiện trạng CNTT | Chương 1.2.3–1.2.5; `docs/khao-sat.md`, `phong-van/` | **Hoàn thành** |
| 3 | Ma trận P01–P12, FR/NFR | Chương 2.2.4; `problem-matrix.md`, `requirements.md` | **Hoàn thành** |
| 4 | Thiết kế CSDL 14 bảng, API `/api/v1`, RBAC | Chương 3.2–3.3; `database-design.md`, `api-spec.md` | **Hoàn thành** |
| 5 | Cài đặt prototype React + FastAPI + SQLite | 11 menu, `oxeyns.db`, code `backend/` + `frontend/` | **Hoàn thành** |
| 6 | Kiểm thử và tài liệu | pytest 17/17; UAT 10/10; user manual, validation draft | **Hoàn thành (MVP)** |

**Bảng 4.2 — Đánh giá pain point ưu tiên P0**

| Mã | Vấn đề | Giải pháp prototype | Đánh giá |
|----|--------|----------------------|----------|
| P01 | Tồn kho thủ công | `stock_batches`, `stock_movements`, Dashboard | Đạt |
| P02 | Khó truy xuất lô | `GET /reports/trace`, trace-suggestions | Đạt |
| P03 | Xuất không link mẻ SX | `production_material_usages`, `production_order_id` | Đạt |
| P06 | Không cảnh báo CCP | `ccp.py`, chặn complete/issue khi fail | Đạt |

Prototype chạy local trên **SQLite** (`backend/oxeyns.db`), đủ demo end-to-end:

```text
Nhập NVL → CCP1 (C14) → Tạo/duyệt mẻ → Xuất NVL → Operation (Ttop)
→ Lab (% t-CA) → CCP2 → Hoàn thành → Lô TP → Truy xuất → Audit / PDF
```

Thời gian chạy thử: UI ~25 phút; API E2E ~8 giây (`test_e2e_api.py`).

### 4.1.2. Sản phẩm bàn giao

**Bảng 4.3 — Danh mục sản phẩm**

| Loại | Đường dẫn / mô tả |
|------|-------------------|
| **Mã nguồn backend** | `backend/app/` — FastAPI, SQLAlchemy, routers, `ccp.py`, export PDF/CSV |
| **Mã nguồn frontend** | `frontend/src/` — React 19, TypeScript, 12 trang UI |
| **CSDL demo** | `backend/oxeyns.db` — SQLite, dữ liệu seed |
| **Kiểm thử** | `backend/tests/` — 17 pytest |
| **Đặc tả yêu cầu** | `docs/requirements.md` (Phụ lục A) |
| **Đặc tả API** | `docs/api-spec.md` (Phụ lục B) |
| **Thiết kế CSDL** | `docs/database-design.md` (Phụ lục C) |
| **Biểu mẫu BM-xx** | `docs/bieu-mau/` (Phụ lục D) |
| **Phỏng vấn** | `docs/phong-van/` (Phụ lục E) |
| **UAT** | `docs/uat-results.md`, `uat-test-cases.md` (Phụ lục F) |
| **Wireframe** | `docs/wireframes/` (Phụ lục G) |
| **As-is / to-be** | `process-as-is.md`, `process-to-be.md` (Phụ lục H) |
| **Ma trận vấn đề** | `docs/problem-matrix.md` (Phụ lục I) |
| **Hướng dẫn sử dụng** | `docs/user-manual.md`, `code.txt` (Phụ lục J) |
| **Validation FSSC 8.7** | `docs/software-validation.md` (Phụ lục K) |
| **Báo cáo TTTN** | `docs/bao-cao/` — mục lục + `noi-dung/` |
| **Slide / demo** | `docs/demo-slides.md`, `demo-video-script.md` (Phụ lục M) |

Sản phẩm đáp ứng yêu cầu TTTN: **phân tích + đề xuất + minh chứng prototype chạy được**, không cam kết go-live production.

---

## 4.2. Kinh nghiệm thực tiễn đã tích lũy được

Qua kỳ thực tập, em rút ra các kinh nghiệm sau:

**1. Nghiệp vụ trước, công nghệ sau.** Hiểu rõ CCP1 (C14), CCP2 (Ttop, % t-CA), biểu mẫu BM-xx và chu kỳ thẩm tra 14 ngày giúp thiết kế CSDL và API đúng trọng tâm. Nếu code UI trước khi chốt luồng nghiệp vụ, dễ phải sửa lại nhiều lần.

**2. Trung tâm dữ liệu là lô hàng và mẻ sản xuất.** Mọi bảng (`stock_batches`, `production_orders`, `production_material_usages`, `operation_records`, `lab_tests`) đều xoay quanh `batch_no` và `order_no` — là nền tảng truy xuất và giám sát CCP.

**3. Tách rule CCP thành module độc lập.** File `ccp.py` với `evaluate_ccp1`, `evaluate_ccp2` giúp pytest kiểm tra nhanh (13 case), đối chiếu trực tiếp giới hạn HACCP trong Sổ tay ATTP.

**4. Audit log và tiếng Việt cần làm sớm.** ATTP quan tâm “ai làm gì khi nào”; `audit_logs` + `audit_display.py` (nhãn tiếng Việt) phục vụ màn Nhật ký và thẩm tra. Giao diện tiếng Việt giúp demo với Thủ kho/QL NM dễ hiểu hơn.

**5. SQLite đủ cho MVP TTTN.** Một file `oxeyns.db` đơn giản hóa cài đặt (chỉ cần `uvicorn` + `npm run dev`), phù hợp demo bảo vệ. SQLAlchemy cho phép đổi `DATABASE_URL` sau này — nhưng **chưa thực hiện trong đề tài**.

**6. Kiểm thử tự động + UAT bổ sung cho nhau.** pytest bảo đảm regression API; UAT 10 kịch bản bám luồng nghiệp vụ Oxeyns (nhập kho, mẻ SX, CCP fail, truy xuất…).

---

## 4.3. Những vấn đề chưa được giải quyết

Trong phạm vi thời gian thực tập và MVP, các hạng mục sau **chưa hoàn thiện**:

**Bảng 4.4 — Hạn chế và ảnh hưởng**

| Hạng mục | Trạng thái | Ảnh hưởng |
|----------|------------|-----------|
| Go-live production | Chưa | Phần mềm chưa dùng chính thức tại nhà máy |
| Validation IQ/OQ/PQ có ký ATTP | Chỉ draft | Chưa đủ điều kiện FSSC 8.7 go-live |
| UAT sign-off Thủ kho/QL NM | Chưa ký | Kết quả UAT mô phỏng sinh viên |
| Phỏng vấn trực tiếp | Synthesized | Cần biên bản buổi tại NM |
| PDF khớp 100% mẫu BM-xx in | Chưa | Dùng PDF/CSV đơn giản, font DejaVu |
| UI pha trộn BM-01/GMP05 | API có, UI chưa | Chưa số hóa đủ bước phối trộn |
| FIFO/FEFO xuất kho | Chưa | Chọn lô xuất thủ công |
| Import file GC tự động | Chưa | Lab nhập tay |
| Cảnh báo CCP qua email/SMS | Chưa | Chỉ cảnh báo trên UI/Dashboard |
| Workflow duyệt YCMH nhiều cấp | Chưa | YCMH lưu pending đơn giản |
| PostgreSQL / Docker | File `docker-compose.yml` có; **backend chưa kết nối, chưa test** | Vẫn dùng SQLite |
| TT-TVTH thu hồi sản phẩm | Ngoài phạm vi | Chưa module riêng |

Các hạn chế trên **không làm sai lệch** kết luận về tính khả thi của hướng giải pháp trong phạm vi TTTN — prototype đã chứng minh luồng cốt lõi chạy được.

---

## 4.4. Hướng phát triển

Đề xuất lộ trình sau thực tập, chia theo giai đoạn:

**Giai đoạn 1 — Chuẩn bị go-live (3–6 tháng)**

- Hoàn thiện validation IQ/OQ/PQ với ATTP; UAT có chữ ký key user.
- Pilot song song giấy + phần mềm 1–2 tháng.
- Đào tạo 6 user theo `docs/dao-tao.md`.
- (Tùy chọn) Chuyển `DATABASE_URL` sang PostgreSQL, cấu hình backup (`docs/backup-rollback.md`).

**Giai đoạn 2 — Mở rộng chức năng (6–12 tháng)**

- Export PDF khớp template BM-xx in chuẩn FSSC.
- UI pha trộn BM-01/GMP05 đầy đủ.
- Workflow duyệt YCMH/phiếu nhiều cấp.
- Gợi ý FIFO khi xuất kho.

**Giai đoạn 3 — Tích hợp (12+ tháng)**

- Đọc file GC tự động từ máy Lab.
- Cảnh báo CCP qua email.
- API tích hợp ERP/kế toán tập đoàn (nếu có).
- Mobile/tablet cho Kỹ thuật ghi operation tại hiện trường.

---

## 4.5. Kiến nghị đối với doanh nghiệp và nhà trường

### 4.5.1. Kiến nghị đối với Oxeyns Long An

1. **Thành lập nhóm change control** gồm ATTP, QL NM và IT trước khi chuyển từ Excel/giấy sang phần mềm — đánh giá rủi ro theo FSSC.
2. **Ưu tiên validation mục 8.7** trước khi dùng phần mềm cho quyết định CCP chính thức.
3. **Chỉ định key user** mỗi bộ phận (Thủ kho, Lab, Kỹ thuật) phản hồi UI và tham gia UAT có chữ ký.
4. **Duy trì song song** hồ sơ giấy và hệ thống trong giai đoạn pilot để giảm rủi ro gián đoạn sản xuất.
5. **Giữ SQLite cho demo nội bộ**; chỉ chuyển PostgreSQL khi đã có kế hoạch server, backup và vận hành IT.

### 4.5.2. Kiến nghị đối với nhà trường

1. Khuyến khích đề tài TTTN có **sản phẩm chạy được** (mã nguồn + kiểm thử), không chỉ lý thuyết.
2. Bổ sung nội dung về **phần mềm trong ATTP** (validation, audit trail) vào môn liên quan chất lượng / phân tích thiết kế HTTT.
3. Tạo điều kiện sinh viên **demo và bảo vệ** với slide/video (`demo-slides.md`) trước hội đồng và doanh nghiệp.

---

## Kết luận chung

Đề tài **phân tích và xây dựng prototype hệ thống quản lý kho, sản xuất tích hợp giám sát CCP** tại Công ty TNHH Oxeyns – Chi nhánh Long An đã **hoàn thành các mục tiêu** trong phạm vi thỏa thuận (Chương 1.4). Em đã:

- Phân tích hiện trạng và ma trận vấn đề P01–P12;
- Thiết kế CSDL 14 bảng và API REST `/api/v1` với RBAC 6 vai trò;
- Cài đặt prototype **React 19 + FastAPI + SQLite** với 11 menu, rule CCP1/CCP2, truy xuất lô hai chiều, audit log và xuất PDF/CSV tiếng Việt;
- Kiểm thử **pytest 17/17** và **UAT 10/10** trên môi trường demo local.

Prototype chứng minh hướng số hóa kho – sản xuất – Lab – ATTP **khả thi** cho doanh nghiệp quy mô nhỏ. Bước tiếp theo thuộc quyết định của Oxeyns: validation chính thức, pilot có key user và (nếu cần) nâng cấp hạ tầng — **PostgreSQL/Docker chưa nằm trong phạm vi đề tài đã thực hiện**.

Em xin trân trọng cảm ơn quý thầy cô và Công ty Oxeyns đã tạo điều kiện hoàn thành kỳ thực tập và báo cáo này.

## 4.6. Cập nhật kết quả và giới hạn Digital QMS

Các hạn chế “chưa có FEFO”, “chưa import GC”, “chưa có module thu hồi” và “PostgreSQL chưa thuộc phạm vi” ở phần baseline phía trên không còn phản ánh đầy đủ trạng thái mã nguồn: M1–M6 đã được triển khai, gồm FEFO/reservation, Recall Simulator, GC/SPC và trợ lý AI chỉ đọc. Bằng chứng tự động hiện xác nhận các rule trọng yếu như chặn quarantine, CAPA idempotent, reservation atomic, recall nhiều cấp, import GC atomic và trợ lý không tin câu trả lời thiếu dữ liệu.

Tuy vậy, kết luận nghiệm thu vẫn **provisional**. Task 10 mới ghi nhận SQLite profile 46 test pass và frontend build pass; PostgreSQL integration/concurrency chưa chạy lại, Playwright chưa chạy xanh do full stack không hoạt động, 20/20 UAT con người và mọi trường thời gian trong `docs/thesis-metrics.md` còn pending. Không có chữ ký giả định từ công ty hoặc giảng viên. Vì vậy đề tài có thể kết luận **đã hoàn thành triển khai kỹ thuật trong phạm vi**, nhưng chưa được kết luận đã validation/go-live hoặc đạt phần trăm cải thiện nghiệp vụ trước khi hoàn tất Gate G5.
