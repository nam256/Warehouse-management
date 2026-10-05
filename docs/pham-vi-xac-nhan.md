# Phạm vi đề tài TTTN và luận văn Digital QMS

**Đề tài luận văn đề xuất:** Nghiên cứu và xây dựng hệ thống quản lý chất lượng số tích hợp Hold‑Release, CAPA, FEFO và mô phỏng thu hồi lô cho nhà máy tinh dầu — ứng dụng tại Oxeyns Long An  
**Đơn vị:** Công ty TNHH Oxeyns – Chi nhánh Long An  
**Ngày lập:** 20/06/2026  
**Ngày khóa đặc tả Digital QMS:** 18/07/2026  
**Trạng thái:** Đang triển khai tạm thời theo ủy quyền của người dùng; **chưa có xác nhận chính thức của giảng viên hướng dẫn/Gate G1**

> Tài liệu này phân biệt rõ prototype TTTN đã có và phần mở rộng mới của luận văn. Việc khóa đặc tả để chuẩn bị kỹ thuật không thay thế email, văn bản hoặc chữ ký chấp thuận của giảng viên.
>
> “Khóa” ở đây chỉ có nghĩa là dùng làm baseline kỹ thuật nhất quán khi triển khai; không có nghĩa là giảng viên đã phê duyệt đề tài.

---

## 1. Baseline TTTN đã có

| Hạng mục | Phạm vi | Ghi chú |
|----------|---------|---------|
| Phân tích hiện trạng | **Có** | Kho, SX, Lab, ATTP; sản phẩm trọng tâm **t-Cinnamic Aldehyde (t-CA)** |
| Đề xuất giải pháp | **Có** | Kiến trúc 4 module, ERD, API, luồng dữ liệu |
| Prototype / demo | **Có** | Web app MVP chạy local/Docker — **không thay thế ERP production** |
| Triển khai chính thức tại NM | **Ngoài phạm vi TTTN** | Lộ trình mô tả; vận hành thật do công ty quyết định sau UAT |

**Kết luận:** Báo cáo TTTN gồm **phân tích + đề xuất + minh chứng prototype**, không cam kết go-live toàn bộ nhà máy trong thời gian thực tập.

---

## 2. Phạm vi sản phẩm MVP baseline

### Trong phạm vi

- Đăng nhập, phân quyền RBAC (admin, thu_kho, ky_thuat, lab, ql_nm, attp)
- Module Kho: nhập/xuất/tồn theo lô, CCP1 (C14), cảnh báo tồn thấp, YCMH
- Module Sản xuất: lệnh/mẻ SX, operation record (T, P), CCP2 (Ttop, % t-CA)
- Module Lab: nhập GC data, liên kết CCP
- Module Báo cáo: dashboard, truy xuất lô 2 chiều, export CSV, audit log API
- Tài liệu: UAT, user manual, xác nhận phần mềm (FSSC 8.7) ở mức prototype

### Ngoài phạm vi MVP baseline

- Tích hợp trực tiếp máy GC
- TT-TVTH thu hồi/triệu hồi vận hành thật (luận văn chỉ bổ sung Recall Simulator read-only)
- Mixing report chi tiết (BM-01/GMP05) — mô tả trong thiết kế, chưa đủ UI
- Workflow duyệt lệnh SX nhiều cấp (nếu công ty chưa yêu cầu bắt buộc)
- Các tinh dầu khác (sả, cam, bạc hà…) — mở rộng sau khi ổn định t-CA

---

## 3. Phạm vi mới của luận văn Digital QMS

### 3.1 Lõi bắt buộc trước Gate G4

| Module | Phạm vi khóa | Điểm phân biệt với baseline TTTN |
|---|---|---|
| M1 Hold‑Release | Board chất lượng, lịch sử trạng thái, Release Certificate | Tách kết quả Lab khỏi quyết định sử dụng; Lab gửi, ATTP quyết định |
| M2 CAPA/NCR | Tạo tự động từ fail/reject, điều tra, hành động, xác minh, đóng | Theo dõi sai lệch đến khi hoàn tất, có idempotency và overdue |
| M3 FEFO/Reservation | Phân bổ nhiều lô theo hạn dùng, giữ chỗ atomic | Phân biệt on-hand/reserved/available và ngăn over-allocation |
| M4 QR/Recall | Batch Passport, QR, Recall Simulator downstream, CSV | Truy cập hồ sơ theo QR và mô phỏng phạm vi thu hồi nhiều tầng |

### 3.2 Quyết định nghiệp vụ không thay đổi khi code

