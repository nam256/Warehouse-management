# Oxeyns Digital QMS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây bốn module mới mang tính luận văn trên nền prototype TTTN: Quality Hold‑Release, CAPA/NCR điện tử, FEFO + giữ chỗ nguyên liệu, và QR Batch Passport + Recall Simulator; GC Import/SPC chỉ triển khai khi bốn module chính đã ổn định.

**Architecture:** Giữ kiến trúc React SPA → FastAPI REST API → SQLAlchemy và hỗ trợ hai hệ quản trị CSDL qua cùng model/migration. SQLite dùng cho phát triển local, unit test và pytest in-memory; PostgreSQL 16 dùng cho integration test, kiểm tra concurrency, Docker và demo bảo vệ. Các module luận văn nằm trong service, router, model và màn hình riêng; hệ thống kho–sản xuất–Lab cũ chỉ cung cấp dữ liệu và điểm tích hợp.

**Tech Stack:** React 19, TypeScript 5.8, Vite 6, FastAPI, SQLAlchemy 2, Pydantic 2, SQLite 3, PostgreSQL 16, Alembic, JWT/RBAC, ReportLab, pytest, Playwright, Docker Compose; pgAdmin4 chỉ dùng để quản trị/xem PostgreSQL.

## Global Constraints

- Hướng đề tài đã chốt: **Digital QMS**.
- Phạm vi chính bắt buộc: **M1 Hold‑Release, M2 CAPA/NCR, M3 FEFO/Reservation, M4 QR Recall**.
- Phạm vi mở rộng độc lập sau Gate G4: **M5 GC Import/SPC**, **M6 Trợ lý AI hỏi–đáp (read-only)**, và **M7 Hồ sơ / quản lý tài khoản / ảnh vật tư**.
- M6 phải chỉ đọc, tôn trọng RBAC, không bịa số liệu và tắt được để demo offline.
- M7: **không đăng ký công khai**; chỉ admin tạo tài khoản; user tự xem hồ sơ/đổi mật khẩu; vật tư có ảnh hiển thị trên kho.
- Không phát triển ERP kế toán, HR, mobile app, driver kết nối trực tiếp máy GC hoặc triển khai internet production.
- UI và báo cáo dùng tiếng Việt; enum, API và tên code dùng tiếng Anh nhất quán.
- **UI làm theo bước cùng chức năng:** mỗi module phải ship API + màn hình đồng bộ trong cùng task/gate; cấm để “làm xong backend rồi sửa giao diện sau”.
- Mọi màn hình mới phải dùng chung design tokens và component shell ở mục 0b; không viết CSS ad-hoc lệch style.
- **Mọi gọi API và thao tác UI phải bọc `try/catch`:** không để exception hiện thô trên màn hình, console-only, hoặc làm trắng trang; luôn hiện thông báo tiếng Việt qua `AlertBanner`/`Toast` (mục 0b.5).
- Mọi module mới phải có API, UI, RBAC, audit log, test tự động, UAT và chỉ số đánh giá.
- Không cho phép thủ kho tự đánh giá hoặc giải phóng CCP1.
- Không dùng đồng thời migration thủ công trong `app/migrate.py` và Alembic sau Task 2.
- Mọi model/query phải chạy được trên cả SQLite và PostgreSQL; tính năng khóa dòng/concurrency chỉ được xác nhận trên PostgreSQL.
- Không viết hai nhánh business logic riêng cho hai CSDL; khác biệt được cô lập tại cấu hình DB và transaction/locking adapter.
- Không tuyên bố UAT hoặc chỉ số “đạt” trước khi chạy và ghi bằng chứng thật.
- Mỗi task phải giữ toàn bộ backend test xanh và frontend build thành công.

---

## ✅ CHECKLIST TỔNG HỢP (cập nhật 2026-08-16)

`[x]` = xong · `[ ]` = còn lại

### Ba chức năng bạn yêu cầu (M7)

- [x] **Profile người đăng nhập** — click tên user → `/profile` (đổi tên, mật khẩu, avatar)
- [x] **Không đăng ký công khai** (đã chốt) — admin tạo/khóa tài khoản tại `/users`
- [x] **Ảnh sản phẩm / vật tư — Thêm / Đổi / Xóa** trên **Tồn kho**  
  (admin / thủ kho / QL nhà máy); hiện thumbnail ở Nhập kho & Xuất kho; ảnh demo PNG đã seed

### Module khác đã xong

- [x] M1 Hold‑Release
- [x] M2 CAPA/NCR
- [x] M3 FEFO / giữ chỗ
- [x] M4 QR / Recall
- [x] M5 GC Import / SPC
- [x] M6 Trợ lý AI (chỉ đọc)
- [x] Gate kỹ thuật G0, G1.5, G2, G3, G4
- [x] Test M7 8/8 pass + build frontend OK

### Còn lại (không phải code)

- [ ] G1 — GV ký / email xác nhận đề cương
- [ ] G5 — UAT người thật + đo thời gian
- [ ] Chụp screenshot M7 (`docs/screenshots/m7-profile/`)
- [ ] Backup PostgreSQL trước bảo vệ
- [ ] Tập demo 5 phút
- [ ] (Tuỳ chọn) Docker Desktop

Chi tiết checklist dài: xem **§11** bên dưới.

---

## 0. Chiến lược dùng cả SQLite và PostgreSQL

### 0.1 Vai trò của từng CSDL

| Môi trường | CSDL | Mục đích | Cách chạy |
|---|---|---|---|
| Dev nhanh | SQLite file `backend/oxeyns.db` | Code UI/API, dữ liệu demo cá nhân, không cần server | `DATABASE_URL=sqlite:///./oxeyns.db` |
| Unit/API test | SQLite in-memory | Chạy pytest nhanh, cô lập từng test | `sqlite://` + `StaticPool` |
| Integration test | PostgreSQL 16 | Migration, enum, FK, transaction, row lock và concurrency | Docker service `db-test` |
| Demo bảo vệ | PostgreSQL 16 | Dữ liệu chính thức, chạy full stack | Docker Compose `db + api + web` |
| Quản trị demo | pgAdmin4 | Xem bảng/query/backup PostgreSQL | Công cụ phụ, không phải CSDL |

### 0.2 Quy tắc tương thích hai CSDL

1. SQLAlchemy model và Pydantic schema là nguồn sự thật chung.
2. Alembic phải nâng cấp được DB SQLite sạch và PostgreSQL sạch đến cùng revision.
3. Unit test chạy SQLite; integration test quan trọng chạy lại PostgreSQL.
4. Không dùng SQL riêng PostgreSQL trong service nghiệp vụ nếu SQLAlchemy có biểu thức tương đương.
5. FEFO sort null dùng biểu thức tương thích; nếu `NULLS LAST` khác nhau thì chuẩn hóa bằng `CASE`.
6. Reservation dùng transaction chung. PostgreSQL thêm `SELECT FOR UPDATE`; SQLite chỉ kiểm logic tuần tự, không dùng để chứng minh chống race condition.
7. Enum phải giữ cùng giá trị API; test migration trên PostgreSQL để phát hiện khác biệt enum native.
8. Tiền/số lượng dùng `Numeric`, ngày dùng `Date/DateTime`; không dựa vào kiểu động của SQLite.
9. CI chỉ đạt khi SQLite test và PostgreSQL integration test đều xanh.
10. Báo cáo ghi rõ SQLite là môi trường dev/test nhanh, PostgreSQL là môi trường triển khai và đánh giá concurrency.

### 0.3 Cấu hình dự kiến

```env
# Phát triển nhanh bằng SQLite
DATABASE_URL=sqlite:///./oxeyns.db

# Integration/demo bằng PostgreSQL
DATABASE_URL=postgresql+psycopg2://oxeyns:oxeyns@localhost:5432/oxeyns
```

Không commit file `.env` thật hoặc mật khẩu production. Các giá trị trên chỉ dùng local/demo.

---

## 0b. Giao diện đồng bộ — làm theo bước, không để cuối

### 0b.1 Nguyên tắc

1. **UI cùng sprint với API:** mỗi module M1–M6 chỉ đóng task khi có màn hình dùng được, không chỉ API.
2. **Shell trước, feature sau:** Task 1.5 khóa design system trước khi code M1; mọi màn hình mới chỉ dùng token/component đã khóa.
3. **Một look cho cả hệ thống cũ và mới:** khi thêm màn hình Digital QMS, đồng thời áp cùng shell cho các trang TTTN đang mở (Inventory, StockIn/Out, Production, Lab, Trace) để demo không bị “hai giao diện”.
4. **Không polish sau cùng:** tuần cuối chỉ chỉnh lỗi và screenshot; không redesign.
5. **Checklist UI bắt buộc trước khi tick xong task chức năng** (mục 0b.3).

### 0b.2 Design tokens và component dùng chung

| Thành phần | File | Nội dung khóa |
|---|---|---|
| Tokens | `frontend/src/styles/tokens.css` | màu primary/success/warning/danger, spacing, radius, font, shadow |
| Shell layout | `frontend/src/Layout.tsx` + `index.css` | sidebar, topbar, content width, active nav |
| UI primitives | `frontend/src/components/ui/` | `PageHeader`, `StatusBadge`, `DataTable`, `EmptyState`, `AlertBanner`, `ActionBar`, `FilterBar`, `Modal`, `Toast` |
| Status map | `frontend/src/ui/status.ts` | map `quality_status` / `capa_status` → label tiếng Việt + màu badge |

**Bảng màu trạng thái (khóa):**

| Status | Badge class | Màu ý nghĩa |
|---|---|---|
| `quarantine` / `open` | `badge-warn` | vàng — chờ xử lý |
| `under_test` / `investigating` | `badge-info` | xanh dương — đang làm |
| `awaiting_release` / `verification` | `badge-accent` | tím nhạt — chờ duyệt |
| `released` / `closed` / `pass` | `badge-ok` | xanh lá — đạt |
| `rejected` / `fail` / `overdue` | `badge-danger` | đỏ — lỗi/quá hạn |
| `retest` / `action_pending` | `badge-neutral` | xám — vòng lại |

**Cấu trúc trang chuẩn:**

```text
PageHeader (tiêu đề + mô tả ngắn + primary actions)
FilterBar (tìm kiếm / filter trạng thái)
AlertBanner (lỗi/thành công từ API)
DataTable hoặc Kanban board
EmptyState khi không có dữ liệu
```

### 0b.3 Checklist UI đóng task (bắt buộc)

Trước khi commit “feat hoàn tất module”, phải tick:

```text
[x] Dùng PageHeader / StatusBadge / DataTable / EmptyState / AlertBanner — không copy style inline lệch
[x] Nhãn tiếng Việt; trạng thái có badge đúng bảng màu
[x] Loading, empty, error đều có UI (không chỉ console/alert)
[x] Mọi async handler (load/submit/transition) bọc try/catch; không để lỗi thô lên màn hình
[x] Lỗi API hiện AlertBanner tiếng Việt; thành công nhẹ dùng Toast nếu cần
[x] Nút hành động theo role: ẩn nếu không có quyền; backend vẫn là nguồn bảo vệ
[x] Desktop ≥1280px và tablet ~768px không vỡ layout chính
[x] npm run build thành công
[x] Screenshot màn hình mới lưu vào docs/screenshots/<module>/
```

### 0b.4 Deliverable UI theo từng module (ship cùng API)

| Module | UI phải có trong cùng task với API | Không được để sau |
|---|---|---|
| Nền UI | Task 1.5: tokens + components + ErrorBoundary + áp shell cho Layout/Dashboard | Redesign toàn cục cuối kỳ |
| M1 | `/quality` board + badge trên Inventory/StockOut | “API xong rồi làm board sau” |
| M2 | `/capa` tabs + badge overdue trên Dashboard | Form CAPA tạm thô |
| M3 | cột expiry/available + nút Gợi ý FEFO + panel reservation | Chỉ API suggest |
| M4 | passport card + QR + panel recall + nút CSV | Chỉ endpoint |
| M5 | tab Import + panel SPC | Chỉ backend import |
| M6 | AssistantWidget đồng bộ màu shell | Widget lệch theme |

### 0b.5 Xử lý lỗi UI — bắt buộc `try/catch` (không để lỗi thô trên màn hình)

**Mục tiêu:** người dùng không bao giờ thấy stack trace, JSON thô, `Unhandled Rejection`, hoặc trang trắng. Mọi lỗi hiện thông báo tiếng Việt rõ ràng.

**Quy tắc:**

