import { expect, test } from "@playwright/test";

test("scale chữ tiêu đề và nội dung dùng token hợp lý", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.goto("/inventory");
  await expect(page.getByRole("heading", { name: /Báo cáo tồn kho/i })).toBeVisible();
  const sizes = await page.evaluate(() => {
    const root = getComputedStyle(document.documentElement);
    const title = document.querySelector(".page-header h1");
    const description = document.querySelector(".page-header p");
    const body = document.body;
    return {
      textMd: root.getPropertyValue("--text-md").trim(),
      text2xl: root.getPropertyValue("--text-2xl").trim(),
      body: getComputedStyle(body).fontSize,
      title: title ? getComputedStyle(title).fontSize : "",
      description: description ? getComputedStyle(description).fontSize : "",
    };
  });

  expect(sizes.textMd).toBe("0.9375rem");
  expect(sizes.text2xl).toBe("1.5rem");
  expect(sizes.body).toBe("15px");
  expect(sizes.title).toBe("24px");
  expect(sizes.description).toBe("13px");
});
