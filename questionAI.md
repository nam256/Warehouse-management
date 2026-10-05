# Danh mục câu hỏi cho Trợ lý AI Oxeyns

Kế hoạch code/test: `chatbox.md`. Chip gợi ý trên widget = 8 câu bảo vệ (chào, tồn, khả dụng, in PX, sổ xuất, HSD, CAPA, chỉ đọc).

## 1. Phạm vi của trợ lý

Trợ lý demo chạy `local` (từ khóa + tool, không cần API key), **chỉ đọc**. Không phải ChatGPT tổng quát.

**Câu không nghiệp vụ:** `xin chào` / `cảm ơn` / hỏi ngoài QMS → trả lời ngắn, **không** đọc tồn kho.

**Công cụ được phép:**

1. `get_inventory` — tồn kho (hỏi “còn bao nhiêu”).
2. `get_batch_status` — trạng thái lô / CCP1.
3. `list_expiring_batches` — hạn dùng / FEFO (đúng quyền).
4. `list_open_capa` — CAPA/NCR đang mở.
5. `simulate_recall` — mô phỏng thu hồi (cần mã lô).
6. `explain_stock_reports` — hướng dẫn báo cáo tồn/xuất, phiếu PX, chat có mất không.
7. `list_stock_issues` — phiếu xuất gần đây.

Hội thoại lưu trên **trình duyệt** (đóng khung không mất; F5 khôi phục; Đoạn chat mới mới xóa). Server chỉ log câu hỏi + tool.

Câu hỏi nên ngắn, rõ, hoặc bấm chip gợi ý.

---

## 2. Nhóm câu có thể hỏi

### 2.1. Tồn kho

**Từ khóa nhận diện:** `tồn kho`, `ton kho`, `inventory`, `còn bao nhiêu`, `con bao nhieu`.

**Có thể hỏi tổng quan:**

- Tồn kho hiện tại còn bao nhiêu?
- Cho tôi xem tồn kho.
- Kiểm tra tồn kho.
- Liệt kê tồn kho hiện tại.
- Tổng hợp tồn kho.
- Hiện còn bao nhiêu nguyên liệu?
- Kho còn bao nhiêu hàng?
- Ton kho hien tai con bao nhieu?
- Kiem tra inventory.

**Có thể hỏi theo mã vật tư dạng `NVL-...`:**

- Tồn kho NVL-QUE còn bao nhiêu?
- NVL-QUE còn bao nhiêu?
- Kiểm tra tồn kho NVL-QUE.
- Cho tôi xem số lượng NVL-QUE.
- NVL-QUE còn khả dụng bao nhiêu?
- Ton kho NVL-QUE con bao nhieu?
- Kiem tra inventory NVL-QUE.

**Dữ liệu trả về:**

- Mã và tên vật tư.
- Đơn vị tính.
- Tổng số lượng.
- Số lượng đã giữ chỗ.
- Số lượng khả dụng.

**Lưu ý:**

- Muốn lọc chính xác theo vật tư, nên ghi mã có dạng `NVL-QUE`.
- Nếu không ghi mã, trợ lý trả danh sách tổng quan, tối đa 15 dòng trong câu trả lời.

---

### 2.2. Trạng thái chất lượng của lô

**Từ khóa nhận diện:** `trạng thái lô`, `trang thai lo`, `giải phóng`, `giai phong`, `quality`, `CCP1`, `quarantine`.

Trợ lý cũng nhận diện mã lô bắt đầu bằng `TP`, `NVL`, `BB`, `LO` hoặc `BATCH`, theo sau là ít nhất 4 chữ số.

**Có thể hỏi tổng quan:**

- Cho tôi xem trạng thái các lô.
- Lô nào đang chờ giải phóng?
- Lô nào đang quarantine?
- Lô nào chưa đạt CCP1?
- Kiểm tra trạng thái chất lượng các lô.
- Danh sách lô đang kiểm nghiệm.
- Danh sách lô đã được giải phóng.
- Trang thai lo hien tai.
- Lo nao dang cho giai phong?

**Có thể hỏi theo mã lô:**

