# Hướng dẫn đóng góp — Oxeyns Kho & SX (TTTN)

Tài liệu này dành cho **dev chính**, sinh viên hỗ trợ IT và các thành viên tham gia đề tài thực tập tại Công ty TNHH Oxeyns – Chi nhánh Long An.

---

## Mục đích

- Thống nhất quy trình làm việc trên Git
- Giảm xung đột code giữa module Kho, Sản xuất, Lab, Báo cáo
- Đảm bảo commit message và PR dễ truy vết trong báo cáo TTTN

---

## Chiến lược nhánh (Branch strategy)

```
main          ← ổn định, demo/báo cáo, chỉ merge qua PR đã review
  └── develop ← tích hợp hàng ngày, chạy được end-to-end
        ├── feature/module-kho-nhap-xuat
        ├── feature/module-sx-operation-record
        ├── feature/module-lab-ccp
        └── feature/docs-uat-bao-cao
```

### Quy tắc

| Nhánh | Mục đích | Ai merge |
|-------|----------|----------|
| `main` | Bản release/demo cho GV và công ty | Dev chính + review |
| `develop` | Tích hợp tính năng đã test cơ bản | Dev chính |
| `feature/*` | Một tính năng hoặc một module | Người implement |

### Quy trình làm việc

1. **Checkout** từ `develop`: `git checkout develop && git pull`
2. **Tạo nhánh**: `git checkout -b feature/ten-ngan-gon`
3. **Commit** thường xuyên, message rõ ràng (xem bên dưới)
4. **Push** và mở Pull Request vào `develop`
5. Sau UAT/demo ổn định: PR `develop` → `main` (tag phiên bản nếu cần, ví dụ `v0.1-mvp-demo`)

### Hotfix (sửa lỗi gấp trên demo)

```text
main → hotfix/ten-loi → PR vào main → cherry-pick hoặc merge ngược develop
```

---

## Quy ước đặt tên nhánh

| Loại | Mẫu | Ví dụ |
|------|-----|-------|
| Tính năng | `feature/<module>-<mo-ta>` | `feature/kho-fifo-lot` |
| Sửa lỗi | `fix/<module>-<mo-ta>` | `fix/ccp-c14-validation` |
| Tài liệu | `docs/<noi-dung>` | `docs/uat-test-cases` |
| Refactor | `refactor/<pham-vi>` | `refactor/audit-middleware` |

Dùng chữ thường, gạch ngang; tránh tiếng Việt có dấu trong tên nhánh.

---

## Quy ước commit message

Áp dụng **Conventional Commits** (rút gọn cho đề tài):

```text
<type>(<scope>): <mô tả ngắn bằng tiếng Việt hoặc Anh>

[body tùy chọn — giải thích why, không what]
```

### Type

| Type | Khi nào dùng |
|------|----------------|
| `feat` | Tính năng mới (API, UI, export PDF…) |
| `fix` | Sửa bug |
| `docs` | Chỉ thay đổi tài liệu (`docs/`, README, plan) |
| `test` | Thêm/sửa test |
| `refactor` | Tái cấu trúc, không đổi hành vi |
| `chore` | Dependency, script, cấu hình |

### Scope gợi ý

`kho` | `sx` | `lab` | `ccp` | `auth` | `reports` | `db` | `fe` | `be` | `devops`

### Ví dụ

```text
feat(kho): thêm phiếu nhập NVL và gắn lô batch NCC
fix(ccp): chặn hoàn thành mẻ khi Ttop ngoài 107–110°C
docs(uat): bổ sung kịch bản E2E nhập → SX → Lab
test(be): unit test rule CCP1 C14 13.02–14.39
```

### Nguyên tắc

- Một commit = một thay đổi logic có thể review được
- Không commit secret (`.env`, mật khẩu thật)
- Thay đổi schema DB: kèm migration (hoặc ghi rõ trong PR) + cập nhật `docs/database-design.md`

---

## Pull Request

- Tiêu đề theo format commit
- Mô tả: **What / Why / How test**
- Link issue hoặc mục trong `plan.md` nếu có
- Sinh viên IT: PR tài liệu/UAT không cần chạy full test backend; PR code nên có ít nhất smoke test local

---

## Phân công vai trò

| Vai trò | Trách nhiệm trên repo |
|---------|------------------------|
| Dev chính | Core API, DB, logic nghiệp vụ, merge `develop` |
| Sinh viên IT | Spec, UAT, tài liệu `docs/`, test case, demo slide |
| QL NM / Thủ kho | UAT nghiệp vụ, phản hồi trên PR tài liệu |

---

## Môi trường & chạy local

Xem `README.md`. Trước khi PR code:

```powershell
# Backend
cd backend && .\.venv\Scripts\uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev
```

---

## Liên hệ

- Vấn đề nghiệp vụ (BM-xx, CCP): đội ATTP / QL nhà máy
- Vấn đề kỹ thuật repo: dev chính
- Phạm vi báo cáo TTTN: GV hướng dẫn + `docs/pham-vi-xac-nhan.md`
