# CHƯƠNG 1: TỔNG QUÁT

## 1.1. Giới thiệu cơ quan thực tập

### 1.1.1. Thông tin công ty Oxeyns – Chi nhánh Long An

Công ty TNHH Oxeyns – Chi nhánh Long An là đơn vị sản xuất hương liệu và tinh dầu thiên nhiên, trực thuộc hệ thống Oxeyns. Nhà máy đặt tại **KCN Tân Kim, huyện Cần Giuộc, tỉnh Long An**, với diện tích xưởng khoảng **250 m²**, công suất khoảng **36 tấn/năm**. Sản phẩm chủ lực là **t-Cinnamic Aldehyde (t-CA)** — hợp chất hương liệu chiết xuất từ **tinh dầu quế**, phục vụ thị trường trong và ngoài nước.

Về quản lý chất lượng, doanh nghiệp vận hành theo **FSSC 22000**, **HACCP Codex** và đáp ứng chứng nhận **Kosher**. Hệ thống ghi chép được chuẩn hóa qua Sổ tay ATTP, các quy trình QT-xx, SSOP và bộ biểu mẫu **BM-xx/GMPxx**. Quy mô nhân sự trực tiếp tham gia kho – sản xuất – Lab – ATTP khoảng **sáu người**, phù hợp mô hình sản xuất tinh khiết quy mô vừa và nhỏ (SME) nhưng yêu cầu hồ sơ chất lượng tương đương doanh nghiệp xuất khẩu.

**Bảng 1.1 — Thông tin chung doanh nghiệp**

| Mục | Nội dung |
|-----|----------|
| Tên đơn vị | Công ty TNHH Oxeyns – Chi nhánh Long An |
| Địa điểm | KCN Tân Kim, Cần Giuộc, Long An |
| Lĩnh vực | Hương liệu thiên nhiên, tinh dầu |
| Sản phẩm chính | t-Cinnamic Aldehyde (t-CA) từ dầu quế |
| Quy mô | ~6 nhân sự; ~250 m²; ~36 tấn/năm |
| Tiêu chuẩn | FSSC 22000, HACCP, Kosher |
| Ghi chép hiện tại | Excel + biểu mẫu giấy BM-xx/GMPxx |

### 1.1.2. Tổ chức và vai trò các bộ phận (Thủ kho, KT, Lab, QL NM, ATTP)

Cơ cấu tổ chức tại nhà máy Long An bám sát luồng vật tư và luồng thông tin chất lượng. Năm nhóm nghiệp vụ chính có vai trò như sau:

**Thủ kho** tiếp nhận tinh dầu quế và nguyên liệu khác: đối chiếu số lượng, khối lượng, kiểm sơ bộ màu – mùi – tỷ trọng; ghi **BM-01/GMP01** cho mỗi lô nhập; bảo quản NVL nhiệt độ phòng, tránh ánh nắng; xuất kho theo yêu cầu sản xuất; lập báo cáo tồn hàng tuần/tháng (**BM-02/GMP01**). Thủ kho là điểm ghi nhận đầu vào **CCP1** (chỉ số phóng xạ C14).

**Bộ phận Kỹ thuật** vận hành chưng cất chân không (thời gian mẻ khoảng 32–37 giờ), chiết rót, bơm Nitơ và phối trộn. Kỹ thuật viên ghi **operation record** (**BM-01/GMP03**) với nhiệt độ, áp suất và **nhiệt độ đỉnh Ttop** — thông số then chốt của **CCP2**. Lệnh/mẻ sản xuất tham chiếu **BM-01/GMP04**.

**Phòng Lab** thực hiện phân tích **C14** (nguyên liệu), **hàm lượng % t-CA** và **sắc ký khí (GC)** theo **BM-02/GMP05**. Kết quả Lab quyết định trạng thái đạt/không đạt CCP và điều kiện hoàn thành mẻ sản xuất.

**Quản lý nhà máy (QL NM)** điều phối kế hoạch, **duyệt mẻ sản xuất**, theo dõi tiến độ, cân đối nguyên liệu và tổng hợp báo cáo. QL NM cần cái nhìn tổng hợp về tồn kho, mẻ đang chạy và cảnh báo chất lượng — nhu cầu được phản ánh qua màn **Bảng tổng quan** trong prototype.

