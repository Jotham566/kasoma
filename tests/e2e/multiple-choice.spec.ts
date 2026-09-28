import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

async function login(page: Page, email: string) {
  await page.goto("/onboarding");
  await page.getByLabel("Email or mobile number", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
}

test("FR-GRD-001: reviewed multiple choice, checkbox recovery and exact-set scoring", async ({
  browser,
}) => {
  const authorContext = await browser.newContext();
  const reviewerContext = await browser.newContext();
  const learnerContext = await browser.newContext();
  try {
    const author = await authorContext.newPage();
    const reviewer = await reviewerContext.newPage();
    const learner = await learnerContext.newPage();
    await login(author, "fixture-multiple-content_author@example.invalid");
    await author.goto("/admin/content");
    await expect(author.getByRole("status")).toHaveText(
      "Staff workspace ready.",
    );
    await author
      .getByLabel("Title", { exact: true })
      .fill("Browser multiple-choice fixture");
    await author
      .getByRole("combobox", { name: "Subject", exact: true })
      .selectOption({ label: "Physics" });
    await author
      .getByLabel("Topic cluster")
      .selectOption({ label: "Waves, Light and Sound" });
    await author
      .getByLabel("Question prompt")
      .fill("Synthetic check: select Alpha and Gamma.");
    await author.getByLabel("Response format").selectOption("MULTIPLE_CHOICE");
    await author
      .getByRole("button", { name: "Add option", exact: true })
      .click();
    for (const [id, label] of [
      ["A", "Alpha"],
      ["B", "Beta"],
      ["C", "Gamma"],
    ]) {
      await author.getByLabel(`Option ${id}`, { exact: true }).fill(label);
    }
    await author.getByLabel("Correct option A", { exact: true }).check();
    await author.getByLabel("Correct option C", { exact: true }).check();
    await author
      .getByLabel("Worked solution", { exact: true })
      .fill("Alpha and Gamma are options A and C.");
    await author
      .getByLabel("Feedback and remediation")
      .fill("Compare every option with both requested labels.");
    await author
      .getByLabel("Source and provenance")
      .fill("Original synthetic multiple-choice test");
    await author.getByLabel("Rights status").selectOption("ORIGINAL_KASOMA");
    await author
      .getByLabel("Rights evidence")
      .fill("Original software fixture");
    await author.getByLabel("Rights conditions").fill("Synthetic testing only");
    await author
      .getByLabel("Change reason", { exact: true })
      .fill("Exercise multiple-choice authoring");
    await author
      .getByRole("button", { name: "Save draft", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText("Version 1: DRAFT.");
    await expect(
      author.getByText("Correct option: A, C.", { exact: false }),
    ).toBeVisible();
    expect(
      (await new AxeBuilder({ page: author }).analyze()).violations,
    ).toEqual([]);
    await author
      .getByLabel("Submission reason")
      .fill("Synthetic independent multiple-choice review");
    await author
      .getByRole("button", { name: "Submit for review", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText(
      "Version 1: IN_REVIEW.",
    );
    await login(reviewer, "fixture-multiple-academic_reviewer@example.invalid");
    await reviewer.goto("/admin/content");
    await expect(reviewer.getByRole("status")).toHaveText(
      "Staff workspace ready.",
    );
    const queued = reviewer.getByRole("button", {
      name: "Browser multiple-choice fixture — v1 · IN_REVIEW",
    });
    while (!(await queued.count())) {
      await reviewer
        .getByRole("button", { name: "Load more", exact: true })
        .click();
      await expect(reviewer.getByRole("status")).toHaveText(
        "More items loaded.",
      );
    }
    await queued.click();
    const checks = reviewer
      .getByRole("group", { name: "Independent academic checklist" })
      .getByRole("checkbox");
    await expect(checks).toHaveCount(15);
    for (const check of await checks.all()) await check.check();
    await reviewer
      .getByLabel("Review comments")
      .fill("Synthetic units and precision checks passed");
    await reviewer
      .getByRole("button", { name: "Approve", exact: true })
      .click();
    await expect(reviewer.getByRole("status")).toHaveText(
      "Version 1: APPROVED.",
    );

    await login(learner, "e4-multiple-learner@example.invalid");
    await learner
      .getByLabel("Display name", { exact: true })
      .fill("Synthetic multiple-choice learner");
    await learner.getByLabel("Date of birth").fill("2000-01-01");
    await learner.getByLabel("Physics", { exact: true }).check();
    await learner.getByRole("button", { name: "Save profile" }).click();
    await expect(learner.getByRole("status")).toHaveText("Profile saved.");
    await learner
      .getByLabel("I give my own consent for this synthetic test.")
      .check();
    await learner.getByRole("button", { name: "Record my consent" }).click();
    await expect(
      learner.getByText("Required declarations are recorded.", {
        exact: false,
      }),
    ).toBeVisible();
    await learner.goto("/revise");
    await learner
      .getByRole("combobox", { name: "Topic", exact: true })
      .selectOption({ label: "Waves, Light and Sound" });
    const delivered = learner.waitForResponse("**/api/v1/sessions/*/next-item");
    await learner
      .getByRole("button", { name: "Start five-question practice" })
      .click();
    const payload = await (await delivered).text();
    expect(payload).not.toContain("correct_choice");
    await expect(
      learner.getByRole("button", { name: "Submit answer" }),
    ).toBeDisabled();
    await expect(
      learner.getByRole("button", { name: "Show worked solution" }),
    ).toHaveCount(0);
    await learner.getByRole("checkbox", { name: "Alpha", exact: true }).check();
    await learner.getByRole("button", { name: "Submit answer" }).click();
    await expect(
      learner.getByText("0 of 1 points", { exact: true }),
    ).toBeVisible();
    await learner.getByRole("button", { name: "Next question" }).click();
    await learner.getByRole("checkbox", { name: "Gamma", exact: true }).check();
    await learner.getByRole("checkbox", { name: "Alpha", exact: true }).focus();
    await learner.keyboard.press("Space");
    expect(
      (await new AxeBuilder({ page: learner }).analyze()).violations,
    ).toEqual([]);
    let lost = false;
    await learner.route("**/api/v1/sessions/*/attempts", async (route) => {
      if (!lost) {
        lost = true;
        const saved = await route.fetch();
        expect(saved.status()).toBe(200);
        await route.abort();
      } else await route.continue();
    });
    await learner.getByRole("button", { name: "Submit answer" }).click();
    await expect(learner.getByRole("status")).toContainText(
      "Check your connection, then retry. Saved answers are safe.",
    );
    await expect(
      learner.getByRole("checkbox", { name: "Alpha", exact: true }),
    ).toBeChecked();
    await expect(
      learner.getByRole("checkbox", { name: "Gamma", exact: true }),
    ).toBeChecked();
    await learner.getByRole("button", { name: "Submit answer" }).click();
    await expect(
      learner.getByText("1 of 1 points", { exact: true }),
    ).toBeVisible();
    await learner.reload();
    await expect(
      learner.getByText("2 of 5 answers saved", { exact: true }),
    ).toBeVisible();
    await learner.getByRole("button", { name: "Show worked solution" }).click();
    await expect(
      learner.getByText("Alpha and Gamma are options A and C.", {
        exact: true,
      }),
    ).toBeVisible();
  } finally {
    await Promise.allSettled([
      authorContext.close(),
      reviewerContext.close(),
      learnerContext.close(),
    ]);
  }
});
