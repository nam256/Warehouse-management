# TRƯỜNG ĐẠI HỌC TÀI NGUYÊN VÀ MÔI TRƯỜNG TP.HCM
## KHOA CÔNG NGHỆ THÔNG TIN

---

# ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP

**Tên đề tài:** Nghiên cứu và xây dựng hệ thống quản lý chất lượng số tích hợp Hold-Release, CAPA, FEFO và mô phỏng thu hồi lô cho nhà máy tinh dầu — ứng dụng tại Oxeyns Long An

| | |
|---|---|
| **Giảng viên hướng dẫn** | Học vị. *Tên giảng viên hướng dẫn* |
| **Sinh viên thực hiện** | *Tên sinh viên* |
| **Mã số sinh viên** | ……………… |
| **Lớp** | ……………… |
| **Khoá** | ……………… |

*TP. Hồ Chí Minh, tháng 8 năm 2026*

---

## 1. Mở đầu

### 1.1. Tính thực tiễn của đề tài

Công ty TNHH Oxeyns – Chi nhánh Long An sản xuất hương liệu thiên nhiên, sản phẩm chủ lực là **t-Cinnamic Aldehyde (t-CA)** từ tinh dầu quế. Nhà máy vận hành theo **FSSC 22000**, **HACCP** và chứng nhận **Kosher**, nhưng hồ sơ chất lượng vẫn phân tán: Thủ kho dùng Excel/phiếu giấy BM-01/GMP01; Kỹ thuật ghi operation record trên giấy; Lab lưu kết quả GC riêng; ATTP ghép chứng từ khi thẩm tra CCP 14 ngày/lần.

Kỳ **thực tập tốt nghiệp** đã xây prototype **Oxeyns Kho & SX** (bốn module: Kho, Sản xuất, Lab/CCP, Báo cáo/ATTP) — số hóa ghi chép, chưa phải lớp quản lý chất lượng số. Đề tài **luận văn** tái sử dụng nền đó và bổ sung **Digital QMS** (M1–M7). Chi tiết chức năng và điểm nâng cấp so với thực tập nêu tại mục **6.1**.

### 1.2. Cơ sở khoa học của đề tài

Đề tài gắn **HACCP/FSSC 22000** vào logic phần mềm: hai CCP có giới hạn đo được (CCP1 — C14: 13,02–14,39 dpm/gC; CCP2 — Ttop 107–110 °C và % t-CA > 99%); Hold-Release tách vai trò Lab gửi duyệt / ATTP quyết định; CAPA/NCR theo vòng đời điều tra–hành động–xác minh–đóng; FEFO ưu tiên hạn dùng sớm nhất; truy xuất lô hai chiều và mô phỏng thu hồi; SPC trên chuỗi GC; trợ lý tra cứu chỉ đọc theo RBAC.

Về kỹ thuật: ứng dụng web **React 19 + TypeScript + Vite** (giao diện), **FastAPI + SQLAlchemy 2** (API), **JWT/RBAC** (6 vai trò), **SQLite** (phát triển/kiểm thử) và **PostgreSQL 16** (demo, concurrency). Mỗi module có API, UI, audit log và kiểm thử.

---

## 2. Mục đích nghiên cứu

- Tìm hiểu và vận dụng **React, TypeScript, FastAPI, SQLAlchemy, JWT/RBAC**, kiểm thử **pytest/Playwright**, xuất báo cáo PDF/CSV.
- Nắm nghiệp vụ nhà máy tinh dầu: kho theo lô, mẻ chưng cất, Lab/CCP, Hold-Release, CAPA, FEFO, truy xuất/thu hồi, nhập GC/SPC, tra cứu hồ sơ lô.
- Thiết kế và cài đặt đủ **Digital QMS M1–M7** (API + UI), chạy được, đủ demo bảo vệ.
- Viết khóa luận theo quy định Khoa Công nghệ thông tin, Trường Đại học Tài nguyên và Môi trường TP. Hồ Chí Minh.

---

## 3. Đối tượng và phạm vi nghiên cứu

