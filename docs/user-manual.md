# Hướng dẫn sử dụng — Oxeyns Kho & SX

**Phiên bản:** MVP v0.1-demo  
**Đối tượng:** Thủ kho, Kỹ thuật, Lab, QL nhà máy, ATTP

---

## 1. Truy cập hệ thống

1. Mở trình duyệt (Chrome/Edge khuyến nghị)
2. Truy cập URL demo (vd. `http://localhost:5173` hoặc server nội bộ)
3. Đăng nhập bằng tài khoản được cấp
4. Sidebar trái hiển thị menu theo **quyền role**

---

## 2. Đăng nhập / Đăng xuất

- Nhập **Tài khoản** và **Mật khẩu** → **Đăng nhập**
- Góc sidebar: tên user và role
- **Đăng xuất** khi rời máy (bảo mật)

*Tài khoản demo: xem `README.md`*

---

## 3. Dashboard (`/`)

**Ai dùng:** Tất cả (nội dung theo quyền)

| Thành phần | Ý nghĩa |
|------------|---------|
| Thẻ tồn NVL/BTP/TP | Số liệu tổng hợp realtime |
| Mẻ đang chạy | Production order status `running` |
| CCP fail / pending | Lô hoặc mẻ cần xử lý |
| Cảnh báo tồn thấp | NVL dưới ngưỡng tối thiểu |
| Danh sách cảnh báo | Chi tiết gần đây |

**Thao tác:** Click menu trái để vào module chi tiết.

---

## 4. Tồn kho (`/inventory`)

**Ai dùng:** Thủ kho, QL NM, ATTP (xem)

- Xem tồn theo **mã hàng** và **lô**
- Cột trạng thái CCP1 (nếu là NVL)
- Cảnh báo tồn thấp theo **tồn khả dụng** (lô cách ly không tính được xuất)
- Export CSV/PDF cùng số với trang Báo cáo (vật lý / giữ chỗ / khả dụng)

---

## 5. Nhập kho (`/stock-in`) — BM-01/GMP01

**Ai dùng:** Thủ kho

### Tạo phiếu nhập

1. Chọn **Nhà cung cấp** và **Nguyên liệu**
2. Nhập **Mã lô NCC**, số lượng, khối lượng
3. Điền **kiểm tra sơ bộ** (màu, mùi, tỷ trọng…)
4. **Lưu** — hệ thống tạo **mã lô nội bộ**, CCP1 = `pending`
5. Chờ Lab nhập C14 → `pass` mới xuất SX

### Lưu ý

- Lô **fail CCP1** bị cô lập — không xuất cho sản xuất
- Mọi thao tác ghi **audit log**

---

## 6. Xuất kho (`/stock-out`)

**Ai dùng:** Thủ kho

1. Chọn **mẻ sản xuất** (Production Order) nếu xuất cho SX
2. Chọn **lô NVL** (chỉ lô CCP1 pass, còn tồn)
3. Nhập số lượng xuất → **Lưu**
4. Tồn giảm tương ứng; liên kết material usage với mẻ

**Lỗi thường gặp:** Xuất vượt tồn → hệ thống báo lỗi, không lưu.

---

## 7. Sản xuất (`/production`) — BM-01/GMP03

**Ai dùng:** Kỹ thuật

### Tạo mẻ

1. **Tạo mẻ mới** — chọn sản phẩm (t-CA), SL kế hoạch, ngày
2. Trạng thái: `draft` → bắt đầu → `running`

### Operation Record

1. Chọn mẻ → thêm **công đoạn** (chưng cất, chiết rót…)
2. Nhập **T**, **P**, **Ttop** (CCP2: 107–110°C)
3. Lưu từng bước trong suốt mẻ (32–37h)

### Hoàn thành mẻ

- Chỉ khi **CCP2 pass** (% t-CA từ Lab + Ttop hợp lệ)
- Nếu fail → xử lý corrective action, không đóng mẻ

---

## 8. Lab (`/lab`) — BM-02/GMP05

**Ai dùng:** Lab

1. **Tạo kết quả GC mới**
2. Chọn loại mẫu: NVL (CCP1) hoặc mẻ SX (CCP2)
3. Nhập **C14** hoặc **% t-CA**, số báo cáo lab, ngày
4. Lưu → hệ thống cập nhật trạng thái CCP tự động

---

## 9. Truy xuất (`/trace`)

**Ai dùng:** QL NM, ATTP, Thủ kho (xem)