- Trạng thái lô TP-20260624-001 là gì?
- Kiểm tra lô TP-20260624-001.
- Lô TP-20260624-001 đã được giải phóng chưa?
- CCP1 của lô TP-20260624-001 là gì?
- Quality status của TP-20260624-001.
- TP-20260624-001 đang ở trạng thái nào?
- Trang thai lo TP-20260624-001.
- Kiem tra CCP1 lo TP-20260624-001.

**Dữ liệu trả về:**

- Mã lô.
- Mã vật tư.
- Số lượng.
- `quality_status`.
- `ccp1_status`.
- Hạn dùng nếu có.

**Lưu ý:**

- Câu “Lô nào đang chờ giải phóng?” hiện gọi danh sách trạng thái lô nhưng chưa lọc riêng trạng thái `awaiting_release`; người dùng cần đọc trạng thái trong kết quả.
- Nếu mã lô không tồn tại, trợ lý trả “Không tìm thấy lô phù hợp”.

---

### 2.3. Hạn dùng và FEFO

**Từ khóa nhận diện:** `hết hạn`, `het han`, `hạn dùng`, `han dung`, `FEFO`, `expiry`.

**Có thể hỏi với khoảng mặc định 30 ngày:**

- Lô nào sắp hết hạn?
- Cho tôi xem các lô hết hạn.
- Kiểm tra hạn dùng.
- Danh sách lô theo FEFO.
- Có lô nào đã hết hạn không?
- Lô nào cần xuất trước theo FEFO?
- Lo nao sap het han?
- Kiem tra han dung.

**Có thể chỉ định số ngày:**

- Lô nào hết hạn trong 7 ngày?
- Lô nào sắp hết hạn trong 15 ngày?
- Kiểm tra hạn dùng trong 30 ngày.
- Liệt kê lô hết hạn trong 60 ngày.
- Cho tôi xem các lô có hạn dùng trong 90 ngày tới.
- Lo nao het han trong 10 ngay?
- Kiem tra FEFO 45 ngay.

**Dữ liệu trả về:**

- Mã lô.
- Mã vật tư.
- Số lượng.
- Hạn dùng.
- Trạng thái đã hết hạn hay chưa.
- Trạng thái chất lượng.

**Quyền được phép:**

- `admin`
- `thu_kho`
- `ky_thuat`
- `ql_nm`

Vai trò khác có thể nhận thông báo không có quyền xem dữ liệu FEFO/hạn dùng.

**Lưu ý:**

- Khoảng ngày được giới hạn từ 0 đến 365 ngày.
- Nếu không ghi số ngày, hệ thống dùng 30 ngày.

---

### 2.4. CAPA/NCR

**Từ khóa nhận diện:** `CAPA`, `NCR`, `khắc phục`, `khac phuc`.

**Có thể hỏi:**

- Có CAPA nào đang mở?
- Liệt kê CAPA đang mở.
- CAPA nào đang quá hạn?
- Hiện có bao nhiêu CAPA chưa đóng?
- Cho tôi xem tình trạng CAPA.
- Có NCR nào đang mở không?
- Liệt kê NCR chưa xử lý.
- Hành động khắc phục nào đang chờ?
- Danh sách hành động khắc phục.
- CAPA dang mo?
- NCR nao qua han?
- Liet ke hanh dong khac phuc.

**Dữ liệu trả về:**

- ID CAPA/NCR.
- Tiêu đề hoặc nguyên nhân.
- Trạng thái.
- Hạn xử lý.
- Dấu hiệu quá hạn.

**Lưu ý:**

- Trợ lý hiện chỉ trả các CAPA chưa đóng.
- Câu “CAPA nào quá hạn?” vẫn lấy danh sách CAPA đang mở và đánh dấu từng mục quá hạn; chưa lọc riêng chỉ các mục quá hạn.

---

### 2.5. Mô phỏng thu hồi

**Từ khóa nhận diện:** `thu hồi`, `thu hoi`, `recall`.

**Bắt buộc:** câu hỏi phải có mã lô.

**Có thể hỏi:**

