# Hướng dẫn triển khai (Deploy)

**Dự án:** Oxeyns Kho & SX — MVP demo/staging  
**Stack:** FastAPI + React/nginx + SQLite hoặc PostgreSQL 16

## 1. Chọn profile cơ sở dữ liệu

- **SQLite** dành cho phát triển cá nhân và chạy pytest nhanh. Không cần Docker.
- **PostgreSQL** dành cho integration/concurrency tests và demo bảo vệ.
- Ứng dụng đổi CSDL **chỉ bằng `DATABASE_URL`**, không sửa mã nguồn.

Các file mẫu nằm trong `backend/`:

- `.env.sqlite.example`: SQLite local.
- `.env.postgres.example`: PostgreSQL cài trực tiếp trên máy.
- `.env.example`: profile SQLite mặc định.

Backend dùng tên biến **`SECRET_KEY`** để ký token. Không dùng `JWT_SECRET`.
Phải thay secret mẫu khi triển khai staging hoặc máy dùng chung.

## 2. SQLite local

```powershell
Set-Location backend
Copy-Item ".env.sqlite.example" ".env"
py -m pip install -r requirements.txt
py -m alembic upgrade head
py -m uvicorn app.main:app --reload --port 8000
```

Kiểm tra profile SQLite:

```powershell
$env:DATABASE_URL="sqlite://"
py -m pytest tests -q -m "not postgres"
```

## 3. PostgreSQL local theo tài khoản người dùng

Cấu hình PostgreSQL cài trực tiếp:

- Host: `localhost`
- Port: `5432`
- User: `postgres`
- Password: `postgres123`
- Database: `oxeyns`
- URL: `postgresql+psycopg2://postgres:postgres123@localhost:5432/oxeyns`

Tạo database `oxeyns` nếu chưa có bằng pgAdmin4 hoặc:

```powershell
createdb -h localhost -p 5432 -U postgres oxeyns
```

Không xóa hoặc ghi đè database khác. Sau khi database tồn tại:

```powershell
Set-Location backend
Copy-Item ".env.postgres.example" ".env"
py -m alembic upgrade head
py -m pytest tests -q -m "postgres or integration"
py -m uvicorn app.main:app --reload --port 8000
```

## 4. Docker Compose: db + api + web

Stack Compose dùng credentials dịch vụ riêng mặc định:

- Database/user/password: `oxeyns` / `oxeyns` / `oxeyns`
- Host nội bộ từ API: `db:5432`
- URL nội bộ:
  `postgresql+psycopg2://oxeyns:oxeyns@db:5432/oxeyns`

Đây là credentials container, khác với tài khoản PostgreSQL local
`postgres/postgres123`. Có thể override bằng `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_DB`, và bắt buộc đặt `SECRET_KEY` an toàn khi
triển khai ngoài máy cá nhân.

```powershell
$env:SECRET_KEY="replace-with-a-long-random-secret"
docker compose up --build -d
docker compose ps
```

`db` phải healthy trước khi `api` chạy `alembic upgrade head`; `web` chỉ khởi
động sau khi API healthy. Các địa chỉ:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health
- PostgreSQL: `localhost:5432`

Seed demo được chạy trong lifespan của API. Có thể chạy lại idempotently:

```powershell
docker compose exec api python -m app.seed
```

## 5. PostgreSQL test container tùy chọn

`docker-compose.test.yml` mở PostgreSQL tạm thời tại cổng `5433`, dùng tmpfs:

```powershell
docker compose -f docker-compose.test.yml up -d
$env:DATABASE_URL="postgresql+psycopg2://oxeyns_test:oxeyns_test@localhost:5433/oxeyns_test"
Set-Location backend
py -m alembic upgrade head
py -m pytest tests -q -m "postgres or integration"
```

Sau khi test:

```powershell
docker compose -f docker-compose.test.yml down
```

## 6. pgAdmin4 (tùy chọn)

pgAdmin4 không nằm trong Compose stack. Có thể dùng bản cài trên máy và kết nối:

- PostgreSQL local của người dùng: `localhost:5432`, database `oxeyns`, user
  `postgres`, password `postgres123`.
- PostgreSQL Compose mặc định: `localhost:5432`, database/user/password đều là
  `oxeyns`.

Nếu cổng `5432` đã được PostgreSQL local sử dụng thì không chạy đồng thời
Compose `db` với mapping mặc định; dùng test stack cổng `5433` hoặc dừng một
trong hai dịch vụ.

## 7. Frontend build và Playwright smoke

```powershell
Set-Location frontend
npm ci
npm run build
```

Playwright smoke yêu cầu toàn bộ Compose stack đang healthy:

```powershell
npx playwright install chromium
npm run e2e
```

Smoke đăng nhập bằng `lab/lab123`, mở `/quality`, và xác nhận trang
Hold-Release hiển thị. Có thể đổi URL bằng `PLAYWRIGHT_BASE_URL`.

## 8. CI và Gate G4

`.github/workflows/ci.yml` có ba jobs:

1. SQLite: mọi test trừ marker `postgres`.
2. PostgreSQL 16: Alembic và test marker `postgres or integration`.
3. Frontend: build, dựng Compose stack và chạy Playwright Chromium.

Gate G4 đạt khi SQLite tests, PostgreSQL migration/integration tests, frontend
build và Playwright smoke đều exit code 0.

## 9. Phạm vi TTTN

Triển khai staging local/VPS nội bộ đủ cho demo báo cáo. Go-live chính thức cần
HTTPS, firewall, secret riêng, backup/rollback và quy trình validation ATTP
trong `docs/software-validation.md`.