- Nhập **mã lô TP** hoặc **mã lô NVL** hoặc **mã mẻ SX**
- Xem chuỗi: NCC → lô NVL → mẻ → lô TP
- Phục vụ khách hàng và thẩm tra FSSC

---

## 10. YCMH (`/purchase`)

**Ai dùng:** Thủ kho

- Tạo **phiếu yêu cầu mua hàng** khi tồn thấp (từ cảnh báo hoặc thủ công)
- Theo dõi trạng thái phiếu (draft/sent — tùy cấu hình)

---

## 11. CCP / HACCP (`/haccp`)

**Ai dùng:** ATTP, Lab, QL NM

- Xem log giám sát CCP1/CCP2
- Lọc theo kỳ (phục vụ thẩm tra 14 ngày/lần)
- Trạng thái pass/fail/pending

---

## 12. Audit (`/audit`)

**Ai dùng:** ATTP, admin

- Tra cứu **audit trail**: user, thời gian, hành động, giá trị cũ/mới
- Lọc theo module: Kho, SX, Lab…
- **Không sửa/xóa** log trên UI

---

## 13. Báo cáo (`/reports`)

**Ai dùng:** Mọi tài khoản đã đăng nhập (Thủ kho in phiếu; QL NM / ATTP đối chiếu hồ sơ)

File CSV mở bằng Excel (UTF-8 BOM, có dấu tiếng Việt). PDF: bấm **Xem trước** trên trang Báo cáo (hoặc Xuất kho) rồi **Tải xuống** nếu đúng phiếu.

| Báo cáo | Mô tả | Ghi nhớ khi bảo vệ |
|---------|--------|---------------------|
| Tồn kho hiện tại | CSV/PDF: tồn **vật lý**, **giữ chỗ**, **khả dụng**. Có chế độ theo vật tư hoặc theo lô (HSD, CCP1, Hold-Release). | Cùng công thức với màn `/inventory`. Lô cách ly: vật lý > 0, khả dụng = 0. |
| Tồn kho theo kỳ | Đầu kỳ / nhập / xuất / hoàn tồn / cuối kỳ. Để trống ngày = đầu tháng → hôm nay. | Tính ngược từ sổ movement, **không** phải khóa sổ kế toán. |
| Sổ xuất kho | CSV/PDF danh sách phiếu PX trong kỳ (xuất tay và xuất cho mẻ SX). | Kỳ rỗng vẫn ra file, tổng 0 kg. |
| Phiếu xuất kho | PDF một số PX. Xem trước rồi tải. Trang Xuất kho in ngay sau khi lưu. | Hồ sơ số hóa, không thay phiếu giấy pháp lý. |
| Phiếu nhập nguyên liệu | PDF theo lô. **Số lượng = SL lúc nhập**, không phải tồn hiện tại nếu đã xuất bớt. | |
| Biên bản vận hành chưng cất | PDF nhiệt độ / t-CA theo lần ghi nhận. | |
| Bảng cân đối nguyên liệu | Đối chiếu đầu vào mẻ và thành phẩm. | |
| Biên bản pha trộn | Công thức và khối lượng pha. | |
| Kết quả sắc ký khí | Kết quả kiểm nghiệm phòng lab. | |

**Hạn chế xuất tay:** mỗi lần lưu phiếu xuất là **một lô**. Sản xuất đã phân bổ FEFO lúc duyệt mẻ.

**Đối chiếu số (demo):** tồn trên UI = file snapshot; tổng xuất kỳ + tồn cuối khớp ledger; phiếu nhập 200 kg vẫn 200 sau khi xuất 10 kg.

---

## 14. Xử lý sự cố nhanh

| Triệu chứng | Gợi ý |
|-------------|--------|
| Không đăng nhập được | Kiểm tra API backend đang chạy |
| Không xuất được lô | Kiểm tra CCP1 pass và tồn |
| Không hoàn thành mẻ | Kiểm tra CCP2 Lab |
| Trang trống sau login | Refresh; xóa cache; thử Edge/Chrome |

Liên hệ IT nội bộ / sinh viên hỗ trợ demo.

---

## 15. Phụ lục — Phím & thói quen tốt

- Luôn **đăng xuất** khi dùng máy chung
- Nhập **đúng mã lô NCC** — sai batch ảnh hưởng truy xuất
- Không chia sẻ mật khẩu cá nhân
- Báo ATTP ngay khi CCP fail

---

*Triển khai: `docs/deploy.md` | Đào tạo: `docs/dao-tao.md`*
