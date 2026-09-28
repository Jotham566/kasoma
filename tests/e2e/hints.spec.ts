import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-GRD-006: reviewed hints survive lost acknowledgement and preserve grading", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e4-hints@example.invalid");
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
  await page.goto("/revise");
  await page
    .getByRole("button", { name: "Start five-question practice" })
    .click();
  const hints = page.getByRole("region", { name: "Reviewed hints" });
  // All seed questions have reviewed hints; another browser test may publish a legacy item.
  for (
    let i = 0;
    i < 4 &&
    (await hints
      .getByText("No more reviewed hints are available for this question.")
      .isVisible());
    i++
  ) {
    await page.getByRole("radio", { name: "Alpha", exact: true }).check();
    await page
      .getByRole("button", { name: "Submit answer", exact: true })
      .click();
    await page.getByRole("button", { name: "Next question" }).click();
  }
  await expect(
    hints.getByRole("button", { name: "Show next reviewed hint" }),
  ).toBeVisible();
  await page.route(
    "**/api/v1/sessions/*/items/*/hint",
    async (route) => {
      const result = await route.fetch();
      expect(result.status()).toBe(200);
      expect((await result.json()).hints).toHaveLength(1);
      await route.abort("failed");
    },
    { times: 1 },
  );
  await hints.getByRole("button", { name: "Show next reviewed hint" }).click();
  await expect(hints.getByText(/Saved hint usage is retained/)).toBeVisible();
  await hints.getByRole("button", { name: "Show next reviewed hint" }).click();
  await expect(hints.getByText(/^Hint 1:/)).toBeVisible();
  await expect(hints.getByText(/^Hint 2:/)).toHaveCount(0);
  await page.reload();
  await expect(hints.getByText(/^Hint 1:/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Show worked solution" }),
  ).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByRole("radio", { name: "Alpha", exact: true }).check();
  const submitted = page.waitForResponse(
    (response) =>
      response.url().endsWith("/attempts") &&
      response.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  expect(await (await submitted).json()).toMatchObject({
    score: 1,
    hint_count: 1,
    highest_hint_level: 1,
  });
  await expect(
    hints.getByText(/Your submitted score and evidence stay unchanged/),
  ).toBeVisible();
  await hints.getByRole("button", { name: "Show next reviewed hint" }).focus();
  await page.keyboard.press("Enter");
  await expect(hints.getByText(/^Hint 2:/)).toBeVisible();
  await page.reload();
  await expect(hints.getByText(/^Hint 2:/)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});
