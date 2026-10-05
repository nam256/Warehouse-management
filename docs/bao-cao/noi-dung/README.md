# Nội dung báo cáo TTTN — Oxeyns Kho & SX

Thư mục chứa **nội dung prose đầy đủ** cho báo cáo thực tập, ánh xạ 1:1 với `BAOCAO.TXT`.

**Trạng thái:** Đã soạn xong tất cả phần (mở đầu + 4 chương + tài liệu tham khảo).

---

## Cấu trúc file

| File | Nội dung | Mục BAOCAO.TXT |
|------|----------|----------------|
| `00-mo-dau.md` | Lời mở đầu, cảm ơn, lịch TT, DM hình/bảng, Abstract | Trang 3–17 |
| `chuong-1.md` | Tổng quát (1.1–1.6) | Chương 1 |
| `chuong-2.md` | Cơ sở lý thuyết (2.1–2.2) | Chương 2 |
| `chuong-3.md` | Cài đặt thử nghiệm (3.1–3.4) | Chương 3 |
| `chuong-4.md` | Kết luận (4.1–4.5) | Chương 4 |
| `tai-lieu-tham-khao.md` | Tài liệu tham khảo [1]–[36] | Cuối báo cáo |

**Lưu ý kỹ thuật trong báo cáo:** CSDL thực tế là **SQLite** (`backend/oxeyns.db`). PostgreSQL/Docker chỉ được nêu là hướng mở rộng — **chưa triển khai**.

---

## Phụ lục A–M

Đính kèm từ `docs/` khi ghép Word — không copy vào `noi-dung/`:

| Phụ lục | File |
|---------|------|
| A | `docs/requirements.md` |
| B | `docs/api-spec.md` |
| C | `docs/database-design.md` |
| D | `docs/bieu-mau/` |
| E | `docs/phong-van/` |
| F | `docs/uat-results.md`, `test.md` |
| G | `docs/wireframes/` |
| H | `process-as-is.md`, `process-to-be.md`, `data-flow.md` |
| I | `docs/problem-matrix.md` |
| J | `docs/user-manual.md`, `code.txt` |
| K | `docs/software-validation.md` |
| L | `docs/screenshots/` *(cần chụp 11 menu)* |
| M | `pham-vi-xac-nhan.md`, `dao-tao.md`, `demo-slides.md` |

---

## Ghép Word — checklist

1. Copy theo thứ tự: `00-mo-dau` → Chương 1–4 → Tài liệu tham khảo.
2. Điền **họ tên, MSSV, ngày** trong `00-mo-dau.md`.
3. Vẽ **ERD (14 bảng), use case, 14 sequence, state machine** từ `chuong-3.md`.
4. Chụp **screenshot** 11 menu → Phụ lục L.
5. Điền **số trang** trong mục lục `BAOCAO.TXT`.
6. Đính kèm Phụ lục A–M.

---

## Demo khi bảo vệ

```powershell
cd backend
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

cd frontend
npm run dev
```

- UI: http://localhost:5173  
- API docs: http://localhost:8000/docs  

**Tài khoản:** `admin/admin123`, `thu_kho/kho123`, `attp/attp123`, … (chi tiết `chuong-3.md` §3.2.1.1).

**Luồng demo nhanh:** Nhập kho → Lab C14 → Tạo mẻ → Operation Ttop → Lab % t-CA → Hoàn thành → Truy xuất lô.
