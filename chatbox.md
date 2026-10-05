# Kế hoạch trợ lý chatbox (M6) — đúng trọng tâm, đủ câu bảo vệ

> Làm theo từng task `- [ ]`. Test đỏ rồi mới sửa router. Không bịa số liệu. Không default tồn kho.

**Goal:** Chatbox demo bảo vệ **không trả lời lệch**. Chào thì chào. Hỏi báo cáo thì hướng dẫn in/PDF/công thức. Hỏi số thì đọc DB qua tool. Câu hội đồng hay hỏi phải có đáp án vàng + pytest. Đóng khung **không mất** hội thoại; tắc mạng **không xóa** tin đã gửi; muốn xóa thì bấm **Đoạn chat mới**.

**Lỗi đã chụp (bắt buộc hết):** user gõ `xin chào` → dump `BTP-THO / NVL-QUE / TP-TCA sẵn 0 kg` + nguồn “Tồn kho”. Nguyên nhân: `_route_local_tools` **không khớp từ khóa thì gọi `get_inventory`**.

**Architecture:** `AssistantWidget` → `POST /api/v1/assistant/ask` (JWT) → `answer_question`. Demo dùng `ai_provider=local` (từ khóa + tool, không cần API key). LLM openai/ollama chỉ thêm, **không được tin nội dung nếu không gọi tool**. Ghi `AssistantQueryLog` (câu hỏi + tên tool + thời điểm). Không ghi nghiệp vụ kho/SX.

**Tech stack:** FastAPI, SQLAlchemy, React/TS, pytest, `localStorage` cho thread trên trình duyệt.

**File đụng:** `backend/app/services/assistant.py`, `assistant_intent.py` (mới), `report_kb.py`, `backend/tests/test_assistant.py`, `frontend/src/components/AssistantWidget.tsx`, `frontend/src/api.ts`, `frontend/src/App.tsx`, `questionAI.md`, `testluanvan.md`.

---

## Global constraints

- UI và câu trả lời tiếng Việt có dấu.
- Chỉ đọc: không xuất kho, không giải phóng/từ chối lô, không đóng CAPA, không tạo `RecallSimulation`.
- Số kg / trạng thái lô **chỉ** từ tool whitelist. Không có dữ liệu → “không tìm thấy”.
- Câu không nghiệp vụ (chào, cảm ơn, thời tiết, viết hộ luận văn) **cấm** gọi tool tồn kho.
- `AI_ASSISTANT_ENABLED=false` tắt cả module, không ảnh hưởng M1–M5.
- Không cam kết ChatGPT lúc bảo vệ; nhánh `local` phải đủ demo.
- Không lưu hội thoại lên SQLite/Postgres (tránh biến M6 thành ghi nghiệp vụ). Server chỉ log metadata.

---

## 1. Hiện trạng (nói thật)

| Hạng mục | Đã có | Sai / thiếu |
|----------|--------|-------------|
| Router `local` | 7 tool: tồn, lô, HSD, CAPA, thu hồi, giải thích báo cáo, sổ PX | **Default = tồn kho** → chào cũng dump seed |
| Báo cáo | `report_kb.py` + vài test in PX / khả dụng / kỳ / xuất tay | Gợi ý chip biến mất sau tin đầu |
| Log | `AssistantQueryLog` | Không lưu câu trả lời, không `thread_id` |
| UI | Kéo được, JWT, typing | `messages` chỉ RAM — **F5 mất hết** |
| Đóng khung (×) | `setOpen(false)` | Chat còn RAM nhưng user tưởng mất; F5 thì mất thật |
| Tắc / treo | `busy` khóa nút gửi | Không timeout, không Hủy, không Abort — reload thì mất thread |
| Đoạn chat mới | Không có | Không tách “lỗi” vs “tôi muốn xóa” |
| `questionAI.md` | Từ khóa cũ 5 tool | Chưa chào, chưa báo cáo, chưa persistence |

**Câu hội đồng: “Sao chào lại ra tồn kho?”**

> Lỗi router: câu không khớp keyword thì gọi `get_inventory`. Sửa: phân intent; không khớp thì hỏi lại hoặc ngoài phạm vi — **không bao giờ** default tồn kho.

---

## 2. Mục tiêu khi xong