**Đội An toàn thực phẩm (ATTP)** duy trì Sổ tay ATTP, tổ chức **thẩm tra CCP 14 ngày/lần** và thẩm tra nội bộ HACCP hàng năm (hoặc khi thay đổi quy trình/thiết bị). ATTP yêu cầu hồ sơ CCP đầy đủ, có **audit trail** và — nếu dùng phần mềm giám sát CCP — phải có **xác nhận phần mềm** theo FSSC mục 8.7.

*[Hình 1.1 — Sơ đồ tổ chức và luồng phối hợp Kho → SX → Lab → ATTP]*

---

## 1.2. Giới thiệu về nội dung thực tập

### 1.2.1. Lý do chọn đề tài và bối cảnh FSSC 22000 / HACCP / Kosher

Em chọn đề tài **phân tích và xây dựng prototype hệ thống quản lý kho, sản xuất tích hợp giám sát CCP** vì các lý do sau:

**Thứ nhất**, Oxeyns bắt buộc tuân thủ **HACCP** và **FSSC 22000**. Hai điểm CCP (tiếp nhận NVL và chưng cất) có giới hạn đo lường cụ thể; mọi lô phải có bằng chứng đạt chuẩn khi thẩm tra. Hiện giới hạn được đối chiếu thủ công giữa phiếu kho, operation record và kết quả Lab — dễ chậm và khó truy vết khi có khiếu nại.

**Thứ hai**, chứng nhận **Kosher** và khách hàng quốc tế đòi hỏi **truy xuất nguồn gốc lô hàng** hai chiều. Hồ sơ phân tán trên Excel và giấy khiến thời gian đáp ứng yêu cầu truy vết kéo dài, không phù hợp kỳ vọng đối tác.

**Thứ ba**, quy mô nhỏ (~6 nhân sự) không phù hợp triển khai ERP/MES lớn ngay, nhưng vẫn cần **giải pháp web tập trung** cho kho – sản xuất – Lab – ATTP. Prototype **React + FastAPI + SQLite** minh họa hướng đi khả thi, chi phí thấp. PostgreSQL chỉ nêu trong tài liệu triển khai tương lai — **chưa dùng trong đề tài**.

Vai trò thực tập của em: khảo sát, phân tích, thiết kế CSDL/API, cài đặt và kiểm thử prototype — không cam kết go-live production trong thời gian TTTN.

### 1.2.2. Quy trình sản xuất t-Cinnamic Aldehyde (t-CA)

Theo tài liệu quy trình sản xuất và chương trình thẩm tra HACCP nội bộ, quy trình t-CA tại Oxeyns Long An gồm các bước:

1. **Tiếp nhận dầu quế** — kiểm tra chứng từ, lấy mẫu, ghi BM-01/GMP01; đánh giá **CCP1** (C14: **13,02 – 14,39 dpm/gC**).
2. **Bảo quản** — lưu kho nhiệt độ phòng, tránh nắng.
3. **Chưng cất chân không** (32–37 giờ/mẻ) — nhiệt độ vận hành khoảng **108–115°C**, áp suất **(-0,99) – (-0,10) MPa**; ghi operation record; kiểm soát **CCP2** (**Ttop: 107–110°C**; **% t-CA > 99%**).
4. **Chiết rót, bơm Nitơ** — bảo vệ sản phẩm trung gian.
5. **Phối trộn** — biên bản **BM-01/GMP05**.
6. **Đóng phuy, dán nhãn** — tạo lô thành phẩm, gắn mã lô truy xuất.

**Luồng thông tin** song song: phiếu nhập/xuất kho → lệnh/mẻ SX → kết quả Lab (C14, GC, % t-CA) → hồ sơ thẩm tra CCP. Đề tài tập trung số hóa từ **nhập kho** đến **hoàn thành mẻ và tạo lô TP**; chưa số hóa đầy đủ pha trộn và logistics sau đóng gói.

