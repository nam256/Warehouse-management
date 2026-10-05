# Checklist test tay — Oxeyns Digital QMS

**URL:** http://localhost:5173  
**Trình duyệt:** Chrome / Edge  
**Quy tắc:** Đăng xuất rồi đăng nhập lại mỗi khi đổi vai trò. Không dùng `admin` để né quyền khi test nghiệp vụ.

---

## 0. Chuẩn bị

Backend cổng 8000, frontend cổng 5173.

```powershell
# Terminal 1
cd C:\Users\nam\Desktop\BC_TTTN\backend
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

# Terminal 2
cd C:\Users\nam\Desktop\BC_TTTN\frontend
npm run dev
```

Reset dữ liệu (khuyến nghị trước khi làm Phần 2):

```powershell
cd C:\Users\nam\Desktop\BC_TTTN\backend
.\.venv\Scripts\python reset_db.py
```

| Vai trò trên UI | User | Mật khẩu |
|-----------------|------|----------|
| Thủ kho | `thu_kho` | `kho123` |
| Phòng kiểm nghiệm | `lab` | `lab123` |
| An toàn thực phẩm | `attp` | `attp123` |
| Nhân viên kỹ thuật | `ky_thuat` | `kt123` |
| Quản lý nhà máy | `ql_nm` | `ql123` |
| Quản trị viên | `admin` | `admin123` |

| Điểm KS | Đạt | Không đạt |
|---------|-----|-----------|
| CCP1 C14 | `13.50` | `12.00` |
| CCP2 | Ttop `108` + % t-CA `99.5` | Ttop `105` hoặc % t-CA `98` |

### Sổ ghi mã (điền khi test)

| Dữ liệu | Mã ghi được |
|---------|-------------|
| Lô NVL đạt, HSD gần (LOT-DAT) | |
| Lô NVL đạt, HSD xa (LOT-DAT-2) | |
| Lô NVL hỏng CCP1 (LOT-HONG) | |
| Mẻ sản xuất | |
| Lô thành phẩm | |
| Mã CAPA | |

---

# PHẦN 1 — Test từng chức năng

## A. Đăng nhập / phân quyền

- [ ] Sai mật khẩu → *Sai tên đăng nhập hoặc mật khẩu*
- [ ] `Tài khoản dùng thử` + **Đăng nhập** → vào Dashboard
- [ ] `thu_kho` **không** thấy menu **Quản lý tài khoản**
- [ ] `admin` thấy **Quản lý tài khoản**
- [ ] Nút **Đăng xuất** → về trang login

## B. Hồ sơ / tài khoản / ảnh (M7)

**Hồ sơ** (mọi user, click tên góc trên):

- [ ] Đổi họ tên → *Đã cập nhật hồ sơ.* Topbar đổi tên
- [ ] Đổi mật khẩu < 6 ký tự → báo lỗi
- [ ] Đổi mật khẩu OK → đăng xuất, đăng nhập bằng mật khẩu mới (đổi lại mật khẩu cũ nếu còn test)

**Admin → Quản lý tài khoản:**

- [ ] `thu_kho` mở `/users` → bị chặn / không có menu
- [ ] Admin **Tạo tài khoản** (user + vai trò) → hiện trong danh sách
- [ ] Khóa user → user đó không đăng nhập được
- [ ] Không có form đăng ký công khai trên login

**Tồn kho — ảnh vật tư** (admin / thủ kho / QL NM):

- [ ] **Thêm ảnh** PNG/JPG cho `NVL-QUE` → thumbnail hiện
- [ ] **Đổi ảnh** → ảnh mới
- [ ] **Xóa ảnh** → hết thumbnail
- [ ] Thumbnail hiện ở **Nhập kho** và **Xuất kho**

## C. Kho (nền TTTN + M3)

**Tồn kho**

- [ ] Có cột tồn vật lý / tồn khả dụng / hạn dùng
- [ ] Tab Tất cả / Nguyên liệu / Thành phẩm / Bán thành phẩm
- [ ] **Xuất CSV** / **Xuất PDF** tải được

**Nhập kho** (`thu_kho`)

- [ ] Nhập NVL + hạn dùng → lô **Chờ xử lý** / CCP1 chờ kiểm nghiệm
- [ ] Thủ kho **không** nhập được C14 / không tự pass chất lượng
- [ ] Lô mới chưa xuất được cho sản xuất

**Xuất kho** (`thu_kho`)

