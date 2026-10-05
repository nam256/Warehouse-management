import { expect, test } from "@playwright/test";

test("topbar hiển thị người đang đăng nhập", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);

  const userChip = page.locator(".topbar-user");
  await expect(userChip).toBeVisible();
  await expect(userChip).toContainText(/Quản trị|admin/i);
  await expect(page.getByLabel(/Đang đăng nhập/i)).toBeVisible();
  await expect(page.locator(".topbar").getByRole("button", { name: "Đăng xuất" })).toBeVisible();
});

test.describe("mobile", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("topbar vẫn hiện tên người dùng trên điện thoại", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Tên đăng nhập").fill("lab");
    await page.getByLabel("Mật khẩu").fill("lab123");
    await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
    await expect(page).toHaveURL(/\/$/);

    await expect(page.locator(".topbar-user")).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  });
});