### 1.2.3. Hệ thống ATTP, chương trình thẩm tra và biểu mẫu BM-xx đang dùng

Hệ thống quản lý chất lượng được cụ thể hóa qua Sổ tay ATTP, QT-xx, SSOP và biểu mẫu BM-xx/GMPxx. Các biểu mẫu liên quan trực tiếp đề tài:

| Biểu mẫu | Mục đích tại Oxeyns | Chức năng trong prototype |
|----------|---------------------|---------------------------|
| BM-01/GMP01 | Phiếu nhập kho NVL | Màn Nhập kho + `stock_batches` |
| BM-02/GMP01 | Báo cáo tồn kho | Dashboard + export CSV |
| BM-01/GMP03 | Operation record chưng cất | Màn Sản xuất — `operation_records` |
| BM-01/GMP04 | Lệnh/mẻ sản xuất | Tạo & duyệt `production_orders` |
| BM-01/GMP05 | Biên bản pha trộn | Bảng `mixing_reports` (UI chưa đầy đủ) |
| BM-02/GMP05 | Kết quả GC / Lab | Màn Kiểm nghiệm — `lab_tests` |
| Biên bản thẩm tra CCP | Thẩm tra 14 ngày/lần | Giám sát CCP + xuất PDF |

**Chương trình thẩm tra** quy định: thẩm tra CCP **14 ngày/lần** (đối chiếu hồ sơ với thực tế); thẩm tra nội bộ HACCP **hàng năm** hoặc khi có thay đổi quy trình, thiết bị, khiếu nại nghiêm trọng. Khi không đạt CCP: cô lập lô, báo cáo, hành động khắc phục — prototype lưu bảng `corrective_actions` và chặn xuất/hoàn thành mẻ khi CCP fail.

Prototype **ánh xạ** biểu mẫu sang chức năng phần mềm và xuất PDF/CSV; **chưa thay thế** mẫu in chuẩn FSSC — cần validation ATTP trước go-live.

### 1.2.4. Hiện trạng CNTT (Excel, giấy, chưa ERP/MES tích hợp)

Khảo sát (`docs/khao-sat.md`, `docs/hien-trang-cntt.md`) cho thấy nhà máy Long An **chưa triển khai ERP/MES** tích hợp. Dữ liệu quản lý như sau:

**Bảng 1.3 — Hiện trạng công cụ CNTT theo bộ phận**

| Bộ phận | Công cụ | Tần suất / cách lưu |
|---------|---------|---------------------|
| Thủ kho | Excel, Google Sheets; giấy BM-01/GMP01 | Mỗi lô nhập; báo cáo tồn tuần/tháng |
| Kỹ thuật | Giấy BM-01/GMP03, BM-01/GMP04 | Mỗi mẻ SX |
| Lab | File GC trên PC; BM-02/GMP05 | Theo mẫu phân tích |
| QL NM | Excel tổng hợp, email | Báo cáo định kỳ |
| ATTP | Hồ sơ giấy + file rời nhiều phòng | Thẩm tra CCP 14 ngày |

**Hệ quả chính:**

- **P01** — Tồn kho cập nhật thủ công, dễ lệch số liệu giữa Excel và thực tế.
- **P02** — Khó truy xuất lô NVL → mẻ SX → TP khi có yêu cầu từ khách hàng hoặc ATTP.
- **P03** — Phiếu xuất kho không liên kết tự động với mẻ sản xuất.
- **P06** — Không cảnh báo tự động khi chỉ số CCP vượt giới hạn tới hạn.
- **P07** — Hồ sơ thẩm tra CCP phân tán; mất thời gian ghép chứng từ.
- Thiếu **audit trail** điện tử — khó chứng minh ai sửa dữ liệu, khi nào.

Đây là cơ sở phân tích as-is/to-be và thiết kế prototype web trong Chương 3.

### 1.2.5. Kết quả khảo sát / phỏng vấn (Thủ kho, Kỹ thuật, Lab, QL NM, ATTP)

