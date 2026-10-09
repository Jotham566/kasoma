import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-DIAG: saved answers survive lost acknowledgement and resume; results include uncertainty", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e5-diagnostic@example.invalid");
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
  await page.goto("/diagnostic");
  await page
    .getByRole("button", { name: "Start or resume diagnostic" })
    .click();
  await expect(
    page.getByRole("group", { name: "Question 1", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("progressbar", { name: "Saved answers" }),
  ).toHaveAttribute("max", "15");
  await page.screenshot({
    path: ".local/ui-review/diagnostic-desktop.png",
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.route(
    "**/api/v1/sessions/*/attempts",
    async (route) => {
      const response = await route.fetch();
      expect(response.status()).toBe(200);
      expect(await response.json()).toMatchObject({ status: "SAVED" });
      await route.abort("failed");
    },
    { times: 1 },
  );
  await page.getByRole("radio", { name: "Alpha", exact: true }).check();
  await page.getByRole("button", { name: "Save answer and continue" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Saved answers are safe",
  );
  await page.getByRole("button", { name: "Save answer and continue" }).click();
  await expect(
    page.getByText("1 of 15 answers saved", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("progressbar", { name: "Saved answers" }),
  ).toHaveAttribute("value", "1");
  await page.reload();
  await expect(
    page.getByRole("group", { name: "Question 2", exact: true }),
  ).toBeVisible();
  for (let index = 1; index < 15; index++) {
    await expect(page.getByText(/points|Estimate:/)).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "Show worked solution" }),
    ).toHaveCount(0);
    await page.getByRole("radio", { name: "Alpha", exact: true }).check();
    await page
      .getByRole("button", { name: "Save answer and continue" })
      .focus();
    await page.keyboard.press("Enter");
    await expect(
      page.getByText(`${index + 1} of 15 answers saved`, { exact: true }),
    ).toBeVisible();
  }
  await expect(
    page.getByRole("region", { name: "Diagnostic results" }),
  ).toBeVisible();
  await expect(page.getByText(/Evidence confidence:/).first()).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "What to do next" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByRole("link", { name: "Practise this topic" }).click();
  await expect(
    page.getByRole("button", { name: "Start five-question practice" }),
  ).toBeVisible();
});