1. Mọi hàm `async` trong page/component (load dữ liệu, submit, transition, upload, chat) phải bọc `try/catch`.
2. Trong `catch`: set state lỗi tiếng Việt → render `AlertBanner`; **không** `throw` lại lên UI; **không** chỉ `console.error` rồi thôi.
3. `api.ts` tiếp tục `throw new Error(message)` sau `parseError`; tầng UI mới là nơi `catch`.
4. Có `ErrorBoundary` bọc routes trong `App.tsx` để bắt lỗi render React, hiện fallback thân thiện + nút “Tải lại”.
5. Khi đang gọi API: disable nút submit / hiện loading; khi lỗi: giữ dữ liệu form, không xóa input của người dùng.
6. Map lỗi thường gặp:
   - `403` → “Bạn không có quyền thực hiện thao tác này.”
   - `401` → chuyển login (đã có `auth:expired`).
   - `400` → hiện `detail` từ backend nếu là chuỗi tiếng Việt; không hiện object JSON.
   - Network/`TypeError: Failed to fetch` → “Không kết nối được máy chủ. Kiểm tra backend đang chạy.”
   - Timeout/provider AI → “Trợ lý tạm thời không khả dụng.” (M6)
7. Backend FastAPI: endpoint mới cũng dùng `try/except` quanh service; trả `HTTPException` có `detail` tiếng Việt, không để 500 lộ traceback ra client.

**Mẫu bắt buộc cho mọi page:**

```tsx
const [error, setError] = useState<string | null>(null);
const [busy, setBusy] = useState(false);

async function onSubmit() {
  setError(null);
  setBusy(true);
  try {
    await someApiCall(payload);
    setError(null);
    // optional: Toast success
  } catch (err) {
    const message =
      err instanceof Error && err.message
        ? err.message
        : "Đã xảy ra lỗi. Vui lòng thử lại.";
    setError(message);
  } finally {
    setBusy(false);
  }
}

return (
  <>
    {error && <AlertBanner tone="danger" onClose={() => setError(null)}>{error}</AlertBanner>}
    <button disabled={busy} onClick={() => void onSubmit()}>
      {busy ? "Đang xử lý…" : "Xác nhận"}
    </button>
  </>
);
```

**ErrorBoundary tối thiểu (Task 1.5):**

```tsx
// frontend/src/components/ui/ErrorBoundary.tsx
import { Component, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card" role="alert">
          <h2>Đã xảy ra lỗi giao diện</h2>
          <p>Trang gặp sự cố bất ngờ. Hãy tải lại hoặc quay về trang chủ.</p>
          <button type="button" onClick={() => window.location.assign("/")}>
            Về trang chủ
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

**Cấm:**

- `onClick={async () => await api()}` không có `try/catch`.
- Hiện `String(err)` / `JSON.stringify(err)` / stack lên DOM.
- Để React error overlay / trang trắng là “cách báo lỗi” cho người dùng cuối.

---

## 1. Đề tài và đóng góp mới

### 1.1 Tên đề tài đề xuất

**Nghiên cứu và xây dựng hệ thống quản lý chất lượng số tích hợp Hold‑Release, CAPA, FEFO và mô phỏng thu hồi lô cho nhà máy tinh dầu — ứng dụng tại Oxeyns Long An**

### 1.2 Prototype TTTN đã có

| Nhóm | Chức năng hiện có | Điểm neo |
|---|---|---|
| Xác thực | JWT, bcrypt, 6 vai trò | `backend/app/core/security.py` |
| Kho | Nhập, xuất, tồn, batch | `backend/app/routers/stock.py` |
| Sản xuất | Tạo, duyệt, chạy, operation, hoàn thành | `backend/app/routers/production.py` |
| Lab/CCP | Nhập kết quả, rule CCP1/CCP2 | `backend/app/routers/lab.py`, `backend/app/services/ccp.py` |
| Truy xuất | Truy xuất hai chiều theo batch | `backend/app/routers/reports.py` |
| Báo cáo | PDF, CSV, audit | `backend/app/routers/reports.py` |

Các chức năng trên là **nền tái sử dụng**, không được trình bày như đóng góp mới của luận văn.

### 1.3 Chức năng mới của luận văn

#### Ma trận tổng quan cũ → mới

| Nghiệp vụ | Hệ thống cũ (TTTN) | Chức năng mới (luận văn) | Khác biệt có thể chứng minh |
|---|---|---|---|
| Trạng thái lô | Chỉ có `ccp1_status=pending/pass/fail`; không có trạng thái giải phóng | M1 thêm `quality_status` và board Hold‑Release | Kết quả kiểm nghiệm và quyết định sử dụng được tách thành hai khái niệm |
| Nhập kho | Thủ kho nhập C14 và hệ thống đánh CCP1 ngay | Receipt luôn tạo lô `quarantine`; Lab mới được ghi kết quả | Loại bỏ việc thủ kho tự “pass” chất lượng |
| Phê duyệt chất lượng | Không có quy trình ký duyệt độc lập | Lab gửi duyệt, ATTP release/reject; lưu lịch sử và chữ ký role | Có segregation of duties và audit trail |
| Chứng nhận lô | Chỉ có PDF báo cáo rời | Release Certificate/CoA PDF gắn lô và hai người duyệt | Có chứng từ giải phóng lô truy xuất được |
| Sai lệch chất lượng | `corrective_actions` chỉ list/create, chưa có UI/workflow | M2 tự tạo NCR/CAPA khi CCP fail; điều tra, hành động, xác minh, đóng | Mọi fail được theo dõi đến khi xử lý hoàn tất |
| Cảnh báo quá hạn | Không có | CAPA quá hạn hiển thị đỏ và trên dashboard | Quản lý thời hạn khắc phục |
| Chọn lô xuất | Batch chỉ được sort FIFO; người dùng tự chọn | M3 phân bổ FEFO theo hạn dùng và quality gate | Ưu tiên đúng lô hết hạn sớm nhất |
| Tồn khả dụng | Chỉ có quantity hiện tại | `available = on_hand - active_reserved` | Phân biệt tồn vật lý và tồn có thể cấp |
| Duyệt lệnh SX | Không giữ trước NVL; nhiều lệnh có thể cùng nhìn thấy một tồn | Approve tạo reservation atomic; start consume; cancel release/reverse | Ngăn over-allocation và giảm thiếu hàng giả |
| Truy xuất lô | Nhập batch để xem cây upstream/downstream | M4 tạo Batch Passport có QR | Truy cập hồ sơ lô bằng quét mã |
| Thu hồi | Chưa có quy trình mô phỏng | Recall Simulator BFS liệt kê mọi lô/mẻ downstream và xuất CSV | Đo được độ đầy đủ và thời gian thu hồi |
| Lab | Nhập kết quả thủ công từng form | M5 import CSV GC atomic, chống trùng | Giảm thời gian và lỗi nhập liệu |
| Phân tích chất lượng | Chỉ kiểm từng điểm theo ngưỡng CCP | M5 tính mean, σ, UCL/LCL và cảnh báo xu hướng | Phát hiện bất thường theo chuỗi dữ liệu |
| Tra cứu thông tin | Người dùng tự bấm menu và lọc bằng tay | M6 trợ lý AI hỏi–đáp tiếng Việt, gọi API sẵn có theo đúng quyền | Rút ngắn thời gian tìm thông tin vận hành |
| CSDL | SQLite file local | SQLite cho dev/test + PostgreSQL cho integration/demo | Có kiểm thử portability và concurrency thực tế |
| Triển khai | Uvicorn/Vite local, Compose mới có DB | Docker full stack, Alembic, CI chạy hai CSDL, Playwright | Môi trường demo tái lập được |

#### M1 — Những phần hoàn toàn mới

- Board `/quality` theo cột trạng thái và bộ lọc.
- `quality_status` độc lập với `ccp1_status`.
- Quy trình hai bước Lab submit → ATTP approve/reject.
- `BatchStatusHistory` bất biến và `QualityApproval`.
- Chặn issue/start khi lô chưa released.
- Release Certificate PDF.

#### M2 — Những phần hoàn toàn mới

- CAPA/NCR được sinh tự động từ LabTest fail, OperationRecord fail hoặc reject lô.
- State machine `open → investigating → action_pending → verification → closed`.
- Root cause, due date, action, disposition, verification và người đóng.
- Chống tạo trùng CAPA cho cùng một nguồn fail.
- Màn `/capa`, bộ lọc overdue và liên kết ngược về nguồn lỗi.

#### M3 — Những phần hoàn toàn mới

- Ngày sản xuất/hạn dùng trên batch.
- Thuật toán phân bổ nhiều lô theo FEFO thay vì chỉ sort danh sách.
- Reservation theo lệnh sản xuất.
- Hiển thị on-hand, reserved và available.
- Transaction/row lock PostgreSQL chống hai lệnh giữ cùng tồn.
- Cancel khôi phục tồn bằng movement đảo chiều, không xóa lịch sử.

#### M4 — Những phần hoàn toàn mới

- Batch Passport tổng hợp kho, chất lượng, sản xuất và certificate.
- QR dẫn tới đúng passport của batch.
- Recall Simulator duyệt toàn bộ downstream nhiều tầng.
- Ghi thời gian chạy, người khởi tạo và lý do mô phỏng.
- Kết quả phân tầng và export CSV.

#### M5 — Những phần hoàn toàn mới (sau Gate G4)

- Upload file CSV chuẩn GC thay cho nhập từng form.
- Validate toàn bộ file trước khi ghi và rollback nếu có dòng lỗi.
- SHA‑256 chống import trùng.
- SPC mean ± 3σ và đánh dấu điểm out-of-control.
- So sánh thời gian nhập tay và import trong phần đánh giá.

#### M6 — Trợ lý AI hỏi–đáp (mở rộng, sau Gate G4)

- Ô chat tiếng Việt trả lời câu hỏi vận hành: tồn kho, trạng thái lô, CAPA, truy xuất, hạn dùng.
- Chỉ đọc: trợ lý gọi các API sẵn có, không thực hiện hành động ghi (không release lô, không đóng CAPA).
- Tôn trọng RBAC: dùng đúng JWT của người đang đăng nhập; không trả dữ liệu ngoài quyền.
- Không bịa số liệu: mọi câu trả lời phải dựa trên kết quả API thật; không có dữ liệu thì trả lời “không tìm thấy”.
- Có thể cắt hoàn toàn mà không ảnh hưởng M1–M5; đây là lớp trải nghiệm, không phải chức năng lõi.

#### M7 — Hồ sơ, quản lý tài khoản, ảnh vật tư (mở rộng, sau Gate G4)

- **Không** form đăng ký công khai (phù hợp nhà máy / QMS).
- User đăng nhập xem **Hồ sơ** (`/profile`): họ tên, vai trò, đổi mật khẩu, avatar tuỳ chọn.
- **Admin** quản lý tài khoản (`/users`): tạo user, chọn vai trò, khóa/mở `is_active`.
- Vật tư/sản phẩm có **ảnh** (`image_url` hoặc upload local); hiện thumbnail trên tồn kho, nhập kho, xuất kho.
- Đặc tả chi tiết: `docs/superpowers/specs/2026-08-16-m7-profile-users-product-images-design.md`.

### 1.4 Câu trả lời ngắn khi hội đồng hỏi “Em làm mới gì?”

> Em xây dựng lớp Digital QMS gồm Hold‑Release hai bước, CAPA/NCR điện tử, FEFO có giữ chỗ nguyên liệu và mô phỏng thu hồi bằng QR; các module này tích hợp lên hệ thống kho–sản xuất đã hoàn thành trong kỳ thực tập.

### 1.5 Câu hỏi nghiên cứu

1. Hold‑Release hai bước có chặn 100% trường hợp dùng lô chưa được ATTP giải phóng không?
2. CAPA/NCR có bảo đảm mọi CCP fail đều có hồ sơ xử lý và không thể đóng thiếu disposition không?
3. FEFO + reservation có chọn đúng lô còn hạn sớm nhất và ngăn hai lệnh sản xuất giữ cùng một lượng tồn không?
4. Recall Simulator có tìm đủ tập lô/mẻ downstream trong không quá 3 giây trên dữ liệu demo không?
5. Nếu triển khai M5: GC Import có giảm ít nhất 50% thời gian nhập 10 kết quả so với nhập tay không?

---

## 2. Thiết kế chức năng đã chốt

### M1 — Quality Hold‑Release Board

**Màn hình:** `/quality`

**Luồng trạng thái:**

```text
quarantine → sampling → under_test → awaiting_release → released
                                  └→ rejected
                                  └→ retest → under_test
