# PHẦN MỞ ĐẦU

> Điền họ tên, MSSV, ngày tháng, chữ ký trước khi nộp bản in.
>
> **Trạng thái phạm vi luận văn (18/07/2026):** đặc tả Digital QMS đang được chuẩn bị/triển khai tạm thời theo ủy quyền của người dùng. Giảng viên hướng dẫn chưa ký xác nhận Gate G1; nội dung dưới đây không được diễn giải là đã có phê duyệt của giảng viên.
>
> Các chỗ `[Họ tên…]`, `[Tên…]`, ngày và số trang ký hiệu `…` là metadata hành chính chưa được cung cấp, được giữ có chủ đích để điền trước khi nộp; chúng không phải placeholder của đặc tả nghiệp vụ.

---

## LỜI MỞ ĐẦU

Ngành hương liệu và tinh dầu thiên nhiên đang đối mặt áp lực ngày càng lớn về an toàn thực phẩm, truy xuất nguồn gốc và minh bạch hồ sơ chất lượng. Các doanh nghiệp vừa và nhỏ, dù quy mô nhân sự khiêm tốn, vẫn phải tuân thủ các khung tiêu chuẩn quốc tế như FSSC 22000, HACCP và các yêu cầu chứng nhận riêng (Kosher, Halal…). Việc quản lý thông tin kho bãi, sản xuất và kiểm nghiệm bằng Excel và biểu mẫu giấy tuy đủ dùng ở giai đoạn đầu, nhưng dần bộc lộ hạn chế khi cần đối chiếu lô hàng, giám sát điểm kiểm soát tới hạn (CCP) và chuẩn bị hồ sơ thẩm tra định kỳ.

Trong kỳ thực tập tốt nghiệp tại **Công ty TNHH Oxeyns – Chi nhánh Long An**, em được tiếp cận quy trình sản xuất **t-Cinnamic Aldehyde (t-CA)** từ tinh dầu quế — sản phẩm chủ lực của nhà máy. Oxeyns vận hành với khoảng sáu nhân sự trực tiếp thuộc các khâu kho, sản xuất, Lab và an toàn thực phẩm (ATTP), nhưng hệ thống ghi chép phân tán: Thủ kho dùng phiếu nhập BM-01/GMP01 và bảng tồn Excel; Kỹ thuật ghi operation record BM-01/GMP03 trên giấy; Lab lưu kết quả GC riêng; ATTP phải ghép chứng từ khi thẩm tra CCP mỗi 14 ngày. Từ thực tế đó, prototype TTTN ban đầu tập trung vào quản lý lô hàng, mẻ sản xuất và giám sát CCP1/CCP2. Đây là **baseline tái sử dụng**, không được trình bày như đóng góp mới của luận văn.

Trên nền baseline đó, hướng luận văn đề xuất là **“Nghiên cứu và xây dựng hệ thống quản lý chất lượng số tích hợp Hold‑Release, CAPA, FEFO và mô phỏng thu hồi lô cho nhà máy tinh dầu — ứng dụng tại Oxeyns Long An”**. Đóng góp mới gồm bốn module lõi: **M1 Hold‑Release**, **M2 CAPA/NCR**, **M3 FEFO/Material Reservation** và **M4 QR Batch Passport/Recall Simulator**. M5 GC Import/SPC và M6 trợ lý AI hỏi–đáp chỉ là mở rộng độc lập sau Gate G4; không thuộc điều kiện hoàn thành lõi.

Các quyết định nghiệp vụ được khóa như sau: Hold‑Release tách thành hai bước, Lab gửi duyệt và ATTP quyết định; thành phẩm sau CCP2 `pass` ở `awaiting_release`, không tự động `released`; reservation phải atomic và rollback toàn bộ khi thiếu tồn; Recall Simulator chỉ đọc đối với dữ liệu nghiệp vụ. M6, nếu triển khai, chỉ được truy vấn API theo JWT/RBAC và không được ghi trạng thái nghiệp vụ, release/reject lô hoặc xác minh/đóng CAPA; preview recall qua M6 không tạo hồ sơ mô phỏng, ngoài metadata audit tối thiểu bắt buộc. Mỗi module phải bàn giao API và UI trong cùng gate, dùng design system chung; mọi thao tác bất đồng bộ trên UI phải bắt lỗi bằng `try/catch` và hiển thị thông báo tiếng Việt thân thiện.