**Đối tượng:** quy trình chất lượng sản xuất t-CA tại Oxeyns Long An; ngôn ngữ/công cụ **TypeScript, Python, React, FastAPI, SQLite, PostgreSQL**; kỹ năng khảo sát, phân tích as-is/to-be, thiết kế CSDL/API, cài đặt và kiểm thử.

**Trong phạm vi**

- Sản phẩm t-CA; luồng Kho → Sản xuất → Lab → ATTP.
- **Nền TTTN (tái sử dụng, không tính đóng góp mới):** đăng nhập JWT, 6 vai trò; kho (nhập/xuất/tồn, lô, YCMH); sản xuất (mẻ, operation, cân đối vật tư); Lab/CCP1–CCP2; HACCP 14 ngày; dashboard, truy xuất 2 chiều, audit, PDF/CSV.
- **Luận văn (đóng góp mới, đã triển khai đủ):** M1 Hold-Release; M2 CAPA/NCR; M3 FEFO/giữ chỗ; M4 QR Batch Passport / mô phỏng thu hồi; M5 nhập GC/SPC; M6 trợ lý AI chỉ đọc; M7 hồ sơ, quản lý tài khoản, ảnh vật tư.
- Prototype demo local/Docker — không thay thế hệ thống vận hành chính thức.

**Ngoài phạm vi:** ERP kế toán, HR, app mobile, kết nối trực tiếp máy GC, go-live production/internet.

**Loại phần mềm:** ứng dụng web quản lý chất lượng số (Digital QMS), kiến trúc SPA + REST API.

---

## 4. Phương pháp nghiên cứu

**Lý thuyết:** khảo sát Sổ tay ATTP, HACCP, quy trình t-CA, biểu mẫu BM-xx; tổng hợp MIS/HACCP/FSSC, Hold-Release, CAPA, FEFO, truy xuất lô; phân tích as-is/to-be, ma trận vấn đề, ERD, đặc tả API.

**Thực nghiệm:** cài đặt backend/frontend; seed dữ liệu demo; pytest (CCP, Hold-Release, CAPA, FEFO, recall, GC/SPC, trợ lý AI, hồ sơ/user); UAT theo ca sản xuất t-CA; hoàn thiện khóa luận và slide demo.

---

## 5. Thời gian thực hiện

Từ tháng 6 năm 2026 đến hết thời gian hoàn thiện khóa luận và bảo vệ (dự kiến theo lịch Khoa). Chi tiết theo mục **Dự kiến kế hoạch thực hiện**.

---

## 6. Kết quả dự kiến đạt được

### 6.1. Thiết kế được phần mềm gì

Xây dựng **hệ thống quản lý chất lượng số (Digital QMS) — Oxeyns Long An**: ứng dụng web tiếng Việt, JWT, 6 vai trò (admin, thủ kho, kỹ thuật, lab, quản lý nhà máy, ATTP).

**Công nghệ luận văn:** React 19 + TypeScript + Vite; FastAPI + SQLAlchemy 2 + Pydantic 2; SQLite (dev/test) **và** PostgreSQL 16 (demo, concurrency); Alembic; ReportLab; Docker Compose; pytest, Playwright.

#### 6.1.1. Phần mềm thực tập (nền tái sử dụng — không phải đóng góp mới)

Bốn module TTTN: **Kho, Sản xuất, Lab/CCP, Báo cáo/ATTP**.

| Nhóm | Chức năng đã có từ thực tập |
|------|-----------------------------|
| Xác thực | JWT, bcrypt, 6 vai trò, route theo quyền |
| Kho | CRUD vật tư/NCC (API); phiếu nhập BM-01/GMP01; lô NVL; xuất theo mẻ; tồn realtime; cảnh báo tồn thấp → YCMH; lịch sử nhập/xuất; PDF phiếu nhập |
| Sản xuất | Lệnh/mẻ (draft → duyệt QL NM → chạy → xong); operation record (T, P, Ttop); nhánh chưng cất lại BTP; cân đối vật tư; mixing report API |
| Lab & CCP | Form nhập GC từng mẫu; rule CCP1 (C14 13,02–14,39) và CCP2 (Ttop 107–110 °C, % t-CA > 99); cảnh báo fail; `corrective_actions` list/create; màn HACCP 14 ngày |
| Báo cáo | Dashboard tồn/mẻ/CCP; truy xuất 2 chiều NVL ↔ TP; audit log; export PDF/CSV các BM-xx |

