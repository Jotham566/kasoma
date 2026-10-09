import { expect, test } from "@playwright/test";
import { randomUUID } from "node:crypto";
import { readFile } from "node:fs/promises";

for (const fault of ["stall", "corrupt"] as const) {
  test(`FR-ID-006: ${fault} mid-transfer cannot save a successful export; frozen retry works`, async ({
    page,
  }) => {
    const request = page.request;
    const headers = { Origin: "http://127.0.0.1:13000" };
    const challenge = await request.post("/api/v1/auth/otp/request", {
      headers,
      data: {
        identifier: `export-${fault}-${randomUUID()}@example.invalid`,
        device_id: randomUUID(),
      },
    });
    expect(challenge.status()).toBe(202);
    expect(
      (
        await request.post("/api/v1/auth/otp/verify", {
          headers,
          data: {
            challenge_id: (await challenge.json()).challenge_id,
            code: "246810",
          },
        })
      ).ok(),
    ).toBeTruthy();
    const created = await request.post("/api/v1/me/data-requests", {
      headers: { ...headers, "Idempotency-Key": randomUUID() },
      data: { kind: "EXPORT", affirmative: true },
    });
    expect(created.status()).toBe(201);
    const target = (await created.json()).id;
    const path = `/api/v1/me/data-requests/${target}`;
    // These routes exist only in scripts.e2e_api's isolated synthetic database process.
    // They are not gateway routes and are absent from production images and API contracts.
    const fixture = `http://127.0.0.1:18000/__fixture/exports/${target}`;
    expect((await request.post(`${fixture}/history`)).ok()).toBeTruthy();
    expect(
      (
        await request.post(path + "/export-job", {
          headers: { ...headers, "Idempotency-Key": randomUUID() },
          data: {},
        })
      ).status(),
    ).toBe(202);
    await expect
      .poll(
        async () =>
          (await (await request.get(path + "/export-job")).json()).status,
      )
      .toBe("READY");
    const ready = await (await request.get(path + "/export-job")).json();
    expect(ready.size_bytes).toBeGreaterThan(2 * 65536);
    const original = await (await request.get(path + "/export-file")).body();
    expect(original.length).toBe(ready.size_bytes);
    expect(JSON.parse(original.toString()).request_id).toBe(target);
    await page.goto("/privacy");
    await expect(page.getByRole("status")).toHaveText("Requests loaded.");
    await page
      .getByRole("button", { name: "Check background status", exact: true })
      .click();
    const save = page.getByRole("link", {
      name: "Save background export",
      exact: true,
    });
    await expect(save).toBeVisible();
    expect((await request.post(`${fixture}/fault/${fault}`)).ok()).toBeTruthy();
    const started = page.waitForEvent("download");
    await save.click();
    const failed = await started;
    if (fault === "stall") {
      await expect
        .poll(
          async () =>
            (await (await request.get(`${fixture}/observations`)).json()).reads,
        )
        .toBeGreaterThanOrEqual(2);
      await failed.cancel();
    }
    expect(await failed.failure()).toBeTruthy();
    await expect
      .poll(
        async () =>
          (await (await request.get(`${fixture}/observations`)).json()).closed,
      )
      .toBeGreaterThanOrEqual(1);
    expect(
      (await (await request.get(path + "/export-job")).json()).status,
    ).toBe("READY");
    expect((await request.post(`${fixture}/fault/normal`)).ok()).toBeTruthy();
    const retried = page.waitForEvent("download");
    await save.click();
    const complete = await retried;
    expect(await complete.failure()).toBeNull();
    expect(await readFile((await complete.path())!)).toEqual(original);
  });
}