- Mô phỏng thu hồi lô TP-20260624-001.
- Thu hồi lô TP-20260624-001 ảnh hưởng những đâu?
- Phạm vi recall của TP-20260624-001 là gì?
- Lô TP-20260624-001 có những lô downstream nào?
- Kiểm tra truy xuất thu hồi TP-20260624-001.
- Nếu thu hồi TP-20260624-001 thì có bao nhiêu lô liên quan?
- Mo phong thu hoi lo TP-20260624-001.
- Recall TP-20260624-001.

**Dữ liệu trả về:**

- Lô gốc.
- Các lô downstream liên quan.
- Các lệnh sản xuất liên quan.
- Phạm vi ảnh hưởng.

**Lưu ý:**

- Đây chỉ là mô phỏng đọc dữ liệu.
- Thao tác không đánh dấu thu hồi, không khóa lô và không thay đổi tồn kho.
- Nếu thiếu mã lô, trợ lý yêu cầu cung cấp mã lô.

---

## 3. Câu hỏi kết hợp

Trợ lý local hiện chỉ chọn một nhóm chính cho mỗi câu hỏi. Thứ tự ưu tiên nhận diện là:

1. Thu hồi.
2. CAPA/NCR.
3. Hạn dùng/FEFO.
4. Trạng thái lô.
5. Tồn kho.
6. Không nhận diện được thì mặc định trả tổng quan tồn kho.

Ví dụ:

- “Lô TP-20260624-001 còn bao nhiêu và đã giải phóng chưa?”  
  Có mã lô và nội dung trạng thái nên hệ thống ưu tiên **trạng thái lô**, không trả đầy đủ phân tích tồn kho.

- “CAPA nào liên quan đến lô TP-20260624-001?”  
  Có từ `CAPA`, nên hệ thống trả **toàn bộ CAPA đang mở**, chưa lọc theo mã lô.

- “Lô nào hết hạn và tồn kho còn bao nhiêu?”  
  Có từ `hết hạn`, nên hệ thống ưu tiên **hạn dùng/FEFO**.

Nên tách câu hỏi kết hợp thành nhiều câu riêng để nhận kết quả rõ ràng.

---

## 4. Nhóm câu không thể hỏi hoặc chưa được hỗ trợ

### 4.1. Câu yêu cầu thay đổi dữ liệu

Trợ lý không được thực hiện:

- Giải phóng lô TP-20260624-001.
- Duyệt lô này giúp tôi.
- Chuyển lô sang trạng thái released.
- Đánh dấu CCP1 đạt.
- Tạo phiếu nhập kho.
- Nhập thêm 100 kg NVL-QUE.
- Xuất kho lô TP-20260624-001.
- Giữ chỗ nguyên liệu cho lệnh sản xuất.
- Hủy giữ chỗ nguyên liệu.
- Tạo lệnh sản xuất mới.
- Duyệt hoặc khởi động lệnh sản xuất.
- Hoàn thành lệnh sản xuất.
- Tạo CAPA mới.
- Đóng CAPA số 12.
- Xác minh CAPA giúp tôi.
- Xóa CAPA/NCR.
- Đổi hạn dùng của lô.
- Đánh dấu lô đã thu hồi.
- Xóa hoặc sửa dữ liệu hệ thống.

**Lý do:** trợ lý được thiết kế chỉ đọc và không có công cụ ghi dữ liệu.

---

### 4.2. Câu hỏi nghiệp vụ ngoài 5 nhóm

Các nhóm sau chưa có công cụ:

- Doanh thu, chi phí, lợi nhuận.
- Kế toán, hóa đơn, công nợ.
- Lương, chấm công, nhân sự.
- Đơn hàng bán, khách hàng, vận chuyển.
- Dự báo nhu cầu hoặc dự báo sản xuất.
- Lập kế hoạch mua hàng tự động.
- Tối ưu lịch sản xuất.
- Đánh giá hiệu suất nhân viên.
- Tính OEE hoặc hiệu suất máy.
- Quản lý bảo trì thiết bị.
- Theo dõi nhiệt độ/độ ẩm thời gian thực.
- Dữ liệu trực tiếp từ máy GC.
- Tra cứu văn bản pháp luật hoặc tiêu chuẩn bên ngoài.
- Tìm kiếm thông tin trên Internet.
- Thời tiết, tin tức hoặc dữ liệu ngoài hệ thống Oxeyns.

