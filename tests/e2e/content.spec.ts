import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

async function signIn(page: Page, role: string) {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill(`e2e-content-${role}@example.invalid`);
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
  await page.goto("/admin/content");
  await expect(page.getByRole("status")).toHaveText("Staff workspace ready.");
}

test("FR-CNT-001–005: independent return, correction, approval and retirement", async ({
  browser,
}) => {
  const authorContext = await browser.newContext();
  const reviewerContext = await browser.newContext();
  const author = await authorContext.newPage();
  const reviewer = await reviewerContext.newPage();
  try {
    await signIn(author, "author");
    await author
      .getByLabel("Title", { exact: true })
      .fill("Browser synthetic selector");
    await author
      .getByLabel("Question prompt")
      .fill("Synthetic workflow fixture: select Alpha.");
    await author.getByLabel("Option A", { exact: true }).fill("Alpha");
    await author.getByLabel("Option B", { exact: true }).fill("Beta");
    await author.getByLabel("Correct option").selectOption("A");
    await author
      .getByLabel("Hint 1", { exact: true })
      .fill("Read both labels before selecting.");
    await author
      .getByLabel("Worked solution", { exact: true })
      .fill("The requested label is Alpha (option A).");
    await author
      .getByLabel("Feedback and remediation")
      .fill("Read both labels again.");
    await author
      .getByLabel("Source and provenance")
      .fill("Original synthetic browser fixture");
    await author.getByLabel("Rights status").selectOption("ORIGINAL_KASOMA");
    await author
      .getByLabel("Rights evidence")
      .fill("Original fixture without third-party material");
    await author
      .getByLabel("Rights conditions")
      .fill("Synthetic test use only");
    await author
      .getByLabel("Change reason", { exact: true })
      .fill("Create synthetic review fixture");
    await author
      .getByRole("button", { name: "Save draft", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText("Version 1: DRAFT.");
    await author
      .getByLabel("Submission reason")
      .fill("Ready for independent review");
    await author
      .getByRole("button", { name: "Submit for review", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText(
      "Version 1: IN_REVIEW.",
    );
    await expect(
      author.getByRole("button", { name: "Approve", exact: true }),
    ).toBeDisabled();
    await signIn(reviewer, "reviewer");
    const queued = reviewer.getByRole("button", {
      name: "Browser synthetic selector — v1 · IN_REVIEW",
    });
    while (!(await queued.count())) {
      await reviewer
        .getByRole("button", { name: "Load more", exact: true })
        .click();
      await expect(reviewer.getByRole("status")).toHaveText(
        "More items loaded.",
      );
    }
    await reviewer
      .getByRole("button", {
        name: "Browser synthetic selector — v1 · IN_REVIEW",
      })
      .click();
    await expect(
      reviewer.getByRole("region", { name: "Authored hints" }),
    ).toContainText("Read both labels before selecting.");
    await reviewer
      .getByLabel("Review comments")
      .fill("Make remediation more explicit");
    await reviewer
      .getByRole("button", { name: "Return for correction" })
      .click();
    await expect(reviewer.getByRole("status")).toHaveText("Version 1: DRAFT.");
    await author.getByRole("button", { name: "Reload selected item" }).click();
    await author
      .getByLabel("Feedback and remediation")
      .fill("Read Alpha and Beta, then select the requested Alpha label.");
    await author
      .getByLabel("Change reason", { exact: true })
      .fill("Clarified synthetic remediation");
    await author
      .getByRole("button", { name: "Save draft", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText("Version 1: DRAFT.");
    await author
      .getByLabel("Submission reason")
      .fill("Addressed review comment");
    await author
      .getByRole("button", { name: "Submit for review", exact: true })
      .click();
    await expect(author.getByRole("status")).toHaveText(
      "Version 1: IN_REVIEW.",
    );
    await reviewer
      .getByRole("button", { name: "Reload selected item" })
      .click();
    await expect(
      reviewer
        .getByRole("group", { name: "Independent academic checklist" })
        .getByRole("checkbox"),
    ).toHaveCount(15);
    for (const checkbox of await reviewer
      .getByRole("group", { name: "Independent academic checklist" })
      .getByRole("checkbox")
      .all())
      await checkbox.check();
    await reviewer
      .getByLabel("Review comments")
      .fill("Synthetic checklist passed after correction");
    expect(
      (await new AxeBuilder({ page: reviewer }).analyze()).violations,
    ).toEqual([]);
    await reviewer
      .getByRole("button", { name: "Approve", exact: true })
      .focus();
    await reviewer.keyboard.press("Enter");
    await expect(reviewer.getByRole("status")).toHaveText(
      "Version 1: APPROVED.",
    );
    await reviewer
      .getByLabel("Retirement reason")
      .fill("Finish synthetic retirement test");
    await reviewer
      .getByRole("button", { name: "Retire version", exact: true })
      .click();
    await expect(reviewer.getByRole("status")).toHaveText(
      "Version 1: RETIRED.",
    );
    await author.getByRole("button", { name: "Reload selected item" }).click();
    await author
      .getByRole("button", { name: "Create next draft version" })
      .click();
    await expect(author.getByRole("status")).toHaveText("Version 2: DRAFT.");
  } finally {
    await authorContext.close();
    await reviewerContext.close();
  }
});

test("staff workspace denies anonymous access without exposing content", async ({
  page,
}) => {
  await page.goto("/admin/content");
  await expect(page.getByRole("status")).toHaveText(
    "Staff access required. Sign in with a provisioned account.",
  );
  await expect(page.getByRole("button", { name: "New draft" })).toHaveCount(0);
  await expect(page.getByText("Correct option:", { exact: false })).toHaveCount(
    0,
  );
});