Hạn chế TTTN: thủ kho có thể tự nhập C14; không có Hold-Release; CAPA chưa có workflow/UI; chọn lô chỉ sort FIFO, người dùng tự chọn; chưa giữ chỗ NVL; chưa QR hồ sơ lô; chưa mô phỏng thu hồi; Lab nhập tay từng form; chưa SPC; chưa trợ lý tra cứu; CSDL chủ yếu SQLite local.

#### 6.1.2. Điểm nâng cấp luận văn so với thực tập

| Nghiệp vụ | Thực tập (TTTN) | Luận văn (Digital QMS) |
|-----------|-----------------|------------------------|
| Trạng thái lô | Chỉ `ccp1_status` pending/pass/fail | M1 thêm `quality_status`, board `/quality` |
| Nhập kho / CCP1 | Thủ kho nhập C14, hệ thống đánh pass ngay | Lô luôn `quarantine`; **chỉ Lab** ghi kết quả |
| Phê duyệt chất lượng | Không có ký duyệt độc lập | Lab gửi duyệt → ATTP release/reject; lịch sử + chữ ký role |
| Chứng nhận lô | PDF báo cáo rời | Release Certificate/CoA PDF gắn lô, hai người duyệt |
| Sai lệch | `corrective_actions` list/create, chưa UI | M2 tự tạo NCR/CAPA; điều tra → hành động → xác minh → đóng |
| Cảnh báo quá hạn | Không có | CAPA overdue (đỏ) trên `/capa` và dashboard |
| Chọn lô xuất | Sort FIFO; người dùng tự chọn | M3 phân bổ FEFO theo hạn dùng + quality gate |
| Tồn | Chỉ quantity hiện tại | `available = on_hand − reserved` |
| Duyệt mẻ SX | Không giữ trước NVL | Approve tạo reservation atomic; hủy hoàn tồn (movement đảo) |
| Truy xuất | Gõ mã lô xem cây 2 chiều | M4 Batch Passport + mã QR |
| Thu hồi | Ngoài phạm vi TTTN | Recall Simulator BFS nhiều tầng, xuất CSV |
| Lab | Nhập từng form | M5 import CSV GC atomic, SHA-256 chống trùng |
| Phân tích CL | Chỉ ngưỡng CCP từng điểm | M5 SPC: mean, σ, UCL/LCL, điểm ngoài kiểm soát |
| Tra cứu | Bấm menu, lọc tay | M6 trợ lý AI tiếng Việt, chỉ đọc, đúng RBAC, không bịa số |
| Tài khoản / ảnh | Seed user, không hồ sơ, không ảnh vật tư | M7 `/profile`, admin `/users` (không đăng ký công khai), ảnh vật tư trên kho |
| CSDL / triển khai | SQLite file, Uvicorn/Vite local | SQLite + PostgreSQL 16, Alembic, Docker full stack |

**Tóm tắt khi hội đồng hỏi “làm mới gì?”:** lớp Digital QMS gồm Hold-Release hai bước, CAPA/NCR điện tử, FEFO có giữ chỗ, mô phỏng thu hồi bằng QR, cộng M5–M7 — **tích hợp lên hệ thống kho–sản xuất đã hoàn thành trong kỳ thực tập**, không viết lại từ đầu.

#### 6.1.3. Đủ chức năng luận văn đã làm (M1–M7)

