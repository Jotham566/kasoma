import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

async function onboard(page: Page, email: string) {
  await page.goto("/onboarding");
  await page.getByLabel("Email or mobile number", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic practice learner");
  await page.getByLabel("Date of birth").fill("2000-01-01");
  await page.getByLabel("Mathematics", { exact: true }).check();
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByRole("status")).toHaveText("Profile saved.");
  await page
    .getByLabel("I give my own consent for this synthetic test.")
    .check();
  await page.getByRole("button", { name: "Record my consent" }).click();
  await expect(
    page.getByText("Required declarations are recorded.", { exact: false }),
  ).toBeVisible();
}

test("FR-REV/GRD: retry after lost acknowledgement, resume, keyboard grading and solution gate", async ({
  page,
  browser,
}) => {
  await onboard(page, "e3-practice@example.invalid");
  await page.goto("/revise");
  await page
    .getByRole("button", { name: "Start five-question practice" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Question 1 of 5" }),
  ).toBeVisible();
  await expect(
    page.getByRole("progressbar", { name: "Saved answers" }),
  ).toHaveAttribute("value", "0");
  await expect(
    page.getByRole("progressbar", { name: "Saved answers" }),
  ).toHaveAttribute("max", "5");
  await page.screenshot({
    path: ".local/ui-review/practice-desktop.png",
    fullPage: true,
  });
  await expect(
    page.getByRole("button", { name: "Show worked solution" }),
  ).toHaveCount(0);
  // NFR-BW-001: a new context has no onboarding/navigation asset cache. The
  // original fixture has no question media, so count every completed response.
  const coldContext = await browser.newContext({
    storageState: await page.context().storageState(),
    serviceWorkers: "block",
  });
  try {
    const cold = await coldContext.newPage();
    const transfers: Promise<{
      bytes: number;
      body: number;
      headers: number;
      script: boolean;
    }>[] = [];
    cold.on("requestfinished", (request) => {
      transfers.push(
        request.sizes().then((sizes) => ({
          bytes: sizes.responseBodySize + sizes.responseHeadersSize,
          body: sizes.responseBodySize,
          headers: sizes.responseHeadersSize,
          script: request.resourceType() === "script",
        })),
      );
    });
    await cold.goto(page.url());
    await expect(
      cold.getByRole("heading", { name: "Question 1 of 5" }),
    ).toBeVisible();
    // Used only to delimit initial transfer measurement, after the real UI assertion.
    await cold.waitForLoadState("networkidle");
    const resources = await Promise.all(transfers);
    const bytes = resources.reduce(
      (total, resource) => total + resource.bytes,
      0,
    );
    const scripts = resources.filter((resource) => resource.script).length;
    expect(scripts).toBeGreaterThan(0);
    expect(resources.every((resource) => resource.bytes > 0)).toBe(true);
    expect(
      resources.every(
        (resource) =>
          resource.body >= 0 &&
          resource.headers >= 0 &&
          (!resource.script || resource.body > 0),
      ),
    ).toBe(true);
    console.log(
      JSON.stringify({
        metric: "cold_question_transfer",
        browser: browser.browserType().name(),
        response_bytes: bytes,
        resources: resources.length,
        scripts,
        limit_bytes: 250000,
      }),
    );
    expect(bytes).toBeLessThanOrEqual(250000);
  } finally {
    await coldContext.close();
  }
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByLabel("Alpha", { exact: true }).check();
  let lost = false;
  await page.route("**/api/v1/sessions/*/attempts", async (route) => {
    if (!lost) {
      lost = true;
      const saved = await route.fetch();
      expect(saved.status()).toBe(200);
      await route.abort();
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Submit answer" }).click();
  await expect(page.getByRole("status")).toContainText("Check your connection");
  await page.getByRole("button", { name: "Submit answer" }).click();
  await expect(
    page.getByRole("heading", { name: "Answer saved" }),
  ).toBeVisible();
  await expect(
    page.getByText("1 of 5 answers saved", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Show worked solution" }).click();
  await expect(
    page.getByText("The requested label is Alpha, option A.", { exact: true }),
  ).toBeVisible();
  const url = page.url();
  // A separate authenticated device resumes the same durable session.
  const otherContext = await browser.newContext({
    storageState: await page.context().storageState(),
  });
  const other = await otherContext.newPage();
  try {
    await other.goto(url);
    await expect(
      other.getByText("1 of 5 answers saved", { exact: true }),
    ).toBeVisible();
    for (let index = 2; index <= 5; index++) {
      await other.getByRole("button", { name: "Next question" }).click();
      await expect(
        other.getByRole("heading", { name: `Question ${index} of 5` }),
      ).toBeVisible();
      await other
        .getByLabel(index === 2 ? "Beta" : "Alpha", { exact: true })
        .focus();
      await other.keyboard.press("Space");
      await other.getByRole("button", { name: "Submit answer" }).focus();
      await other.keyboard.press("Enter");
      await expect(
        other.getByRole("heading", { name: "Answer saved" }),
      ).toBeVisible();
      if (index === 2)
        await expect(
          other.getByText("0 of 1 points", { exact: true }),
        ).toBeVisible();
    }
    await expect(
      other.getByRole("heading", { name: "Practice complete" }),
    ).toBeVisible();
    expect(
      (await new AxeBuilder({ page: other }).analyze()).violations,
    ).toEqual([]);
    await other.reload();
    await expect(
      other.getByText("5 of 5 answers saved", { exact: true }),
    ).toBeVisible();
  } finally {
    await otherContext.close();
  }
});

test("FR-ID-003: withdrawal blocks a previously active learner session", async ({
  page,
}) => {
  await onboard(page, "e3-withdrawal@example.invalid");
  await page.goto("/revise");
  await page
    .getByRole("button", { name: "Start five-question practice" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Question 1 of 5" }),
  ).toBeVisible();
  const url = page.url();
  await page.goto("/onboarding");
  await page
    .getByRole("button", { name: "Withdraw consent and assent" })
    .click();
  await expect(page.getByRole("status")).toContainText("Consent withdrawn");
  await page.goto(url);
  await expect(page.getByRole("status")).toContainText(
    "Learning access is paused",
  );
  await expect(page.getByRole("button", { name: "Submit answer" })).toHaveCount(
    0,
  );
});
