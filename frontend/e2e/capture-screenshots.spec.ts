/**
 * Capture module screenshots for thesis evidence.
 * Run from frontend/: $env:PLAYWRIGHT_BASE_URL='http://localhost:5173'; npx playwright test e2e/capture-screenshots.spec.ts
 */
import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

function shot(folder: string, name: string) {
  const dir = path.resolve(process.cwd(), "..", "docs", "screenshots", folder);
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, name);
  console.log("screenshot ->", file);
  return file;
}

test("capture Digital QMS screenshots", async ({ page }) => {
  test.setTimeout(120_000);

  await page.goto("/login");
  await page.screenshot({ path: shot("00-shell", "login.png"), fullPage: true });

  await page.getByLabel("Tên đăng nhập").fill("admin");
  await page.getByLabel("Mật khẩu").fill("admin123");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/$/);
  await page.screenshot({ path: shot("00-shell", "dashboard.png"), fullPage: true });

  await page.goto("/inventory");
  await expect(page.getByRole("heading").first()).toBeVisible();
  await page.screenshot({ path: shot("00-shell", "inventory.png"), fullPage: true });

  await page.goto("/quality");
  await expect(page.getByRole("heading", { name: /Phê duyệt chất lượng/i })).toBeVisible();
  await page.screenshot({ path: shot("m1-quality", "hold-release.png"), fullPage: true });

  await page.goto("/capa");
  await expect(page.getByRole("heading").first()).toBeVisible();
  await page.screenshot({ path: shot("m2-capa", "capa.png"), fullPage: true });

  await page.goto("/inventory");
  await page.screenshot({ path: shot("m3-fefo", "inventory-fefo.png"), fullPage: true });

  await page.goto("/production");
  await expect(page.getByRole("heading").first()).toBeVisible();
  await page.screenshot({ path: shot("m3-fefo", "production.png"), fullPage: true });

  await page.goto("/trace");
  await expect(page.getByRole("heading").first()).toBeVisible();
  await page.screenshot({ path: shot("m4-recall", "trace.png"), fullPage: true });

  await page.goto("/lab");
  await expect(page.getByRole("heading").first()).toBeVisible();
  await page.screenshot({ path: shot("m5-gc", "lab-spc.png"), fullPage: true });

  const ai = page.getByRole("button", { name: /^AI/i }).first();
  if (await ai.count()) {
    await ai.click();
    await page.waitForTimeout(500);
  }
  await page.screenshot({ path: shot("m6-assistant", "assistant-widget.png"), fullPage: true });
});
