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

test("FR-ID-006: request without learning consent, recover receipt and independently claim review", async ({
  browser,
}) => {
  const learnerContext = await browser.newContext();
  const adminContext = await browser.newContext();
  try {
    const learner = await learnerContext.newPage();
    const admin = await adminContext.newPage();
    await login(learner, "privacy-learner@example.invalid");
    await learner.goto("/privacy");
    await expect(learner.getByRole("status")).toHaveText("Requests loaded.");
    await expect(
      learner.getByRole("button", { name: "Submit request" }),
    ).toBeDisabled();
    expect(
      (await new AxeBuilder({ page: learner }).analyze()).violations,
    ).toEqual([]);
    await learner
      .getByRole("checkbox", { name: "I confirm this request for my account." })
      .focus();
    await learner.keyboard.press("Space");
    let lost = false;
    await learner.route("**/api/v1/me/data-requests", async (route) => {
      if (route.request().method() === "POST" && !lost) {
        lost = true;
        const response = await route.fetch();
        expect(response.status()).toBe(201);
        await route.abort();
      } else await route.continue();
    });
    await learner.getByRole("button", { name: "Submit request" }).click();
    await expect(learner.getByRole("status")).toContainText(
      "Could not confirm the operation",
    );
    await learner.getByRole("button", { name: "Retry request" }).click();
    await expect(learner.getByRole("status")).toHaveText(
      "Request received. Export or deletion has not been completed.",
    );
    await expect(
      learner.getByRole("heading", { name: "Export request", exact: true }),
    ).toHaveCount(1);
    await learner.reload();
    await expect(
      learner.getByText("Queued for review", { exact: true }),
    ).toBeVisible();
    await learner
      .getByRole("radio", { name: "Request deletion of my data", exact: true })
      .check();
    await learner.getByRole("checkbox").check();
    await learner.getByRole("button", { name: "Submit request" }).click();
    await expect(
      learner.getByRole("heading", { name: "Deletion request", exact: true }),
    ).toBeVisible();
    const firstPage = await (
      await learner.request.get("/api/v1/me/data-requests?limit=1")
    ).json();
    expect(firstPage.data).toHaveLength(1);
    expect(firstPage.next_cursor).toBeTruthy();
    const secondPage = await (
      await learner.request.get(
        `/api/v1/me/data-requests?limit=1&cursor=${firstPage.next_cursor}`,
      )
    ).json();
    expect(secondPage.data).toHaveLength(1);
    expect(secondPage.data[0].id).not.toBe(firstPage.data[0].id);
    await learner.goto("/admin/data-requests");
    await expect(learner.getByRole("status")).toHaveText(
      "Administrator access is required.",
    );
    await expect(learner.getByRole("listitem")).toHaveCount(0);

    await login(admin, "e2e-content-privacy-admin@example.invalid");
    await admin.goto("/admin/data-requests");
    await expect(admin.getByRole("status")).toHaveText("Requests loaded.");
    expect(
      (await new AxeBuilder({ page: admin }).analyze()).violations,
    ).toEqual([]);
    const adminPage = await (
      await admin.request.get("/api/v1/admin/data-requests?limit=1")
    ).json();
    expect(adminPage.data).toHaveLength(1);
    expect(adminPage.next_cursor).toBeTruthy();
    let lostClaim = false;
    await admin.route(
      "**/api/v1/admin/data-requests/*/claim",
      async (route) => {
        if (!lostClaim) {
          lostClaim = true;
          const response = await route.fetch();
          expect(response.status()).toBe(200);
          await route.abort();
        } else await route.continue();
      },
    );
    const entry = admin.getByRole("listitem").filter({
      has: admin.getByRole("heading", {
        name: "Export request",
        exact: true,
      }),
    });
    await entry.getByRole("button", { name: "Claim for review" }).click();
    await expect(admin.getByRole("status")).toContainText(
      "Could not confirm the operation",
    );
    await admin.getByRole("button", { name: "Retry review" }).click();
    await expect(admin.getByRole("status")).toHaveText(
      "Review recorded. Fulfillment remains pending.",
    );
    await learner.goto("/privacy");
    await expect(learner.getByText("In review", { exact: true })).toBeVisible();
    await expect(
      learner.getByText("Queued for review", { exact: true }),
    ).toBeVisible();
  } finally {
    await Promise.allSettled([learnerContext.close(), adminContext.close()]);
  }
});
