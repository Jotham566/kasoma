import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const empty = {
  window_start: "2026-10-18T00:00:00Z",
  window_end: "2026-10-19T00:00:00Z",
  sampled_count: 0,
  capped: false,
  sample_limit: 10000,
  measure: "AUDIT_ACTIVITY_SAMPLE",
  counts: [
    "CONTENT",
    "FLAGS",
    "IMPORTS",
    "PRIVACY",
    "ROLES",
    "GRADING_REVIEW",
    "OTHER",
  ].map((category) => ({ category, count: 0 })),
};

test("audit empty, capped and denied refresh states remove stale results", async ({
  page,
}) => {
  let mode = "empty";
  await page.route("**/api/v1/admin/audit", async (route) => {
    if (mode === "denied")
      return route.fulfill({
        status: 403,
        json: { error: { code: "FORBIDDEN" } },
      });
    if (mode === "offline") return route.abort("internetdisconnected");
    return route.fulfill({
      json:
        mode === "empty"
          ? empty
          : {
              ...empty,
              capped: true,
              sampled_count: 10000,
              counts: empty.counts.map((row) => ({
                ...row,
                count: row.category === "CONTENT" ? 10000 : 0,
              })),
            },
    });
  });
  await page.goto("/admin/audit");
  const refresh = page.getByRole("button", { name: "Refresh audit activity" });
  await refresh.click();
  await expect(
    page.getByText("No recorded actions in this window."),
  ).toBeVisible();
  mode = "capped";
  await refresh.click();
  await expect(page.getByText(/Sample limit reached/)).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Audit activity sample" }),
  ).toContainText("10,000");
  mode = "denied";
  await refresh.click();
  await expect(page.getByRole("status")).toContainText("Activity unavailable.");
  await expect(
    page.getByRole("region", { name: "Audit activity sample" }),
  ).toHaveCount(0);
  mode = "offline";
  await refresh.click();
  await expect(page.getByRole("status")).toContainText(
    "Connection interrupted.",
  );
  mode = "empty";
  await refresh.click();
  await expect(page.getByRole("status")).toHaveText(
    "Audit activity refreshed.",
  );
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});
