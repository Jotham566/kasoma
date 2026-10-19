import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-OPS-002/003: reviewed warning edits survive lost acknowledgement and reject stale writes", async ({
  page,
}, info) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-content-configuration-admin@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
  await page.goto("/admin/operations");
  await page.getByRole("link", { name: "Review warning settings" }).click();
  await page.getByRole("button", { name: "Load current settings" }).click();
  await expect(
    page.getByRole("region", { name: "Current warning settings" }),
  ).toContainText("revision 0");
  await page.getByLabel("New threshold (imports)").fill("2");
  await page.getByLabel("Audit reason").selectOption("REDUCE_NOISE");
  let originalKey = "";
  let originalBody = "";
  let requests = 0;
  await page.route(
    "**/api/v1/admin/configuration/failed_imports",
    async (route) => {
      requests++;
      const request = route.request();
      const key = request.headers()["idempotency-key"];
      if (requests === 1) {
        originalKey = key;
        originalBody = request.postData()!;
      } else {
        expect(key).toBe(originalKey);
        expect(request.postData()).toBe(originalBody);
      }
      // Only the isolated fake-provider API is reached. Withhold transport diagnostics
      // because Playwright errors may contain authentication headers.
      let committed;
      try {
        committed = await route.fetch({ maxRetries: 1, maxRedirects: 0 });
      } catch {
        throw new Error(
          "Synthetic configuration interception unavailable; diagnostics withheld.",
        );
      }
      expect(committed.status()).toBe(200);
      if (requests === 1) await route.abort("failed");
      else await route.fulfill({ response: committed });
    },
  );
  await page.getByRole("button", { name: "Save reviewed threshold" }).click();
  await expect(page.getByRole("status")).toContainText(
    "save outcome unconfirmed",
  );
  await expect(page.getByLabel("Setting", { exact: true })).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Load current settings" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Retry same change" }).click();
  await expect(page.getByRole("status")).toContainText(
    "revision 1 (confirmed retry)",
  );
  expect(requests).toBe(2);
  await page.unroute("**/api/v1/admin/configuration/failed_imports");
  await page.getByRole("button", { name: "Load current settings" }).click();
  await expect(page.getByLabel("New threshold (imports)")).toHaveValue("2");

  // An independent administrator command advances the version after this tab loaded.
  const current = await page.request.get("/api/v1/admin/configuration");
  expect(current.status()).toBe(200);
  const snapshot = await current.json();
  const concurrent = await page.request.patch(
    "/api/v1/admin/configuration/failed_imports",
    {
      headers: {
        Origin: "http://127.0.0.1:13000",
        "Idempotency-Key": crypto.randomUUID(),
      },
      data: {
        version: snapshot.version,
        value: 3,
        reason: "REVIEWED_BASELINE",
      },
    },
  );
  expect(concurrent.status()).toBe(200);
  await page.getByLabel("New threshold (imports)").fill("4");
  await page.getByLabel("Audit reason").selectOption("REDUCE_NOISE");
  await page.getByRole("button", { name: "Save reviewed threshold" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Configuration conflict",
  );
  await expect(
    page.getByRole("button", { name: "Save reviewed threshold" }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Load current settings" }).click();
  await expect(page.getByLabel("New threshold (imports)")).toHaveValue("3");
  await page.setViewportSize({ width: 320, height: 740 });
  await page.addStyleTag({ content: "html { font-size: 200%; }" });
  await page.evaluate(
    () =>
      new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve())),
      ),
  );
  const layout = await page.evaluate(() => ({
    fits: document.documentElement.scrollWidth <= innerWidth,
    scroll: document.documentElement.scrollWidth,
    viewport: innerWidth,
    overflow: Array.from(document.querySelectorAll("body *"))
      .filter((element) => {
        const box = element.getBoundingClientRect();
        return box.width > 0 && (box.right > innerWidth + 1 || box.left < -1);
      })
      .slice(0, 12)
      .map((element) => ({
        tag: element.tagName,
        id: element.id,
        classes: element.className,
        left: element.getBoundingClientRect().left,
        width: element.getBoundingClientRect().width,
      })),
  }));
  await page.screenshot({
    path: `.local/ui-review/configuration-layout-${info.project.use.browserName}.png`,
    fullPage: true,
  });
  expect(layout.fits, JSON.stringify(layout)).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: `.local/ui-review/configuration-${info.project.use.browserName}.png`,
    fullPage: true,
  });
  await page.context().setOffline(true);
  await page.getByRole("button", { name: "Load current settings" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Connection interrupted",
  );
  await expect(
    page.getByRole("region", { name: "Current warning settings" }),
  ).toHaveCount(0);
  await page.context().setOffline(false);
  await page.getByRole("button", { name: "Load current settings" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByLabel("New threshold (imports)")).toHaveValue("3");
});
