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

test("FR-GRD-002: author and independently review numeric rules, then grade units and precision", async ({
  browser,
}) => {
  const authorContext = await browser.newContext();
  const reviewerContext = await browser.newContext();
  const learnerContext = await browser.newContext();
  try {
    const author = await authorContext.newPage();
    const reviewer = await reviewerContext.newPage();
    const learner = await learnerContext.newPage();
    await login(author, "fixture-numeric-content_author@example.invalid");
    await author.goto("/admin/content");
    await expect(author.getByRole("status")).toHaveText(
      "Staff workspace ready.",
    );
    await author
      .getByLabel("Title", { exact: true })
      .fill("Browser numeric fixture");
    await author
      .getByRole("combobox", { name: "Subject", exact: true })
      .selectOption({ label: "Physics" });
    await author
      .getByLabel("Topic cluster")
      .selectOption({ label: "Electricity and Magnetism" });
    await author
      .getByLabel("Question prompt")
      .fill(
        "Synthetic length check: enter a length equivalent to 100 cm using three significant figures.",
      );
    await author.getByLabel("Response format").selectOption("NUMERIC");
    await author.getByLabel("Expected numeric value").fill("1");
    await author
      .getByLabel("Canonical unit (empty for dimensionless)")
      .fill("m");
    await author.getByLabel("Unit 1 label", { exact: true }).fill("m");
    await author.getByRole("button", { name: "Add allowed unit" }).click();
    await author.getByLabel("Unit 2 label", { exact: true }).fill("cm");
    await author.getByLabel("Unit 2 factor", { exact: true }).fill("1/100");
    await author.getByLabel("SCIENTIFIC", { exact: true }).check();
    await author.getByLabel("Significant-figure policy").selectOption("EXACT");
    await author.getByLabel("Required significant figures").fill("3");
    await author
      .getByLabel("Worked solution", { exact: true })
      .fill("100 cm is 1.00 m with three significant figures.");
    await author
      .getByLabel("Feedback and remediation")
      .fill("Check the unit and significant figures.");
    await author
      .getByLabel("Source and provenance")
      .fill("Original synthetic numeric test");
    await author.getByLabel("Rights status").selectOption("ORIGINAL_KASOMA");
    await author
      .getByLabel("Rights evidence")
      .fill("Original software fixture");
    await author.getByLabel("Rights conditions").fill("Synthetic testing only");
    await author
      .getByLabel("Change reason", { exact: true })
      .fill("Exercise numeric authoring");
    await author
      .getByRole("button", { name: "Save draft", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText("Version 1: DRAFT.");
    await expect(
      author.getByRole("region", { name: "Numeric answer preview" }),
    ).toContainText("Expected value: 1 m");
    expect(
      (await new AxeBuilder({ page: author }).analyze()).violations,
    ).toEqual([]);
    await author
      .getByLabel("Submission reason")
      .fill("Synthetic independent numeric review");
    await author
      .getByRole("button", { name: "Submit for review", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText(
      "Version 1: IN_REVIEW.",
    );
    await login(reviewer, "fixture-numeric-academic_reviewer@example.invalid");
    await reviewer.goto("/admin/content");
    await expect(reviewer.getByRole("status")).toHaveText(
      "Staff workspace ready.",
    );
    const queued = reviewer.getByRole("button", {
      name: "Browser numeric fixture — v1 · IN_REVIEW",
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

    await login(learner, "e4-numeric-learner@example.invalid");
    await learner
      .getByLabel("Display name", { exact: true })
      .fill("Synthetic numeric learner");
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
      .selectOption({ label: "Electricity and Magnetism" });
    const delivered = learner.waitForResponse("**/api/v1/sessions/*/next-item");
    await learner
      .getByRole("button", { name: "Start five-question practice" })
      .click();
    const payload = await (await delivered).text();
    for (const key of [
      "expected_value",
      "absolute_tolerance",
      "factor",
      "offset",
    ])
      expect(payload).not.toContain(key);
    await learner.getByLabel("Numeric value", { exact: true }).fill("NaN");
    await learner.getByRole("button", { name: "Submit answer" }).click();
    await expect(learner.getByRole("status")).toContainText(
      "Your answer has not been saved",
    );
    await learner.getByLabel("Numeric value", { exact: true }).fill("1.0");
    await learner.getByRole("button", { name: "Submit answer" }).click();
    await expect(
      learner.getByText("0 of 1 points", { exact: true }),
    ).toBeVisible();
    await expect(
      learner.getByText("Use the requested number of significant figures.", {
        exact: true,
      }),
    ).toBeVisible();
    await learner.reload();
    await expect(
      learner.getByText("1 of 5 answers saved", { exact: true }),
    ).toBeVisible();
    await learner.getByRole("button", { name: "Next question" }).click();
    await learner.getByLabel("Numeric value", { exact: true }).fill("1.00e2");
    await learner
      .getByRole("combobox", { name: "Answer unit", exact: true })
      .selectOption("cm");
    expect(
      (await new AxeBuilder({ page: learner }).analyze()).violations,
    ).toEqual([]);
    await learner.getByRole("button", { name: "Submit answer" }).focus();
    await learner.keyboard.press("Enter");
    await expect(
      learner.getByText("1 of 1 points", { exact: true }),
    ).toBeVisible();
    await learner.getByRole("button", { name: "Show worked solution" }).click();
    await expect(
      learner.getByText("100 cm is 1.00 m", { exact: false }),
    ).toBeVisible();
  } finally {
    await Promise.allSettled([
      authorContext.close(),
      reviewerContext.close(),
      learnerContext.close(),
    ]);
  }
});