Về kỹ thuật, baseline đã có **frontend React 19 + TypeScript + Vite**, **backend FastAPI + SQLAlchemy 2**, sáu vai trò với JWT/bcrypt, audit, PDF/CSV và các kiểm thử đã ghi nhận cho phạm vi cũ. Luận văn sử dụng **SQLite** cho phát triển/unit test và **PostgreSQL 16** cho integration, kiểm tra concurrency và demo; cùng model/migration và business logic phải chạy trên cả hai. Các kết quả 17 pytest và 10 UAT được nêu trong tài liệu này chỉ là bằng chứng của **baseline TTTN**, không phải bằng chứng M1–M4 đã hoàn tất.

Báo cáo được trình bày theo **bốn chương**: Chương 1 — Tổng quát (công ty, quy trình t-CA, hiện trạng CNTT, mục tiêu và phạm vi); Chương 2 — Cơ sở lý thuyết (HACCP/FSSC, truy xuất lô, stack kỹ thuật); Chương 3 — Cài đặt thử nghiệm (as-is/to-be, thiết kế CSDL, kiến trúc, kết quả UAT); Chương 4 — Kết luận (đánh giá, hạn chế, hướng phát triển). Các phụ lục A–M đính kèm yêu cầu FR/NFR, đặc tả API, ERD, biểu mẫu BM-xx, kết quả UAT, hướng dẫn sử dụng và validation draft theo FSSC mục 8.7.

Em xin chân thành cảm ơn quý thầy cô và doanh nghiệp đã tạo điều kiện hoàn thành đề tài. Hy vọng báo cáo và prototype là tài liệu tham khảo hữu ích cho Oxeyns khi cân nhắc triển khai chính thức sau giai đoạn validation.

*TP. Hồ Chí Minh, tháng … năm 2026*  
*Sinh viên thực hiện: [Họ tên — MSSV]*  
*Giảng viên hướng dẫn: [Họ tên]*

---

## LỜI CẢM ƠN

Trước hết, em xin gửi lời cảm ơn sâu sắc đến **[Tên khoa — Tên trường]** đã tạo điều kiện cho em hoàn thành kỳ thực tập tốt nghiệp và bảo vệ đề tài.

Em xin chân thành cảm ơn **[Tên giảng viên hướng dẫn]** đã tận tình chỉ bảo về phương pháp nghiên cứu, cấu trúc báo cáo và định hướng kỹ thuật trong suốt quá trình thực hiện.

Em xin cảm ơn **Công ty TNHH Oxeyns – Chi nhánh Long An** đã tiếp nhận em thực tập, cung cấp tài liệu nội bộ về an toàn thực phẩm (Sổ tay ATTP, chương trình thẩm tra HACCP, quy trình sản xuất t-CA, bộ biểu mẫu BM-xx/GMPxx) và tạo điều kiện tìm hiểu nghiệp vụ thực tế tại nhà máy.

Em xin cảm ơn các anh chị thuộc bộ phận **Thủ kho, Kỹ thuật, Lab, Quản lý nhà máy và ATTP** đã chia sẻ kinh nghiệm vận hành, giúp em hiểu rõ pain point về tồn kho, truy xuất lô và giám sát CCP — là cơ sở để xác định yêu cầu phần mềm.

Cuối cùng, em cảm ơn **[người hướng dẫn tại doanh nghiệp / nhóm phát triển]** đã phối hợp triển khai prototype, phản hồi giao diện và hỗ trợ kiểm thử, giúp sản phẩm demo đạt được mục tiêu minh họa trong báo cáo TTTN.

---

## NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN

*(Để trống — giảng viên ký và ghi nhận xét sau khi sinh viên nộp bản in)*

| Mục | Nội dung |
|-----|----------|
| Đánh giá chung | |
| Điểm mạnh | |
| Điểm cần cải thiện | |
| Xác nhận | Đồng ý cho bảo vệ / Cần chỉnh sửa |
| Ngày | |
| Chữ ký | |

---

## NHẬN XÉT CỦA DOANH NGHIỆP

*(Để trống — đại diện Oxeyns ký sau buổi báo cáo thực tập)*

| Mục | Nội dung |
|-----|----------|
| Đánh giá về prototype | |
| Ý kiến triển khai tiếp theo | |
| Ngày | |
| Chữ ký | |

---

## LỊCH LÀM VIỆC THỰC TẬP