Em tổng hợp khảo sát từ tài liệu nội bộ và nội dung **phỏng vấn mô phỏng** (synthesized) tại `docs/phong-van/` — **cần bổ sung biên bản phỏng vấn trực tiếp** khi có buổi tại nhà máy. Phương pháp: đọc Sổ tay ATTP, HACCP, quy trình SX; đối chiếu pain point với ma trận P01–P12.

**Bảng 1.2 — Tóm tắt pain point theo bộ phận**

| Bộ phận | Pain point chính | Mã vấn đề |
|---------|------------------|-----------|
| Thủ kho | Tồn thủ công; khó tìm lô khi xuất; nhập C14 tách file Lab | P01, P02 |
| Kỹ thuật | Operation record giấy, tách rời GC; cân đối NVL tính tay | P04, P05 |
| Lab | Nhập liệu lặp; kết quả chậm hiển thị với Kho/SX | P09 |
| QL NM | Thiếu dashboard; duyệt mẻ qua giấy/Excel | P08, P11 |
| ATTP | Hồ sơ CCP phân tán; không cảnh báo tự động; lo ngại validation PM (FSSC 8.7) | P06, P07 |

**Ưu tiên MVP (P0):** P01 tồn realtime, P02 truy xuất 2 chiều, P03 liên kết xuất–mẻ SX, P06 rule CCP tự động — đã đưa vào prototype (Chi tiết ma trận: Phụ lục I, Chương 2).

---

## 1.3. Mục tiêu thực tập

### 1.3.1. Mục tiêu chung

Phân tích hiện trạng quản lý kho và sản xuất tinh dầu tại Công ty TNHH Oxeyns – Chi nhánh Long An; thiết kế và xây dựng **prototype web** hỗ trợ quản lý lô hàng, mẻ sản xuất, giám sát CCP1/CCP2 và truy xuất nguồn gốc — làm cơ sở đề xuất triển khai chính thức sau giai đoạn thực tập.

### 1.3.2. Mục tiêu cụ thể

1. **Mô tả** quy trình sản xuất t-CA, hai CCP và luồng dữ liệu NVL → SX → TP.
2. **Khảo sát** biểu mẫu BM-xx/GMPxx và hiện trạng CNTT (Excel, giấy, file GC).
3. **Xác định** vấn đề nghiệp vụ qua ma trận P01–P12; lập yêu cầu FR/NFR.
4. **Thiết kế** CSDL 14 bảng, API REST (`/api/v1`), phân quyền 6 vai trò RBAC.
5. **Cài đặt** prototype: frontend **React 19 + TypeScript + Vite**; backend **FastAPI + SQLAlchemy 2**; CSDL **SQLite** (`oxeyns.db`).
6. **Kiểm thử** pytest (17 test case), UAT (10 kịch bản) và soạn tài liệu (user manual, validation draft FSSC 8.7).

---

## 1.4. Phạm vi thực tập

Phạm vi được thống nhất trong `docs/pham-vi-xac-nhan.md`:

**Bảng 1.4 — Phạm vi đề tài**

| Hạng mục | Trong phạm vi | Ngoài phạm vi |
|----------|---------------|---------------|
| Sản phẩm | t-CA | Các tinh dầu khác (sả, cam…) |
| Module | Kho, SX, Lab, Báo cáo/ATTP (11 menu) | ERP toàn tập đoàn |
| CCP | CCP1 (C14), CCP2 (Ttop, % t-CA) | Toàn bộ GMP1–7 chi tiết |
| Truy xuất | 2 chiều NVL ↔ TP | TT-TVTH thu hồi đầy đủ |
| Triển khai | Demo local SQLite (`oxeyns.db`) | Go-live; PostgreSQL (chưa triển khai) |
| Kiểm thử | pytest + UAT mô phỏng | Sign-off UAT có chữ ký NM |
| Validation | Draft IQ/OQ/PQ prototype | Validation ATTP chính thức |
| Tính năng | Nhập/xuất/tồn, mẻ SX, Lab, audit, PDF/CSV | GC auto-import, FIFO UI, mixing UI đầy đủ |

Giới hạn phạm vi giúp tập trung vào quick win P0, đủ demo và bảo vệ TTTN.

