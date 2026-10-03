import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-OPS-002: admin operations snapshot, unavailable heartbeat and accessible refresh", async ({
  page,
}) => {
  await page.goto("/admin/operations");
  await page.getByRole("button", { name: "Refresh operations" }).click();
  await expect(page.getByRole("status")).toContainText("Snapshot unavailable.");
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-content-operations-admin@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
  await page.goto("/admin/operations");
  await page.getByRole("button", { name: "Refresh operations" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Operational snapshot refreshed.",
  );
  await expect(page.getByText("Database: up", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Monitoring worker: unavailable", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Instrumentation still pending" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.route("**/api/v1/admin/operations", (route) =>
    route.abort("failed"),
  );
  await page.getByRole("button", { name: "Refresh operations" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Connection interrupted.",
  );
  await expect(page.getByText("Database: up", { exact: true })).toHaveCount(0);
});