**Ví dụ không hỗ trợ:**

- Doanh thu tháng này là bao nhiêu?
- Công ty đang lãi hay lỗ?
- Nhân viên nào đi trễ?
- Lương tháng này của tôi là bao nhiêu?
- Dự báo cần mua bao nhiêu nguyên liệu tháng sau.
- Máy chưng cất nào sắp hỏng?
- Nhiệt độ kho hiện tại là bao nhiêu?
- Quy định HACCP mới nhất năm nay là gì?

---

### 4.3. Truy vấn phân tích chưa được hỗ trợ

Trợ lý chưa thực hiện các phép phân tích tùy ý như:

- So sánh tồn kho giữa hai thời điểm.
- Biểu đồ xu hướng tồn kho.
- Tỷ lệ lô đạt theo tháng/quý.
- Tỷ lệ CAPA đóng đúng hạn.
- Thời gian xử lý CAPA trung bình.
- Thống kê nhà cung cấp có nhiều lô lỗi nhất.
- Xếp hạng vật tư theo mức tiêu thụ.
- Dự báo ngày hết hàng.
- Phân tích nguyên nhân gốc tự động.
- Phân tích tương quan GC/SPC.
- Tạo báo cáo PDF/Excel theo yêu cầu tự do.

**Ví dụ:**

- So sánh tồn kho tháng này với tháng trước.
- Tỷ lệ lô bị reject trong quý II là bao nhiêu?
- Nhà cung cấp nào có nhiều NCR nhất?
- Vẽ biểu đồ C14 trong 12 tháng.
- Khi nào NVL-QUE sẽ hết hàng?

---

### 4.4. Bộ lọc chi tiết chưa được hỗ trợ

Trợ lý chưa bảo đảm lọc chính xác theo:

- Kho.
- Nhà cung cấp.
- Khoảng ngày sản xuất.
- Loại vật tư.
- Trạng thái CAPA cụ thể.
- Người phụ trách CAPA.
- Mức độ nghiêm trọng.
- Lệnh sản xuất.
- Khách hàng.
- Số lượng tối thiểu/tối đa.

**Ví dụ:**

- Tồn kho NVL-QUE tại kho A.
- Lô nào của nhà cung cấp ABC đang bị quarantine?
- CAPA của Nguyễn Văn A đang quá hạn.
- Lô sản xuất trong khoảng 01/06 đến 30/06.
- Chỉ liệt kê lô có số lượng lớn hơn 100 kg.

Một số câu có thể vẫn trả kết quả tổng quan, nhưng bộ lọc chi tiết trong câu sẽ không được áp dụng.

---

### 4.5. Hội thoại nhiều lượt và tham chiếu ngữ cảnh

Trợ lý local không ghi nhớ ngữ cảnh câu trước để hiểu các đại từ như:

- Lô đó thì sao?
- Còn lô tiếp theo?
- Cái nào quá hạn?
- Cho tôi xem chi tiết mục thứ hai.
- Nó có được giải phóng chưa?
- Tiếp tục đi.

Nên lặp lại đầy đủ thông tin:

- Không nên: “Lô đó đã giải phóng chưa?”
- Nên: “Lô TP-20260624-001 đã giải phóng chưa?”

---

### 4.6. Câu thiếu dữ kiện bắt buộc

Các câu thu hồi thiếu mã lô không thể thực hiện:

- Mô phỏng thu hồi.
- Thu hồi lô này.
- Recall giúp tôi.
- Có bao nhiêu lô bị ảnh hưởng?

Cách hỏi đúng:

- Mô phỏng thu hồi lô TP-20260624-001.

---

### 4.7. Mã không đúng định dạng

Trợ lý nhận diện mã lô tốt nhất khi mã bắt đầu bằng `TP`, `NVL`, `BB`, `LO` hoặc `BATCH`, theo sau là ít nhất 4 chữ số.

Các cách ghi dễ không được nhận diện:

- Lô số một.
- Lô hôm qua.
- Lô mới nhất.
- Mã 123.
- Batch ABC.
- Thành phẩm tháng sáu.

Cách hỏi nên dùng:

