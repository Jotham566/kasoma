import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-REV-001/006: explained recommendation, lost start acknowledgement and durable practice", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e5-recommendation@example.invalid");
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
    page.getByText("Required declarations are recorded.", { exact: false }),
  ).toBeVisible();
  await page.goto("/");
  const card = page.getByRole("region", { name: "Recommended practice" });
  await expect(card.getByText(/gather more evidence/i).first()).toBeVisible();
  await expect(card.getByText(/About .* minutes/)).toBeVisible();
  await expect(
    card.getByRole("link", {
      name: "Gather broader evidence with a diagnostic",
    }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.route(
    "**/api/v1/revision-sessions",
    async (route) => {
      const result = await route.fetch();
      expect(result.status()).toBe(201);
      expect((await result.json()).recommendation_reason).toBeTruthy();
      await route.abort("failed");
    },
    { times: 1 },
  );
  await card
    .getByRole("button", { name: "Start recommended practice" })
    .click();
  await expect(card.getByRole("status")).toContainText(
    "Saved sessions are safe",
  );
  await card.getByRole("button", { name: "Refresh recommendation" }).click();
  await card
    .getByRole("button", { name: "Start recommended practice" })
    .focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Question 1 of 5" }),
  ).toBeVisible();
  const sessionUrl = page.url();
  for (let index = 0; index < 5; index++) {
    await page.getByRole("radio", { name: "Alpha", exact: true }).check();
    await page
      .getByRole("button", { name: "Submit answer", exact: true })
      .click();
    await expect(
      page.getByText(`${index + 1} of 5 answers saved`, { exact: true }),
    ).toBeVisible();
    if (index === 0) {
      await page.reload();
      expect(page.url()).toBe(sessionUrl);
      await expect(
        page.getByText("1 of 5 answers saved", { exact: true }),
      ).toBeVisible();
    }
    if (index < 4)
      await page.getByRole("button", { name: "Next question" }).click();
  }
  await expect(
    page.getByRole("heading", { name: "Practice complete" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.goto("/progress");
  await expect(page.getByRole("status")).toHaveText("Learning record loaded.");
  await expect(
    page
      .getByRole("region", { name: "Subject progress" })
      .getByText(/5 recorded answers/),
  ).toBeVisible();
  await expect(page.getByText(/Evidence confidence:/).first()).toBeVisible();
  await page.getByRole("link", { name: "History", exact: true }).click();
  await expect(
    page.getByText("Status: completed. 5 of 5 answers saved."),
  ).toBeVisible();
  await page.getByRole("link", { name: "Review session" }).click();
  await expect(
    page.getByRole("heading", { name: "Practice complete" }),
  ).toBeVisible();
});