1. Intent: `greet` | `thanks` | `out_of_scope` | `clarify` | `howto_report` | `inventory` | `batch` | `fefo` | `capa` | `recall`.
2. Gợi ý 8 câu bảo vệ **luôn hiện** dưới ô nhập (không chỉ màn hình trống).
3. Đóng khung = ẩn, **giữ chat**. F5 = đọc lại `localStorage` theo username. Đăng xuất = xóa thread máy này. Nút **Đoạn chat mới** = xác nhận rồi xóa.
4. Timeout ~25s + nút Hủy; tin user còn; assistant báo lỗi; `busy=false`.
5. Pytest: chào / ngoài phạm vi / 8 câu gợi ý / không gọi tool sai.

---

## 3. Ma trận intent — cấm trả lời lung tung

Thứ tự classify (trên xuống, dừng ở lớp đầu khớp). Câu chào **ngắn cả câu** mới là `greet` (không nuốt “xin chào, tồn kho còn bao nhiêu?”).

| Intent | Ví dụ | Làm | Cấm |
|--------|--------|-----|-----|
| `recall` | mô phỏng thu hồi lô TP-001 | `simulate_recall` | Ghi simulation; thiếu mã → hướng dẫn, HTTP 200 |
| `capa` | CAPA / NCR đang mở | `list_open_capa` | |
| `howto_report` | in phiếu PX, sổ xuất, tồn theo kỳ, khả dụng vs vật lý, xuất tay vs mẻ, phiếu nhập, chat có mất không, trợ lý có được xuất kho không | `explain_stock_reports` ± `list_stock_issues` | `get_inventory` |
| `fefo` | lô nào sắp hết hạn | `list_expiring_batches` | Lab không quyền → tiếng Việt trên bubble, không nuốt 403 im |
| `batch` | trạng thái lô, CCP1, giải phóng + mã lô | `get_batch_status` | |
| `inventory` | tồn kho còn bao nhiêu, NVL-QUE | `get_inventory` | Bịa kg |
| `greet` | xin chào, hello, hi, chào bạn | 1–2 câu + phạm vi chỉ đọc + bảo bấm gợi ý | Mọi tool, mọi dòng kg |
| `thanks` | cảm ơn, ok, được rồi | 1 câu | Tool |
| `clarify` | in giúp, lô này, cái đó (thiếu mã) | Hỏi đúng 1 thứ còn thiếu | Đoán mã |
| `out_of_scope` | mưa không, giá vàng, viết hộ luận | Từ chối + đẩy về QMS | Tồn kho |

**Quy tắc vàng:** hết bảng mà chưa khớp → `out_of_scope` hoặc `clarify`. Xóa hẳn `return [("get_inventory", {})]`.

---

## 4. Tám câu gợi ý bảo vệ (chip — không được sai)

Bấm chip = gửi nguyên văn. Mỗi dòng là 1 test substring.

| # | Chip | Intent | Phải có trong trả lời | Cấm xuất hiện |
|---|------|--------|------------------------|---------------|
| G1 | In phiếu PX | howto_report | phiếu xuất, xem trước hoặc PDF | dump tồn seed |
| G2 | Sổ xuất | howto_report | sổ xuất, từ ngày, đến ngày | |
| G3 | Tồn theo kỳ | howto_report | tồn đầu, nhập, xuất, tồn cuối | |
| G4 | Khả dụng | howto_report | khả dụng, vật lý, cách ly hoặc giải phóng | dump 3 dòng 0 kg |
| G5 | Tồn kho | inventory | mã vật tư + sẵn / tổng / giữ chỗ | số khác DB |
| G6 | Xuất tay / mẻ | howto_report | thủ công hoặc tay, mẻ | |
| G7 | Hạn dùng | fefo | HSD hoặc “không có lô”; lab: không có quyền | |
| G8 | Khắc phục đang mở | capa | khắc phục hoặc “không có … đang mở”; không hiện `open` tiếng Anh | |

Không chip chào. Gõ `xin chào` vẫn chào, không dump kho.

**Câu hội đồng thêm (phải có trong `report_kb` + test, không bắt buộc chip):**

