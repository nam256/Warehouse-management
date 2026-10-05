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

  await search.fill("tp-tinhdau");
  await expect(table.getByText("Tinh dầu tràm")).toBeVisible();
  await expect(table.getByText("Sả nguyên liệu")).toHaveCount(0);

  await search.fill("sa nguyen lieu");
  await expect(table.getByText("Sả nguyên liệu")).toBeVisible();
  await expect(table.getByText("Tinh dầu tràm")).toHaveCount(0);

  await search.fill("SẢ NGUYÊN LIỆU");
  await expect(table.getByText("Sả nguyên liệu")).toBeVisible();

  await search.fill("khong ton tai");
  await expect(page.getByText("Không tìm thấy sản phẩm")).toBeVisible();
  await expect(table).toHaveCount(0);

  await search.fill("");
  await expect(table.getByText("Tinh dầu tràm")).toBeVisible();
  await expect(table.getByText("Sả nguyên liệu")).toBeVisible();
});

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
    expect(box!.x + box!.width).toBeLessThanOrEqual(391);

    await search.fill("tram");
    await expect(page.locator(".inventory-cards").getByText("Tinh dầu tràm")).toBeVisible();

    await page.getByRole("button", { name: "Chuyển sang giao diện tối" }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(search).toBeVisible();
  });
});
