# Tìm kiếm sản phẩm tồn kho — Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm ô tìm kiếm trong trang **Báo cáo tồn kho**, cho phép lọc tức thời theo mã hoặc tên vật tư trên web và điện thoại.

**Architecture:** Tìm kiếm thực hiện phía frontend trên dữ liệu tồn kho đã tải bằng `getInventory()`. `Inventory.tsx` giữ chuỗi `search`, chuẩn hóa chữ thường + bỏ dấu tiếng Việt, rồi tạo `filteredRows` bằng `useMemo`. Không gọi lại API khi gõ và không đổi backend.

**Tech Stack:** React 19, TypeScript, CSS hiện có (`FilterBar`), `EmptyState`, Playwright.

## Global Constraints

- Không đổi backend, API, database hoặc RBAC.
- Tìm không phân biệt chữ hoa/chữ thường.
- Tìm **không bắt buộc dấu tiếng Việt** (ví dụ `sa` vẫn khớp `Sả`, `tram` khớp `tràm`) — quan trọng khi gõ trên điện thoại.
- Phạm vi tìm: `material_code` và `material_name` (toàn bộ dòng tồn kho, không chỉ thành phẩm).
- Bỏ khoảng trắng đầu/cuối trước khi lọc.
- Chuỗi rỗng / chỉ khoảng trắng → hiện toàn bộ danh sách.
- Kết quả cập nhật ngay khi nhập, không cần nút “Tìm”.
- Ô tìm luôn hiện sau tiêu đề (kể cả khi đang tải / đã lọc hết) để người dùng không phải đoán chỗ nhập.
- Dùng tốt ở viewport 390×844 và dark mode.
- Không thêm thư viện mới.

## Rủi ro đã xử lý trong kế hoạch

| Rủi ro | Cách xử lý |
|---|---|
| `toLocaleLowerCase("vi")` **không** bỏ dấu → gõ không dấu không ra kết quả | Hàm `normalizeSearchText()`: lower + `normalize("NFD")` + bỏ `\p{M}` |
| Test mobile phụ thuộc backend thật → flaky | Mock inventory/batches giống test desktop |
| Race: assert trước khi bảng render | `await expect(table).toBeVisible()` / chờ empty state trước assert chi tiết |
| Nhầm “kho trống” với “không tìm thấy” | Hai `EmptyState` tách điều kiện |
| Đếm test sai sau khi thêm mobile | DoD: 2 test inventory-search + 2 smoke = 4 passed |

---

## File map

| File | Trách nhiệm |
|---|---|
| `frontend/src/pages/Inventory.tsx` | `normalizeSearchText`, state tìm, `filteredRows`, UI ô tìm, empty state, đếm kết quả |
| `frontend/e2e/inventory-search.spec.ts` | Desktop + mobile; mock API; case/dấu/không kết quả/xóa ô |
| `error.txt` | Đánh dấu yêu cầu 11 sau khi verify xanh |

---

### Task 1: Viết kiểm thử tìm kiếm tồn kho

**Files:**
- Create: `frontend/e2e/inventory-search.spec.ts`

**Interfaces:**
- Consumes: `/inventory`, label `Tìm kiếm sản phẩm`, mock `**/api/v1/stock/inventory` và `**/api/v1/stock/batches`.
- Produces: hồi quy hành vi tìm theo mã/tên (hoa–thường + không dấu).

- [x] **Step 1: Tạo helper mock + test desktop**

