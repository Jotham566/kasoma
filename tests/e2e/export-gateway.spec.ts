import { expect, test } from "@playwright/test";
import { randomUUID } from "node:crypto";

test("owned background export crosses the real gateway as a frozen exact-length attachment", async ({
  request,
}) => {
  const headers = { Origin: "http://127.0.0.1:13000" };
  const challenge = await request.post("/api/v1/auth/otp/request", {
    headers,
    data: {
      identifier: `export-http-${randomUUID()}@example.invalid`,
      device_id: randomUUID(),
    },
  });
  expect(challenge.status()).toBe(202);
  const verified = await request.post("/api/v1/auth/otp/verify", {
    headers,
    data: {
      challenge_id: (await challenge.json()).challenge_id,
      code: "246810",
    },
  });
  expect(verified.ok()).toBeTruthy();
  const created = await request.post("/api/v1/me/data-requests", {
    headers: { ...headers, "Idempotency-Key": randomUUID() },
    data: { kind: "EXPORT", affirmative: true },
  });
  expect(created.status()).toBe(201);
  const target = (await created.json()).id;
  const path = `/api/v1/me/data-requests/${target}`;
  const fixture = `http://127.0.0.1:18000/__fixture/exports/${target}`;
  expect((await request.post(`${fixture}/history`)).ok()).toBeTruthy();
  const key = randomUUID();
  const queued = await request.post(path + "/export-job", {
    headers: { ...headers, "Idempotency-Key": key },
    data: {},
  });
  expect(queued.status()).toBe(202);
  await expect
    .poll(
      async () =>
        (await (await request.get(path + "/export-job")).json()).status,
    )
    .toBe("READY");
  const ready = await (await request.get(path + "/export-job")).json();
  const download = await request.get(path + "/export-file");
  expect(download.status()).toBe(200);
  const bytes = await download.body();
  expect(Number(download.headers()["content-length"])).toBe(bytes.length);
  expect(bytes.length).toBe(ready.size_bytes);
  expect(bytes.length).toBeGreaterThan(2 * 65536);
  expect(download.headers()["cache-control"]).toBe("no-store");
  expect(download.headers()["content-disposition"]).toBe(
    `attachment; filename="kasoma-export-${target}.json"`,
  );
  expect(JSON.parse(bytes.toString()).request_id).toBe(target);
  expect(await (await request.get(path + "/export-file")).body()).toEqual(
    bytes,
  );
  const replay = await request.post(path + "/export-job", {
    headers: { ...headers, "Idempotency-Key": key },
    data: {},
  });
  expect((await replay.json()).status).toBe("READY");
  for (const mode of ["corrupt", "stall"]) {
    expect((await request.post(`${fixture}/fault/${mode}`)).ok()).toBeTruthy();
    await expect(
      request.get(path + "/export-file", { timeout: 1000 }),
    ).rejects.toThrow();
    await expect
      .poll(
        async () =>
          (await (await request.get(`${fixture}/observations`)).json()).closed,
      )
      .toBeGreaterThanOrEqual(1);
    expect((await request.post(`${fixture}/fault/normal`)).ok()).toBeTruthy();
    expect(await (await request.get(path + "/export-file")).body()).toEqual(
      bytes,
    );
  }
});

test("attachment navigation returns safely to privacy on a closed upstream failure", async ({
  request,
}) => {
  const path = `/api/v1/me/data-requests/${randomUUID()}/export-file`;
  const navigation = await request.get(path, {
    headers: { "sec-fetch-mode": "navigate", "sec-fetch-site": "same-origin" },
    maxRedirects: 0,
  });
  expect(navigation.status()).toBe(303);
  expect(navigation.headers()["location"]).toBe(
    "/privacy?export_error=REAUTH_REQUIRED",
  );
  expect(navigation.headers()["cache-control"]).toBe("no-store");
  expect(navigation.headers()["content-disposition"]).toBeUndefined();
  expect(navigation.headers()["request_id"]).toMatch(/^[0-9a-f-]{36}$/);
  const page = await request.get(navigation.headers()["location"]);
  expect(page.status()).toBe(200);
  expect(await page.text()).toContain(
    'role="alert">Sign in again to verify your identity before downloading your export.',
  );

  const programmatic = await request.get(path);
  expect(programmatic.status()).toBe(401);
  expect(programmatic.headers()["location"]).toBeUndefined();
  expect((await programmatic.json()).error.code).toBe("REAUTH_REQUIRED");
});

test("attachment route rejects other methods and cross-origin navigation", async ({
  request,
}) => {
  const path = `/api/v1/me/data-requests/${randomUUID()}/export-file`;
  expect((await request.post(path)).status()).toBe(404);
  for (const site of ["same-site", "cross-site"]) {
    const denied = await request.get(path, {
      headers: { "sec-fetch-mode": "navigate", "sec-fetch-site": site },
      maxRedirects: 0,
    });
    expect(denied.status()).toBe(403);
    expect((await denied.json()).error.code).toBe("FORBIDDEN");
    expect(denied.headers()["location"]).toBeUndefined();
  }
});