- [ ] Lô cách ly / chưa giải phóng hiện *(không đủ điều kiện)*
- [ ] **Gợi ý hạn dùng sớm** chọn đúng lô HSD gần hơn
- [ ] Xuất vượt tồn → báo lỗi, không lưu

**Yêu cầu mua hàng**

- [ ] Tạo YCMH khi tồn thấp / thủ công → thấy phiếu

## D. Hold-Release (M1) — Phê duyệt chất lượng

Đăng nhập `lab`:

- [ ] Lô mới: **Bắt đầu lấy mẫu** → **Bắt đầu kiểm nghiệm**
- [ ] Chưa có CCP1 đạt: nút gửi ATTP **disabled**
- [ ] Sau CCP1 đạt: **Gửi Bộ phận an toàn thực phẩm phê duyệt** → **Chờ phê duyệt** (chưa tự giải phóng)

Đăng nhập `thu_kho`:

- [ ] Không có nút **Giải phóng lô**

Đăng nhập `attp`:

- [ ] Không giải phóng được lô còn **Chờ xử lý**
- [ ] Lô **Chờ phê duyệt** + ghi chú → **Giải phóng lô** → **Đã giải phóng**
- [ ] Tải chứng nhận PDF **sau** khi giải phóng được; **trước** thì bị chặn
- [ ] **Từ chối lô** khi cần → trạng thái **Từ chối**

## E. Lab / CCP / GC-SPC (nền + M5)

- [ ] Nhập thủ công CCP1 `13.50` → đạt
- [ ] Nhập CCP1 `12.00` → không đạt + tự có CAPA
- [ ] Gửi lại cùng fail → **không** tạo CAPA mở trùng
- [ ] Tab **Import GC & SPC**: CSV hợp lệ → ghi được
- [ ] CSV có 1 dòng sai → cả file không ghi
- [ ] Import trùng (cùng file) → không nhân đôi
- [ ] SPC hiện mean / UCL / LCL; điểm lệch tô đỏ

## F. CAPA (M2) — Khắc phục sai lệch

- [ ] Tab **Đang mở** thấy phiếu vừa fail
- [ ] **Bắt đầu điều tra** → **Ghi nhận hành động** → **Xác minh CAPA**
- [ ] **Đóng CAPA** khi chưa xác minh → bị chặn
- [ ] Đóng đủ xác minh + disposition → tab **Đã đóng**
- [ ] Tab **Quá hạn** (nếu có due date quá hạn) tô đỏ / lọc được
- [ ] Link nguồn lỗi nhảy đúng Kiểm nghiệm / Sản xuất / Chất lượng

## G. Sản xuất + FEFO / giữ chỗ (M3)

`ky_thuat`:

- [ ] **Tạo mẻ** → bản nháp, chưa giữ chỗ

`ql_nm`:

- [ ] **Duyệt và giữ chỗ nguyên liệu** → giữ lô HSD sớm nhất, trạng thái reserved
- [ ] Tồn khả dụng giảm; tồn vật lý chưa giảm
- [ ] Duyệt khi thiếu tồn → báo lỗi, **không** giữ chỗ một phần
- [ ] Lô hết hạn / cách ly **không** được giữ chỗ

`ky_thuat`:

- [ ] **Bắt đầu sản xuất** → xuất đúng lô đã giữ; tồn vật lý giảm
- [ ] Ghi CCP2 đạt (`108` / `99.5`)
- [ ] **Hoàn thành** → có mã lô thành phẩm, chất lượng **Chờ phê duyệt** (không tự released)
- [ ] **Hủy mẻ** (mẻ khác đang chạy) → hoàn tồn khả dụng, lịch sử không bị xóa
- [ ] CCP2 fail → không hoàn thành được; có CAPA

## H. Truy xuất / QR / thu hồi (M4)

- [ ] Gõ mã lô NVL hoặc TP → cây upstream / downstream
- [ ] **Hộ chiếu số** hiện trạng thái CL, kho, SX
- [ ] QR hiển thị; mở link QR ra đúng lô
- [ ] Tải chứng nhận lô (nếu đã released)
- [ ] `attp`: chạy mô phỏng thu hồi + lý do → đủ tầng downstream
- [ ] **Tải CSV** khớp màn hình
- [ ] Sau recall: tồn / reservation / CAPA **không** đổi

## I. HACCP / Audit / Báo cáo / Dashboard

