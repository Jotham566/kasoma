import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

async function onboard(page: Page, email: string) {
  await page.goto("/onboarding");
  await page.getByLabel("Email or mobile number", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic written-answer learner");
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
}

async function start(page: Page) {
  await page.goto("/revise");
  await page
    .getByRole("button", { name: "Start five-question practice" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Question 1 of 5" }),
  ).toBeVisible();
  await expect(
    page.getByLabel("Your written answer", { exact: true }),
  ).toBeVisible();
}

test("FR-GRD-003/004: pending, bounded automatic polling, pinned evidence and saved resume", async ({
  page,
}) => {
  await onboard(page, "short-text-feedback@example.invalid");
  await start(page);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page
    .getByLabel("Your written answer", { exact: true })
    .fill("  Alpha\n");
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(page.getByText(/Your feedback is being prepared/)).toBeVisible();
  await expect(page.getByText("1 of 1 points", { exact: true })).toHaveCount(0);
  await page.screenshot({
    path: ".local/ui-review/short-text-pending.png",
    fullPage: true,
  });
  await expect(page.getByText("1 of 1 points", { exact: true })).toBeVisible({
    timeout: 15000,
  });
  const feedback = page.getByRole("region", { name: "Answer feedback" });
  await expect(
    feedback.getByText("R1: 1 points", { exact: true }),
  ).toBeVisible();
  await expect(feedback.locator("blockquote")).toHaveText("Alpha");
  const id = new URL(page.url()).searchParams.get("session");
  expect(id).toBeTruthy();
  const saved = await (await page.request.get(`/api/v1/sessions/${id}`)).json();
  expect(saved.answered_count).toBe(1);
  expect(saved.answers[0].grade.method).toBe("RUBRIC_MODEL");
  await page.reload();
  await expect(page.getByText("1 of 1 points", { exact: true })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});

test("FR-GRD-004/FR-ID-006: neutral fallback, exact retry and explicit review request", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await onboard(page, "short-text-neutral@example.invalid");
  await start(page);
  let interrupted = false;
  await page.route("**/api/v1/sessions/*/attempts", async (route) => {
    if (!interrupted && route.request().method() === "POST") {
      interrupted = true;
      const response = await route.fetch();
      expect(response.status()).toBe(200);
      await route.abort();
    } else await route.continue();
  });
  await page.getByLabel("Your written answer", { exact: true }).fill("Beta");
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText(
    "Saved answers are safe",
  );
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(
    page.getByText(/We could not provide a reliable automated grade/),
  ).toBeVisible({ timeout: 15000 });
  await expect(
    page.getByText(/No score or mastery update was produced/),
  ).toBeVisible();
  const feedback = page.getByRole("region", { name: "Answer feedback" });
  await expect(feedback.getByText(/\d+ of \d+ points/)).toHaveCount(0);
  const id = new URL(page.url()).searchParams.get("session");
  const state = await (await page.request.get(`/api/v1/sessions/${id}`)).json();
  expect(state.answered_count).toBe(1);
  expect(state.answers[0].grade.status).toBe("LOW_CONFIDENCE");
  await page
    .getByRole("button", { name: "Request grading review", exact: true })
    .click();
  const review = page.getByRole("region", {
    name: "Request grading review",
    exact: true,
  });
  await expect(review.getByRole("status")).toHaveText(
    "No reports recorded for this answer.",
  );
  await review
    .getByRole("button", { name: "Send report", exact: true })
    .click();
  await expect(review.getByRole("status")).toContainText(
    "Review requested. Your saved answer is retained",
  );
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: ".local/ui-review/short-text-neutral-mobile.png",
    fullPage: true,
  });
});

test("FR-DIAG-004: written diagnostic hides grades until all terminal outcomes", async ({
  page,
}) => {
  await onboard(page, "short-text-diagnostic@example.invalid");
  await page.goto("/diagnostic");
  await page
    .getByRole("button", { name: "Start or resume diagnostic" })
    .click();
  for (let index = 0; index < 15; index += 1) {
    await expect(
      page.getByRole("group", { name: `Question ${index + 1}`, exact: true }),
    ).toBeVisible();
    await page
      .getByLabel("Your written answer", { exact: true })
      .fill(index === 14 ? "Beta" : "Alpha");
    await page
      .getByRole("button", { name: "Save answer and continue" })
      .click();
    if (index === 0) {
      const id = new URL(page.url()).searchParams.get("session");
      const state = await (
        await page.request.get(`/api/v1/diagnostics/${id}`)
      ).json();
      expect(state.status).toBe("ACTIVE");
      const first = state.answered_attempts[0].attempt_id;
      expect(
        (await page.request.get(`/api/v1/attempts/${first}/grade`)).status(),
      ).toBe(403);
    }
  }
  const id = new URL(page.url()).searchParams.get("session");
  await expect
    .poll(
      async () =>
        (await (await page.request.get(`/api/v1/diagnostics/${id}`)).json())
          .status,
      { timeout: 20000 },
    )
    .toBe("COMPLETED");
  await page.reload();
  await expect(
    page.getByRole("progressbar", { name: "Saved answers" }),
  ).toHaveAttribute("value", "15");
  await expect(page.getByText("1 of 1 points", { exact: true })).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});
