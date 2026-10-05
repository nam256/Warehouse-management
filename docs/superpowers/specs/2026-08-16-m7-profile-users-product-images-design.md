# Thiết kế M7 — Hồ sơ người dùng, quản lý tài khoản, ảnh vật tư

**Ngày:** 2026-08-16  
**Trạng thái:** Đã chốt với sinh viên (option 2 — không đăng ký công khai)  
**Phụ thuộc:** Gate G4 đã đạt; M1–M6 kỹ thuật đã đóng  
**Không thuộc lõi luận văn Digital QMS:** đây là mở rộng trải nghiệm vận hành / demo UI.

## Mục tiêu

1. **Hồ sơ người đăng nhập:** xem thông tin, đổi mật khẩu, (tuỳ chọn) ảnh đại diện.  
2. **Quản lý tài khoản:** chỉ **admin** tạo / khóa / đổi vai trò — **không** có form đăng ký công khai.  
3. **Ảnh vật tư/sản phẩm:** upload hoặc URL; hiển thị trên tồn kho, nhập/xuất kho, chọn vật tư.

## Quyết định đã chốt

| Hạng mục | Quyết định |
|---|---|
| Đăng ký công khai | **Không** |
| Tạo tài khoản | Chỉ `admin` |
| Vai trò khi tạo | Admin chọn: `thu_kho`, `ky_thuat`, `ql_nm`, `lab`, `attp`, `admin` |
| Hồ sơ | User xem `username`, `full_name`, `role`; đổi `full_name` + mật khẩu |
| Avatar | Tuỳ chọn: upload ảnh nhỏ hoặc chữ cái như hiện tại |
| Ảnh vật tư | Cột `image_url` (hoặc file lưu local `/uploads/materials/`) |
| Chỗ hiện ảnh | Tồn kho (card/bảng), form nhập kho, xem trước xuất kho |

## API đề xuất

### Auth / Profile
- `GET /auth/me` — đã có; bổ sung `avatar_url` nếu có  
- `PATCH /auth/me` — cập nhật `full_name`, `avatar_url`  
- `POST /auth/me/password` — `{ current_password, new_password }`

### Users (admin)
- `GET /users` — danh sách (admin)  
- `POST /users` — tạo tài khoản `{ username, password, full_name, role }`  
- `PATCH /users/{id}` — đổi `full_name`, `role`, `is_active`

### Materials
- `PATCH /materials/{id}` — thêm/sửa `image_url` (admin hoặc thủ kho — chốt khi code: mặc định admin + thủ kho)  
- `POST /materials/{id}/image` — upload multipart (nếu dùng file local)

## UI

- Topbar / sidebar-user: click → `/profile`  
- Menu admin: **Quản lý tài khoản** → `/users`  
- Login: giữ demo accounts; không thêm link “Đăng ký”  
- Inventory / StockIn / StockOut: thumbnail 40–64px cạnh tên vật tư; empty dùng placeholder

## Ràng buộc an toàn

- Không self-register  
- Đổi mật khẩu bắt buộc mật khẩu hiện tại  
- Admin không tự khóa chính mình nếu là admin cuối cùng (tuỳ chọn NFR)  
- File ảnh: giới hạn loại (`jpg/png/webp`) và dung lượng (ví dụ ≤ 1 MB)  
- Audit: tạo user / đổi role / đổi mật khẩu ghi nhật ký nếu có hook sẵn

## Tiêu chí xong

- [x] Profile xem + đổi tên + đổi mật khẩu  
- [x] Admin tạo user và khóa user  
- [x] Material có ảnh; tồn kho hiện ảnh  
- [x] Migration Alembic (SQLite + PostgreSQL)  
- [ ] Checklist UI 0b.3 + screenshot `docs/screenshots/m7-profile/`  
- [x] Không phá login demo / RBAC hiện có  

## Ngoài phạm vi M7

- OAuth / SSO  
- Quên mật khẩu qua email  
- Gallery nhiều ảnh / CDN production  
- Đăng ký công khai có duyệt