- [ ] **Giám sát điểm kiểm soát**: lọc CCP1/CCP2; xuất biên bản
- [ ] **Nhật ký thao tác**: thấy nhập kho / giải phóng / duyệt mẻ
- [ ] **Báo cáo và xuất file**
  - [ ] Snapshot tồn: CSV/PDF có cột vật lý / giữ chỗ / khả dụng (không còn một cột “Tồn (kg)” mơ hồ)
  - [ ] Theo lô: thấy HSD, CCP1, trạng thái chất lượng tiếng Việt
  - [ ] Tồn theo kỳ: nhập 200, xuất 10 → đầu 0 / nhập 200 / xuất 10 / cuối 190
  - [ ] In phiếu PX sau khi lưu; in lại từ Báo cáo
  - [ ] Sổ xuất kỳ rỗng: file vẫn tải, tổng 0
  - [ ] Phiếu nhập: nhập 200 rồi xuất 10, PDF nhập vẫn 200 kg
  - [ ] Số trên file khớp màn Tồn kho / Xuất kho
  - [ ] CSV mở Excel không lỗi font
- [ ] Dashboard: tồn, mẻ đang chạy, cảnh báo CCP/CAPA/tồn thấp

## J. Trợ lý AI (M6)

- [ ] Nút **Mở trợ lý AI**
- [ ] **Xin chào** → chào / chỉ đọc, **không** hiện NVL-QUE hay 0 kg
- [ ] Tám chip gợi ý luôn hiện; bấm được
- [ ] Hỏi “tồn kho NVL-QUE” → số liệu thật, đúng quyền
- [ ] Hỏi khả dụng vs vật lý / in phiếu PX / sổ xuất ngày → hướng dẫn đúng, không dump tồn seed
- [ ] Hỏi “giải phóng lô …” / đóng CAPA → **không** thực hiện ghi
- [ ] Hỏi chuyện không có dữ liệu → *không tìm thấy* / không bịa số
- [ ] Đóng khung × → mở lại **còn chat**; F5 còn; **Đoạn chat mới** xóa sau xác nhận
- [ ] Treo: nút Hủy hoặc hết ~25s, tin đã gửi còn
- [ ] `lab` hỏi lô hết hạn → báo không có quyền (tiếng Việt)
- [ ] `thu_kho` không thấy dữ liệu ngoài quyền

## K. Test âm / lỗi UI

- [ ] Tắt backend → banner *Không kết nối được máy chủ…* (không trang trắng)
- [ ] 403 hiện tiếng Việt, không JSON thô
- [ ] Nút đang xử lý bị disable, form không bị xóa khi lỗi

---

# PHẦN 2 — Một chu kỳ sản xuất t-CA

Làm **theo thứ tự**. Ghi mã vào sổ mục 0.

### Bước 1 — Thủ kho: nhận 3 lô NVL

Đăng nhập `thu_kho` → **Nhập kho**

- [ ] Lô 1: `NVL-QUE`, 200 kg, HSD **gần** (LOT-DAT) → cách ly
- [ ] Lô 2: `NVL-QUE`, 80 kg, HSD **xa** (LOT-DAT-2) → cách ly
- [ ] Lô 3: `NVL-QUE`, 50 kg (LOT-HONG) → cách ly
- [ ] **Xuất kho**: 3 lô đều không đủ điều kiện

### Bước 2 — Lab: CCP1

Đăng nhập `lab` → **Phê duyệt chất lượng** + **Kiểm nghiệm**

LOT-DAT và LOT-DAT-2:

- [ ] Lấy mẫu → kiểm nghiệm
- [ ] Nhập C14 `13.50` → đạt
- [ ] Gửi ATTP phê duyệt → **Chờ phê duyệt**

LOT-HONG:

- [ ] Nhập C14 `12.00` → không đạt
- [ ] **Khắc phục sai lệch** có 1 CAPA mở (mã: ________)

### Bước 3 — ATTP: giải phóng / từ chối

Đăng nhập `attp` → **Phê duyệt chất lượng**

- [ ] LOT-DAT: ghi chú + **Giải phóng lô** → tải được PDF
- [ ] LOT-DAT-2: **Giải phóng lô**
- [ ] LOT-HONG: **Từ chối lô** (hoặc giữ reject)
- [ ] Thủ kho vẫn không giải phóng được (spot-check)

### Bước 4 — Kỹ thuật: tạo mẻ

Đăng nhập `ky_thuat` → **Sản xuất**

- [ ] Tạo mẻ TP-TCA, SL kế hoạch ~100 kg → bản nháp
- [ ] Chưa có giữ chỗ

