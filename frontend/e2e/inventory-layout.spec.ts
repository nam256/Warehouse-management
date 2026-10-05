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
          material_name: "Tinh dầu tràm lá dài dùng cho sản xuất",
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

test("desktop tồn kho không cần kéo ngang để xem danh sách", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await mockInventoryApis(page);
  await loginAndOpenInventory(page);

  await expect(page.locator(".inventory-table")).toBeVisible();
  await expect(page.locator(".inventory-table").getByText("Tinh dầu tràm lá dài dùng cho sản xuất")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  expect(
    await page.locator(".inventory-table .table-wrap").evaluate((el) => el.scrollWidth <= el.clientWidth + 1),
  ).toBe(true);
});

test.describe("mobile", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("mobile tồn kho dùng thẻ, không kéo ngang", async ({ page }) => {
    await mockInventoryApis(page);
    await loginAndOpenInventory(page);

    await expect(page.locator(".inventory-cards")).toBeVisible();
    await expect(page.locator(".inventory-card").first()).toBeVisible();
    await expect(page.locator(".inventory-cards").getByText("Tinh dầu tràm lá dài dùng cho sản xuất")).toBeVisible();
    await expect(page.locator(".inventory-table")).toBeHidden();

    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  });
});
