import { expect, test } from "@playwright/test";

test("Digital QMS critical flow", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("lab");
  await page.getByLabel("Mật khẩu").fill("lab123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();

  await expect(page).toHaveURL(/\/$/);
  await page.goto("/quality");
  await expect(page.getByRole("heading", { name: "Phê duyệt chất lượng lô" })).toBeVisible();
});