| Tuần | Thời gian | Nội dung công việc | Sản phẩm / kết quả |
|------|-----------|-------------------|---------------------|
| 1 | … | Làm quen công ty, đọc Sổ tay ATTP, HACCP; nắm quy trình t-CA | Ghi chú khảo sát ban đầu |
| 2 | … | Khảo sát quy trình kho, biểu mẫu nhập/tồn (BM-01/GMP01, BM-02/GMP01) | `docs/khao-sat.md` |
| 3 | … | Tổng hợp ý kiến 5 bộ phận: Thủ kho, KT, Lab, QL NM, ATTP | `docs/phong-van/` |
| 4 | … | Phân tích as-is/to-be; lập ma trận vấn đề P01–P12 | `docs/problem-matrix.md` |
| 5 | … | Thiết kế ERD 14 bảng, quy tắc mã lô/phiếu/mẻ SX | `docs/database-design.md` |
| 6 | … | Đặc tả API REST `/api/v1`, phân quyền RBAC | `docs/api-spec.md` |
| 7 | … | Cài đặt backend FastAPI: models, auth JWT, routers kho | `backend/app/` |
| 8 | … | Module sản xuất, Lab, rule CCP (`ccp.py`) | `backend/app/routers/`, `services/` |
| 9 | … | Frontend React: 11 menu, giao diện tiếng Việt | `frontend/src/pages/` |
| 10 | … | Báo cáo PDF/CSV, audit log, truy xuất lô; pytest | `reports.py`, `backend/tests/` |
| 11 | … | UAT 10 kịch bản, user manual, validation draft FSSC 8.7 | `docs/uat-results.md`, `software-validation.md` |
| 12 | … | Hoàn thiện báo cáo TTTN, slide demo, chuẩn bị bảo vệ | `docs/bao-cao/`, `demo-slides.md` |

---

## DANH MỤC HÌNH ẢNH, BẢNG BIỂU

| Ký hiệu | Tên hình / bảng | Trang |
|---------|-----------------|-------|
| Hình 1.1 | Sơ đồ tổ chức và luồng phối hợp Oxeyns Long An | … |
| Bảng 1.1 | Thông tin chung doanh nghiệp | … |
| Bảng 1.2 | Tóm tắt pain point theo bộ phận | … |
| Hình 2.1 | Chuỗi truy xuất lô NVL → mẻ SX → lô TP | … |
| Bảng 2.1 | Công nghệ sử dụng trong prototype | … |
| Bảng 2.2 | Ma trận vấn đề P01–P12 (Impact × Effort) | … |
| Hình 3.1 | Sơ đồ ERD — 14 bảng CSDL | … |
| Hình 3.2 | Use case tổng quát (11 menu, 6 vai trò) | … |
| Hình 3.3–3.16 | Sơ đồ tuần tự 14 luồng nghiệp vụ | … |
| Hình 3.17 | Sơ đồ trạng thái mẻ sản xuất | … |
| Hình 3.18 | Kiến trúc 3 tầng React — FastAPI — SQLite | … |
| Hình 3.19–3.29 | Giao diện 11 menu prototype | … |
| Bảng 3.1 | Kết quả UAT (10 kịch bản) | … |
| Bảng 3.2 | Kết quả pytest (17 test case) | … |
| Bảng 4.1 | Đánh giá mục tiêu đề tài | … |
| Bảng 4.2 | Hạn chế và hướng phát triển | … |

---

## DANH MỤC TỪ VIẾT TẮT