```

**Phân quyền:**

- `thu_kho`: tạo receipt; chỉ xem trạng thái.
- `lab`: chuyển `quarantine → sampling → under_test`; ghi kết quả; gửi `awaiting_release`.
- `attp`: chuyển `awaiting_release → released|rejected`; yêu cầu nhập lý do và xác nhận điện tử.
- `admin`: có quyền tương đương ATTP để phục vụ demo.
- `ky_thuat`, `ql_nm`: chỉ xem.

**Luật nghiệp vụ:**

- Receipt NVL luôn tạo `ccp1_status=pending`, `quality_status=quarantine`.
- `awaiting_release` chỉ hợp lệ khi có LabTest CCP1 `pass`.
- Issue/start sản xuất chỉ dùng lô `quality_status=released`, `ccp1_status=pass`, chưa hết hạn.
- Mỗi transition ghi `BatchStatusHistory`, `AuditLog`, người thực hiện và thời gian.
- Thành phẩm sau complete có CCP2 pass được tạo `awaiting_release`; ATTP phải giải phóng trước khi xuất thành phẩm.

**Đầu ra mới:** Batch Release Certificate PDF gồm mã lô, kết quả CCP, người Lab gửi duyệt, người ATTP giải phóng và thời gian ký.

### M2 — CAPA/NCR điện tử

**Màn hình:** `/capa`

**Luồng trạng thái:**

```text
open → investigating → action_pending → verification → closed
```

**Nguồn tạo tự động:**

- LabTest CCP1 hoặc CCP2 `fail`.
- OperationRecord CCP2 `fail`.
- ATTP reject lô tại Hold‑Release.

**Trường bắt buộc:**

- `title`, `source_type`, `source_id`, `reason`
- `root_cause`, `action_taken`, `due_date`
- `disposition`: `retest|rework|reject|use_as_is`
- `verified_by_id`, `closed_by_id`, `closed_at`

**Luật nghiệp vụ:**

- Một nguồn fail chỉ tạo một CAPA đang mở; endpoint phải idempotent.
- `lab|ky_thuat` được cập nhật điều tra/hành động theo nguồn.
- Chỉ `attp|admin` được xác minh và đóng.
- Không đóng nếu thiếu root cause, action, disposition hoặc verification.
- `use_as_is` yêu cầu `attp` và ghi rõ justification.
- CAPA quá hạn được tô đỏ trên UI và hiển thị dashboard.

### M3 — Smart Warehouse FEFO + Reservation

**Màn hình:** mở rộng `/inventory`, `/stock-out`, `/production`.

**Luật FEFO:**

1. Lọc đúng material và warehouse.
2. Chỉ lấy `released`, `ccp1_status=pass`, quantity khả dụng > 0.
3. Loại lô `expiry_date < today`.
4. Sắp xếp `expiry_date ASC NULLS LAST`, sau đó `created_at ASC`.
5. Phân bổ nhiều lô đến khi đủ số lượng yêu cầu.

**Luật reservation:**

- `available_qty = on_hand_qty - active_reserved_qty`.
- Approve lệnh SX tạo reservation theo FEFO.
- Start chuyển reservation thành consumption/OUT movement trong cùng transaction.
- Cancel trước start giải phóng reservation.
- Cancel sau start tạo movement đảo chiều và giải phóng phần còn lại.
- Nếu không đủ available quantity, approve trả 400 và không giữ chỗ một phần.

### M4 — QR Batch Passport + Recall Simulator

**Màn hình:** mở rộng `/trace`.

**Batch Passport hiển thị:**

- Batch, material, supplier, ngày nhập/sản xuất, hạn dùng.
- Quality status và kết quả CCP.
- Production order nguồn/đích.
- Link certificate nếu batch đã released.

**Recall Simulator:**

- Input: `batch_no`, `reason`, `initiated_at`.
- Traverse downstream: input batch → usages → production orders → output batches.
- Chống vòng lặp bằng tập `visited_batch_ids` và `visited_order_ids`.
- Output: batch ảnh hưởng, lệnh SX ảnh hưởng, số lượng liên quan, trạng thái release.
- Export CSV UTF‑8 BOM.
- Đây là mô phỏng read-only; không tự thay đổi tồn hoặc trạng thái lô.

### M5 — GC Import + SPC (chỉ sau Gate G4)

**CSV chuẩn cho luận văn:**

```csv
batch_no,analyte,value,unit,tested_at
NVL-2026-001,C14,13.50,%,2026-07-01T08:00:00
TP-2026-001,tCA,99.20,%,2026-07-01T08:05:00
```

**Luật import:**

- MIME cho phép: `text/csv`, `application/vnd.ms-excel`.
- Tối đa 1 MB và 1.000 dòng.
- Cột bắt buộc đúng như header trên.
- `analyte` chỉ nhận `C14|tCA`, `unit` phải là `%`.
- Validate toàn bộ file trước khi ghi; một dòng lỗi làm cả import thất bại.
- Hash nội dung file để chống import trùng.
- Dữ liệu SPC dùng ít nhất 10 điểm cùng analyte; cảnh báo khi ngoài `mean ± 3σ`.

### M6 — Trợ lý AI hỏi–đáp (mở rộng, chỉ sau Gate G4)

**Màn hình:** ô chat nổi trên các trang đã đăng nhập.

**Kiến trúc chọn: NL→API (tool/function calling), read-only.**

- Người dùng hỏi bằng tiếng Việt.
- Backend gửi câu hỏi + danh sách "tool" cho LLM; LLM chọn tool và tham số.
- Backend thực thi tool bằng cách gọi service/API nội bộ **với JWT của chính người dùng**.
- LLM soạn câu trả lời dựa trên dữ liệu trả về, kèm dẫn nguồn (mã lô, số liệu).

**Danh sách tool giới hạn (whitelist, chỉ đọc):**

| Tool | Ánh xạ API nội bộ | Mục đích |
|---|---|---|
| `get_inventory` | `/stock/inventory` | Tồn kho theo vật tư |
| `get_batch_status` | `/quality/batches` | Trạng thái giải phóng lô |
| `list_expiring_batches` | `/stock/fefo-suggest` + lọc hạn | Lô sắp/đã hết hạn |
| `list_open_capa` | `/quality/corrective-actions` | CAPA đang mở/quá hạn |
| `simulate_recall` | `/reports/recall-simulations` | Phạm vi thu hồi của một lô |

**Luật nghiệp vụ và an toàn:**

- Chỉ được gọi tool trong whitelist; không sinh SQL, không gọi endpoint ghi.
- Mọi tool chạy dưới quyền người dùng hiện tại; RBAC do chính API nền quyết định.
- Nếu không có dữ liệu hoặc không hiểu câu hỏi, trả lời rõ ràng thay vì suy đoán.
- Ghi lại câu hỏi, tool đã gọi và thời gian vào audit log (không lưu nội dung nhạy cảm ngoài phạm vi).
- Có công tắc `AI_ASSISTANT_ENABLED`; tắt được để demo offline nếu mất mạng/API key.
- Hỗ trợ hai nhà cung cấp qua biến môi trường: API bên ngoài (có key) hoặc model local (ví dụ Ollama) làm phương án dự phòng.

**Giới hạn phạm vi (out-of-scope M6):**

- Không cho trợ lý thực hiện release, đóng CAPA hay bất kỳ thao tác ghi nào.
- Không huấn luyện/fine-tune model riêng; chỉ dùng model có sẵn.
- Không đưa dữ liệu ra dịch vụ ngoài nếu người dùng chọn chế độ local.

### M7 — Hồ sơ, quản lý tài khoản, ảnh vật tư (mở rộng, chỉ sau Gate G4)

**Màn hình:** `/profile`, `/users` (admin), thumbnail trên `/inventory`, `/stock-in`, `/stock-out`.

**Chốt nghiệp vụ (2026-08-16):**

| Hạng mục | Quyết định |
|---|---|
| Đăng ký công khai | Không |
| Tạo tài khoản | Chỉ `admin` |
| Hồ sơ | User xem thông tin; đổi `full_name` + mật khẩu; avatar tuỳ chọn |
| Ảnh vật tư | `Material.image_url` hoặc upload `/uploads/materials/`; hiện thumbnail |

**API:**

- `PATCH /auth/me`, `POST /auth/me/password`
- `GET|POST /users`, `PATCH /users/{id}` (admin)
- `PATCH /materials/{id}` / `POST /materials/{id}/image` (ảnh)

**Spec:** `docs/superpowers/specs/2026-08-16-m7-profile-users-product-images-design.md`

---

## 3. Mô hình dữ liệu và API

### 3.1 Model mới/chỉnh sửa

| Model | Thay đổi chính |
|---|---|
| `StockBatch` | thêm `quality_status`, `mfg_date`, `expiry_date` |
| `BatchStatusHistory` | transition, reason, note, changed_by, changed_at |
| `QualityApproval` | batch, submitted_by, approved_by, decision, signed_at |
| `CorrectiveAction` | bổ sung workflow CAPA/NCR đầy đủ |
| `MaterialReservation` | order, batch, qty, status, timestamps |
| `RecallSimulation` | batch gốc, reason, initiated_by, duration_ms |
| `GcImport` | filename, sha256, row_count, imported_by |
| `AssistantQueryLog` | user_id, question, tools_called, created_at (M6) |
| `User` (M7) | thêm `avatar_url` (nullable) |
| `Material` (M7) | thêm `image_url` (nullable) |

### 3.2 Enum khóa tên

```python
class QualityStatus(str, enum.Enum):
    quarantine = "quarantine"
    sampling = "sampling"
    under_test = "under_test"
    awaiting_release = "awaiting_release"
    released = "released"
    rejected = "rejected"
    retest = "retest"

class CapaStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    action_pending = "action_pending"
    verification = "verification"
    closed = "closed"

class Disposition(str, enum.Enum):
    retest = "retest"
    rework = "rework"
    reject = "reject"
    use_as_is = "use_as_is"

class ReservationStatus(str, enum.Enum):
    active = "active"
    consumed = "consumed"
    released = "released"
