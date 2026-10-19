import { expect, test, type Route } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-OPS-002: OTP observations distinguish zero, loss and unavailable data", async ({
  page,
}, info) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-content-otp-admin@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
  await page.goto("/admin/operations");
  const region = page.getByRole("region", {
    name: "Local OTP adapter observations",
  });
  let mode: "zero" | "positive" | "legacy" | "unavailable" = "zero";
  const fixture = async (route: Route) => {
    const response = await route.fetch();
    expect(response.status()).toBe(200);
    const body = await response.json();
    // Presentation states only; actual SDK/Redis and authorization are integration-tested.
    if (mode === "legacy") delete body.otp_dispatch;
    else
      body.otp_dispatch =
        mode === "unavailable"
          ? null
          : {
              observed_attempts: mode === "positive" ? 4 : 0,
              email_returned: mode === "positive" ? 2 : 0,
              email_failed: mode === "positive" ? 1 : 0,
              sms_returned: mode === "positive" ? 1 : 0,
              sms_failed: 0,
              interval_count: mode === "positive" ? 2 : 0,
              capped: mode === "positive",
              retention_seconds: 300,
              measure: "LOCAL_API_OTP_ADAPTER_ATTEMPTS",
              best_effort: true,
            };
    await route.fulfill({ response, json: body });
  };
  await page.route("**/api/v1/admin/operations", fixture);
  const refresh = async () => {
    await page.getByRole("button", { name: "Refresh operations" }).click();
    await expect(page.getByRole("status")).toHaveText(
      "Operational snapshot refreshed.",
    );
  };
  await refresh();
  await expect(region.locator("dd")).toHaveText(["0", "0", "0", "0", "0"]);
  mode = "positive";
  await refresh();
  await expect(region.locator("dd")).toHaveText(["4", "2", "1", "1", "0"]);
  await expect(region).toContainText("some observations were dropped");
  await expect(region).toContainText("A return is not delivery or receipt");
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await region.screenshot({
    path: `.local/ui-review/otp-outcomes-${info.project.use.browserName}.png`,
  });
  for (const unavailable of ["legacy", "unavailable"] as const) {
    mode = unavailable;
    await refresh();
    await expect(region).toContainText("Missing values do not mean zero");
    await expect(region.locator("dd")).toHaveCount(0);
  }
  await page.unroute("**/api/v1/admin/operations", fixture);
  await page.context().setOffline(true);
  await page.getByRole("button", { name: "Refresh operations" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Connection interrupted",
  );
  await page.context().setOffline(false);
  await page.route("**/api/v1/admin/operations", fixture);
  mode = "positive";
  await page.getByRole("button", { name: "Refresh operations" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("status")).toHaveText(
    "Operational snapshot refreshed.",
  );
  await expect(region.locator("dd")).toHaveText(["4", "2", "1", "1", "0"]);
});
