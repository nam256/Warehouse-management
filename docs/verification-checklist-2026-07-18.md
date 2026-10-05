# Verification evidence — 2026-07-18

## Environment
- Python 3.13.3, Node v22.16.0, npm 10.9.2
- PostgreSQL local listening `:5432` (user `postgres`)
- Backend `:8000`, frontend Vite `localhost:5173`
- Docker Desktop: **not installed** (waived; use local PostgreSQL)

## Automated verification

| Check | Command / evidence | Result |
|---|---|---|
| SQLite API tests | `py -m pytest tests -q -m "not postgres"` | previously 46+ passed |
| Postgres profile | `tests/test_postgres_profile.py` with `DATABASE_URL=postgresql+.../oxeyns` | **1 passed** |
| Postgres concurrency | `tests/test_postgres_concurrency.py` | **1 passed** |
| Alembic PG | `alembic upgrade head` / `alembic current` → `dcc79cce7fb4` | **pass** |
| Playwright smoke | `PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test e2e/digital-qms.spec.ts` | **1 passed** |
| Screenshots | `e2e/capture-screenshots.spec.ts` → `docs/screenshots/**/*.png` | **10 PNG** |

## Screenshot files
- `docs/screenshots/00-shell/login.png`
- `docs/screenshots/00-shell/dashboard.png`
- `docs/screenshots/00-shell/inventory.png`
- `docs/screenshots/m1-quality/hold-release.png`
- `docs/screenshots/m2-capa/capa.png`
- `docs/screenshots/m3-fefo/inventory-fefo.png`
- `docs/screenshots/m3-fefo/production.png`
- `docs/screenshots/m4-recall/trace.png`
- `docs/screenshots/m5-gc/lab-spc.png`
- `docs/screenshots/m6-assistant/assistant-widget.png`

## Remaining human / formal items
- G1 formal GV email/signature (implementation proceeded under student authorization; docs provisional)
- G5 key-user UAT signatures and manual stopwatch metrics in `docs/thesis-metrics.md`
- Docker Compose full stack when Docker Desktop is available