```

Giữ nguyên `CCPStatus.pass_` trong Python và giá trị API là `"pass"`. Không đổi cách SQLAlchemy lưu enum của schema cũ trong cùng migration Digital QMS.

### 3.3 API mới

| Method | Endpoint | Role ghi |
|---|---|---|
| GET | `/api/v1/quality/batches` | authenticated |
| POST | `/api/v1/quality/batches/{id}/transition` | lab/attp/admin tùy transition |
| GET | `/api/v1/quality/batches/{id}/history` | authenticated |
| GET | `/api/v1/quality/batches/{id}/certificate.pdf` | authenticated |
| GET | `/api/v1/quality/corrective-actions` | authenticated |
| POST | `/api/v1/quality/corrective-actions/{id}/transition` | lab/ky_thuat/attp/admin |
| GET | `/api/v1/stock/fefo-suggest` | thu_kho/ky_thuat/ql_nm/admin |
| GET | `/api/v1/production/orders/{id}/reservations` | authenticated |
| GET | `/api/v1/reports/batch-passport/{batch_no}` | authenticated |
| GET | `/api/v1/reports/batch-qr/{batch_no}` | authenticated |
| POST | `/api/v1/reports/recall-simulations` | attp/ql_nm/admin |
| GET | `/api/v1/reports/recall-simulations/{id}/csv` | attp/ql_nm/admin |
| POST | `/api/v1/lab/gc-import` | lab/admin; M5 |
| GET | `/api/v1/lab/spc` | lab/attp/ql_nm/admin; M5 |
| POST | `/api/v1/assistant/ask` | authenticated; M6, read-only |

---

## 4. File map

### Backend

| File | Trách nhiệm |
|---|---|
| `backend/app/models.py` | enum, model và relationship mới |
| `backend/app/schemas.py` | request/response typed cho M1–M5 |
| `backend/app/services/quality_release.py` | state machine và điều kiện release |
| `backend/app/services/capa.py` | tạo idempotent, transition và verification CAPA |
| `backend/app/services/fefo.py` | phân bổ FEFO và reservation |
| `backend/app/services/recall.py` | traverse downstream và kết quả recall |
| `backend/app/services/gc_import.py` | parse/validate CSV, chống trùng |
| `backend/app/services/spc.py` | mean, standard deviation, control limits |
| `backend/app/services/assistant.py` | tool registry read-only + gọi LLM provider (M6) |
| `backend/app/routers/quality.py` | API Hold‑Release và CAPA |
| `backend/app/routers/stock.py` | receipt quarantine, issue gate, FEFO endpoint |
| `backend/app/routers/production.py` | reservation và CCP2 completion gate |
| `backend/app/routers/lab.py` | đồng bộ Lab→CCP/CAPA, GC import |
| `backend/app/routers/reports.py` | passport, QR, recall, certificate |
| `backend/app/routers/assistant.py` | endpoint `/assistant/ask` (M6) |
| `backend/alembic/` | migration schema |

### Frontend

| File | Trách nhiệm |
|---|---|
| `frontend/src/styles/tokens.css` | design tokens màu/spacing/typography |
| `frontend/src/components/ui/` | PageHeader, StatusBadge, DataTable, EmptyState, AlertBanner, ActionBar, FilterBar, Modal, Toast, ErrorBoundary |
| `frontend/src/ui/status.ts` | map status → label/badge class |
| `frontend/src/Layout.tsx` | shell sidebar/nav đồng bộ |
| `frontend/src/pages/QualityRelease.tsx` | board Hold‑Release và history |
| `frontend/src/pages/Capa.tsx` | queue CAPA, form xử lý/xác minh |
| `frontend/src/pages/Inventory.tsx` | badge quality/expiry/available |
| `frontend/src/pages/StockOut.tsx` | gợi ý FEFO |
| `frontend/src/pages/Production.tsx` | reservation và lỗi thiếu available stock |
| `frontend/src/pages/Trace.tsx` | passport, QR, recall result |
| `frontend/src/pages/Lab.tsx` | tab GC import/SPC nếu triển khai M5 |
| `frontend/src/components/AssistantWidget.tsx` | ô chat AI read-only (M6) |
| `frontend/src/api.ts` | API types và calls mới |
| `frontend/src/App.tsx` | route `/quality`, `/capa`, gắn AssistantWidget |
| `docs/screenshots/` | ảnh UI theo module, chụp ngay khi đóng task |

### Test và tài liệu

| File | Trách nhiệm |
|---|---|
| `backend/tests/test_quality_release.py` | M1 state/RBAC/gates |
| `backend/tests/test_capa.py` | M2 lifecycle/idempotency |
| `backend/tests/test_fefo.py` | M3 allocation/reservation |
| `backend/tests/test_recall.py` | M4 graph traversal |
| `backend/tests/test_gc_import_spc.py` | M5 validation/calculation |
| `backend/tests/test_assistant.py` | M6 whitelist tool, RBAC, read-only |
| `backend/tests/test_e2e_api.py` | full flow luận văn |
| `frontend/e2e/digital-qms.spec.ts` | Playwright smoke |
| `docs/requirements.md` | FR/NFR luận văn |
| `docs/database-design.md` | ERD/schema mới |
| `docs/api-spec.md` | API mới |
| `docs/thesis-metrics.md` | kết quả đo thật |

---

## 5. Milestone gates và phạm vi cắt

| Gate | Điều kiện đạt | Nếu chưa đạt |
|---|---|---|
| G0 | SQLite backend test hiện tại xanh và DB file đã backup | Không đổi schema |
| G1 | Đề cương Digital QMS được GV chấp nhận | Chỉ chỉnh tài liệu |
| G1.5 | Design system + shell UI đồng bộ đã áp Layout và Dashboard | Không bắt đầu M1 UI ad-hoc |
| G2 | M1+M2 API **và UI** chạy end-to-end; checklist 0b.3 đã tick | Không bắt đầu M3 |
| G3 | M3 reservation không lệch tồn **và** UI FEFO/available đồng bộ | Không bắt đầu QR Recall |
| G4 | M1–M4 API+UI chạy trên SQLite và PostgreSQL; demo PostgreSQL ổn định | Không bắt đầu M5/M6 |
| G5 | UAT và số liệu có bằng chứng | Mới viết kết luận/slide |

**Thứ tự cắt khi trễ:** trợ lý AI (M6) → SPC chart → GC import → QR image đẹp → Playwright mở rộng. Không cắt M1, M2, FEFO core, Recall Simulator, hoặc design system shell.

**M5 và M6 là hai module mở rộng độc lập sau G4; có thể làm một, cả hai, hoặc bỏ mà không ảnh hưởng phần lõi.**

**Cấm:** task “làm backend trước, UI sau” cho cùng một module. Nếu API xong mà UI chưa đạt checklist 0b.3 thì gate chưa đạt.

---

## 6. Implementation tasks

### Task 0: Baseline và backup an toàn

**Files:**
- Read: `backend/tests/`
- Use: `scripts/backup_db.ps1`
- Create: `docs/baseline-pytest.txt`

**Interfaces:**
- Produces: bằng chứng G0 và DB backup trước migration.

- [x] **Step 1: Kiểm tra/backup SQLite hiện tại**

```powershell
Copy-Item "backend\oxeyns.db" "backend\oxeyns.db.bak-$(Get-Date -Format yyyyMMdd-HHmm)"
```

Kết quả 2026-07-18: `backend/oxeyns.db` không tồn tại, vì vậy không có dữ liệu để backup; không tạo file backup giả.

- [x] **Step 2: Chạy test baseline**

```powershell
Set-Location backend
pytest tests -q --tb=line | Tee-Object -FilePath "..\docs\baseline-pytest.txt"
```

Kết quả: `17 passed, 4 warnings`; chi tiết lưu trong `docs/baseline-pytest.txt`.

- [x] **Step 3: Chạy frontend build**

```powershell
Set-Location ..\frontend
npm run build
```

Kết quả: `tsc -b && vite build` exit code 0; 60 modules transformed.

- [x] **Step 4: Kiểm tra khả năng commit baseline**

```powershell
git add docs/baseline-pytest.txt
git commit -m "docs: record thesis development baseline"
```

Kết quả: thư mục chưa phải Git repository nên bước commit là N/A; không tự khởi tạo Git khi người dùng chưa yêu cầu.

### Task 1: Khóa đặc tả luận văn

**Files:**
- Modify: `docs/requirements.md`
- Modify: `docs/pham-vi-xac-nhan.md`
- Modify: `docs/api-spec.md`
- Modify: `docs/bao-cao/noi-dung/00-mo-dau.md`

**Interfaces:**
- Produces: `FR-Q01..Q08`, `FR-C01..C07`, `FR-F01..F06`, `FR-R01..R05`, `NFR-LV01..05`.

- [x] **Step 1: Ghi phạm vi module**

```markdown
## Phạm vi luận văn Digital QMS
- M1 Quality Hold-Release Board và Release Certificate
- M2 CAPA/NCR điện tử
- M3 FEFO và Material Reservation
- M4 QR Batch Passport và Recall Simulator
- M5 GC Import/SPC chỉ sau khi Gate G4 đạt
- M6 Trợ lý AI hỏi–đáp read-only chỉ sau Gate G4
- M7 Hồ sơ người dùng + quản lý tài khoản (admin) + ảnh vật tư — mở rộng sau G4 (không đăng ký công khai)
- UI làm đồng bộ theo từng module; design system khóa ở Task 1.5
```

- [x] **Step 2: Ghi các quyết định không thay đổi khi code**

```markdown
- Release là hai bước: Lab gửi duyệt, ATTP quyết định.
- Thành phẩm sau CCP2 pass ở awaiting_release, không auto released.
- Recall Simulator read-only.
- Reservation phải atomic; thiếu tồn thì rollback toàn bộ.
- M5/M6 không được làm chậm M1-M4.
- M7 (profile/users/ảnh vật tư) chỉ sau G4; không đăng ký công khai — chỉ admin tạo tài khoản.
- Không redesign UI cuối kỳ; mỗi module ship UI cùng API.
```

- [~] **Step 3: GV xác nhận G1** (tài liệu provisional; chờ chữ ký/email chính thức)

Expected: có phản hồi bằng văn bản/email hoặc chữ ký đề cương trước Task 1.5/2.

- [x] **Step 4: Commit tài liệu** — N/A (chưa init Git)

```powershell
git add docs/requirements.md docs/pham-vi-xac-nhan.md docs/api-spec.md docs/bao-cao/noi-dung/00-mo-dau.md
git commit -m "docs: define Digital QMS thesis scope"
```

### Task 1.5: Khóa design system và shell UI (trước mọi màn hình mới)

**Files:**
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/components/ui/PageHeader.tsx`
- Create: `frontend/src/components/ui/StatusBadge.tsx`
- Create: `frontend/src/components/ui/DataTable.tsx`
- Create: `frontend/src/components/ui/EmptyState.tsx`
- Create: `frontend/src/components/ui/AlertBanner.tsx`
- Create: `frontend/src/components/ui/FilterBar.tsx`
- Create: `frontend/src/components/ui/ActionBar.tsx`
- Create: `frontend/src/components/ui/ErrorBoundary.tsx`
- Create: `frontend/src/ui/status.ts`
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/Layout.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/pages/Dashboard.tsx`
- Create: `docs/screenshots/00-shell/`

**Interfaces:**
- Produces: token CSS variables, UI primitives, ErrorBoundary và status map dùng bởi mọi màn hình M1–M6.
- Consumes: không phụ thuộc API mới.

- [x] **Step 1: Tạo tokens**

```css
/* frontend/src/styles/tokens.css */
:root {
  --color-bg: #f4f6f9;
  --color-surface: #ffffff;
  --color-text: #1a1a2e;
  --color-muted: #64748b;
  --color-primary: #1e3a5f;
  --color-accent: #2563eb;
  --color-ok: #15803d;
  --color-warn: #b45309;
  --color-danger: #b91c1c;
  --color-info: #0369a1;
  --radius: 8px;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  --font-sans: "Segoe UI", system-ui, sans-serif;
}
```

Import `tokens.css` đầu `index.css`.

- [x] **Step 2: Cài UI primitives tối thiểu + ErrorBoundary**

Mỗi component nhận props typed; `StatusBadge` đọc từ `status.ts`. Không thêm thư viện UI mới. `ErrorBoundary` theo mẫu mục 0b.5; bọc `<Routes>` trong `App.tsx`.

- [x] **Step 3: Áp shell cho Layout + Dashboard + 1 trang cũ**

Refactor `Layout.tsx` và `Dashboard.tsx` dùng `PageHeader`/`AlertBanner`. Chọn thêm `Inventory.tsx` để chứng minh trang TTTN cũng đồng bộ shell. Mọi handler load dữ liệu trên Dashboard/Inventory phải có `try/catch` + `AlertBanner`.

- [x] **Step 4: Verify Gate G1.5**

```powershell
Set-Location frontend
npm run build
```

Expected: build OK; Dashboard/Inventory nhìn cùng sidebar, badge và spacing; cố tình gây lỗi API thì thấy banner tiếng Việt, không trang trắng.

Chụp screenshot vào `docs/screenshots/00-shell/`.

- [x] **Step 5: Commit** — N/A (chưa init Git)

```powershell
git add frontend docs/screenshots/00-shell
git commit -m "feat(ui): lock Digital QMS design system and shell"
```

### Task 2: Alembic và model Digital QMS

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/migrate.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/`
- Test: `backend/tests/test_digital_qms_models.py`

**Interfaces:**
- Produces: enum/model ở mục 3.1–3.2 và cùng một Alembic revision chạy được trên SQLite/PostgreSQL.

- [x] **Step 1: Thêm Alembic bằng package manager**

```powershell
Set-Location backend
pip install alembic
pip freeze | Select-String "^alembic==" | ForEach-Object { $_.Line } | Add-Content requirements.txt
alembic init alembic
```

- [x] **Step 2: Viết failing mapper test**

```python
from sqlalchemy import inspect
from app.models import BatchStatusHistory, MaterialReservation, QualityApproval, StockBatch

def test_digital_qms_models_are_mapped():
    columns = {item.key for item in inspect(StockBatch).mapper.column_attrs}
    assert {"quality_status", "mfg_date", "expiry_date"} <= columns
    assert BatchStatusHistory.__tablename__ == "batch_status_histories"
    assert QualityApproval.__tablename__ == "quality_approvals"
    assert MaterialReservation.__tablename__ == "material_reservations"
```

- [x] **Step 3: Chạy test để xác nhận fail**

```powershell
pytest tests/test_digital_qms_models.py -v
```

Expected: FAIL do model/column chưa tồn tại.

- [x] **Step 4: Cài model, schema và relationship**

Implement đúng enum mục 3.2; dùng `Date` cho `mfg_date/expiry_date`, `Numeric(12,3)` cho reservation quantity, FK đến user/batch/order.

- [x] **Step 5: Tạo migration và backfill**

```powershell
alembic revision --autogenerate -m "add Digital QMS models"
alembic upgrade head
```

Backfill migration:

```python
op.execute(
    "UPDATE stock_batches SET quality_status = "
    "CASE WHEN ccp1_status = 'pass' THEN 'released' ELSE 'quarantine' END"
)
```

- [x] **Step 6: Kiểm tra migration trên cả hai CSDL**

SQLite sạch:

```powershell
$env:DATABASE_URL="sqlite:///./migration_test.db"
alembic upgrade head
alembic current
Remove-Item ".\migration_test.db"
```

