import { expect, test, type Page } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import AxeBuilder from "@axe-core/playwright";

async function login(page: Page, email: string) {
  await page.goto("/onboarding");
  await page.getByLabel("Email or mobile number", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
}

test("FR-ID-006: background command replay, explicit status and native frozen attachment", async ({
  page,
}) => {
  await page.addInitScript(() => {
    URL.createObjectURL = () => {
      throw new Error("Background exports must not use a browser Blob");
    };
  });
  await login(page, `background-export-${randomUUID()}@example.invalid`);
  await page.goto("/privacy");
  await expect(page.getByRole("status")).toHaveText("Requests loaded.");
  await page
    .getByRole("checkbox", { name: "I confirm this request for my account." })
    .check();
  await page
    .getByRole("button", { name: "Submit request", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Export request", exact: true }),
  ).toBeVisible();
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: ".local/ui-review/privacy-mobile.png",
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  let dropped = false;
  const keys: string[] = [];
  await page.route("**/api/v1/me/data-requests/*/export-job", async (route) => {
    if (route.request().method() === "POST") {
      keys.push(route.request().headers()["idempotency-key"]);
      if (!dropped) {
        dropped = true;
        expect((await route.fetch()).status()).toBe(202);
        await route.abort();
        return;
      }
    }
    await route.continue();
  });
  await page
    .getByRole("button", { name: "Prepare background export", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText(
    "Could not confirm the operation",
  );
  await page
    .getByRole("button", { name: "Retry background command", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText(
    "Background command confirmed",
  );
  expect(keys).toHaveLength(2);
  expect(keys[0]).toBe(keys[1]);
  await expect
    .poll(
      async () => {
        await page
          .getByRole("button", { name: "Check background status", exact: true })
          .click();
        await expect(page.getByRole("status")).toHaveText(
          "Background export status refreshed.",
        );
        return await page
          .getByRole("link", { name: "Save background export", exact: true })
          .count();
      },
      { intervals: [500], timeout: 10000 },
    )
    .toBe(1);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const save = async () => {
    const event = page.waitForEvent("download");
    await page
      .getByRole("link", { name: "Save background export", exact: true })
      .click();
    const download = await event;
    expect(await download.failure()).toBeNull();
    expect(download.suggestedFilename()).toMatch(
      /^kasoma-export-[0-9a-f-]+\.json$/,
    );
    return readFile((await download.path())!);
  };
  const original = await save();
  expect(JSON.parse(original.toString()).format_version).toBe(
    "kasoma-personal-export-v1",
  );
  await page.reload();
  await expect(page.getByRole("status")).toHaveText("Requests loaded.");
  await page
    .getByRole("button", { name: "Check background status", exact: true })
    .click();
  await expect(
    page.getByRole("link", { name: "Save background export", exact: true }),
  ).toBeVisible();
  expect(await save()).toEqual(original);
  let unexpectedDownloads = 0;
  const recordDownload = () => unexpectedDownloads++;
  page.on("download", recordDownload);
  const jobRoute = "**/api/v1/me/data-requests/*/export-job";
  let expired = true;
  const unavailable = async (route: import("@playwright/test").Route) => {
    if (expired) {
      const response = await route.fetch();
      await route.fulfill({
        response,
        json: { ...(await response.json()), status: "EXPIRED" },
      });
      return;
    }
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: { code: "SERVICE_UNAVAILABLE", message: "synthetic failure" },
      }),
    });
  };
  await page.route(jobRoute, unavailable);
  await page
    .getByRole("link", { name: "Save background export", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveText(
    "This copy has expired. Submit a new export request.",
  );
  expect(unexpectedDownloads).toBe(0);
  expired = false;
  await page
    .getByRole("link", { name: "Save background export", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveText(
    "The download could not start. Check your connection and try again. Your request is retained.",
  );
  expect(unexpectedDownloads).toBe(0);
  page.off("download", recordDownload);
  await page.unroute(jobRoute, unavailable);
  expect(await save()).toEqual(original);
  await expect(page.getByRole("main").getByRole("alert")).toHaveCount(0);
  await page.context().clearCookies();
  await page
    .getByRole("link", { name: "Save background export", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveText(
    "Sign in again to verify your identity before downloading your export.",
  );
});

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
    const owned = [firstPage.data[0], secondPage.data[0]];
    const exportReference = owned.find((row) => row.kind === "EXPORT").id;
    const deletionReference = owned.find((row) => row.kind === "DELETE").id;
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
      has: admin.getByText(`Reference: ${exportReference}`, { exact: true }),
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
    let lostExport = false;
    await learner.route(
      "**/api/v1/me/data-requests/*/export",
      async (route) => {
        if (!lostExport) {
          lostExport = true;
          const response = await route.fetch();
          expect(response.status()).toBe(200);
          expect(response.headers()["cache-control"]).toBe("no-store");
          expect(response.headers()["content-disposition"]).toContain(
            "attachment;",
          );
          await route.abort();
        } else await route.continue();
      },
    );
    await learner
      .getByRole("button", { name: "Download export", exact: true })
      .click();
    await expect(learner.getByRole("status")).toContainText(
      "Could not confirm the operation",
    );
    const downloaded = learner.waitForEvent("download");
    await learner
      .getByRole("button", { name: "Retry download", exact: true })
      .click();
    const file = await downloaded;
    expect(file.suggestedFilename()).toMatch(/^kasoma-export-.*\.json$/);
    const payload = JSON.parse(await readFile((await file.path())!, "utf8"));
    expect(payload.format_version).toBe("kasoma-personal-export-v1");
    expect(payload.records.identifiers[0].value).toBe(
      "privacy-learner@example.invalid",
    );
    expect(payload.exclusions.length).toBeGreaterThan(0);
    await expect(learner.getByRole("status")).toHaveText(
      "Export made available. The same copy is available for 24 hours.",
    );
    await expect(
      learner.getByText("Export made available", { exact: true }),
    ).toBeVisible();
    expect(
      (await new AxeBuilder({ page: learner }).analyze()).violations,
    ).toEqual([]);
    await admin.reload();
    await expect(
      entry.getByText("Export made available", { exact: true }),
    ).toBeVisible();
    await expect(
      admin.getByRole("button", { name: "Download export" }),
    ).toHaveCount(0);
    const deletion = admin.getByRole("listitem").filter({
      has: admin.getByText(`Reference: ${deletionReference}`, { exact: true }),
    });
    await expect(
      deletion.getByRole("button", { name: "Preview deletion impact" }),
    ).toHaveCount(0);
    await deletion.getByRole("button", { name: "Claim for review" }).click();
    await expect(admin.getByRole("status")).toHaveText(
      "Review recorded. Fulfillment remains pending.",
    );
    let lostPreview = false;
    await admin.route(
      "**/api/v1/admin/data-requests/*/deletion-preview",
      async (route) => {
        if (!lostPreview) {
          lostPreview = true;
          const response = await route.fetch();
          expect(response.status()).toBe(200);
          expect((await response.json()).execution_enabled).toBe(false);
          await route.abort();
        } else await route.continue();
      },
    );
    await deletion
      .getByRole("button", { name: "Preview deletion impact" })
      .click();
    await expect(admin.getByRole("status")).toContainText(
      "Could not confirm the operation",
    );
    await expect(
      admin.getByRole("heading", { name: "Deletion impact preview" }),
    ).toHaveCount(0);
    await deletion
      .getByRole("button", { name: "Preview deletion impact" })
      .click();
    await expect(admin.getByRole("status")).toHaveText(
      "Deletion impact loaded. No account data was changed.",
    );
    await expect(
      admin.getByText(
        "Legal-hold coverage is incomplete; other records still require review.",
        {
          exact: true,
        },
      ),
    ).toBeVisible();
    await admin
      .getByText("Record counts and retention", { exact: true })
      .focus();
    await admin.keyboard.press("Enter");
    await expect(admin.getByRole("table")).toBeVisible();
    expect(
      (await new AxeBuilder({ page: admin }).analyze()).violations,
    ).toEqual([]);
    const holds = deletion.getByRole("region", { name: "Record legal holds" });
    await holds.getByRole("button", { name: "Manage record holds" }).click();
    await expect(holds.getByRole("status")).toHaveText("Holds loaded.");
    await expect(holds.getByLabel("Record type").locator("option")).toHaveText([
      "Data request",
      "Consent",
      "Attempt",
      "Content flag",
      "Grade (attempt reference)",
      "Mastery evidence",
      "Mastery history",
      "Flag history",
      "Grading history",
      "Data request review (request reference)",
    ]);
    await expect(
      holds.getByText(/For a grade, use its attempt reference/),
    ).toBeVisible();
    await holds
      .getByLabel("Decision reference", { exact: true })
      .fill(randomUUID());
    // The browser context defaults to UTC; the form explicitly labels device time.
    await holds
      .getByLabel("Hold ends (your device time)")
      .fill(new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 16));
    await holds
      .getByRole("checkbox", {
        name: "I confirm an authorized preservation decision for this record and period.",
      })
      .check();
    let lostHold = false;
    await admin.route(
      "**/api/v1/admin/data-requests/*/holds",
      async (route) => {
        if (route.request().method() === "POST" && !lostHold) {
          lostHold = true;
          expect((await route.fetch()).status()).toBe(201);
          await route.abort();
        } else await route.continue();
      },
    );
    await holds
      .getByRole("button", { name: "Create hold", exact: true })
      .click();
    await expect(holds.getByRole("status")).toContainText(
      "Could not confirm the operation",
    );
    await expect(
      holds.getByLabel("Record reference", { exact: true }),
    ).toBeDisabled();
    await holds.getByRole("button", { name: "Retry hold operation" }).click();
    await expect(holds.getByRole("status")).toHaveText(
      "Hold decision recorded. Deletion remains disabled.",
    );
    await expect(holds.getByRole("listitem")).toHaveCount(1);
    await holds.getByLabel("Record type").selectOption("DATA_REQUEST_REVIEW");
    await expect(
      holds.getByRole("checkbox", {
        name: "I confirm an authorized preservation decision for this record and period.",
      }),
    ).not.toBeChecked();
    await holds
      .getByLabel("Hold ends (your device time)")
      .fill(new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 16));
    await holds
      .getByRole("checkbox", {
        name: "I confirm an authorized preservation decision for this record and period.",
      })
      .check();
    await holds
      .getByLabel("Decision reference", { exact: true })
      .fill(randomUUID());
    await holds
      .getByRole("button", { name: "Create hold", exact: true })
      .click();
    await expect(holds.getByRole("listitem")).toHaveCount(2);
    const requestId = await holds
      .getByLabel("Record reference", { exact: true })
      .inputValue();
    const holdPage = await (
      await admin.request.get(
        `/api/v1/admin/data-requests/${requestId}/holds?limit=1`,
      )
    ).json();
    expect(holdPage.data).toHaveLength(1);
    expect(holdPage.next_cursor).toBeTruthy();
    const holdNext = await (
      await admin.request.get(
        `/api/v1/admin/data-requests/${requestId}/holds?limit=1&cursor=${holdPage.next_cursor}`,
      )
    ).json();
    expect(holdNext.data).toHaveLength(1);
    expect(holdNext.data[0].id).not.toBe(holdPage.data[0].id);
    expect(
      [holdPage.data[0].record_type, holdNext.data[0].record_type].sort(),
    ).toEqual(["DATA_REQUEST", "DATA_REQUEST_REVIEW"]);
    await holds
      .getByRole("button", { name: /^Release hold / })
      .first()
      .click();
    await holds.getByLabel("Release decision reference").fill(randomUUID());
    await holds
      .getByRole("checkbox", {
        name: "I confirm an authorized release decision for this hold.",
      })
      .check();
    let lostRelease = false;
    await admin.route(
      "**/api/v1/admin/data-requests/*/holds/*/release",
      async (route) => {
        if (!lostRelease) {
          lostRelease = true;
          expect((await route.fetch()).status()).toBe(200);
          await route.abort();
        } else await route.continue();
      },
    );
    await holds
      .getByRole("button", { name: "Confirm release", exact: true })
      .click();
    await expect(holds.getByRole("status")).toContainText(
      "Could not confirm the operation",
    );
    await holds.getByRole("button", { name: "Retry hold operation" }).click();
    await expect(holds.getByText(/— RELEASED/)).toHaveCount(1);
    await deletion
      .getByRole("button", { name: "Preview deletion impact" })
      .click();
    await expect(
      admin.getByText("Active registered holds: 1", { exact: true }),
    ).toBeVisible();
    expect(
      (await new AxeBuilder({ page: admin }).analyze()).violations,
    ).toEqual([]);
    await admin.reload();
    await expect(admin.getByRole("status")).toHaveText("Requests loaded.");
    await expect(
      admin.getByRole("heading", { name: "Deletion impact preview" }),
    ).toHaveCount(0);
    await learner.reload();
    await expect(learner.getByText("In review", { exact: true })).toBeVisible();
    await expect(
      learner.getByRole("button", { name: "Preview deletion impact" }),
    ).toHaveCount(0);
  } finally {
    await Promise.allSettled([learnerContext.close(), adminContext.close()]);
  }
});