| Mã | Câu | Đáp án vàng |
|----|-----|-------------|
| H1 | Chat lưu server không? | Log câu hỏi + tool. **Nội dung hội thoại lưu trên trình duyệt.** |
| H2 | Tắt khung chat có mất không? | Không. Chỉ ẩn, mở lại còn. |
| H3 | Tạo chat mới? | Nút Đoạn chat mới, có xác nhận. Không xóa `AssistantQueryLog`. |
| H4 | Tắc mạng / treo? | Timeout hoặc Hủy. Tin đã gửi **còn**. Không F5 để “thoát treo”. |
| H5 | AI bịa số? | Không. Không tool thì không đưa kg. |
| H6 | Khác ChatGPT? | `local` = từ khóa + tool, không phải LLM tổng quát. |
| H7 | Phiếu nhập lấy kg nào? | Lúc nhập (PN), không phải tồn sau khi đã xuất. |
| H8 | Xuất tay vs xuất mẻ? | Thủ công vs gắn SX-…; hủy mẻ → HT, không xóa PX gốc. |

---

## 5. Hội thoại: đóng, F5, tắc, chat mới

| Sự kiện | Hành vi đúng |
|---------|----------------|
| Đóng × / thu gọn AI | Ẩn panel. **Giữ** `messages` + ghi `localStorage`. |
| Mở lại | Hiện đúng thread cũ. |
| F5 / đóng tab mở lại | Đọc `oxeyns.assistant.thread.<username>`, tối đa 50 tin. |
| Đăng xuất | Xóa key thread user đó (máy demo dùng chung). |
| Đoạn chat mới | `confirm` → `[]` + ghi đè storage. Log server **không** xóa. |
| Timeout 25s / Hủy | `AbortController`. Bubble lỗi assistant. `busy=false`. User bubble còn. |
| 503 / AI tắt | Banner + không xóa lịch sử. |

Không làm: sync thread lên DB; không “tự xóa khi đóng khung”.

---

## 6. Thiết kế code

### 6.1. `backend/app/services/assistant_intent.py`

- `classify_intent(question) -> str`
- Chuẩn hóa lower + gộp space.
- `greet` chỉ khi **cả câu** là chào (`xin chào`, `hello`, `hi`, `chào bạn`, … ± dấu câu).
- Unit test bảng ≥ 20 câu → đúng intent (không cần HTTP).

`_answer_with_local`: greet/thanks/out_of_scope/clarify **trả text, `tools_called=[]`**. Còn lại mới `_route_local_tools`.

`_system_prompt`: chào không gọi tool; không bịa kg.

### 6.2. `report_kb.py`

Thêm topic H1–H8 (chat lưu đâu, chỉ đọc, phiếu nhập, xuất tay/mẻ). `is_report_howto_question` nhận: mất chat, đoạn chat mới, bịa số, duyệt lô, được xuất kho.

### 6.3. `AssistantWidget.tsx` + `App.tsx`

- Chip G1–G8 **cố định** dưới composer.
- `username` từ `App`: key storage theo user.
- Nút Đoạn chat mới; badge “Chỉ đọc · hội thoại lưu trên máy này”.
- `askAssistant(question, { signal })` + timeout 25s + nút Hủy khi `busy`.
- `logout()` gọi xóa thread local.

### 6.4. Không thêm tool cho greet

Whitelist tool giữ 7 cái hiện tại.

---

## 7. Test

Viết **trước** khi xóa default tồn kho.

| Test | Kỳ vọng |
|------|---------|
| `test_hello_does_not_call_inventory` | `xin chào`, `hello` → `tools_called==[]`; answer không chứa `NVL-QUE` / `0 kg`; có chữ chào hoặc chỉ đọc |
| `test_thanks_no_tools` | cảm ơn → không tool |
| `test_weather_out_of_scope` | hôm nay mưa không → không tồn kho; nhắc QMS |
| `test_quantity_still_inventory` | Tồn kho còn bao nhiêu? → `get_inventory` (hồi quy) |
| `test_hello_then_quantity` | “xin chào, tồn kho còn bao nhiêu?” → inventory (không nuốt thành greet) |
| Report tests đã có | in PX, khả dụng, kỳ, xuất tay — **không** `get_inventory` |
| `test_recall_without_batch` | 200 + mã lô (đã có) |
| `test_classify_intent_table` | 20 câu → enum |
| `test_scope_cannot_issue` | G8 → chỉ đọc, không tool xuất |
| UI checklist 10 phút | G1–G8; đóng/mở còn; F5 còn; đoạn mới xóa; Hủy khi treo |