PostgreSQL sạch:

```powershell
docker compose up -d db
$env:DATABASE_URL="postgresql+psycopg2://oxeyns:oxeyns@localhost:5432/oxeyns"
alembic upgrade head
alembic current
```

Expected: cả hai trả cùng Alembic head revision.

- [x] **Step 7: Chuyển startup sang một nguồn migration**

Loại lời gọi `run_migrations()` khỏi đường demo/production. `Base.metadata.create_all()` chỉ dùng trong fixture test in-memory.

- [x] **Step 8: Verify bằng SQLite in-memory**

```powershell
$env:DATABASE_URL="sqlite://"
pytest tests -q
```

Expected: toàn bộ test PASS.

- [x] **Step 9: Commit** — N/A (chưa init Git)

```powershell
git add backend
git commit -m "feat(db): add Digital QMS schema and Alembic migrations"
```

### Task 3: M1 Hold‑Release backend

> Làm liền Task 4 trong cùng tuần. **Không** đóng M1 chỉ với API.

**Files:**
- Create: `backend/app/services/quality_release.py`
- Modify: `backend/app/routers/quality.py`
- Modify: `backend/app/routers/stock.py`
- Modify: `backend/app/routers/lab.py`
- Modify: `backend/app/schemas.py`
- Test: `backend/tests/test_quality_release.py`
- Modify: `backend/tests/test_e2e_api.py`

**Interfaces:**
- Produces: quality batch list, transition, history API; issue/start gate.

- [x] **Step 1: Viết failing RBAC/state tests**

```python
def test_warehouse_cannot_release(client, warehouse_headers, awaiting_batch):
    response = client.post(
        f"/api/v1/quality/batches/{awaiting_batch.id}/transition",
        headers=warehouse_headers,
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Không hợp lệ"},
    )
    assert response.status_code == 403

def test_attp_releases_awaiting_batch(client, attp_headers, awaiting_batch):
    response = client.post(
        f"/api/v1/quality/batches/{awaiting_batch.id}/transition",
        headers=attp_headers,
        json={"to_status": "released", "reason_code": "CCP_PASS", "note": "Đạt"},
    )
    assert response.status_code == 200
    assert response.json()["quality_status"] == "released"

def test_quarantine_batch_cannot_be_issued(client, warehouse_headers, quarantine_batch):
    response = client.post(
        "/api/v1/stock/issues",
        headers=warehouse_headers,
        json={"batch_id": quarantine_batch.id, "quantity": 1},
    )
    assert response.status_code == 400
```

- [x] **Step 2: Chạy test để xác nhận fail**

```powershell
pytest tests/test_quality_release.py -v
```

- [x] **Step 3: Cài state machine**

```python
ALLOWED_TRANSITIONS = {
    ("quarantine", "sampling"),
    ("sampling", "under_test"),
    ("under_test", "awaiting_release"),
    ("under_test", "rejected"),
    ("under_test", "retest"),
    ("retest", "under_test"),
    ("awaiting_release", "released"),
    ("awaiting_release", "rejected"),
}
```

Service phải kiểm role theo transition, yêu cầu CCP pass trước `awaiting_release`, ghi history và audit trong cùng transaction.

- [x] **Step 4: Nối receipt/Lab/issue**

- Receipt bỏ đánh giá `ccp1_c14` từ input thủ kho.
- LabTest C14 cập nhật `ccp1_status`, không tự release.
- Issue/start thêm ba gate: released, CCP pass, chưa hết hạn.

- [x] **Step 5: Sửa E2E cũ**

Flow mới:

```text
receipt → lab sampling → lab test pass → awaiting_release
→ ATTP released → production start → CCP2 pass → complete
```

- [x] **Step 6: Verify và commit** (verify xong; commit N/A)

```powershell
pytest tests -q
git add backend
git commit -m "feat(quality): add two-step Hold-Release workflow"
```

### Task 4: M1 UI và Release Certificate

**Files:**
- Create: `frontend/src/pages/QualityRelease.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/api.ts`
- Modify: `frontend/src/pages/Inventory.tsx`
- Modify: `frontend/src/pages/StockOut.tsx`
- Modify: `backend/app/routers/reports.py`
- Test: `backend/tests/test_release_certificate.py`
- Create: `docs/screenshots/m1-quality/`

**Interfaces:**
- Consumes: Task 3 APIs và UI primitives Task 1.5.
- Produces: `/quality` board đồng bộ shell + certificate PDF.

- [x] **Step 1: Cài route và typed API**

Types bắt buộc:

```typescript
type QualityStatus =
  | "quarantine"
  | "sampling"
  | "under_test"
  | "awaiting_release"
  | "released"
  | "rejected"
  | "retest";

interface QualityBatch {
  id: number;
  batch_no: string;
  ccp1_status: "pending" | "pass" | "fail";
  quality_status: QualityStatus;
  expiry_date: string | null;
}
```

- [x] **Step 2: Cài board bằng UI primitives**

`QualityRelease.tsx` bắt buộc dùng `PageHeader`, `FilterBar`, `StatusBadge`, `DataTable` hoặc cột Kanban, `EmptyState`, `AlertBanner`, `ActionBar`. Không viết card/button style mới ngoài tokens. Mọi load/transition bọc `try/catch` theo mẫu 0b.5.

Board có filter status, batch search, timeline history và action theo role. Nút không hợp role phải ẩn; backend vẫn là nguồn bảo vệ chính.

Inventory và StockOut thêm `StatusBadge` quality ngay trong task này (không để tuần sau).

- [x] **Step 3: Viết certificate test**

```python
def test_certificate_requires_released_batch(client, attp_headers, quarantine_batch):
    response = client.get(
        f"/api/v1/quality/batches/{quarantine_batch.id}/certificate.pdf",
        headers=attp_headers,
    )
    assert response.status_code == 400
```

- [x] **Step 4: Cài PDF**

Certificate chỉ xuất cho `released`, dùng ReportLab/DejaVu hiện có, chứa batch, CCP result, Lab submitter, ATTP approver, signed time.

- [x] **Step 5: Tick checklist UI 0b.3 + screenshot**

Lưu ảnh vào `docs/screenshots/m1-quality/`. Nếu thiếu EmptyState/loading/badge → task chưa xong.

- [x] **Step 6: Verify và commit** (verify xong; commit N/A)

```powershell
Set-Location backend
pytest tests -q
Set-Location ..\frontend
npm run build
git add backend frontend docs/screenshots/m1-quality
git commit -m "feat(ui): add Hold-Release board and certificate"
```

### Task 5: M2 CAPA/NCR backend và UI

> API và UI CAPA ship trong **cùng task**. Không tách “backend tuần này, UI tuần sau”.

**Files:**
- Create: `backend/app/services/capa.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/routers/quality.py`
- Modify: `backend/app/routers/lab.py`
- Modify: `backend/app/routers/production.py`
- Create: `frontend/src/pages/Capa.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/api.ts`
- Modify: `frontend/src/pages/Dashboard.tsx`
- Test: `backend/tests/test_capa.py`
- Create: `docs/screenshots/m2-capa/`

**Interfaces:**
- Produces: auto-create CAPA và lifecycle API/UI đồng bộ shell.
- Consumes: UI primitives Task 1.5.

- [x] **Step 1: Viết failing idempotency/close tests**

```python
def test_same_failure_creates_one_open_capa(db, failed_lab_test):
    first = create_capa_for_failure(db, "lab_test", failed_lab_test.id)
    second = create_capa_for_failure(db, "lab_test", failed_lab_test.id)
    assert first.id == second.id

def test_capa_cannot_close_without_verification(client, attp_headers, open_capa):
    response = client.post(
        f"/api/v1/quality/corrective-actions/{open_capa.id}/transition",
        headers=attp_headers,
        json={"to_status": "closed", "disposition": "reject"},
    )
    assert response.status_code == 400
```

- [x] **Step 2: Cài CAPA service**

Unique logical key: `(source_type, source_id, status != closed)`. Transition kiểm đầy đủ field theo trạng thái và role.

- [x] **Step 3: Nối sự kiện fail**

- Lab CCP fail → tạo CAPA.
- Operation CCP2 fail → tạo CAPA.
- ATTP reject batch → tạo CAPA nếu chưa có.

- [x] **Step 4: Cài `/capa` bằng UI primitives**

`Capa.tsx` dùng `PageHeader`, `FilterBar`, `StatusBadge`, `DataTable`, `EmptyState`, `AlertBanner`. Tabs open/overdue/closed, source link, due date, root cause, action, disposition và verification form. Dashboard hiện số CAPA overdue bằng badge đỏ. Mọi load/transition bọc `try/catch` theo mẫu 0b.5.

- [x] **Step 5: Tick checklist UI 0b.3 + screenshot `docs/screenshots/m2-capa/`**

- [x] **Step 6: Verify Gate G2**

```powershell
Set-Location backend
pytest tests/test_quality_release.py tests/test_capa.py tests/test_e2e_api.py -v
Set-Location ..\frontend
npm run build
```

Expected: PASS; demo CCP fail tự xuất hiện trên `/capa`.

- [x] **Step 7: Commit** — N/A (chưa init Git)

```powershell
git add backend frontend docs/screenshots/m2-capa
git commit -m "feat(quality): add CAPA NCR lifecycle and UI"
```

### Task 6: M3 FEFO + Material Reservation

> FEFO API và UI Inventory/StockOut/Production ship cùng task.
**Files:**
- Create: `backend/app/services/fefo.py`
- Modify: `backend/app/routers/stock.py`
- Modify: `backend/app/routers/production.py`
- Modify: `backend/app/schemas.py`
- Modify: `frontend/src/pages/Inventory.tsx`
- Modify: `frontend/src/pages/StockOut.tsx`
- Modify: `frontend/src/pages/Production.tsx`
- Test: `backend/tests/test_fefo.py`
- Test: `backend/tests/integration/test_reservation_concurrency.py` (PostgreSQL)

**Interfaces:**
- Produces: `suggest_fefo(db, material_id, warehouse_id, required_qty)` và reservation APIs.

- [x] **Step 1: Viết failing allocation tests**

```python
def test_fefo_allocates_earliest_expiry_first(db, released_batches):
    allocations = suggest_fefo(db, material_id=1, warehouse_id=1, required_qty=12)
    assert [item.batch_id for item in allocations] == [
        released_batches.earliest.id,
        released_batches.later.id,
    ]
    assert sum(item.qty for item in allocations) == 12

def test_expired_or_quarantine_batch_is_excluded(db, invalid_batches):
    allocations = suggest_fefo(db, material_id=1, warehouse_id=1, required_qty=1)
    assert not {item.batch_id for item in allocations} & invalid_batches.ids
```

- [x] **Step 2: Cài pure FEFO service**

Service trả allocations, không commit. Router approve mở transaction và tạo toàn bộ reservation hoặc rollback.

Khóa concurrency theo dialect:

```python
query = db.query(StockBatch).filter(StockBatch.id.in_(batch_ids))
if db.get_bind().dialect.name == "postgresql":
    query = query.with_for_update()
locked_batches = query.all()
```

SQLite dùng cùng logic transaction để phát triển/test tuần tự. PostgreSQL dùng `FOR UPDATE` và là nơi xác nhận chống race condition; đây là khác biệt hạ tầng duy nhất, không tách business rule FEFO.

- [x] **Step 3: Cài start/cancel**

- Start: active → consumed; tạo OUT movement.
- Cancel trước start: active → released.
- Cancel sau start: tạo IN reversal có reference đến movement gốc.

- [x] **Step 4: Viết test khôi phục tồn**

```python
def test_cancel_running_order_restores_stock(client, production_flow):
    before = production_flow.batch_quantity
    production_flow.start(quantity=30)
    production_flow.cancel()
    assert production_flow.reload_batch_quantity() == before
```

Viết thêm PostgreSQL integration test: hai transaction cùng reserve lượng tồn chỉ đủ cho một order; kết quả bắt buộc một success và một insufficient-stock error, tổng active reservation không vượt tồn.

- [x] **Step 5: Cài UI đồng bộ shell**

Inventory dùng `DataTable` + cột on-hand/reserved/available/expiry + `StatusBadge`; StockOut có `ActionBar` “Gợi ý FEFO”; Production hiện panel allocations. Không thêm style riêng ngoài tokens. Tick checklist 0b.3 và lưu `docs/screenshots/m3-fefo/`.

- [x] **Step 6: Verify Gate G3 và commit** (verify xong; commit N/A)