- Hold‑Release là hai bước: `lab` gửi lô sang `awaiting_release`; `attp|admin` mới được quyết định `released|rejected`.
- Receipt nguyên liệu bắt đầu với `ccp1_status="pending"` và `quality_status="quarantine"`; thủ kho không được tự đánh giá/giải phóng CCP1.
- Thành phẩm sau CCP2 `pass` vẫn là `quality_status="awaiting_release"`, không auto-release.
- Issue/start chỉ dùng lô đã `released`, CCP đạt, chưa hết hạn và còn lượng khả dụng.
- Reservation phải atomic; thiếu tồn khả dụng thì rollback toàn bộ, không giữ chỗ một phần.
- Recall Simulator chỉ đọc đối với nghiệp vụ: không đổi tồn, reservation, chất lượng lô hoặc CAPA.
- Mỗi module phải ship API và UI cùng gate, dùng chung design system. Mọi thao tác async UI có `try/catch` và lỗi tiếng Việt thân thiện.

### 3.3 Mở rộng tùy chọn, độc lập sau Gate G4

- **M5 GC Import/SPC:** chỉ bắt đầu khi M1–M4 API+UI đã ổn định trên SQLite và PostgreSQL.
- **M6 trợ lý AI:** chỉ đọc đối với dữ liệu nghiệp vụ, tôn trọng JWT/RBAC và chỉ dùng API/tool whitelist. Không được gọi endpoint ghi nghiệp vụ, release/reject lô, thay đổi reservation hoặc xác minh/đóng CAPA; recall qua M6 chỉ là preview không lưu `RecallSimulation`. Chỉ metadata audit tối thiểu của truy vấn được phép ghi; M6 có thể tắt để demo offline.
- M5 và M6 có thể làm một, cả hai hoặc cắt bỏ; không được làm chậm bốn module lõi.

### 3.4 Ngoài phạm vi luận văn

- ERP kế toán, HR, mobile app, driver kết nối trực tiếp máy GC.
- Go-live internet/production hoặc thay thế hệ thống vận hành chính thức của nhà máy.
- Trợ lý AI ghi dữ liệu, tự quyết định chất lượng hoặc fine-tune model riêng.
- Recall vận hành thật tự động thay đổi tồn/trạng thái; M4 chỉ mô phỏng read-only.

---

## 4. Stack công nghệ định hướng

| Tầng | Công nghệ | Ghi chú |
|------|-----------|---------|
| Frontend | React + TypeScript + Vite | Giao diện tiếng Việt |
| Backend | FastAPI + SQLAlchemy | REST API, OpenAPI `/docs` |
| CSDL | SQLite và PostgreSQL 16 | SQLite cho dev/unit test; PostgreSQL cho integration, concurrency và demo |
| Auth | JWT + bcrypt | Role-based |
| DevOps | Docker Compose | DB + API + FE local |

**Dev chính:** triển khai core backend/frontend.  
**Sinh viên IT:** khảo sát, spec, UAT, tài liệu, đào tạo, hỗ trợ làm rõ yêu cầu.

---

## 5. Vai trò sinh viên (hỗ trợ IT)

- Khảo sát quy trình và tổng hợp phỏng vấn *(tài liệu tổng hợp — xem `docs/phong-van/`; đánh dấu synthesized)*
- Viết/soạn `docs/requirements.md`, test case UAT, user manual
- Phối hợp dev: clarify FR, map biểu mẫu BM-xx
- Demo và slide báo cáo trước GV / hội đồng
- **Không** chịu trách nhiệm solo toàn bộ codebase production

---

## 6. Hướng dẫn viên và trạng thái xác nhận

| Vai trò | Ghi nhận |
|---------|----------|
| GV hướng dẫn trường | *(Điền họ tên khi có xác nhận chính thức; hiện đang chờ sign-off Gate G1)* |
| Người hướng dẫn tại công ty | QL nhà máy / đại diện ATTP Oxeyns Long An |

---

## 7. Tiêu chuẩn và tuân thủ

- FSSC 22000, HACCP Codex — tham chiếu Sổ tay ATTP nội bộ
- Phần mềm giám sát CCP: mô tả trong `docs/software-validation.md` (mục 8.7)
- Truy xuất lô: thiết kế batch NVL → mẻ SX → lô TP

---

## 8. Chấp thuận (mẫu — chưa ký)

| Bên | Họ tên | Chữ ký | Ngày |
|-----|--------|--------|------|
| Sinh viên | | | |
| GV hướng dẫn | | | |
| Oxeyns (QL NM) | | | |

**Ghi nhận triển khai tạm thời:** người dùng đã ủy quyền tiếp tục chuẩn bị/triển khai kỹ thuật theo đặc tả trên trong khi chờ giảng viên xác nhận. Ô chữ ký trống có nghĩa là **chưa phê duyệt**, không được diễn giải thành đồng ý mặc nhiên.

*Tài liệu này phục vụ đính kèm báo cáo TTTN/luận văn; không phải biên bản go-live hoặc xác nhận vận hành production.*