---

## 8. Task

- [x] **T0** File kế hoạch này.
- [x] **T1** `classify_intent` + xóa default `get_inventory`. Pytest chào / ngoài phạm vi / hồi quy tồn kho.
- [x] **T2** `report_kb` H1–H8 + G8 + test substring.
- [x] **T3** Chip G1–G8 luôn hiện.
- [x] **T4** `localStorage` thread theo user; đóng khung không xóa; F5 khôi phục; logout xóa; Đoạn chat mới.
- [x] **T5** Timeout 25s, Hủy, lỗi không xóa lịch sử.
- [x] **T6** Lab gọi FEFO: 403 → câu tiếng Việt trên bubble.
- [x] **T7** Cập nhật `questionAI.md` (7 tool + chào + persistence).
- [x] **T8** Checklist 10 phút vào `testluanvan.md`.

**Thứ tự demo:** T1 + T3 trước (chào không dump kho + chip). T4 + T5 ngay sau (hội đồng hỏi “tắc / mất chat không”).

---

## 9. Rủi ro bảo vệ

| Rủi ro | Cách nói / xử lý |
|--------|------------------|
| `local` không “thông minh” | Đúng: từ khóa + tool; bảo hội đồng bấm chip |
| DB demo tồn 0 | Số 0 vẫn đúng — **không** giải thích tồn khi user chỉ chào |
| LLM bật nhầm, không tool | Giữ test: không tin content model |
| Hai tài khoản một máy | Key theo username; logout xóa |

---

## 10. Xong việc khi

- [x] `xin chào` không ra NVL-QUE / nguồn Tồn kho
- [x] Tám chip đúng bảng mục 4
- [x] Đóng chat không mất; F5 còn; Đoạn chat mới xóa có hỏi
- [x] Tắc: Hủy hoặc timeout, lịch sử còn
- [x] `pytest tests/test_assistant.py` xanh
- [x] Không cam kết go-live LLM


## 11. Catalog câu hỏi bảo vệ (KB phải trả lời được)

Toàn bộ câu dưới đây **có chip trong khung chat** (kéo danh sách gợi ý). Không chip chào. Kéo góc trên-trái để phóng to. Đáp án xuống dòng. Chip khắc phục ghi **Khắc phục đang mở**, không viết tắt CAPA.

### Báo cáo / xuất kho (ưu tiên)

| Hỏi | Ý đáp |
|-----|--------|
| Làm sao in phiếu xuất kho? | Xuất kho → lưu → Xem trước → PDF; in lại ở Báo cáo |
| Sổ xuất kho lọc ngày ra sao? | Từ ngày–đến ngày; kỳ trống vẫn tải, tổng 0 |
| Tồn theo kỳ tính thế nào? | Đầu = cuối − nhập + xuất; replay sổ, không khóa kế toán |
| Khả dụng khác vật lý? | Vật lý / giữ chỗ / khả dụng; cách ly = khả dụng 0 |
| Xuất tay khác xuất mẻ? | Thủ công vs gắn SX-…; hủy mẻ → HT, không xóa PX |
| Phiếu nhập lấy kg nào? | Lúc nhập (PN), không phải tồn sau khi đã xuất |
| Xuất vượt khả dụng? | Không tạo phiếu |
| File khác màn hình? | Cùng công thức khả dụng |
| Xuất nhiều lô một lần? | Mỗi lần một lô; SX đã FEFO lúc duyệt mẻ |
| Trợ lý xuất kho / duyệt lô được không? | Chỉ đọc |

### Vận hành & trợ lý (cũng có chip)

Nhập kho · sản xuất · kiểm nghiệm · giải phóng lô · tồn thấp · mua hàng · điểm kiểm soát · nhật ký · NVL/BTP/TP · tồn kho hiện tại · hạn dùng · khắc phục đang mở · chat có mất không · không phải kế toán.

Số kg / lô sắp hết hạn / khắc phục đang mở / thu hồi + mã lô → **tool đọc DB**, không bịa.