---

## 1.5. Phương pháp nghiên cứu

Đề tài kết hợp các phương pháp:

**1. Khảo sát tài liệu** — Đọc Sổ tay ATTP, chương trình thẩm tra HACCP (`docs/chuongtrinhthamtra.txt`), quy trình SX (`docs/quytrinhsanxuat.txt`), biểu mẫu `docs/bieu-mau/`.

**2. Tổng hợp ý kiến nghiệp vụ** — Nội dung synthesized từ năm bộ phận (`docs/phong-van/thu-kho.md`, `ky-thuat.md`, `lab.md`, `ql-nm.md`, `attp.md`).

**3. Phân tích hệ thống** — Mô hình as-is/to-be; ma trận vấn đề Impact × Effort (`docs/problem-matrix.md`); bảng yêu cầu FR/NFR (`docs/requirements.md`).

**4. Thiết kế giải pháp** — ERD 14 bảng (`docs/database-design.md`); đặc tả API (`docs/api-spec.md`); use case 11 menu / 6 role; wireframe (`docs/wireframes/`).

**5. Thực nghiệm phần mềm** — Cài đặt `backend/` và `frontend/`; seed dữ liệu demo; pytest (`backend/tests/`); UAT theo `docs/uat-results.md` và `code.txt`; luồng E2E: nhập NVL → CCP1 → mẻ SX → CCP2 → lô TP → truy xuất → audit.

Chuỗi thực hiện: **hiểu nghiệp vụ → xác định vấn đề → thiết kế → prototype → kiểm thử → báo cáo**.

---

## 1.6. Ý nghĩa khoa học và thực tiễn

**Về mặt khoa học**, đề tài minh họa cách liên kết **HACCP/FSSC 22000** với thiết kế phần mềm: rule CCP trong `ccp.py`, audit log, phân quyền RBAC và khung validation mục 8.7 — không chỉ “số hóa biểu mẫu” mà gắn ràng buộc an toàn thực phẩm vào logic hệ thống.

**Về mặt thực tiễn**:

- Giảm rủi ro sai lệch tồn kho và rút ngắn thời gian truy xuất lô khi thẩm tra hoặc đối tác yêu cầu.
- Hỗ trợ ATTP tập trung hồ sơ CCP, xuất biên bản 14 ngày từ màn Giám sát CCP.
- Chứng minh **giải pháp web nhẹ** (SQLite, FastAPI) khả thi cho SME; lộ trình sau TTTN có thể nâng cấp PostgreSQL và tích hợp GC (chưa thực hiện).
- Bàn giao mã nguồn (`backend/`, `frontend/`), CSDL demo (`oxeyns.db`) và bộ tài liệu kỹ thuật — tài sản tri thức cho Oxeyns khi quyết định pilot sau TTTN.

---

**Cấu trúc các chương tiếp theo:** Chương 2 trình bày cơ sở lý thuyết HACCP và stack kỹ thuật; Chương 3 mô tả thiết kế, cài đặt và kết quả thử nghiệm prototype; Chương 4 tổng kết, hạn chế và hướng phát triển.

## 1.7. Cập nhật phạm vi Digital QMS

Từ các gap của baseline — release chưa tách vai trò đầy đủ, xử lý sai lệch chưa có CAPA điện tử, chọn lô còn thủ công và truy xuất chưa có mô phỏng thu hồi — đề tài đã triển khai M1 Hold‑Release, M2 CAPA/NCR, M3 FEFO/Material Reservation và M4 Batch Passport/Recall Simulator. M5 GC Import/SPC và M6 trợ lý AI chỉ đọc cũng được triển khai như phần mở rộng độc lập.

Trạng thái “đã triển khai” chỉ mô tả mã nguồn và bằng chứng test tự động. Chưa có cơ sở để tuyên bố go-live, cải thiện thời gian hoặc chấp nhận nghiệp vụ: 20 trường hợp UAT trực tiếp, các phép đo và sign-off giảng viên/doanh nghiệp vẫn pending theo `docs/uat-results.md` và `docs/thesis-metrics.md`.
