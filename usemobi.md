# Kế hoạch giao diện Mobile Web — Oxeyns Digital QMS

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Làm web Oxeyns dùng tốt trên điện thoại (360–430px), menu dạng drawer ☰, bảng/form không vỡ layout, vẫn giữ design system hiện tại.

**Architecture:** Không tách app mobile. Nâng cấp `Layout.tsx` + CSS responsive trong `index.css`/`tokens.css`. Desktop giữ sidebar cố định; dưới `720px` sidebar thành drawer trượt + overlay. Không đổi API/backend/nghiệp vụ.

**Tech Stack:** React 19, TypeScript, Vite, CSS thuần (tokens sẵn có), Playwright viewport 390×844.

## Global Constraints

- Breakpoint chính: `max-width: 720px` (mobile); kiểm tra thêm `390×844` và `768px`.
- Menu mobile: nút ☰ mở drawer; đóng khi chọn route, bấm overlay, Escape.
- Touch target tối thiểu ~44px; không zoom ngang; chữ tối thiểu 14px.
- Form 1 cột; nút chính full-width trên mobile.
- Bảng rộng: cuộn ngang trong `.table-wrap`, không phá toàn trang.
- Không thêm thư viện UI mới.
- Tiếng Việt trên UI; không redesign màu/token toàn cục — chỉ bổ sung layout mobile.
- Không đổi backend/API.

---

## Hiện trạng (đã khảo sát)

| Hạng mục | Hiện tại | Vấn đề trên điện thoại |
|---|---|---|
| Viewport | Đã có `width=device-width` | OK |
| Sidebar | Fixed 248px; dưới 720px thành block full + nav 2 cột | Chiếm nửa màn hình, khó dùng |
| Main | `margin-left: sidebar` | OK desktop; mobile đã về 0 |
| Form | `form-grid` 2 cột → 1 cột <640px | Còn chỗ nút/filter chật |
| Bảng | `.table-wrap` overflow-x | Thiếu sticky header/cột thao tác |
| AI widget | fixed góc phải | Có thể che nút |

---

## File map

| File | Việc |
|---|---|
| `frontend/src/Layout.tsx` | State drawer, nút ☰, overlay, đóng theo route |
| `frontend/src/index.css` | Media query mobile drawer, form, table, topbar |
| `frontend/src/styles/tokens.css` | (tuỳ chọn) biến `--touch-min` |
| `frontend/e2e/mobile-smoke.spec.ts` | Smoke login + mở menu + vào 1 trang @390px |
| `docs/screenshots/mobile/` | PNG bằng chứng (sau khi code) |

---

### Task 1: Drawer navigation trong Layout

**Files:**
- Modify: `frontend/src/Layout.tsx`
- Modify: `frontend/src/index.css` (class `.sidebar--open`, `.nav-overlay`, `.topbar__menu`)

**Interfaces:**
- Produces: `menuOpen: boolean`; `closeMenu()` khi `NavLink` click / overlay / Escape / đổi `location.pathname`.

- [x] **Step 1: Thêm state + hook đóng theo route**

```tsx
import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

const [menuOpen, setMenuOpen] = useState(false);
const location = useLocation();

useEffect(() => {
  setMenuOpen(false);
}, [location.pathname]);

useEffect(() => {
  if (!menuOpen) return;
  const onKey = (e: KeyboardEvent) => {
    if (e.key === "Escape") setMenuOpen(false);
  };
  window.addEventListener("keydown", onKey);
  return () => window.removeEventListener("keydown", onKey);
}, [menuOpen]);
```

- [x] **Step 2: Topbar có nút ☰ (chỉ hiện mobile qua CSS)**

```tsx
<header className="topbar">
  <button
    type="button"
    className="topbar__menu"
    aria-label={menuOpen ? "Đóng menu" : "Mở menu"}
    aria-expanded={menuOpen}
    aria-controls="app-sidebar"
    onClick={() => setMenuOpen((v) => !v)}
  >
    ☰
  </button>
  <strong>Hệ thống quản lý chất lượng số</strong>
</header>
```

- [x] **Step 3: Sidebar + overlay**

```tsx
{menuOpen && (
  <button
    type="button"
    className="nav-overlay"
    aria-label="Đóng menu"
    onClick={() => setMenuOpen(false)}
  />
)}
<aside id="app-sidebar" className={`sidebar${menuOpen ? " sidebar--open" : ""}`}>
  {/* brand + nav + user như hiện tại */}
</aside>
```

- [x] **Step 4: Verify thủ công**

Mở DevTools → iPhone 12/390px: bấm ☰ mở menu; chọn “Tồn kho” → menu đóng; overlay đóng được.

---

### Task 2: CSS mobile shell đẹp và ổn định

**Files:**
- Modify: `frontend/src/index.css` (thay block `@media (max-width: 720px)`)

- [x] **Step 1: Thay media query 720px**

