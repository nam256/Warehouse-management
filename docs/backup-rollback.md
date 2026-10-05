# Kế hoạch Backup & Rollback

**Hệ thống:** Oxeyns Kho & SX  
**CSDL:** PostgreSQL (staging) / SQLite (dev)

---

## 1. Mục tiêu

- Bảo vệ dữ liệu kho, lô, mẻ SX, CCP, audit log
- Khôi phục nhanh khi lỗi deploy hoặc hỏng DB
- Đáp ứng NFR backup trong `docs/requirements.md`

---

## 2. Thành phần cần backup

| Thành phần | Ưu tiên | Ghi chú |
|------------|---------|---------|
| PostgreSQL database | **Cao** | Toàn bộ nghiệp vụ |
| File `.env` | Cao | Không commit Git — lưu vault nội bộ |
| Upload/GC files (future) | Trung bình | Khi bật attachment |
| Docker images | Thấp | Rebuild từ repo |

---

## 3. Backup PostgreSQL

### 3.1. Script có sẵn

```powershell
# scripts/backup_db.ps1
.\scripts\backup_db.ps1 -OutputDir "D:\Backup\Oxeyns"
```

### 3.2. Thủ công (pg_dump)

```powershell
docker compose exec -T db pg_dump -U oxeyns oxeyns > backup_YYYYMMDD_HHMM.sql
```

### 3.3. Lịch backup đề xuất (staging/demo)

| Loại | Tần suất | Retention |
|------|----------|-----------|
| Full DB | Hàng ngày (2h sáng) | 30 ngày |
| Trước deploy | Mỗi lần release | Giữ 5 bản |
| Trước migration | Bắt buộc | 1 bản + verify restore |

Lưu backup **ngoài server** (NAS hoặc PC ATTP/IT).

---

## 4. Backup SQLite (dev)

```powershell
copy backend\oxeyns.db backend\backups\oxeyns_YYYYMMDD.db
```

---

## 5. Khôi phục (Restore)

### PostgreSQL

```powershell
# Dừng API để tránh ghi trong lúc restore
docker compose stop api

docker compose exec -T db psql -U oxeyns -d oxeyns < backup_YYYYMMDD.sql

docker compose start api
```

### SQLite

```powershell
copy backend\backups\oxeyns_YYYYMMDD.db backend\oxeyns.db
```

### Kiểm tra sau restore

- Login admin
- Đối chiếu số lô/mẻ với backup log
- Chạy smoke UAT TC-01

---

## 6. Rollback ứng dụng

| Tình huống | Hành động |
|------------|-----------|
| Lỗi code release mới | `git checkout <tag-cũ>` + rebuild Docker |
| Lỗi migration | Restore DB backup trước migration + revert code |
| Lỗi cấu hình `.env` | Khôi phục `.env` từ bản lưu |

```powershell
git checkout v0.1-mvp-demo
docker compose up -d --build
```

---

## 7. RTO / RPO (mục tiêu demo)

| Chỉ số | Mục tiêu prototype |
|--------|---------------------|
| RPO (mất dữ liệu tối đa) | 24h (backup daily) |
| RTO (thời gian khôi phục) | &lt; 2h |

Production chính thức: công ty quy định lại theo FSSC.

---

## 8. Checklist vận hành

- [ ] Đặt lịch Task Scheduler chạy `backup_db.ps1`
- [ ] Test restore **1 lần/tháng** trên máy dev
- [ ] Ghi log backup (ngày, kích thước file, người thực hiện)
- [ ] Không lưu backup trên cùng ổ với DB production

---

*Triển khai: `docs/deploy.md`*