| Module | Chức năng đã triển khai |
|--------|-------------------------|
| **M1 Hold-Release** | Board `/quality` theo cột; luồng `quarantine → sampling → under_test → awaiting_release → released \| rejected \| retest`; Lab gửi, ATTP quyết định; `BatchStatusHistory` + `QualityApproval`; chặn xuất/bắt đầu SX khi lô chưa `released`; thành phẩm CCP2 pass ở `awaiting_release` (không tự giải phóng); Release Certificate PDF; thủ kho không tự đánh giá CCP1 |
| **M2 CAPA/NCR** | Tự sinh khi Lab fail, operation fail hoặc reject lô; chống trùng cùng nguồn; state `open → investigating → action_pending → verification → closed`; nguyên nhân, hạn xử lý, hành động, disposition, xác minh; không đóng khi thiếu xác minh; màn `/capa`, lọc overdue |
| **M3 FEFO / giữ chỗ** | NSX/HSD trên lô; gợi ý và phân bổ nhiều lô hạn sớm nhất; reservation theo lệnh SX; cột on-hand / reserved / available; thiếu tồn thì rollback toàn bộ; PostgreSQL `SELECT FOR UPDATE` chống hai lệnh giữ cùng tồn; hủy mẻ hoàn tồn bằng phiếu đảo, không xóa lịch sử |
| **M4 QR / thu hồi** | Batch Passport (kho + CL + SX + certificate); QR mở đúng hồ sơ lô; Recall Simulator duyệt downstream nhiều tầng; ghi người chạy, lý do, thời gian; kết quả phân tầng; xuất CSV |
| **M5 GC Import / SPC** | Upload CSV GC; validate cả file rồi ghi, lỗi thì rollback; SHA-256 chống import trùng; SPC mean ± 3σ, UCL/LCL, điểm out-of-control |
| **M6 Trợ lý AI** | Chat tiếng Việt: tồn kho, trạng thái lô, CAPA, truy xuất, hạn dùng; chỉ gọi API sẵn có; tôn trọng JWT/RBAC; không ghi nghiệp vụ (không release lô, không đóng CAPA); không bịa số — thiếu dữ liệu thì “không tìm thấy”; tắt được khi demo offline |
| **M7 Hồ sơ / user / ảnh** | `/profile`: họ tên, vai trò, đổi mật khẩu, avatar; **không** đăng ký công khai; admin `/users`: tạo, chọn vai trò, khóa/mở tài khoản; ảnh vật tư (thêm/đổi/xóa) hiện thumbnail Tồn kho, Nhập kho, Xuất kho |

**Luồng demo:** nhận tinh dầu quế → cách ly → CCP1 (Lab) → ATTP giải phóng → giữ chỗ FEFO → chưng cất → CCP2 → thành phẩm chờ release → QR / mô phỏng thu hồi; fail thì vào CAPA.

Phần mềm là **prototype chạy được** (API + UI từng module), đủ kiểm thử tự động; không cam kết go-live production tại nhà máy.

### 6.2. Khóa luận theo yêu cầu của Khoa

Viết **khóa luận tốt nghiệp** đúng thể thức Khoa Công nghệ thông tin, Trường Đại học Tài nguyên và Môi trường TP. Hồ Chí Minh: lời mở đầu, ba chương, kết luận, tài liệu tham khảo, phụ lục (yêu cầu, API, CSDL, UAT, hướng dẫn sử dụng). Nộp đúng hạn; kèm mã nguồn, CSDL demo và slide/video minh họa.

---

## 7. Nội dung khóa luận

**LỜI MỞ ĐẦU** — lý do chọn đề tài; phân biệt nền TTTN và đóng góp luận văn M1–M7.

**Chương 1. TỔNG QUAN TÀI LIỆU**

- Giới thiệu Oxeyns Long An, quy trình t-CA, CCP1/CCP2, biểu mẫu BM-xx.
- Hiện trạng Excel/giấy; pain point kho, SX, Lab, ATTP.
- Cơ sở HACCP/FSSC, Hold-Release, CAPA, FEFO, truy xuất lô, SPC, RBAC.
- Stack React, FastAPI, SQLAlchemy, JWT, SQLite/PostgreSQL; phân biệt nền TTTN và lớp QMS.

**Chương 2. PHƯƠNG PHÁP THỰC HIỆN**