```css
@media (max-width: 720px) {
  .topbar {
    position: sticky;
    top: 0;
    z-index: 30;
    gap: var(--space-3);
    padding: 0 var(--space-3);
  }
  .topbar__menu {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 44px;
    min-height: 44px;
    padding: 0;
    border-radius: var(--radius);
    background: var(--color-primary);
  }
  .nav-overlay {
    position: fixed;
    inset: 0;
    z-index: 40;
    border: 0;
    background: rgba(15, 23, 42, 0.45);
  }
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 50;
    width: min(86vw, 300px);
    transform: translateX(-105%);
    transition: transform 0.2s ease;
    max-height: 100vh;
  }
  .sidebar--open { transform: translateX(0); }
  .sidebar nav {
    display: flex;
    flex-direction: column;
  }
  .sidebar nav a {
    min-height: 44px;
    display: flex;
    align-items: center;
  }
  .main-shell { margin-left: 0; }
  .main {
    padding: var(--space-3);
    padding-bottom: calc(var(--space-6) + 72px); /* chỗ cho AI widget */
  }
  .page-header { flex-direction: column; gap: var(--space-3); }
  .page-header h1 { font-size: 1.25rem; }
  .filter-bar, .action-bar {
    align-items: stretch;
  }
  .filter-bar > button,
  .form-actions button,
  .action-bar button {
    width: 100%;
    min-height: 44px;
  }
  .capa-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
  }
  .capa-tabs button { flex: 0 0 auto; white-space: nowrap; }
  .table-wrap, .card:has(table) {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .data-table th, .data-table td, table th, table td {
    white-space: nowrap;
    font-size: 0.85rem;
  }
  .assistant-widget {
    right: var(--space-3);
    bottom: var(--space-3);
  }
  .assistant-panel {
    width: min(100vw - 1.5rem, 360px);
  }
  .spc-metrics { grid-template-columns: 1fr 1fr; }
  .lab-gc-grid { grid-template-columns: 1fr; }
}
```

- [x] **Step 2: Ẩn nút ☰ trên desktop**

```css
.topbar__menu { display: none; }
.nav-overlay { display: none; }
```

(Trong media 720px mới `display: inline-flex` / hiện overlay.)

- [x] **Step 3: `npm run build` phải xanh**

Run: `Set-Location frontend; npm run build`  
Expected: exit 0.

---

### Task 3: Chỉnh các màn hình hay vỡ trên mobile

**Files:**
- Modify nhẹ nếu cần: `Dashboard.tsx`, `QualityRelease.tsx`, `Capa.tsx`, `Production.tsx`, `Trace.tsx`, `Lab.tsx`, `Inventory.tsx` (chỉ className/wrapper, không đổi logic).

- [x] **Step 1: Bọc mọi bảng còn thiếu bằng `.table-wrap`**

Ví dụ:

```tsx
<div className="table-wrap card">
  <DataTable ... />
</div>
```

- [x] **Step 2: ActionBar nhiều nút trên mobile**

CSS đã `button { width: 100% }` trong filter/action; nếu hàng nút trong table quá dài, giữ cuộn ngang — không ép card layout mới trừ khi cần.

- [x] **Step 3: Login card đã OK** — chỉ kiểm tra padding trên 360px.

---

### Task 4: Playwright mobile smoke + screenshot

**Files:**
- Create: `frontend/e2e/mobile-smoke.spec.ts`
- Create: `docs/screenshots/mobile/` (PNG sau khi chạy)

- [x] **Step 1: Viết smoke**

```ts
import { expect, test } from "@playwright/test";

test.use({ viewport: { width: 390, height: 844 } });

test("mobile drawer navigation", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.getByRole("button", { name: /Mở menu/i }).click();
  await page.getByRole("link", { name: "Phê duyệt chất lượng" }).click();
  await expect(page.getByRole("heading", { name: /Phê duyệt chất lượng/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Mở menu/i })).toBeVisible();
});
```

- [x] **Step 2: Chạy**

```powershell
$env:PLAYWRIGHT_BASE_URL='http://localhost:5173'
npx playwright test e2e/mobile-smoke.spec.ts --reporter=list
```

Expected: 1 passed.

- [x] **Step 3: Chụp PNG** (có thể thêm vào `capture-screenshots.spec.ts` với viewport 390).

---

### Task 5: Definition of Done mobile

- [x] 390px: login, dashboard, tồn kho, phê duyệt chất lượng, CAPA, sản xuất, lab, trace mở được, không scroll ngang toàn trang.
- [x] Drawer mở/đóng đúng; không kẹt overlay.
- [x] Desktop ≥1280px không đổi hành vi sidebar cố định.
- [x] `npm run build` xanh; Playwright mobile smoke xanh.
- [x] Screenshot lưu `docs/screenshots/mobile/`.

---

## Thứ tự cắt nếu thiếu thời gian

1. Drawer + overlay (bắt buộc)  
2. Form/table overflow  
3. CAPA tabs scroll  
4. AI widget padding  
5. Screenshot đẹp / polish animation  

## Không làm trong phạm vi này

- App native / PWA install  
- Đổi API hoặc RBAC  
- Redesign màu/token toàn cục  
- Bottom tab bar (đã chọn drawer)

---

## Execution Handoff

Plan lưu tại `usemobi.md`.

1. **Subagent-Driven:** mỗi Task 1–4 một vòng implement + verify.  
2. **Inline:** làm tuần tự trong session này.

**Khuyến nghị bắt đầu ngay Task 1 (Layout drawer).**
