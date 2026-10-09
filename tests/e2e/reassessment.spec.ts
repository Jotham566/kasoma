import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-GRD-008: unseen reassessment survives retry and preserves original feedback", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e4-reassessment@example.invalid");
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
  await expect(
    page.getByRole("heading", { name: "Answer saved", exact: true }),
  ).toBeVisible();
  const originalUrl = page.url();
  await page.route(
    "**/api/v1/attempts/*/reassessment",
    async (route) => {
      const saved = await route.fetch();
      expect(saved.status()).toBe(200);
      expect((await saved.json()).kind).toBe("REASSESSMENT");
      await route.abort("failed");
    },
    { times: 1 },
  );
  await page
    .getByRole("button", { name: "Try an unseen reassessment" })
    .click();
  await expect(page.getByRole("status")).toContainText("Check your connection");
  await page
    .getByRole("button", { name: "Try an unseen reassessment" })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Check your understanding",
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Question 1 of 1" }),
  ).toBeVisible();
  const childUrl = page.url();
  expect(childUrl).not.toBe(originalUrl);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Question 1 of 1" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Reviewed hints" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Show worked solution" }),
  ).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByRole("radio", { name: "Alpha", exact: true }).check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Practice complete" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Answer feedback" }),
  ).toContainText("1 of 1 points");
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Practice complete" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page
    .getByRole("button", { name: "Return to original practice" })
    .click();
  await expect(page).toHaveURL(originalUrl);
  await expect(
    page.getByRole("region", { name: "Answer feedback" }),
  ).toContainText("1 of 1 points");
  await page
    .getByRole("button", { name: "Try an unseen reassessment" })
    .click();
  await expect(page).toHaveURL(childUrl);
  await expect(
    page.getByRole("heading", { name: "Practice complete" }),
  ).toBeVisible();
});