### Bước 5 — QL nhà máy: duyệt FEFO

Đăng nhập `ql_nm`

- [ ] **Duyệt và giữ chỗ nguyên liệu**
- [ ] Giữ **LOT-DAT** (HSD gần) trước LOT-DAT-2
- [ ] Không giữ LOT-HONG
- [ ] **Tồn kho**: khả dụng LOT-DAT giảm; vật lý chưa giảm

### Bước 6 — Kỹ thuật: chạy mẻ + CCP2

Đăng nhập `ky_thuat`

- [ ] **Bắt đầu sản xuất** → xuất đúng lô giữ chỗ; tồn vật lý giảm
- [ ] Ghi nhiệt độ đỉnh `108`, % t-CA `99.5`
- [ ] **Hoàn thành** → mã lô TP: ________
- [ ] Lô TP trạng thái **Chờ phê duyệt** (chưa released)

### Bước 7 — Lab + ATTP: thành phẩm

- [ ] `lab` / `attp`: gửi duyệt (nếu cần) rồi **Giải phóng** lô TP
- [ ] Tải certificate lô TP

### Bước 8 — ATTP: truy xuất + thu hồi

Đăng nhập `attp` → **Truy xuất lô**

- [ ] Tra LOT-DAT → thấy mẻ + lô TP
- [ ] Tra lô TP → thấy NVL
- [ ] QR hộ chiếu đúng mã
- [ ] Recall từ LOT-DAT → ra mẻ + lô TP
- [ ] Tải CSV; tồn kho không đổi sau recall

### Bước 9 — ATTP: đóng CAPA lô hỏng

- [ ] CAPA LOT-HONG: điều tra → hành động → xác minh → đóng
- [ ] Không đóng được nếu bỏ trống xác minh

### Bước 10 — Tra cứu chéo

- [ ] Dashboard thấy mẻ xong / CAPA đã đóng
- [ ] Nhật ký có nhập kho, giải phóng, duyệt mẻ, hoàn thành
- [ ] Trợ lý AI: hỏi tồn LOT-DAT / trạng thái lô TP → đúng số
- [ ] Báo cáo CSV/PDF: snapshot tồn, tồn theo kỳ, sổ xuất, phiếu PX, phiếu nhập (SL lúc nhập)

---

# PHẦN 3 — Ca phụ (làm sau ca chính)

## P1. FEFO hai lô

- [ ] Còn cả LOT-DAT và LOT-DAT-2 released
- [ ] Tạo mẻ nhỏ, duyệt → hệ thống ưu tiên HSD gần hơn

## P2. Thiếu tồn

- [ ] Tạo mẻ SL lớn hơn tồn khả dụng
- [ ] Duyệt → lỗi; không có reservation dở

## P3. Hủy mẻ đang chạy

- [ ] Tạo mẻ, duyệt, bắt đầu, **Hủy mẻ**
- [ ] Tồn khả dụng trở lại; movement đảo còn trong lịch sử

## P4. CCP2 fail

- [ ] Mẻ running, ghi Ttop `105` hoặc % t-CA `98`
- [ ] Không hoàn thành được
- [ ] Có CAPA nguồn vận hành

## P5. GC import lỗi

- [ ] CSV 1 dòng `batch_no` không tồn tại → 422, không ghi dòng nào

## P6. Quyền chéo

- [ ] `thu_kho` không release, không đóng CAPA, không duyệt mẻ
- [ ] `ky_thuat` không giải phóng lô
- [ ] `lab` không bấm **Giải phóng lô** (chỉ gửi duyệt)

---

# Ảnh chụp bảo vệ (4 tấm)

Chụp khi demo, lưu vào slide/phụ lục — không cần đặt file vào repo:

- [ ] Tồn kho UI cạnh file CSV/PDF snapshot (ba cột vật lý / giữ chỗ / khả dụng)
- [ ] Phiếu xuất PDF (số PX, SL, người lập)
- [ ] Sổ xuất kho theo kỳ
- [ ] Cảnh báo tồn thấp khi khả dụng thấp dù tồn vật lý còn (lô cách ly / giữ chỗ)

---

# Kết quả buổi test

| Phần | Pass | Fail | Ghi chú |
|------|------|------|---------|
| 1. Chức năng | | | |
| 2. Chu kỳ t-CA | | | |
| 3. Ca phụ | | | |

Người test: ________    Ngày: ________    DB: SQLite / PostgreSQL