| Viết tắt | Tiếng Việt / Tiếng Anh |
|----------|-------------------------|
| API | Giao diện lập trình ứng dụng (Application Programming Interface) |
| ATTP | An toàn thực phẩm |
| BM-xx / GMPxx | Biểu mẫu / Thực hành sản xuất tốt (biểu mẫu nội bộ Oxeyns) |
| BTP | Bán thành phẩm |
| CCP | Điểm kiểm soát tới hạn (Critical Control Point) |
| CNTT | Công nghệ thông tin |
| CSV | Giá trị phân tách bằng dấu phẩy (Comma-Separated Values) |
| ERD | Sơ đồ thực thể – liên kết (Entity-Relationship Diagram) |
| FR / NFR | Yêu cầu chức năng / phi chức năng |
| FSSC | Hệ thống chứng nhận an toàn thực phẩm |
| GC | Sắc ký khí (Gas Chromatography) |
| GMP | Thực hành sản xuất tốt (Good Manufacturing Practice) |
| HACCP | Phân tích mối nguy và điểm kiểm soát tới hạn |
| IQ / OQ / PQ | Xác nhận lắp đặt / vận hành / hiệu năng (validation) |
| JWT | JSON Web Token |
| Lab | Phòng kiểm nghiệm |
| MVP | Sản phẩm khả dụng tối thiểu (Minimum Viable Product) |
| NVL | Nguyên liệu |
| ORM | Ánh xạ đối tượng – quan hệ (SQLAlchemy) |
| PDF | Định dạng tài liệu Portable Document Format |
| RBAC | Phân quyền theo vai trò (Role-Based Access Control) |
| REST | Kiến trúc truyền tải đại diện trạng thái (API HTTP) |
| SME | Doanh nghiệp vừa và nhỏ |
| SQL | Ngôn ngữ truy vấn có cấu trúc |
| SX | Sản xuất |
| t-CA | t-Cinnamic Aldehyde |
| TP | Thành phẩm |
| TTTN | Thực tập tốt nghiệp |
| UAT | Kiểm thử chấp nhận người dùng (User Acceptance Testing) |
| UI | Giao diện người dùng |
| YCMH | Yêu cầu mua hàng |

---

## TÓM TẮT (ABSTRACT)

### Tiếng Việt

Báo cáo nghiên cứu hướng xây dựng lớp **Digital QMS** trên prototype quản lý kho–sản xuất–Lab tại **Công ty TNHH Oxeyns – Chi nhánh Long An**. Baseline TTTN đã số hóa một phần lô hàng, mẻ sản xuất, CCP1/CCP2, truy xuất hai chiều, RBAC và audit; các chức năng này là nền tái sử dụng, không phải đóng góp mới của luận văn.

Phạm vi mới gồm bốn module lõi: Hold‑Release hai bước Lab–ATTP; CAPA/NCR điện tử; FEFO kết hợp giữ chỗ nguyên liệu atomic; và QR Batch Passport kết hợp Recall Simulator read-only. GC Import/SPC và trợ lý AI chỉ đọc là mở rộng tùy chọn sau Gate G4. Kiến trúc dùng React/TypeScript, FastAPI/SQLAlchemy, SQLite cho phát triển và unit test, PostgreSQL 16 cho integration, concurrency và demo. API và UI được phát triển đồng bộ theo module, có RBAC, audit và xử lý lỗi tiếng Việt thân thiện.

Các số liệu **17/17 pytest** và **10/10 UAT** trước đây chỉ phản ánh baseline TTTN trên demo local. Đến Task 10, M1–M6 đã được triển khai và SQLite profile ghi nhận **46 test pass**; đây là bằng chứng kỹ thuật, không phải UAT con người. UAT trực tiếp, phép đo thời gian, PostgreSQL/Playwright full-stack và sign-off giảng viên/doanh nghiệp vẫn đang chờ; vì vậy kết quả Digital QMS được trình bày ở trạng thái provisional.

**Từ khóa:** Digital QMS; Hold‑Release; CAPA/NCR; FEFO; material reservation; batch passport; recall simulator; FastAPI; React; SQLite; PostgreSQL.

### English

This thesis proposes a Digital QMS layer on top of the existing warehouse–production–laboratory internship prototype at Oxeyns Long An. The mandatory new scope comprises two-step Lab–Food Safety Hold‑Release, electronic CAPA/NCR, FEFO with atomic material reservation, and a QR Batch Passport with a read-only Recall Simulator. GC Import/SPC and a read-only AI assistant are optional extensions after Gate G4. The architecture uses React/TypeScript and FastAPI/SQLAlchemy, with SQLite for development and unit tests and PostgreSQL 16 for integration, concurrency testing, and the defense demo.

The previously recorded 17/17 pytest and 10/10 UAT results apply only to the internship baseline. By Task 10, M1–M6 had been implemented and the SQLite profile recorded 46 passing tests; this is technical evidence, not human UAT. Manual UAT, timed measurements, full-stack PostgreSQL/Playwright evidence, and supervisor/company sign-off remain pending, so Digital QMS conclusions are provisional.

**Keywords:** Digital QMS; Hold‑Release; CAPA/NCR; FEFO; material reservation; batch passport; recall simulator; FastAPI; React; SQLite; PostgreSQL.