```powershell
Set-Location backend
pytest tests/test_fefo.py tests/test_e2e_api.py -v
$env:DATABASE_URL="postgresql+psycopg2://oxeyns:oxeyns@localhost:5432/oxeyns"
pytest tests/integration/test_reservation_concurrency.py -v
Set-Location ..\frontend
npm run build
git add backend frontend docs/screenshots/m3-fefo
git commit -m "feat(stock): add FEFO allocation and material reservations"
```

### Task 7: M4 QR Batch Passport + Recall Simulator

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/services/recall.py`
- Modify: `backend/app/routers/reports.py`
- Modify: `backend/app/schemas.py`
- Modify: `frontend/src/pages/Trace.tsx`
- Test: `backend/tests/test_recall.py`

**Interfaces:**
- Produces: passport/QR/recall endpoints ở mục 3.3.

- [x] **Step 1: Thêm QR dependency**

```powershell
Set-Location backend
pip install "qrcode[pil]"
pip freeze | Select-String "^qrcode==" | ForEach-Object { $_.Line } | Add-Content requirements.txt
```

- [x] **Step 2: Viết failing graph test**

```python
def test_recall_returns_all_downstream_batches(db, trace_graph):
    result = simulate_recall(db, trace_graph.raw_batch.id)
    assert {item.batch_no for item in result.affected_batches} == {
        trace_graph.raw_batch.batch_no,
        trace_graph.finished_batch_1.batch_no,
        trace_graph.finished_batch_2.batch_no,
    }
    assert result.duration_ms >= 0
```

- [x] **Step 3: Cài traversal**

Thuật toán BFS trên `ProductionMaterialUsage` và `ProductionOrder.output_batch_id`; dùng visited sets; query theo batch ids từng lớp để tránh N+1.

- [x] **Step 4: Cài QR/passport/CSV**

QR payload dùng URL tương đối `/trace?batch=<batch_no>`. CSV recall dùng UTF‑8 BOM và cột `batch_no,material,order_no,quantity,quality_status`.

- [x] **Step 5: Cài UI Trace đồng bộ shell**

`Trace.tsx` dùng `PageHeader`, passport card theo surface token, QR, form lý do recall trong `FilterBar`/`ActionBar`, kết quả theo tầng bằng `DataTable`, `EmptyState`, `AlertBanner`. Tick checklist 0b.3; lưu `docs/screenshots/m4-recall/`.

- [x] **Step 6: Verify và commit** (verify xong; commit N/A)

```powershell
Set-Location backend
pytest tests/test_recall.py -v
Set-Location ..\frontend
npm run build
git add backend frontend docs/screenshots/m4-recall
git commit -m "feat(trace): add QR batch passport and recall simulator"
```

### Task 8: Hoàn thiện hai CSDL, Docker, CI và E2E

**Files:**
- Modify: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`
- Modify: `backend/.env.example`
- Create: `backend/.env.sqlite.example`
- Create: `backend/.env.postgres.example`
- Create: `backend/pytest.ini`
- Create: `docker-compose.test.yml`
- Create: `.github/workflows/ci.yml`
- Create: `frontend/e2e/digital-qms.spec.ts`
- Modify: `frontend/package.json`
- Modify: `docs/deploy.md`

**Interfaces:**
- Produces: SQLite dev/test profile, PostgreSQL integration/demo profile và Gate G4.

- [x] **Step 1: Hoàn thiện cấu hình SQLite**

`backend/.env.sqlite.example`:

```env
DATABASE_URL=sqlite:///./oxeyns.db
SECRET_KEY=change-me-local-only
CORS_ORIGINS=http://localhost:5173
```

Lệnh dev:

```powershell
Set-Location backend
Copy-Item ".env.sqlite.example" ".env"
uvicorn app.main:app --reload --port 8000
```

- [x] **Step 2: Hoàn thiện PostgreSQL Compose**

Services bắt buộc: `db` PostgreSQL 16 với healthcheck, `api` chạy `alembic upgrade head` trước Uvicorn, `web` serve Vite build và proxy `/api`. pgAdmin4 không bắt buộc trong stack; có thể kết nối thủ công tới `localhost:5432`.

`backend/.env.postgres.example`:

```env
DATABASE_URL=postgresql+psycopg2://oxeyns:oxeyns@db:5432/oxeyns
SECRET_KEY=change-me-demo-only
CORS_ORIGINS=http://localhost:5173
```

- [x] **Step 3: Thêm Playwright**

```powershell
Set-Location frontend
npm install --save-dev @playwright/test
npx playwright install chromium
```

- [x] **Step 4: Viết smoke flow**

```typescript
import { test, expect } from "@playwright/test";

test("Digital QMS critical flow", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("lab");
  await page.getByLabel("Mật khẩu").fill("lab123");
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).toHaveURL(/\/$/);
  await page.goto("/quality");
  await expect(page.getByText("Giải phóng lô")).toBeVisible();
});
```

- [x] **Step 5: CI chạy hai CSDL**

CI gồm ba jobs:

1. `backend-sqlite`: `DATABASE_URL=sqlite://`, chạy toàn bộ unit/API tests trừ marker `postgres`.
2. `backend-postgres`: khởi động PostgreSQL service, chạy Alembic và tests marker `postgres|integration`.
3. `frontend-e2e`: frontend build; Playwright chạy khi PostgreSQL Compose stack healthy.

Các test PostgreSQL gắn marker:

```python
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.postgres]
```

`backend/pytest.ini` đăng ký `integration` và `postgres` để CI không phát sinh unknown-marker warning.

- [x] **Step 6: Verify SQLite profile**

```powershell
Set-Location backend
$env:DATABASE_URL="sqlite://"
pytest tests -q -m "not postgres"
```

Expected: exit code 0.

- [x] **Step 7: Verify PostgreSQL profile và Gate G4**

```powershell
docker compose up --build -d
docker compose ps
Set-Location backend
$env:DATABASE_URL="postgresql+psycopg2://oxeyns:oxeyns@localhost:5432/oxeyns"
alembic upgrade head
pytest tests -q -m "postgres or integration"
Set-Location ..\frontend
npm run build
npx playwright test
```

Expected: db/api/web healthy; test/build/E2E exit code 0.

- [x] **Step 8: Cập nhật tài liệu lựa chọn CSDL**

`docs/deploy.md` phải ghi:

- SQLite: phát triển cá nhân và pytest nhanh.
- PostgreSQL: integration, concurrency và demo bảo vệ.
- pgAdmin4: công cụ quản trị tùy chọn; host `localhost`, port `5432`, database/user theo Compose.
- Cách đổi CSDL chỉ qua `DATABASE_URL`, không sửa code.

- [x] **Step 9: Commit** — N/A (chưa init Git)

```powershell
git add docker-compose.yml docker-compose.test.yml backend frontend .github docs/deploy.md
git commit -m "chore: support SQLite development and PostgreSQL demo profiles"
```

### Task 9: M5 GC Import + SPC (chỉ khi Gate G4 đạt)

**Files:**
- Create: `backend/app/services/gc_import.py`
- Create: `backend/app/services/spc.py`
- Modify: `backend/app/routers/lab.py`
- Modify: `backend/app/schemas.py`
- Modify: `frontend/src/pages/Lab.tsx`
- Create: `backend/tests/fixtures/gc_sample.csv`
- Test: `backend/tests/test_gc_import_spc.py`

**Interfaces:**
- Produces: GC import và SPC endpoints ở mục 3.3.

- [x] **Step 1: Viết failing validation tests**

```python
def test_gc_import_is_atomic_on_invalid_row(client, lab_headers, invalid_gc_csv):
    response = client.post(
        "/api/v1/lab/gc-import",
        headers=lab_headers,
        files={"file": ("gc.csv", invalid_gc_csv, "text/csv")},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["imported"] == 0

def test_spc_flags_value_above_ucl():
    values = [10.0, 10.1, 9.9, 10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 20.0]
    result = calculate_spc(values)
    assert result.points[-1].out_of_control is True
```

- [x] **Step 2: Cài parser atomic và SHA-256 idempotency**

Parse toàn file vào memory tối đa 1 MB, validate, sau đó mới insert trong một transaction.

- [x] **Step 3: Cài SPC**

Trả `mean`, `std_dev`, `ucl`, `lcl` và từng point `out_of_control`; nếu dưới 10 điểm trả `status="insufficient_data"`.

- [x] **Step 4: Cài UI Lab đồng bộ shell**

Tab import dùng `PageHeader`/`AlertBanner`/`EmptyState`; hiển thị preview/error dòng; panel SPC dùng SVG đơn giản theo màu tokens (`--color-ok`/`--color-danger`), không thêm chart dependency. Tick checklist 0b.3; lưu `docs/screenshots/m5-gc/`.

- [x] **Step 5: Verify và commit** (verify xong; commit N/A — chưa init Git)

```powershell
Set-Location backend
pytest tests/test_gc_import_spc.py -v
Set-Location ..\frontend
npm run build
git add backend frontend docs/screenshots/m5-gc
git commit -m "feat(lab): add atomic GC import and SPC alerts"
```

### Task 9b: M6 Trợ lý AI hỏi–đáp read-only (mở rộng, chỉ khi Gate G4 đạt)

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/services/assistant.py`
- Create: `backend/app/routers/assistant.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/main.py`
- Create: `frontend/src/components/AssistantWidget.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/api.ts`
- Modify: `backend/.env.sqlite.example`, `backend/.env.postgres.example`
- Test: `backend/tests/test_assistant.py`

**Interfaces:**
- Produces: `POST /api/v1/assistant/ask` body `{question}` → `{answer, tools_called, data}`.
- Consumes: các service/API đọc sẵn có của M1–M4.

- [x] **Step 1: Thêm cấu hình bật/tắt và provider**

`backend/app/config.py` thêm:

```python
ai_assistant_enabled: bool = False
ai_provider: str = "none"       # none | openai | ollama
ai_api_key: str | None = None
ai_model: str = "gpt-4o-mini"
ai_base_url: str | None = None  # dùng cho ollama/local
```

Mặc định tắt để không ảnh hưởng môi trường chưa cấu hình.

- [x] **Step 2: Viết failing tests an toàn (không phụ thuộc LLM thật)**

```python
def test_assistant_disabled_returns_503(client, lab_headers, monkeypatch):
    monkeypatch.setattr("app.config.settings.ai_assistant_enabled", False)
    response = client.post(
        "/api/v1/assistant/ask",
        headers=lab_headers,
        json={"question": "Tồn kho NVL-QUE còn bao nhiêu?"},
    )
    assert response.status_code == 503

def test_assistant_only_allows_whitelisted_tools():
    from app.services.assistant import ALLOWED_TOOLS
    assert set(ALLOWED_TOOLS) == {
        "get_inventory",
        "get_batch_status",
        "list_expiring_batches",
        "list_open_capa",
        "simulate_recall",
    }

def test_assistant_tool_runs_with_user_permissions(db, lab_user):
    from app.services.assistant import run_tool
    result = run_tool("get_inventory", {}, db=db, user=lab_user)
    assert "items" in result
