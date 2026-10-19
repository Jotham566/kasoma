import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-ID-001/003/004/005: adult profile, consent, withdrawal and logout", async ({
  page,
  context,
}, testInfo) => {
  await page.goto("/onboarding");
  await expect(page.getByRole("status")).toHaveText("Sign in to continue.");
  await expect(
    page.getByRole("button", { name: "Verify contact again", exact: true }),
  ).toHaveCount(0);
  await page.screenshot({
    path: testInfo.outputPath("signed-out-profile.png"),
    fullPage: true,
  });
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-adult@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  const verification = page.waitForResponse("**/api/v1/auth/otp/verify");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  expect(await (await verification).json()).toEqual({ authenticated: true });
  await expect(
    page.getByRole("button", { name: "Verify contact again", exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic adult");
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
  await expect(
    page.getByRole("link", { name: "Find your starting point", exact: true }),
  ).toBeVisible();
  const cookies = await context.cookies();
  expect(
    cookies
      .filter((cookie) => cookie.name.startsWith("kasoma_"))
      .every((cookie) => cookie.httpOnly && cookie.sameSite === "Strict"),
  ).toBeTruthy();
  expect(await page.evaluate(() => document.cookie)).not.toContain(
    "kasoma_access",
  );
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.reload();
  await expect(
    page.getByText(/^Required declarations are recorded\./),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Find your starting point", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Withdraw consent and assent" })
    .click();
  await expect(page.getByRole("status")).toHaveText(
    "Consent withdrawn. Learning access is paused.",
  );
  await expect(
    page.getByRole("link", { name: "Find your starting point", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Sign out all devices" }).click();
  await expect(page.getByRole("status")).toHaveText("Signed out.");
  await expect(
    page.getByRole("button", { name: "Verify contact again", exact: true }),
  ).toHaveCount(0);
});

test("FR-ID-003: minor remains blocked until distinct guardian consent and assent", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-minor@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic minor");
  await page.getByLabel("Date of birth").fill("2010-01-01");
  await page.getByLabel("Physics", { exact: true }).check();
  await page.getByRole("button", { name: "Save profile" }).click();
  await page.getByLabel("I separately assent to this synthetic test.").check();
  await page.getByRole("button", { name: "Record learner assent" }).click();
  await expect(
    page.getByText("Learning access is paused until", { exact: false }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Find your starting point", exact: true }),
  ).toHaveCount(0);
  await page
    .getByLabel("Guardian email or mobile number")
    .fill("e2e-guardian@example.invalid");
  await page.getByRole("button", { name: "Send guardian code" }).click();
  await page
    .getByLabel("Guardian name", { exact: true })
    .fill("Synthetic guardian");
  await page.getByLabel("Relationship to learner").fill("Parent");
  await page.getByLabel("Guardian code", { exact: true }).fill("246810");
  await page
    .getByLabel("I am the parent or guardian", { exact: false })
    .check();
  await page.getByRole("button", { name: "Record guardian consent" }).click();
  await expect(
    page.getByText(/^Required declarations are recorded\./),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Find your starting point", exact: true }),
  ).toBeVisible();
});

test("web rejects cross-origin mutations and recovers from offline requests", async ({
  page,
  request,
}) => {
  const response = await request.post("/api/v1/auth/otp/request", {
    headers: { Origin: "https://untrusted.invalid" },
    data: {},
  });
  expect(response.status()).toBe(403);
  let resumeCatalog!: () => void;
  const catalogGate = new Promise<void>((resolve) => {
    resumeCatalog = resolve;
  });
  await page.route("**/api/v1/curriculum/subjects", async (route) => {
    await catalogGate;
    await route.continue();
  });
  await page.goto("/onboarding");
  await expect(
    page.getByRole("button", { name: "Send code", exact: true }),
  ).toBeDisabled();
  resumeCatalog();
  await expect(page.getByRole("status")).toHaveText("Sign in to continue.");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("offline@example.invalid");
  await page.route("**/api/v1/auth/otp/request", (route) => route.abort());
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Check your connection");
  await page.unroute("**/api/v1/auth/otp/request");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await expect(
    page.getByLabel("Verification code", { exact: true }),
  ).toBeVisible();
});
