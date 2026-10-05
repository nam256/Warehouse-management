# Oxeyns — Hệ thống quản lý kho & sản xuất tinh dầu (MVP)

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (Docker)
- **Frontend:** React + TypeScript + Vite

## Chạy nhanh (dev)

### Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173

### Tài khoản demo

| User | Password | Role |
|------|----------|------|
| admin | admin123 | admin |
| thu_kho | kho123 | thu_kho |
| ky_thuat | kt123 | ky_thuat |

## Cấu trúc

- `docs/` — tài liệu phân tích, API, DB
- `backend/` — API
- `frontend/` — Web UI
- `plan.md` — checklist tiến độ

## Giai đoạn tiếp theo

Module 2 (Sản xuất), Module 3 (Lab/CCP), Module 4 (Báo cáo export) — xem `plan.md`.