```ts
import { expect, test, type Page } from "@playwright/test";

async function mockInventoryApis(page: Page) {
  await page.route("**/api/v1/stock/inventory", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          material_id: 101,
          material_code: "TP-TINHDAU-01",
          material_name: "Tinh dầu tràm",
          material_type: "finished_product",
          total_quantity: 25,
          reserved_quantity: 5,
          available_quantity: 20,
          nearest_expiry: "2027-12-31",
          unit: "kg",
          min_stock: 10,
          low_stock: false,
        },
        {
          material_id: 102,
          material_code: "NVL-SA-02",
          material_name: "Sả nguyên liệu",
          material_type: "raw_material",
          total_quantity: 8,
          reserved_quantity: 0,
          available_quantity: 8,
          nearest_expiry: "2027-06-30",
          unit: "kg",
          min_stock: 10,
          low_stock: true,
        },
      ]),
    });
  });

  await page.route("**/api/v1/stock/batches", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: "[]",
    });
  });
}

async function loginAndOpenInventory(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);
  await page.goto("/inventory");
  await expect(page.getByRole("heading", { name: /Báo cáo tồn kho/i })).toBeVisible();
}

test("lọc tồn kho theo mã và tên sản phẩm", async ({ page }) => {
  await mockInventoryApis(page);
  await loginAndOpenInventory(page);

  const search = page.getByLabel("Tìm kiếm sản phẩm");
  const table = page.getByRole("table", { name: "Báo cáo tồn kho vật tư" });
  await expect(search).toBeVisible();
  await expect(table).toBeVisible();

  // Mã — không phân biệt hoa/thường
  await search.fill("tp-tinhdau");
  await expect(table.getByText("Tinh dầu tràm")).toBeVisible();
  await expect(table.getByText("Sả nguyên liệu")).toHaveCount(0);

  // Tên — không dấu vẫn khớp
  await search.fill("sa nguyen lieu");
  await expect(table.getByText("Sả nguyên liệu")).toBeVisible();
  await expect(table.getByText("Tinh dầu tràm")).toHaveCount(0);

  // Tên — có dấu + hoa
  await search.fill("SẢ NGUYÊN LIỆU");
  await expect(table.getByText("Sả nguyên liệu")).toBeVisible();

  // Không có kết quả
  await search.fill("khong ton tai");
  await expect(page.getByText("Không tìm thấy sản phẩm")).toBeVisible();
  await expect(table).toHaveCount(0);

  // Xóa ô → hiện lại đủ
  await search.fill("");
  await expect(table.getByText("Tinh dầu tràm")).toBeVisible();
  await expect(table.getByText("Sả nguyên liệu")).toBeVisible();
});
```

- [x] **Step 2: Chạy test để xác nhận đang thất bại**

```powershell
Set-Location frontend
$env:PLAYWRIGHT_BASE_URL='http://localhost:5173'
npx playwright test e2e/inventory-search.spec.ts --reporter=list
```

Expected: FAIL vì chưa có input label `Tìm kiếm sản phẩm`.

---

### Task 2: Thêm tìm kiếm vào trang tồn kho

**Files:**
- Modify: `frontend/src/pages/Inventory.tsx`

**Interfaces:**
- Consumes: `rows: Row[]` từ API.
- Produces: `normalizeSearchText(value: string): string`, `search: string`, `filteredRows: Row[]`, UI label `Tìm kiếm sản phẩm`.

- [x] **Step 1: Bổ sung import**

```tsx
import { useEffect, useMemo, useState } from "react";
import FilterBar from "../components/ui/FilterBar";
```

- [x] **Step 2: Thêm hàm chuẩn hóa tìm kiếm (bỏ dấu)**

Đặt **ngay trên** component `Inventory` (cùng file):

```tsx
function normalizeSearchText(value: string): string {
  return value
    .trim()
    .toLocaleLowerCase("vi")
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}
```

Lý do: người dùng điện thoại thường gõ không dấu; chỉ `toLocaleLowerCase("vi")` **không** đủ (`"sa".includes` không khớp `"sả"`).

- [x] **Step 3: State + `filteredRows`**

```tsx
const [search, setSearch] = useState("");

const filteredRows = useMemo(() => {
  const term = normalizeSearchText(search);
  if (!term) return rows;

  return rows.filter((row) =>
    [row.material_code, row.material_name].some((value) =>
      normalizeSearchText(value ?? "").includes(term),
    ),
  );
}, [rows, search]);
```

Đặt sau `useEffect` load data, trước `columns`.

- [x] **Step 4: UI ô tìm + đếm kết quả (sau `PageHeader`, trước banner lỗi)**

```tsx
<FilterBar ariaLabel="Tìm kiếm tồn kho">
  <label>
    Tìm kiếm sản phẩm
    <input
      type="search"
      value={search}
      onChange={(event) => setSearch(event.target.value)}
      placeholder="Nhập mã hoặc tên (có/không dấu)"
      autoComplete="off"
      enterKeyHint="search"
    />
  </label>
</FilterBar>
{!loading && rows.length > 0 && (
  <p className="section-description" aria-live="polite">
    {normalizeSearchText(search)
      ? `Hiển thị ${filteredRows.length}/${rows.length} vật tư`
      : `${rows.length} vật tư`}
  </p>
)}
```

