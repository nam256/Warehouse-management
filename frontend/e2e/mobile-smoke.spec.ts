import { expect, test } from "@playwright/test";

test.use({ viewport: { width: 390, height: 844 } });

test("mobile drawer navigation", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.getByRole("button", { name: /Mở menu/i }).click();
  await expect(page.locator("#app-sidebar")).toHaveClass(/sidebar--open/);
  await page.getByRole("link", { name: "Phê duyệt chất lượng" }).click();
  await expect(page.getByRole("heading", { name: /Phê duyệt chất lượng/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Mở menu/i })).toBeVisible();
});
