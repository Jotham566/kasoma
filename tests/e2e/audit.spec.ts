import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-OPS-003: authenticated aggregate audit refresh and mobile access", async ({
  page,
}) => {
  await page.goto("/admin/audit");
  await page.getByRole("button", { name: "Refresh audit activity" }).click();
  await expect(page.getByRole("status")).toContainText("Activity unavailable.");
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-content-audit-admin@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
  await page.goto("/admin/audit");
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/api/v1/admin/audit") && r.status() === 200,
  );
  const refresh = page.getByRole("button", { name: "Refresh audit activity" });
  await refresh.focus();
  await page.keyboard.press("Enter");
  const result = await (await response).json();
  expect(result.sampled_count).toBeGreaterThan(0);
  expect(result.counts).toHaveLength(7);
  expect(JSON.stringify(result)).not.toContain("@example.invalid");
  await expect(page.getByRole("status")).toHaveText(
    "Audit activity refreshed.",
  );
  const sample = page.getByRole("region", { name: "Audit activity sample" });
  await expect(sample).toContainText("Staff role changes");
  await expect(sample).toContainText("Africa/Kampala");
  await expect(sample).toContainText(
    "does not establish complete audit coverage",
  );
  await page.screenshot({
    path: ".local/ui-review/audit-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 320, height: 740 });
  await page.getByRole("button", { name: "Workspace menu" }).click();
  await expect(
    page.getByRole("link", { name: "Audit", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await page.getByRole("button", { name: "Workspace menu" }).click();
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await refresh.boundingBox())?.height).toBeGreaterThanOrEqual(44);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: ".local/ui-review/audit-mobile-large-text.png",
    fullPage: true,
  });
});
