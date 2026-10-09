import { expect, test } from "@playwright/test";
import { createHmac, randomUUID } from "node:crypto";
import AxeBuilder from "@axe-core/playwright";

test("FR-WA-001/004/006: consent-gated code, signed local linking, STOP and unlink retry", async ({
  page,
  request,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-channel@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic channel learner");
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
  await page.goto("/channels/whatsapp");
  await page.getByRole("button", { name: "Refresh channel status" }).click();
  await expect(page.getByText("NOT_LINKED", { exact: true })).toBeVisible();
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: ".local/ui-review/channel-mobile.png",
    fullPage: true,
  });
  let lostCode = false;
  await page.route("**/api/v1/channels/whatsapp/link-code", async (route) => {
    if (!lostCode) {
      lostCode = true;
      expect((await route.fetch()).status()).toBe(201);
      await route.abort();
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Get a link code" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Retry to recover the same code.",
  );
  await page.getByRole("button", { name: "Retry code request" }).click();
  const instruction = await page.locator("code").innerText();
  expect(instruction).toMatch(/^LINK [0-9A-F]{12}$/);
  const expiry = page.getByRole("region", { name: "One-time link code" });
  await expect(expiry).toContainText("(Kampala). Keep this code private.");
  const timestamp = await expiry.locator("time").getAttribute("datetime");
  expect(timestamp).toBeTruthy();
  const expected = new Intl.DateTimeFormat("en-UG", {
    timeZone: "Africa/Kampala",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(timestamp!));
  await expect(expiry.locator("time")).toHaveText(expected);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  async function send(body: string) {
    const raw = JSON.stringify({
      object: "whatsapp_business_account",
      entry: [
        {
          id: "synthetic-business",
          changes: [
            {
              field: "messages",
              value: {
                messaging_product: "whatsapp",
                metadata: { phone_number_id: "synthetic-phone" },
                messages: [
                  {
                    id: "wamid." + randomUUID(),
                    from: "256700000090",
                    timestamp: String(Math.floor(Date.now() / 1000)),
                    type: "text",
                    text: { body },
                  },
                ],
              },
            },
          ],
        },
      ],
    });
    const signature = createHmac(
      "sha256",
      "synthetic-e2e-channel-signing-000000000",
    )
      .update(raw)
      .digest("hex");
    expect(
      (
        await request.post("http://127.0.0.1:18000/api/v1/webhooks/whatsapp", {
          data: raw,
          headers: {
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=" + signature,
          },
        })
      ).status(),
    ).toBe(200);
  }
  await send(instruction);
  await expect
    .poll(async () => {
      await page
        .getByRole("button", { name: "Refresh channel status" })
        .click();
      return page.locator("strong").innerText();
    })
    .toBe("ACTIVE");
  await expect(page.locator("code")).toHaveCount(0);
  await send("STOP");
  await expect
    .poll(async () => {
      await page
        .getByRole("button", { name: "Refresh channel status" })
        .click();
      return page.locator("strong").innerText();
    })
    .toBe("STOPPED");
  await expect
    .poll(async () => {
      const response = await page.request.get("/api/v1/channels/whatsapp/link");
      return (await response.json()).revision;
    })
    .toBe(2);
  await page.getByRole("button", { name: "Refresh channel status" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Channel status refreshed.",
  );
  let lostUnlink = false;
  await page.route("**/api/v1/channels/whatsapp/link", async (route) => {
    if (route.request().method() === "DELETE" && !lostUnlink) {
      lostUnlink = true;
      expect((await route.fetch()).status()).toBe(200);
      await route.abort();
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Unlink and cancel codes" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Retry the same request.",
  );
  await page.getByRole("button", { name: "Retry unlink" }).click();
  await expect(page.getByText("UNLINKED", { exact: true })).toBeVisible();
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
});