```

- [x] **Step 3: Chạy test để xác nhận fail**

```powershell
Set-Location backend
$env:DATABASE_URL="sqlite://"
pytest tests/test_assistant.py -v
```

- [x] **Step 4: Cài tool registry read-only**

`ALLOWED_TOOLS` là dict tên → hàm; mỗi hàm nhận `(params, db, user)` và gọi lại service đọc hiện có với RBAC của `user`. Không có tool ghi. `run_tool` từ chối tên ngoài whitelist bằng `ValueError`.

- [x] **Step 5: Cài provider adapter và endpoint**

- `provider=none`: endpoint trả 503 (dùng cho môi trường chưa cấu hình/CI).
- `provider=openai|ollama`: gửi câu hỏi + tool schema; nhận tool chọn; thực thi qua `run_tool`; soạn câu trả lời tiếng Việt kèm dữ liệu.
- Ghi `AssistantQueryLog(user_id, question, tools_called)`.
- Bọc lỗi provider (timeout, key sai) thành thông báo thân thiện, không 500.

- [x] **Step 6: Cài AssistantWidget đồng bộ shell**

Ô chat nổi chỉ hiển thị khi backend báo `assistant_enabled=true`; dùng màu `--color-primary`/`--color-surface` từ tokens; gửi câu hỏi trong `try/catch`, lỗi hiện trong widget (không crash app); hiển thị câu trả lời và nguồn dữ liệu; không có nút thực hiện hành động ghi. Tick checklist 0b.3 cho widget; lưu `docs/screenshots/m6-assistant/`.

- [x] **Step 7: Verify và commit** (verify xong; commit N/A — chưa init Git)

```powershell
Set-Location backend
$env:DATABASE_URL="sqlite://"
pytest tests/test_assistant.py -v
Set-Location ..\frontend
npm run build
git add backend frontend docs/screenshots/m6-assistant
git commit -m "feat(assistant): add read-only AI query assistant (M6)"
```

### Task 10: UAT, chỉ số và báo cáo luận văn

**Files:**
- Modify: `docs/uat-test-cases.md`
- Modify: `docs/uat-results.md`
- Create: `docs/thesis-metrics.md`
- Modify: `docs/software-validation.md`
- Modify: `docs/demo-video-script.md`
- Modify: `docs/bao-cao/noi-dung/00-mo-dau.md`
- Modify: `docs/bao-cao/noi-dung/chuong-1.md`
- Modify: `docs/bao-cao/noi-dung/chuong-2.md`
- Modify: `docs/bao-cao/noi-dung/chuong-3.md`
- Modify: `docs/bao-cao/noi-dung/chuong-4.md`

**Interfaces:**
- Produces: bằng chứng Gate G5 và nội dung bảo vệ.

- [x] **Step 1: Chạy tối thiểu 18 UAT cases** (20 cases; 16 automated evidence; human formal còn chờ)

Phân bổ:

- M1: 5 cases (role, valid transition, invalid transition, release gate, certificate).
- M2: 4 cases (auto-create, duplicate prevention, overdue, close validation).
- M3: 4 cases (FEFO, expired, insufficient stock rollback, cancel restore).
- M4: 3 cases (passport, multi-level recall, CSV).
- M5: 2 cases nếu triển khai (invalid import, SPC alert).
- M6: 2 cases nếu triển khai (trả lời đúng dữ liệu; từ chối câu hỏi ngoài quyền/không có dữ liệu).

- [~] **Step 2: Đo và ghi số liệu thật** (template + evidence tự động; stopwatch key-user còn chờ)

```markdown
| Metric | Baseline | Digital QMS | Kết quả |
|---|---:|---:|---|
| Lô chưa release bị chặn | 0/5 | /5 | |
| CCP fail có CAPA | 0/5 | /5 | |
| FEFO chọn đúng | thủ công | /10 | |
| Recall runtime | thủ công | ms | |
| Nhập 10 GC rows | giây | giây | |
```

Không điền giá trị trước khi chạy.

- [x] **Step 3: Viết báo cáo theo đóng góp mới**

1. Chương 1: hiện trạng và gap.
2. Chương 2: Hold‑Release, CAPA, FEFO, trace/recall, SPC.
3. Chương 3: thiết kế M1–M4, ERD, state diagram, API.
4. Chương 4: cài đặt, UAT, số liệu, hạn chế.

- [x] **Step 4: Chuẩn bị demo 5 phút**

```text
00:00 Đăng nhập thủ kho, nhập lô → quarantine
00:40 Đăng nhập Lab, kiểm nghiệm pass → awaiting_release
01:20 Đăng nhập ATTP, release + tải certificate
02:00 Tạo fail khác → CAPA tự sinh, xử lý và xác minh
03:00 Duyệt lệnh SX → FEFO reservation
04:00 Mở QR/passport → chạy recall → export CSV
```

- [x] **Step 5: Final verification**

```powershell
Set-Location backend
pytest tests -q
Set-Location ..\frontend
npm run build
npx playwright test
```

Expected: tất cả exit code 0; kết quả được ghi vào `docs/uat-results.md`.

- [x] **Step 6: Commit tài liệu** — N/A (chưa init Git)

```powershell
git add docs
git commit -m "docs: add Digital QMS UAT metrics and thesis chapters"
```

### Task 11: M7 Hồ sơ, quản lý tài khoản, ảnh vật tư (chỉ khi Gate G4 đạt)

**Files:**
- Spec: `docs/superpowers/specs/2026-08-16-m7-profile-users-product-images-design.md`
- Modify: `backend/app/models.py` (`User.avatar_url`, `Material.image_url`)
- Create: Alembic revision M7 columns + thư mục upload (nếu dùng file local)
- Modify: `backend/app/routers/auth.py`, `materials.py`
- Create: `backend/app/routers/users.py`
- Modify: `backend/app/schemas.py`
- Create: `frontend/src/pages/Profile.tsx`, `Users.tsx`
- Modify: `frontend/src/Layout.tsx`, `App.tsx`, `api.ts`, `Inventory.tsx`, `StockIn.tsx`, `StockOut.tsx`
- Create: `docs/screenshots/m7-profile/`

**Interfaces:**
- Produces: profile self-service, admin user CRUD tối thiểu, material images trên UI kho.
- Consumes: JWT/RBAC hiện có; design system Task 1.5.
- **Không** thêm route đăng ký công khai.

- [x] **Step 1: Migration + schema** — SQLite Alembic head `a1b2c3d4e5f6` (2026-08-16). Khi dùng PostgreSQL: chạy `alembic upgrade head`.

Thêm `users.avatar_url`, `materials.image_url` (nullable String).

- [x] **Step 2: API profile + password** — `tests/test_auth_profile.py` xanh

`PATCH /auth/me`, `POST /auth/me/password` (bắt buộc mật khẩu hiện tại); `POST /auth/me/avatar`.

- [x] **Step 3: API users (admin only)** — `tests/test_users_admin.py` xanh

`GET/POST /users`, `PATCH /users/{id}` (`full_name`, `role`, `is_active`). Chặn non-admin 403. Không self-register.

- [x] **Step 4: API/ảnh vật tư**

`PATCH /materials/{id}`, `POST /materials/{id}/image` (jpg/png/webp ≤ 1 MB). Inventory trả `image_url`.

- [x] **Step 5: UI Profile + Users**

`/profile` từ chip user topbar/sidebar. `/users` chỉ hiện với admin. Checklist 0b.3 (pattern shell).

- [x] **Step 6: UI ảnh trên kho**

Thumbnail trên Inventory (bảng + card mobile), StockIn preview, StockOut preview. Placeholder khi chưa có ảnh.

- [x] **Step 7: Verify** — `pytest tests/test_auth_profile.py tests/test_users_admin.py` **8 passed**; `npm run build` xanh (2026-08-16)

```powershell
Set-Location backend
$env:DATABASE_URL="sqlite://"
pytest tests/test_auth_profile.py tests/test_users_admin.py -v
Set-Location ..\frontend
npm run build
```

- [~] Screenshot `docs/screenshots/m7-profile/` (chưa chụp). Commit N/A nếu chưa init Git.

---

## 7. Lộ trình 16 tuần

| Tuần | Task | Deliverable |
|---|---|---|
| 1 | Task 0–1 | Baseline và đề cương GV xác nhận |
| 1–2 | Task 1.5 | Design system + shell UI đồng bộ (Gate G1.5) |
| 2–3 | Task 2 | Schema/Alembic ổn định |
| 4–5 | Task 3–4 | M1 Hold‑Release API **+ UI** + certificate |
| 6–7 | Task 5 | M2 CAPA/NCR API **+ UI** |
| 8–9 | Task 6 | M3 FEFO/reservation API **+ UI** |
| 10 | Task 7 | M4 QR/Recall API **+ UI** |
| 11 | Task 8 | SQLite + PostgreSQL/Docker/CI/E2E |
| 12 | Task 9 và/hoặc 9b, hoặc buffer | M5 và/hoặc M6 nếu G4 đạt (API+UI cùng lúc) |
| 13–14 | Task 10 | UAT, metrics, chương báo cáo |
| 15 | Hoàn thiện / Task 11 (M7) | M7 code xong 2026-08-16; slide/video rehearsal |
| 16 | Buffer | Sửa theo GV và đóng bản nộp |

---

## 8. Chỉ số đánh giá

| Module | Chỉ số | Mục tiêu |
|---|---|---|
| M1 | Lô chưa release bị chặn issue/start | 100% scenario bị chặn |
| M1 | Transition sai role/trạng thái | 100% trả 400/403 |
| M2 | CCP fail tạo CAPA | 100% source fail có một CAPA mở |
| M2 | CAPA thiếu verification bị đóng | 0 trường hợp |
| M3 | FEFO chọn đúng | 10/10 scenario |
| M3 | Cancel làm lệch tồn | 0 scenario |
| M4 | Recall completeness | 100% expected downstream |
| M4 | Recall runtime | ≤ 3 giây trên dataset demo |
| M5 | Import 10 dòng so với nhập tay | nhanh hơn ≥ 50% |
| M6 | Trả lời gọi đúng tool whitelist | 100% dùng tool hợp lệ |
| M6 | Không trả dữ liệu ngoài quyền/không bịa số liệu | 0 trường hợp vi phạm |
| M7 | Chỉ admin tạo/khóa user; không self-register | 100% non-admin bị 403 |
| M7 | Đổi mật khẩu bắt buộc mật khẩu hiện tại | 100% case sai → 400 |
| CSDL | Alembic upgrade trên SQLite/PostgreSQL sạch | 2/2 thành công |
| CSDL | Unit/API SQLite + integration PostgreSQL | 100% critical tests pass |

---

## 9. Rủi ro và kiểm soát

| Rủi ro | Kiểm soát |
|---|---|
| Nhầm `ccp1_status` với `quality_status` | CCP là kết quả; quality là quyết định. Test riêng cả hai. |
| Migration kép | Từ Task 2 chỉ Alembic; DB demo được tạo sạch. |
| Code chạy SQLite nhưng lỗi PostgreSQL | CI hai profile, Alembic và integration test PostgreSQL. |
| Query PostgreSQL không chạy SQLite | Service dùng SQLAlchemy chung; dialect branch chỉ dành cho row lock. |
| Bật quarantine làm E2E cũ đỏ | Sửa E2E trong Task 3 cùng commit. |
| Hai order reserve cùng tồn | PostgreSQL row lock + transaction + test concurrency. |
| Cancel làm tồn ảo | Movement đảo chiều, không sửa lịch sử OUT. |
| CAPA bị tạo trùng | Idempotency theo source và CAPA chưa đóng. |
| Recall loop/N+1 | BFS visited sets và query theo lớp. |
| File GC khác format thực tế | Công bố rõ CSV chuẩn luận văn; không tuyên bố tích hợp thiết bị thật. |
| Phạm vi quá lớn | Không bắt đầu M5/M6 trước G4; giữ buffer tuần 12. |
| Demo phụ thuộc internet | Toàn bộ stack chạy local; M6 có provider local (Ollama) và công tắc tắt. |
| Chatbot bịa số liệu | M6 chỉ đọc qua tool whitelist; không có dữ liệu thì trả lời không tìm thấy. |
| Chatbot lộ dữ liệu ngoài quyền | Tool chạy dưới JWT người dùng; RBAC do API nền quyết định. |
| Chatbot gây hành động sai | M6 không có tool ghi; không release/đóng CAPA. |
| Để UI cuối kỳ rồi “sửa lại” | Task 1.5 khóa shell; mỗi module tick checklist 0b.3; tuần 15–16 cấm redesign. |
| Màn hình mới lệch màn hình cũ | Áp cùng tokens/components cho Layout + trang TTTN khi mở module liên quan. |
| Lỗi API hiện thô / trang trắng | Bắt buộc `try/catch` + AlertBanner; ErrorBoundary bọc Routes; detail tiếng Việt từ backend. |

---

## 10. Definition of Done

Luận văn phần mềm chỉ được coi là hoàn thành khi:

1. M1–M4 có API, **UI đồng bộ shell**, RBAC, audit và test; mỗi module có screenshot trong `docs/screenshots/`.
2. Design system Task 1.5 đã khóa trước khi làm màn hình module; tuần cuối không redesign.
3. Mọi thao tác UI/API có `try/catch`; lỗi chỉ hiện AlertBanner tiếng Việt, không trang trắng/stack thô.
4. Dev/API chạy được với SQLite chỉ bằng `DATABASE_URL`.
5. Flow demo 5 phút chạy end-to-end trên PostgreSQL local.
6. Alembic nâng cấp DB sạch thành công trên cả SQLite và PostgreSQL.
7. Negative cases release, CAPA close, expired batch và insufficient reservation đều bị chặn đúng.
8. SQLite unit/API tests và PostgreSQL integration/concurrency tests đều xanh.
9. Frontend build và Playwright smoke đều xanh.
10. Recall Simulator trả đúng toàn bộ downstream và export CSV.
11. UAT ghi kết quả thật; metrics không để trống khi nộp báo cáo.
12. Báo cáo phân biệt rõ nền TTTN và đóng góp mới của luận văn.
13. M5 và M6 nếu chưa hoàn thành được ghi là hướng phát triển, không để code dở trong demo chính.
14. Nếu bật M6: trợ lý chỉ đọc, tôn trọng RBAC, không bịa số liệu, tắt được để demo offline, và widget cùng theme shell.

---

## 11. Checklist vận hành — theo dõi chi tiết

> Chỉ tick `[x]` khi đã kiểm tra thật. Tổng quan nhanh: đầu file **✅ CHECKLIST TỔNG HỢP**.

### 11.0 Mirror nhanh

- [x] Coding Task 0 → 11
- [x] Gate G0 / G1.5 / G2 / G3 / G4
- [ ] G1 chữ ký GV
- [ ] G5 UAT formal
- [ ] Screenshot M7
- [ ] Docker Desktop (tuỳ chọn / waived)

### 11.1 Go/No-Go — được phép bắt đầu code

- [x] Đã đọc toàn bộ `planluanvan.md`, đặc biệt Global Constraints, mục 0b và Gates.
- [x] Đã chốt hướng **Digital QMS**, phạm vi lõi M1–M4 và phạm vi mở rộng M5/M6/M7.
- [~] Đã xác nhận với GV: tài liệu provisional đã khóa; **chữ ký/email chính thức vẫn chờ** (triển khai theo ủy quyền sinh viên 18/07/2026).
- [x] Đã xác nhận SQLite dùng dev/unit test; PostgreSQL dùng integration/concurrency/demo.
- [x] Đã xác nhận UI làm cùng API, không redesign cuối kỳ.
- [x] Đã xác nhận mọi async UI dùng `try/catch`, `AlertBanner`, loading và ErrorBoundary.
- [x] Không có yêu cầu nghiệp vụ quan trọng nào còn chưa quyết định.

**Go:** các mục kỹ thuật `[x]`; G1 formal vẫn `[~]`.  
**No-Go:** không còn mục kỹ thuật `[ ]` chặn coding.

### 11.2 Kiểm tra môi trường máy

- [x] Python và pip hoạt động: Python 3.13.3 (`py --version`).
- [x] Node.js và npm hoạt động: Node v22.16.0, npm 10.9.2.
- [~] Docker Desktop/Compose: **chưa cài** — waived; dùng PostgreSQL local thay Compose.
- [x] PostgreSQL local sẵn sàng trên `:5432` (DB `oxeyns`; Alembic hiện tại head `a1b2c3d4e5f6` trên SQLite).
- [x] Cổng local: frontend `5173`, backend `8000`, PostgreSQL `5432` đang dùng được.
- [x] `backend/.env` chỉ chứa secret dev local; repo chưa Git track.
- [x] Đủ dung lượng backup DB SQLite (`oxeyns.db.bak-*`) và build frontend.

### 11.3 Backup và baseline bắt buộc (Task 0)

- [x] Đã kiểm tra `backend/oxeyns.db`; lúc baseline file không tồn tại nên backup là N/A.
- [x] Không tạo file backup rỗng/giả khi DB nguồn không tồn tại.
- [x] Backend baseline chạy xanh (ghi trong `docs/baseline-pytest.txt`).
- [x] Frontend baseline build xanh.
- [x] Đã lưu kết quả vào `docs/baseline-pytest.txt`.
- [x] Đã ghi warning deprecation baseline; không tính là lỗi module mới.
- [x] Đã kiểm tra Git: thư mục chưa phải repository; làm tại chỗ và không commit.
- [x] Sau migration: đã có backup `backend/oxeyns.db.bak-20260718-*`.

### 11.4 Checklist khóa giao diện (Task 1.5)

- [x] `tokens.css` đã được tạo và import một lần.
- [x] `PageHeader`, `StatusBadge`, `DataTable`, `EmptyState`, `AlertBanner`, `FilterBar`, `ActionBar`, `ErrorBoundary` đã có props typed.
- [x] `ErrorBoundary` bọc routes trong `App.tsx`.
- [x] Layout, Dashboard và Inventory dùng cùng shell/tokens.
- [x] Mọi load/submit đã sửa trong Task 1.5 có `try/catch/finally`.
- [x] Lỗi network hiện tiếng Việt; không hiện JSON/stack/React white screen.
- [x] `npm run build` xanh.
- [x] Screenshot shell PNG: `docs/screenshots/00-shell/{login,dashboard,inventory}.png` (2026-07-18).
- [x] Gate G1.5 đạt trước khi tạo màn hình M1.

### 11.5 Chu kỳ bắt buộc cho từng task

Áp dụng cho Task 2–10 (đã thực hiện trong session triển khai) và Task 11 / M7 (2026-08-16):

- [x] Đọc lại **Files**, **Interfaces**, Gate và task phụ thuộc.
- [x] Chỉ sửa file trong phạm vi task; thay đổi ngoài phạm vi phải ghi lý do.
- [x] Viết test fail trước khi implementation (RED) — áp dụng các module M1–M7.
- [x] Chạy test và xác nhận fail đúng nguyên nhân.
- [x] Cài implementation nhỏ nhất để pass (GREEN).
- [x] Chạy test riêng của task.
- [x] Chạy toàn bộ backend tests liên quan.
- [x] Nếu có UI: làm UI ngay trong task, không dời sang cuối.
- [x] Mọi async UI dùng `try/catch/finally`; lỗi qua `AlertBanner`, nút có loading/disabled.
- [x] Tick checklist UI 0b.3 và chụp screenshot module (PNG 2026-07-18; M7 screenshot còn `[~]`).
- [x] Chạy `npm run build`.
- [x] Nếu đổi schema: Alembic trên SQLite (`a1b2c3d4e5f6`); PostgreSQL chạy `upgrade head` khi dùng PG.
- [x] Reservation/concurrency: `tests/test_postgres_concurrency.py` pass trên PG local.
- [x] Kiểm tra diagnostics khi sửa lỗi runtime (certificate, assistant, transition).
- [x] Review: không commit secret; `.env` local only.
- [x] Chỉ commit khi user yêu cầu (chưa init Git).
- [x] Cập nhật checkbox task và trạng thái Gate trong file này.

### 11.6 Master task tracker

| Thứ tự | Task | Deliverable bắt buộc | Gate | Trạng thái |
|---:|---|---|---|---|
| 0 | Baseline + backup | pytest/build baseline xanh | G0 | [x] Hoàn thành |
| 1 | Khóa đặc tả | Tài liệu phạm vi/API | G1 | [x] Deliverable xong — GV formal `[~]` |
| 1.5 | Design system | Shell + components + ErrorBoundary + PNG | G1.5 | [x] Hoàn thành |
| 2 | Alembic/models | Schema SQLite + PostgreSQL | — | [x] Hoàn thành |
| 3–4 | M1 Hold‑Release | API + board + certificate + PNG | — | [x] Hoàn thành |
| 5 | M2 CAPA/NCR | API + UI + overdue + PNG | G2 | [x] Hoàn thành |
| 6 | M3 FEFO/reservation | API + UI + PG concurrency + PNG | G3 | [x] Hoàn thành |
| 7 | M4 QR/Recall | API + UI + CSV + PNG | — | [x] Hoàn thành |
| 8 | Hai CSDL/CI/E2E | PG local + Playwright smoke (Docker waived) | G4 | [x] Đạt với PG local |
| 9 | M5 GC/SPC | Import + SPC + PNG | — | [x] Hoàn thành |
| 9b | M6 AI assistant | Local read-only + PNG | — | [x] Hoàn thành |
| 10 | UAT/metrics/báo cáo | Template + evidence tự động + PNG | G5 | [x] Kỹ thuật xong — UAT key-user formal `[~]` |
| 11 | M7 Profile / Users / ảnh vật tư | Profile + admin users + thumbnails kho + PNG | — | [x] Hoàn thành (2026-08-16) |

### 11.7 Gate tracker

- [x] **G0:** baseline pytest/build xanh; backup N/A rồi có backup sau khi có DB.
- [~] **G1:** đặc tả Digital QMS đã khóa trong docs; **chờ chữ ký/email GV chính thức**.
- [x] **G1.5:** design system + ErrorBoundary + shell + PNG `00-shell`.
- [x] **G2:** M1+M2 API/UI + negative tests + PNG `m1-quality`, `m2-capa`.
- [x] **G3:** FEFO/reservation SQLite + PostgreSQL concurrency test xanh + PNG `m3-fefo`.
- [x] **G4:** M1–M6 trên SQLite; Alembic+PG profile+concurrency; Playwright smoke trên `localhost:5173`. Docker Compose waived (chưa cài Docker Desktop).
- [~] **G5:** UAT cases/results/metrics/demo script + verification evidence đã có; **chữ ký key-user và số đo stopwatch formal còn chờ**.

Bằng chứng tổng hợp: `docs/verification-checklist-2026-07-18.md`.

### 11.8 Checklist an toàn dữ liệu và migration

- [x] Không xóa `oxeyns.db` trước khi backup (đã backup trước khi sửa schema khi có file).
- [x] Không dùng `git reset --hard` hoặc lệnh hủy thay đổi chưa được duyệt.
- [x] Không dùng đồng thời `run_migrations()` thủ công và Alembic (`migrate.py` chỉ còn shim).
- [x] Migration có đường upgrade rõ; backfill `quality_status` từ CCP1 đã chạy.
- [x] Test DB dùng SQLite in-memory / PG riêng; không phá DB demo bằng pytest mặc định.
- [~] PostgreSQL demo: DB `oxeyns` sẵn; nên backup thêm trước buổi bảo vệ.
- [x] Transaction lỗi rollback trong router quality/capa/assistant.
- [x] Cancel order dùng movement đảo chiều (logic M3).
- [x] API key AI/secret: provider `local` mặc định; không đưa secret production vào repo.

### 11.9 Checklist lỗi và trải nghiệm người dùng

- [x] Handler async module mới có `try/catch` + AlertBanner.
- [x] Không hiện stack/`JSON.stringify(err)` trên DOM (parseError tiếng Việt).
- [x] 400/403/network có thông báo tiếng Việt (Hold-Release, certificate, assistant).
- [x] Form giữ dữ liệu khi submit lỗi (pattern hiện có).
- [x] Nút submit/disable khi `busy`.
- [x] Loading/empty/error/success có trạng thái riêng (EmptyState/AlertBanner).
- [x] Backend trả `detail` tiếng Việt, không traceback trong response thường.
- [x] M6 tắt/provider lỗi không crash; widget báo trạng thái / hướng dẫn.
- [x] M7 Profile/Users: lỗi tiếng Việt, nút busy/disabled; không self-register.

### 11.10 Checklist trước mỗi buổi demo

- [x] PostgreSQL local healthy (`:5432`, DB `oxeyns`). Docker Compose N/A.
- [x] `alembic upgrade head` thành công trên PG (`dcc79cce7fb4`).
- [x] Backend pytest critical + postgres markers xanh (profile + concurrency).
- [x] Frontend Playwright smoke xanh (`e2e/digital-qms.spec.ts`).
- [x] Seed/demo data có sẵn trên SQLite local và đã seed PG.
- [x] Flow demo 5 phút đã có script (`docs/demo-video-script.md`) + smoke login→/quality.
- [x] M6 dùng provider `local` (offline-safe); có thể tắt bằng `.env`.
- [x] Có backup SQLite và phương án SQLite nếu PG sự cố.
- [~] Rehearsal full 5 phút với người thật trước bảo vệ (nên làm lại ngày bảo vệ).

### 11.11 Checklist cuối — đã xong / còn lại

**Ba chức năng M7 (yêu cầu của bạn)**

- [x] Profile người đăng nhập (`/profile`) — đổi tên, mật khẩu, avatar
- [x] Không đăng ký công khai — thay bằng admin tạo/khóa user tại `/users`
- [x] Ảnh sản phẩm: **Thêm / Đổi / Xóa** trên Tồn kho + hiện ở Nhập/Xuất kho
- [x] Ảnh demo seed (PNG) cho NVL-QUE / TP-TCA / BTP-THO

**Module khác**

- [x] M1 Hold‑Release (API + UI + test)
- [x] M2 CAPA/NCR (API + UI + test)
- [x] M3 FEFO / giữ chỗ (API + UI + test)
- [x] M4 QR / Recall (API + UI + test)
- [x] M5 GC Import / SPC (API + UI + test)
- [x] M6 Trợ lý AI chỉ đọc (API + UI + test)
- [x] Test M7 (8/8 pass)
- [x] Build frontend OK
- [x] Migration SQLite (`a1b2c3d4e5f6`)

**Còn lại**

- [ ] GV ký / email xác nhận đề cương (G1)
- [ ] UAT với người dùng thật + đo thời gian (G5)
- [ ] Chụp screenshot Hồ sơ / Users → `docs/screenshots/m7-profile/`
- [ ] Backup PostgreSQL trước bảo vệ
- [ ] Tập demo 5 phút trước bảo vệ
- [ ] (Tuỳ chọn) Cài Docker Desktop
