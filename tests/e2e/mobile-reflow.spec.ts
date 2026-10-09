import { expect, test, type Locator, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.use({ viewport: { width: 320, height: 640 }, hasTouch: true });

async function reflows(page: Page) {
  const dimensions = await page.evaluate(() => ({
    width: document.documentElement.clientWidth,
    content: Math.max(
      document.documentElement.scrollWidth,
      document.body.scrollWidth,
    ),
  }));
  expect(dimensions.width).toBe(320);
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.width);
}

async function touchTarget(target: Locator) {
  await expect(target).toBeVisible();
  const bounds = await target.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThanOrEqual(44);
  expect(bounds!.height).toBeGreaterThanOrEqual(44);
  await target.tap();
}

test("NFR-ACC-001/NFR-COMP-001: narrow touch journey reflows and retains saved learning", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e9-mobile@example.invalid");
  await reflows(page);
  await touchTarget(
    page.getByRole("button", { name: "Send code", exact: true }),
  );
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await touchTarget(page.getByRole("button", { name: "Verify and continue" }));
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic mobile learner");
  await page.getByLabel("Date of birth").fill("2000-01-01");
  await page.getByLabel("Mathematics", { exact: true }).check();
  await reflows(page);
  await touchTarget(page.getByRole("button", { name: "Save profile" }));
  await expect(page.getByRole("status")).toHaveText("Profile saved.");
  await page
    .getByLabel("I give my own consent for this synthetic test.")
    .check();
  await touchTarget(page.getByRole("button", { name: "Record my consent" }));
  await expect(
    page.getByText(/^Required declarations are recorded\./),
  ).toBeVisible();
  await reflows(page);

  await page.goto("/revise");
  await touchTarget(
    page.getByRole("button", { name: "Start five-question practice" }),
  );
  for (let index = 1; index <= 5; index++) {
    await expect(
      page.getByRole("heading", { name: `Question ${index} of 5` }),
    ).toBeVisible();
    if (index === 1)
      await page.screenshot({
        path: ".local/ui-review/practice-mobile.png",
        fullPage: true,
      });
    await reflows(page);
    await touchTarget(
      page.locator("label").filter({
        has: page.getByRole("radio", { name: "Alpha", exact: true }),
      }),
    );
    await touchTarget(page.getByRole("button", { name: "Submit answer" }));
    await expect(
      page.getByRole("heading", { name: "Answer saved" }),
    ).toBeVisible();
    await expect(
      page.getByText(`${index} of 5 answers saved`, { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByRole("progressbar", { name: "Saved answers" }),
    ).toHaveAttribute("value", String(index));
    await reflows(page);
    if (index === 1) {
      await touchTarget(
        page.getByRole("button", { name: "Show worked solution" }),
      );
      await expect(
        page.getByText("The requested label is Alpha, option A.", {
          exact: true,
        }),
      ).toBeVisible();
      await reflows(page);
      await page.reload();
      await expect(
        page.getByText("1 of 5 answers saved", { exact: true }),
      ).toBeVisible();
    }
    if (index < 5)
      await touchTarget(page.getByRole("button", { name: "Next question" }));
  }
  await expect(
    page.getByRole("heading", { name: "Practice complete" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await touchTarget(page.getByRole("link", { name: "Progress", exact: true }));
  await expect(page.getByRole("status")).toHaveText("Learning record loaded.");
  await reflows(page);
  await touchTarget(page.getByRole("link", { name: "History", exact: true }));
  await expect(
    page.getByText("Status: completed. 5 of 5 answers saved."),
  ).toBeVisible();
  await reflows(page);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});
