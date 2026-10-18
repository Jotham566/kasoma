import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-GRD-009/FR-CNT-006: lost report acknowledgement and independent audited triage", async ({
  page,
  browser,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("flag-learner@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic diagnostic learner");
  await page.getByLabel("Date of birth").fill("2000-01-01");
  await page.getByLabel("Mathematics", { exact: true }).check();
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByRole("status")).toHaveText("Profile saved.");
  await page
    .getByLabel("I give my own consent for this synthetic test.")
    .check();
  await page.getByRole("button", { name: "Record my consent" }).click();
  await expect(
    page.getByText(/^Required declarations are recorded\./),
  ).toBeVisible();
  await page.goto("/revise");
  await page
    .getByRole("button", { name: "Start five-question practice" })
    .click();
  await page.getByRole("radio", { name: "Alpha", exact: true }).check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  // The save response precedes its authoritative session refresh. Wait for the
  // existing ready signal before exercising the report interaction.
  await expect(
    page.getByRole("button", { name: "Reload saved progress" }),
  ).toBeEnabled();
  await expect(
    page.getByText("1 of 5 answers saved", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Report question or grade" }).click();
  const form = page.getByRole("region", { name: "Report question or grade" });
  await expect(form.getByRole("status")).toContainText("No reports recorded");
  await form.getByLabel("Issue category").selectOption("GRADE_DISPUTE");
  await form
    .getByLabel("Optional issue comment")
    .fill("Synthetic browser concern <script>window.flagLeak=1</script>");
  await page.route(
    "**/api/v1/attempts/*/flag",
    async (route) => {
      if (route.request().method() !== "POST") return route.continue();
      const response = await route.fetch();
      expect(response.status()).toBe(201);
      await route.abort("failed");
    },
    { times: 1 },
  );
  await form.getByRole("button", { name: "Send report" }).click();
  await expect(form.getByRole("status")).toContainText("Could not confirm");
  await form.getByRole("button", { name: "Retry report" }).focus();
  await page.keyboard.press("Enter");
  await expect(form.getByRole("status")).toContainText("Report recorded");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.reload();
  await page.getByRole("button", { name: "Report question or grade" }).click();
  await expect(form.getByText("Recorded: Grade concern")).toBeVisible();
  await form.getByLabel("Issue category").selectOption("GRADE_DISPUTE");
  await expect(
    form.getByRole("button", { name: "Send report" }),
  ).toBeDisabled();
  await page.goto("/admin/flags");
  await expect(page.getByRole("status")).toContainText(
    "Reviewer or administrator access",
  );
  const context = await browser.newContext();
  const staff = await context.newPage();
  try {
    await staff.goto("/onboarding");
    await staff
      .getByLabel("Email or mobile number", { exact: true })
      .fill("e2e-content-flag-reviewer@example.invalid");
    await staff.getByRole("button", { name: "Send code", exact: true }).click();
    await staff.getByLabel("Verification code", { exact: true }).fill("246810");
    await staff.getByRole("button", { name: "Verify and continue" }).click();
    await expect(
      staff.getByRole("button", { name: "Save profile" }),
    ).toBeVisible();
    await staff.goto("/admin/flags");
    await staff.getByRole("button", { name: "Review report" }).click();
    await expect(
      staff.getByText(
        "Synthetic browser concern <script>window.flagLeak=1</script>",
        { exact: true },
      ),
    ).toBeVisible();
    expect(await staff.evaluate(() => "flagLeak" in window)).toBe(false);
    await staff.getByRole("button", { name: "Save triage decision" }).click();
    await expect(staff.getByRole("status")).toContainText("saved and audited");
    await staff
      .getByLabel("Decision", { exact: true })
      .selectOption("RESOLVED");
    await staff
      .getByLabel("Resolution note")
      .fill("Synthetic review completed; evidence unchanged.");
    await staff.route(
      "**/api/v1/admin/content-flags/*",
      async (route) => {
        const response = await route.fetch();
        expect(response.status()).toBe(200);
        await route.abort("failed");
      },
      { times: 1 },
    );
    await staff.getByRole("button", { name: "Save triage decision" }).click();
    await expect(staff.getByRole("status")).toContainText("Could not confirm");
    await staff.getByRole("button", { name: "Retry triage decision" }).focus();
    await staff.keyboard.press("Enter");
    await expect(staff.getByRole("status")).toContainText("saved and audited");
    await expect(
      staff.getByText(
        "Category: GRADE_DISPUTE. Status: RESOLVED. Revision: 3.",
      ),
    ).toBeVisible();
    expect(
      (await new AxeBuilder({ page: staff }).analyze()).violations,
    ).toEqual([]);
    await staff.getByRole("button", { name: "Reload selected flag" }).click();
    await expect(
      staff.getByText(
        "Recorded resolution: Synthetic review completed; evidence unchanged.",
      ),
    ).toBeVisible();
    await staff
      .getByRole("link", { name: "Inspect reported content version" })
      .click();
    await expect(
      staff.getByRole("heading", { name: /Staff preview — version/ }).first(),
    ).toBeVisible();
  } finally {
    await context.close().catch(() => {});
  }
});