Gõ Enter trên mobile không submit form (không bọc `<form>`).

- [x] **Step 5: Hai empty state tách biệt**

Giữ empty khi kho thật sự trống:

```tsx
{!loading && rows.length === 0 && !error && (
  <EmptyState title="Chưa có dữ liệu tồn kho" description="Các vật tư có tồn kho sẽ xuất hiện tại đây." />
)}
```

Thêm empty khi có data nhưng lọc hết:

```tsx
{!loading && rows.length > 0 && filteredRows.length === 0 && (
  <EmptyState
    title="Không tìm thấy sản phẩm"
    description={`Không có vật tư phù hợp với “${search.trim()}”. Thử mã/tên khác hoặc bỏ dấu.`}
  />
)}
```

- [x] **Step 6: Bảng dùng `filteredRows`**

```tsx
{filteredRows.length > 0 && (
  <div className="card table-wrap">
    <DataTable
      columns={columns}
      rows={filteredRows}
      rowKey={(row) => row.material_code}
      caption="Báo cáo tồn kho vật tư"
    />
  </div>
)}
```

- [x] **Step 7: Chạy test desktop**

```powershell
Set-Location frontend
$env:PLAYWRIGHT_BASE_URL='http://localhost:5173'
npx playwright test e2e/inventory-search.spec.ts --reporter=list
```

Expected: `1 passed` (mobile test chưa thêm).

---

### Task 3: Mobile, dark mode, hồi quy

**Files:**
- Modify: `frontend/e2e/inventory-search.spec.ts`
- Modify: `error.txt`

- [x] **Step 1: Thêm test mobile (có mock API)**

```ts
test.describe("mobile", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("ô tìm tồn kho vừa màn hình điện thoại", async ({ page }) => {
    await mockInventoryApis(page);
    await loginAndOpenInventory(page);

    const search = page.getByLabel("Tìm kiếm sản phẩm");
    await expect(search).toBeVisible();

    const box = await search.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(390 + 1); // dung sai 1px subpixel

    await search.fill("tram");
    await expect(page.getByRole("table").getByText("Tinh dầu tràm")).toBeVisible();
  });
});
```

- [x] **Step 2: Kiểm tra dark mode**

1. Mở `/inventory`, bấm **Tối**.
2. Label, input, placeholder, dòng đếm, bảng, empty state đọc rõ.
3. Viewport 390×844: không cuộn ngang toàn trang; ô tìm full width trong `FilterBar`.

- [x] **Step 3: Build + smoke**

```powershell
Set-Location frontend
npm run build
$env:PLAYWRIGHT_BASE_URL='http://localhost:5173'
npx playwright test e2e/inventory-search.spec.ts e2e/mobile-smoke.spec.ts e2e/digital-qms.spec.ts --reporter=list
```

Expected: build xanh; **4 passed** (2 inventory-search + 1 mobile-smoke + 1 digital-qms).

- [x] **Step 4: Đánh dấu `error.txt`**

```text
11. thêm chức năng tìm kiếm sản phẩm trong mục tồn kho ✅
```

Chỉ tick sau Step 3 xanh.

---

## Definition of Done

- [x] `/inventory` có ô `Tìm kiếm sản phẩm`.
- [x] Tìm theo một phần **mã** vật tư.
- [x] Tìm theo một phần **tên** vật tư.
- [x] Không phân biệt hoa/thường.
- [x] Gõ **không dấu** vẫn ra kết quả có dấu.
- [x] Xóa ô → hiện lại toàn bộ.
- [x] Empty state đúng khi không khớp.
- [x] Có dòng đếm `Hiển thị x/y` khi đang lọc.
- [x] Không phát sinh request API mới khi gõ.
- [x] Dark mode + 390×844 ổn.
- [x] Build + Playwright liên quan xanh.

## Không làm trong phạm vi này

- Tìm server-side / phân trang.
- Lọc theo loại vật tư, hạn dùng, trạng thái chất lượng, số lô (có thể làm sau nếu cần).
- Highlight từ khóa trong bảng.
- Đồng bộ từ khóa lên URL / `localStorage`.
- Đổi API/backend/database.
