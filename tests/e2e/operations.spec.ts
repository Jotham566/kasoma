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
  const snapshotResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/v1/admin/operations") &&
      response.status() === 200,
  );
  await page.getByRole("button", { name: "Refresh operations" }).click();
  const baseline = await (await snapshotResponse).json();
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
  await expect(
    page.getByRole("heading", { name: "Local channel delivery" }),
  ).toBeVisible();
  const grading = page.getByRole("region", {
    name: "Grading queue operations",
  });
  await expect(grading).toBeVisible();
  await expect(
    grading.getByText("Queued grading work", { exact: true }),
  ).toBeVisible();
  await expect(grading).toContainText(
    "Oldest pending grading work: 0 seconds.",
  );
  await expect(grading).toContainText("they do not measure academic errors");
  await expect(grading).toContainText(
    "Pending audits include sealed assignments",
  );
  const exports = page.getByRole("region", {
    name: "Personal export operations",
  });
  await expect(
    exports.getByText("Queued exports", { exact: true }),
  ).toBeVisible();
  await expect(
    exports.getByText("Running exports", { exact: true }),
  ).toBeVisible();
  await expect(exports).toContainText("Oldest pending export: 0 seconds.");
  await expect(exports).toContainText(
    "These local alerts do not measure legal fulfillment deadlines.",
  );
  const retirement = page.getByRole("region", {
    name: "Synthetic export evidence maintenance",
  });
  await expect(retirement).toBeVisible();
  await expect(retirement.getByText("Disabled", { exact: true })).toBeVisible();
  await expect(retirement).toContainText("Account deletion is not enabled.");
  await expect(retirement.getByRole("button")).toHaveCount(0);
  const timing = page.getByRole("region", {
    name: "API response-start timing",
  });
  await expect(timing).toBeVisible();
  await expect(timing).toContainText("Best-effort measurements");
  await expect(timing).toContainText("does not measure complete downloads");
  await expect(
    page.getByText("No feedback dispatch samples in the last 24 hours.", {
      exact: true,
    }),
  ).toBeVisible();
  await page.screenshot({
    path: ".local/ui-review/operations-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: ".local/ui-review/operations-mobile.png",
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: ".local/ui-review/operations-mobile-large-text.png",
    fullPage: true,
  });
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "100%";
  });
  // Deterministic presentation states supplement the real authorized snapshot;
  // backend aggregation/authorization is exercised by local Redis integration tests.
  for (const state of [
    {
      sample_size: 0,
      p95_lower_exclusive_ms: null,
      p95_upper_inclusive_ms: null,
      capped: false,
      text: "No observed requests in the retained window.",
    },
    {
      sample_size: 20,
      p95_lower_exclusive_ms: null,
      p95_upper_inclusive_ms: 0,
      capped: false,
      text: "Observed p95: 0 ms, up to 0 ms.",
    },
    {
      sample_size: 20,
      p95_lower_exclusive_ms: 30000,
      p95_upper_inclusive_ms: null,
      capped: true,
      text: "greater than 30000 ms, with no finite upper bound",
    },
  ]) {
    const { text, ...sample } = state;
    await page.route("**/api/v1/admin/operations", (route) =>
      route.fulfill({
        json: {
          ...baseline,
          request_timing: {
            ...sample,
            interval_count: sample.sample_size ? 1 : 0,
            retention_seconds: 300,
            measure: "API_RESPONSE_START",
            best_effort: true,
          },
        },
      }),
    );
    await page.getByRole("button", { name: "Refresh operations" }).click();
    await expect(timing).toContainText(text);
    if (state.capped)
      await expect(timing).toContainText("some intervals were removed");
    await page.unroute("**/api/v1/admin/operations");
  }
  const model = page.getByRole("region", { name: "Local model observations" });
  for (const unknown of [false, true]) {
    await page.route("**/api/v1/admin/operations", (route) =>
      route.fulfill({
        json: {
          ...baseline,
          model_usage: {
            observed_attempts: unknown ? 1 : 0,
            candidate_responses: 0,
            fallback_responses: unknown ? 1 : 0,
            no_result_attempts: 0,
            usage_unknown_attempts: unknown ? 1 : 0,
            reported_input_tokens: 0,
            reported_output_tokens: 0,
            total_input_tokens: unknown ? null : 0,
            total_output_tokens: unknown ? null : 0,
            interval_count: unknown ? 1 : 0,
            capped: unknown,
            retention_seconds: 300,
            measure: "LOCAL_WORKER_GATEWAY_ATTEMPTS",
            best_effort: true,
          },
        },
      }),
    );
    await page.getByRole("button", { name: "Refresh operations" }).click();
    await expect(model).toContainText("Billing and costs are unavailable");
    await expect(model.getByText("Unknown", { exact: true })).toHaveCount(
      unknown ? 2 : 0,
    );
    if (unknown)
      await expect(model).toContainText("some observations were dropped");
    await page.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: `.local/ui-review/model-usage-${unknown ? "unknown" : "zero"}.png`,
      fullPage: true,
    });
    await page.evaluate(() => {
      document.documentElement.style.fontSize = "100%";
    });
    if (unknown)
      await model.screenshot({ path: ".local/ui-review/model-usage-card.png" });
    await page.unroute("**/api/v1/admin/operations");
  }
  await page.route("**/api/v1/admin/operations", (route) =>
    route.fulfill({
      json: {
        ...baseline,
        counts: {
          ...baseline.counts,
          retirement: {
            ...baseline.counts.retirement,
            scheduled: true,
            database_enabled: true,
            scope_allowed: true,
            due_requests: { value: 10000, at_least: true },
            last_attempt_status: "PROCESSED",
            last_removed: 100,
            last_examined: 200,
            observation_available: false,
          },
        },
      },
    }),
  );
  await page.getByRole("button", { name: "Refresh operations" }).click();
  await expect(retirement).toContainText(
    "Enabled in an isolated synthetic scope",
  );
  await expect(retirement).toContainText("At least 10000");
  await expect(retirement).toContainText("100 rows removed; 200 examined");
  await expect(retirement).toContainText("Unavailable");
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await retirement.screenshot({
    path: ".local/ui-review/export-retirement-card.png",
  });
  await page.unroute("**/api/v1/admin/operations");
  await page.route("**/api/v1/admin/operations", (route) =>
    route.abort("failed"),
  );
  await page.getByRole("button", { name: "Refresh operations" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Connection interrupted.",
  );
  await expect(page.getByText("Database: up", { exact: true })).toHaveCount(0);
});
