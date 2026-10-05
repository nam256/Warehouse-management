import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);
});

test("các trang nghiệp vụ dùng cấu trúc giao diện đồng bộ", async ({ page }) => {
  await page.goto("/inventory");
  await expect(page.locator(".inventory-page")).toBeVisible();
  await expect(page.locator(".inventory-table")).toBeVisible();

  await page.goto("/quality");
  await expect(page.locator(".quality-page")).toBeVisible();
  await expect(page.locator(".quality-page .data-table")).toBeVisible();

  await page.goto("/reports");
  await expect(page.locator(".reports-page .report-grid")).toBeVisible();
  await expect(page.locator(".reports-page .report-section").first()).toBeVisible();

  await page.goto("/audit");
  await expect(page.locator(".audit-page")).toBeVisible();
  await expect(page.locator(".audit-page .data-table")).toBeVisible();
});

test.describe("mobile dark mode", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("báo cáo và nhật ký không làm tràn toàn trang", async ({ page }) => {
    await page.goto("/reports");
    await expect(page.locator(".report-grid")).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);

    await page.goto("/audit");
    await page.getByRole("button", { name: "Chuyển sang giao diện tối" }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.locator(".audit-page")).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  });
});
