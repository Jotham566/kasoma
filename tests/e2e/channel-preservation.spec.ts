import { expect, test, type Page } from "@playwright/test";
import { createHmac, randomUUID } from "node:crypto";
import AxeBuilder from "@axe-core/playwright";

async function login(page: Page, email: string) {
  await page.goto("/onboarding");
  await page.getByLabel("Email or mobile number", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
}

test("FR-ID-006/FR-WA-006: exact minimized channel capture, stale version, retry and STOP", async ({
  browser,
  request,
  browserName,
}) => {
  const learnerContext = await browser.newContext();
  const adminContext = await browser.newContext();
  const learner = await learnerContext.newPage();
  const admin = await adminContext.newPage();
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
                    from: "256700000091",
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
  try {
    await login(
      learner,
      `channel-preservation-${randomUUID()}@example.invalid`,
    );
    await learner
      .getByLabel("Display name", { exact: true })
      .fill("Synthetic preservation learner");
    await learner.getByLabel("Date of birth").fill("2000-01-01");
    await learner.getByLabel("Mathematics", { exact: true }).check();
    await learner.getByRole("button", { name: "Save profile" }).click();
    await expect(learner.getByRole("status")).toHaveText("Profile saved.");
    await learner
      .getByLabel("I give my own consent for this synthetic test.")
      .check();
    await learner.getByRole("button", { name: "Record my consent" }).click();
    await expect(
      learner.getByText(/^Required declarations are recorded\./),
    ).toBeVisible();
    await learner.goto("/channels/whatsapp");
    await learner
      .getByRole("button", { name: "Refresh channel status" })
      .click();
    await expect(
      learner.getByText("NOT_LINKED", { exact: true }),
    ).toBeVisible();
    await learner.getByRole("button", { name: "Get a link code" }).click();
    await expect(learner.locator("code")).toHaveText(/^LINK [0-9A-F]{12}$/);
    await send(await learner.locator("code").innerText());
    await expect
      .poll(
        async () =>
          (
            await (
              await learner.request.get("/api/v1/channels/whatsapp/link")
            ).json()
          ).status,
      )
      .toBe("ACTIVE");
    const link = await (
      await learner.request.get("/api/v1/channels/whatsapp/link")
    ).json();
    await send("START");
    await learner.goto("/privacy");
    await learner
      .getByRole("radio", { name: "Request deletion of my data", exact: true })
      .check();
    await learner
      .getByRole("checkbox", { name: "I confirm this request for my account." })
      .check();
    await learner
      .getByRole("button", { name: "Submit request", exact: true })
      .click();
    await expect(
      learner.getByRole("heading", { name: "Deletion request", exact: true }),
    ).toBeVisible();
    const owned = await (
      await learner.request.get("/api/v1/me/data-requests")
    ).json();
    const target = owned.data.find(
      (row: { kind: string }) => row.kind === "DELETE",
    ).id;
    await login(admin, "e2e-content-preservation-admin@example.invalid");
    await admin.goto("/admin/data-requests");
    const entry = admin.getByRole("listitem").filter({
      has: admin.getByText(`Reference: ${target}`, { exact: true }),
    });
    await entry.getByRole("button", { name: "Claim for review" }).click();
    await expect(admin.getByRole("status")).toHaveText(
      "Review recorded. Fulfillment remains pending.",
    );
    await entry.getByRole("button", { name: "Manage record holds" }).click();
    const capture = entry.getByRole("region", {
      name: "Preserve an exact channel version",
    });
    await expect(capture).toBeVisible();
    const endpoint = `/api/v1/admin/data-requests/${target}/channel-preservations`;
    expect((await admin.request.get(endpoint)).status()).toBe(404);
    async function fill(kind: string) {
      await capture
        .getByLabel("Capture source", { exact: true })
        .selectOption(kind);
      await capture
        .getByLabel("Source link UUID", { exact: true })
        .fill(link.link_id);
      await capture
        .getByLabel("Source link revision", { exact: true })
        .fill(String(link.revision));
      await capture
        .getByLabel("Capture decision reference", { exact: true })
        .fill(randomUUID());
      await capture
        .getByLabel("Capture end date and time (device local time)", {
          exact: true,
        })
        .fill(new Date(Date.now() + 86400000).toISOString().slice(0, 16));
    }
    await fill("CHANNEL_LINK_SNAPSHOT");
    await capture.getByRole("button", { name: "Check source version" }).focus();
    await admin.keyboard.press("Enter");
    await expect(capture.getByRole("status")).toContainText(
      "Current source version checked.",
    );
    for (const control of await capture.getByRole("combobox").all()) {
      expect((await control.boundingBox())?.height).toBeGreaterThanOrEqual(44);
    }
    await capture.screenshot({
      path: `.local/ui-review/${browserName}-channel-preservation-desktop.png`,
    });
    await admin.setViewportSize({ width: 320, height: 740 });
    await admin.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    expect(
      await admin.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect(
      (await new AxeBuilder({ page: admin }).analyze()).violations,
    ).toEqual([]);
    for (const control of await capture.getByRole("combobox").all()) {
      expect((await control.boundingBox())?.height).toBeGreaterThanOrEqual(44);
    }
    await admin.screenshot({
      path: `.local/ui-review/${browserName}-channel-preservation-mobile.png`,
      fullPage: true,
    });
    await admin.evaluate(() => {
      document.documentElement.style.fontSize = "100%";
    });
    let lost = false;
    const keys: string[] = [];
    const bodies: string[] = [];
    const saved: { id: string; record_id: string }[] = [];
    await admin.route("**" + endpoint, async (route) => {
      keys.push(route.request().headers()["idempotency-key"]);
      bodies.push(route.request().postData()!);
      if (!lost) {
        lost = true;
        const response = await route.fetch();
        expect(response.status()).toBe(201);
        saved.push(await response.json());
        await route.abort();
      } else await route.continue();
    });
    await capture.getByRole("checkbox").check();
    await capture
      .getByRole("button", { name: "Capture selected version" })
      .click();
    await expect(capture.getByRole("status")).toContainText(
      "Could not confirm the operation.",
    );
    await capture.getByRole("button", { name: "Retry same capture" }).click();
    await expect(capture.getByRole("status")).toContainText(
      "Snapshot and finite decision saved.",
    );
    expect(keys).toHaveLength(2);
    expect(keys[0]).toBe(keys[1]);
    expect(bodies[0]).toBe(bodies[1]);
    expect(saved[0].record_id).not.toBe(link.link_id);
    await admin.unroute("**" + endpoint);
    await fill("CHANNEL_CONVERSATION_SNAPSHOT");
    const inspected = admin.waitForResponse("**" + endpoint + "/inspect");
    await capture.getByRole("button", { name: "Check source version" }).click();
    const oldVersion = (await (await inspected).json()).source_version;
    await expect(capture.getByRole("status")).toContainText(
      "Current source version checked.",
    );
    await send("START");
    await expect
      .poll(async () => {
        const response = await admin.request.post(endpoint + "/inspect", {
          headers: { Origin: "http://127.0.0.1:13000" },
          data: {
            source_kind: "CHANNEL_CONVERSATION_SNAPSHOT",
            source_link_id: link.link_id,
            link_revision: link.revision,
          },
        });
        expect(response.status()).toBe(200);
        return (await response.json()).source_version;
      })
      .not.toBe(oldVersion);
    await capture.getByRole("checkbox").check();
    await capture
      .getByRole("button", { name: "Capture selected version" })
      .click();
    await expect(capture.getByRole("status")).toContainText(
      "The source or decision could not be accepted.",
    );
    await expect(
      capture.getByRole("button", { name: "Capture selected version" }),
    ).toBeDisabled();
    await capture.getByRole("button", { name: "Check source version" }).click();
    await expect(capture.getByRole("status")).toContainText(
      "Current source version checked.",
    );
    await capture.getByRole("checkbox").check();
    const accepted = admin.waitForResponse("**" + endpoint);
    await capture
      .getByRole("button", { name: "Capture selected version" })
      .click();
    const second = await accepted;
    expect(second.status()).toBe(201);
    saved.push(await second.json());
    await expect(capture.getByRole("status")).toContainText(
      "Snapshot and finite decision saved.",
    );
    await send("STOP");
    await expect
      .poll(
        async () =>
          (
            await (
              await learner.request.get("/api/v1/channels/whatsapp/link")
            ).json()
          ).status,
      )
      .toBe("STOPPED");
    await learner.goto("/onboarding");
    await learner
      .getByRole("button", { name: "Withdraw consent and assent" })
      .click();
    await expect(learner.getByRole("status")).toHaveText(
      "Consent withdrawn. Learning access is paused.",
    );
    expect(
      (
        await (
          await learner.request.get("/api/v1/channels/whatsapp/link")
        ).json()
      ).status,
    ).toBe("STOPPED");
    for (const snapshot of saved) {
      await expect(
        entry.getByText(snapshot.record_id, { exact: false }),
      ).toBeVisible();
      await entry
        .getByRole("button", {
          name: `Release hold ${snapshot.id}`,
          exact: true,
        })
        .click();
      const release = entry.getByRole("group", {
        name: `Release hold ${snapshot.id}`,
        exact: true,
      });
      await release.getByLabel("Release decision reference").fill(randomUUID());
      await release.getByRole("checkbox").check();
      await release
        .getByRole("button", { name: "Confirm release", exact: true })
        .click();
      await expect(
        entry.getByRole("button", {
          name: `Release hold ${snapshot.id}`,
          exact: true,
        }),
      ).toHaveCount(0);
    }
  } finally {
    await learnerContext.close();
    await adminContext.close();
  }
});