- Phân tích as-is / to-be; yêu cầu chức năng và phi chức năng.
- Thiết kế CSDL, API REST, phân quyền RBAC, kiến trúc 3 tầng.
- Quy tắc nghiệp vụ: Hold-Release hai bước, CAPA, FEFO atomic, recall chỉ đọc, GC import rollback, trợ lý AI không ghi.

**Chương 3. CÀI ĐẶT THỰC NGHIỆM**

- Cài đặt nền TTTN và đủ bảy module luận văn M1–M7 (API + UI).
- Kết quả chạy thử, kiểm thử tự động, UAT; hạn chế và hướng phát triển.

**KẾT LUẬN** — đánh giá mục tiêu, sản phẩm bàn giao, kiến nghị.

---

## 8. Dự kiến kế hoạch thực hiện

| Thời gian | Nội dung | Địa điểm |
|-----------|----------|----------|
| Tuần 1–2 | Khảo sát công ty, quy trình t-CA, HACCP, biểu mẫu BM-xx; chốt đề cương | Oxeyns Long An; Trường ĐH TN&MT TP.HCM |
| Tuần 3 | Phân tích as-is/to-be, yêu cầu FR/NFR, ma trận vấn đề | Trường / thực tập |
| Tuần 4 | Thiết kế CSDL, API, RBAC, kiến trúc hệ thống | Trường / thực tập |
| Tuần 5 | Cài đặt nền: xác thực, kho, sản xuất, Lab/CCP | Trường / thực tập |
| Tuần 6 | Cài đặt M1 Hold-Release (API + UI) | Trường / thực tập |
| Tuần 7 | Cài đặt M2 CAPA/NCR (API + UI) | Trường / thực tập |
| Tuần 8 | Cài đặt M3 FEFO / giữ chỗ nguyên liệu | Trường / thực tập |
| Tuần 9 | Cài đặt M4 QR Batch Passport / mô phỏng thu hồi | Trường / thực tập |
| Tuần 10 | Cài đặt M5 GC/SPC, M6 trợ lý AI, M7 hồ sơ/user/ảnh; kiểm thử pytest | Trường / thực tập |
| Tuần 11 | UAT theo ca t-CA; hoàn thiện tài liệu, validation draft | Trường / Oxeyns |
| Tuần 12 | Viết khóa luận, slide demo, chuẩn bị bảo vệ | Trường ĐH TN&MT TP.HCM |

---

## 9. Tài liệu tham khảo

1. FSSC International (2023). *FSSC 22000 Version 6 — Scheme Requirements.* https://www.fssc.com/
2. Codex Alimentarius Commission (2023). *General Principles of Food Hygiene / HACCP (CXC 1-1969).*
3. ISO (2018). *ISO 22000:2018 — Food safety management systems.*
4. Công ty TNHH Oxeyns – Chi nhánh Long An. *Sổ tay ATTP; Chương trình thẩm tra HACCP; Quy trình sản xuất t-CA; Bộ biểu mẫu BM-xx/GMPxx* (tài liệu nội bộ).
5. Sommerville, I. (2016). *Software Engineering* (10th ed.). Pearson.
6. FastAPI Documentation. https://fastapi.tiangolo.com/
7. React Documentation. https://react.dev/
8. SQLAlchemy 2.0 Documentation. https://docs.sqlalchemy.org/

---

## 10. Các cơ quan, đơn vị cần liên hệ

- **Khoa Công nghệ thông tin** — Trường Đại học Tài nguyên và Môi trường TP. Hồ Chí Minh, 236 Lê Văn Sỹ, Phường Tân Sơn Hòa, TP. Hồ Chí Minh.
- **Công ty TNHH Oxeyns – Chi nhánh Long An** — KCN Tân Kim, huyện Cần Giuộc, tỉnh Long An (đơn vị thực tập, khảo sát nghiệp vụ).

---

| **GIẢNG VIÊN HƯỚNG DẪN** | **NGƯỜI LẬP ĐỀ CƯƠNG** |
|---|---|
| *(ký và ghi rõ họ tên)* | *(ký và ghi rõ họ tên)* |
| | |
| | |

**TRƯỞNG BỘ MÔN**

*(ký và ghi rõ họ tên)*