- Trạng thái lô TP-20260624-001.
- Mô phỏng thu hồi TP-20260624-001.

---

### 4.8. Câu hỏi kiến thức chung hoặc tư vấn

Trợ lý không phải chatbot tư vấn tổng quát:

- HACCP là gì?
- CAPA là gì?
- FEFO khác FIFO thế nào?
- Hãy viết quy trình ISO 22000.
- Hãy giải thích kết quả GC.
- Tôi nên giải phóng lô này không?
- Hãy đưa ra quyết định chất lượng thay con người.
- Viết luận văn giúp tôi.
- Dịch tài liệu này sang tiếng Anh.

Những nội dung này không sử dụng dữ liệu từ 5 công cụ và có thể bị định tuyến mặc định sang tồn kho.

---

## 5. Hành vi khi không hiểu câu hỏi

Nếu câu hỏi không chứa từ khóa được nhận diện, provider local mặc định gọi nhóm **tồn kho**.

Ví dụ:

- “Xin chào”
- “Bạn làm được gì?”
- “Giúp tôi”
- “Hôm nay thế nào?”

Các câu trên có thể trả về danh sách tồn kho thay vì câu trả lời hội thoại. Đây là giới hạn hiện tại của chế độ local.

---

## 6. Quy tắc bảo mật và độ tin cậy

1. Trợ lý chỉ gọi 5 công cụ trong whitelist.
2. Trợ lý không có công cụ release lô, đóng CAPA hoặc sửa dữ liệu.
3. Mọi truy vấn yêu cầu người dùng đăng nhập.
4. Dữ liệu FEFO/hạn dùng bị giới hạn theo vai trò.
5. Trợ lý chỉ trả số liệu lấy từ cơ sở dữ liệu.
6. Không tìm thấy dữ liệu thì báo không tìm thấy, không tự suy đoán.
7. Mô phỏng thu hồi không tạo giao dịch hay thay đổi trạng thái.
8. Mỗi truy vấn thành công được ghi vào `AssistantQueryLog`, gồm người hỏi, câu hỏi, công cụ đã gọi và thời điểm.

---

## 7. Mẫu câu nên dùng khi demo

1. `Tồn kho hiện tại còn bao nhiêu?`
2. `Tồn kho NVL-QUE còn bao nhiêu?`
3. `Lô nào đang chờ giải phóng?`
4. `Trạng thái lô TP-20260624-001 là gì?`
5. `Lô nào sắp hết hạn trong 30 ngày?`
6. `Có CAPA nào đang mở?`
7. `CAPA nào đang quá hạn?`
8. `Mô phỏng thu hồi lô TP-20260624-001.`

## 8. Mẫu câu không nên dùng khi demo

1. `Xin chào, bạn là ai?`
2. `Bạn làm được những gì?`
3. `Lô đó thì sao?`
4. `Đóng CAPA giúp tôi.`
5. `Giải phóng lô TP-20260624-001.`
6. `Doanh thu tháng này bao nhiêu?`
7. `Dự báo tồn kho tháng sau.`
8. `Thu hồi giúp tôi.` — thiếu mã lô.
9. `Nhà cung cấp nào tốt nhất?`
10. `Hãy quyết định lô này có an toàn không.`

---

## 9. Tóm tắt nhanh

| Nhóm | Có thể hỏi | Không thể thực hiện |
|---|---|---|
| Tồn kho | Tổng, giữ chỗ, khả dụng; lọc mã `NVL-...` | Nhập/xuất/sửa tồn |
| Trạng thái lô | Quality, CCP1, hạn dùng theo mã lô | Release/reject/chuyển trạng thái |
| FEFO | Lô hết hạn hoặc sắp hết hạn trong 0–365 ngày | Tạo lệnh xuất hoặc tự phân bổ |
| CAPA/NCR | Danh sách chưa đóng, trạng thái, quá hạn | Tạo, sửa, xác minh hoặc đóng |
| Recall | Mô phỏng downstream theo mã lô | Đánh dấu thu hồi hoặc khóa lô |
| Ngoài phạm vi | Không hỗ trợ | Kế toán, HR, dự báo, Internet, tư vấn tổng quát |

