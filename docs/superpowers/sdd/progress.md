# SDD Progress Ledger — Digital QMS

**Cập nhật:** 18/07/2026 (checklist kỹ thuật đóng)  
**Phạm vi:** Tasks 0–10 + mục 11 checklist trong `planluanvan.md`  
**Bằng chứng:** `docs/verification-checklist-2026-07-18.md`

| Task | Trạng thái | Ghi chú |
|---|---|---|
| 0–10 | Complete (technical) | API/UI/tests/docs/PNG |
| G0, G1.5, G2, G3, G4 | [x] | G4 dùng PG local; Docker waived |
| G1, G5 | [~] | Chờ chữ ký GV / UAT key-user formal |

## Verification snapshot (18/07/2026 chiều)

- Postgres: `test_postgres_profile` + `test_postgres_concurrency` → **2 passed**
- Playwright smoke → **pass** (`localhost:5173`)
- Screenshots → **10 PNG** dưới `docs/screenshots/`
- SQLite suite + frontend build → xanh (chạy lại cùng ngày)

## Open formal only

1. Email/chữ ký GV cho G1  
2. UAT 20 case với key users + chữ ký G5  
3. Điền số đo stopwatch trong `docs/thesis-metrics.md`  
4. (Tuỳ chọn) cài Docker Desktop để chạy Compose như tài liệu  
