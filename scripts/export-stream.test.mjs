import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { test } from "node:test";
import {
  exportFailureLocation,
  exportNotice,
} from "../apps/web/app/privacy/export-notice.ts";
import {
  ExportUnavailable,
  exportStream,
  fetchExport,
} from "../apps/web/app/api/export-stream.ts";

function fixture(parts, size, headers = {}) {
  let cancelled = false;
  let reads = 0;
  const source = new ReadableStream(
    {
      pull(controller) {
        reads++;
        if (parts.length) controller.enqueue(parts.shift());
        else controller.close();
      },
      cancel() {
        cancelled = true;
      },
    },
    { highWaterMark: 0 },
  );
  const abort = new AbortController();
  const response = new Response(source, {
    headers: {
      "content-length": String(size),
      "content-type": "application/json",
      ...headers,
    },
  });
  return {
    response,
    abort,
    cancelled: () => cancelled,
    reads: () => reads,
    create: (options = {}) =>
      exportStream({
        upstream: response,
        target: randomUUID(),
        requestId: randomUUID(),
        abort,
        ...options,
      }),
  };
}
const bytes = (value) => new TextEncoder().encode(value);

test("attachment navigation errors use only a fixed local destination and allowlisted messages", () => {
  for (const code of [
    "REAUTH_REQUIRED",
    "FORBIDDEN",
    "RESOURCE_NOT_FOUND",
    "EXPORT_NOT_READY",
    "EXPORT_EXPIRED",
    "RATE_LIMITED",
    "SERVICE_UNAVAILABLE",
  ]) {
    assert.equal(exportFailureLocation(code), `/privacy?export_error=${code}`);
    assert.equal(typeof exportNotice(code), "string");
  }
  for (const value of [
    undefined,
    null,
    ["EXPORT_EXPIRED"],
    {},
    "__proto__",
    "constructor",
    "toString",
    "https://evil.invalid",
    "secret provider diagnostic",
    "EXPORT_EXPIRED\n",
  ]) {
    assert.equal(exportNotice(value), undefined);
    if (typeof value === "string")
      assert.equal(
        exportFailureLocation(value),
        "/privacy?export_error=SERVICE_UNAVAILABLE",
      );
  }
});

function transfer(fetcher, changes = {}) {
  return fetchExport({
    url: "http://localhost:8000/api/v1/me/data-requests/synthetic/export-file",
    headers: { Authorization: "Bearer synthetic", request_id: "synthetic" },
    target: randomUUID(),
    requestId: randomUUID(),
    requestSignal: new AbortController().signal,
    fetcher,
    ...changes,
  });
}

test("gateway private fetch rejects redirects and uses separate initial and transfer deadlines", async () => {
  let options;
  const state = fixture([bytes("hello")], 5);
  const result = await transfer(
    async (url, init) => {
      assert.equal(new URL(url).search, "");
      options = init;
      return state.response;
    },
    { initialTimeoutMs: 10 },
  );
  assert.equal(options.headers.Authorization, "Bearer synthetic");
  assert.equal(options.headers["Accept-Encoding"], "identity");
  assert.equal(options.redirect, "error");
  assert.equal(options.cache, "no-store");
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(options.signal.aborted, false);
  assert.equal(await result.text(), "hello");
});

for (const [status, code, expected] of [
  [401, "REAUTH_REQUIRED", 401],
  [403, "FORBIDDEN", 403],
  [404, "RESOURCE_NOT_FOUND", 404],
  [409, "EXPORT_NOT_READY", 409],
  [410, "EXPORT_EXPIRED", 410],
  [429, "RATE_LIMITED", 429],
  [302, "SERVICE_UNAVAILABLE", 503],
  [500, "SERVICE_UNAVAILABLE", 503],
]) {
  test(`gateway rejects ${status} without reading or exposing upstream diagnostics`, async () => {
    let cancelled = false;
    let reads = 0;
    const upstream = new Response(
      new ReadableStream(
        {
          pull() {
            reads++;
            throw new Error("private provider diagnostic");
          },
          cancel() {
            cancelled = true;
          },
        },
        { highWaterMark: 0 },
      ),
      { status },
    );
    await assert.rejects(
      transfer(async () => upstream),
      (error) => {
        assert.ok(error instanceof ExportUnavailable);
        assert.equal(error.status, expected);
        assert.equal(error.code, code);
        assert.equal(error.message, "Private export unavailable");
        return true;
      },
    );
    assert.equal(reads, 0);
    assert.equal(cancelled, true);
  });
}

test("gateway aborts stalled initial fetches on deadline and request disconnect", async () => {
  for (const mode of ["deadline", "disconnect"]) {
    const request = new AbortController();
    let signal;
    const completion = assert.rejects(
      transfer(
        async (url, options) => {
          signal = options.signal;
          return await new Promise((resolve, reject) => {
            options.signal.addEventListener(
              "abort",
              () => reject(new Error("secret URL")),
              { once: true },
            );
          });
        },
        { initialTimeoutMs: 10, requestSignal: request.signal },
      ),
      (error) => {
        assert.equal(error.code, "SERVICE_UNAVAILABLE");
        assert.equal(error.message, "Private export unavailable");
        return true;
      },
    );
    if (mode === "disconnect") request.abort();
    await completion;
    assert.equal(signal.aborted, true);
  }
});

test("invalid attachment identifiers fail closed before reading", () => {
  for (const field of ["target", "requestId"]) {
    const state = fixture([bytes("a")], 1);
    assert.throws(
      () => state.create({ [field]: randomUUID() + "\n" }),
      /Private export unavailable/,
    );
    assert.equal(state.reads(), 0);
    assert.equal(state.abort.signal.aborted, true);
  }
});

test("private attachment streams exact bytes with controlled headers and no eager reads", async () => {
  const state = fixture([bytes('{"ok":'), bytes("true}")], 11, {
    "set-cookie": "must-not-forward",
    "content-disposition": "inline",
  });
  const result = state.create();
  assert.equal(state.reads(), 0);
  assert.equal(await result.text(), '{"ok":true}');
  assert.equal(result.headers.get("content-length"), "11");
  assert.equal(result.headers.get("cache-control"), "no-store");
  assert.equal(result.headers.get("x-content-type-options"), "nosniff");
  assert.match(
    result.headers.get("content-disposition"),
    /^attachment; filename="kasoma-export-/,
  );
  assert.equal(result.headers.get("set-cookie"), null);
  assert.equal(state.abort.signal.aborted, false);
});

for (const [name, parts, size] of [
  ["truncated", [bytes("abc")], 4],
  ["oversized", [bytes("abcde")], 4],
  ["extra chunk", [bytes("abcd"), bytes("extra")], 4],
  ["empty chunk", [bytes("")], 1],
]) {
  test(`private attachment aborts ${name} without a successful complete response`, async () => {
    const state = fixture(parts, size);
    await assert.rejects(
      state.create().text(),
      /Private export transfer incomplete/,
    );
    assert.equal(state.abort.signal.aborted, true);
  });
}

for (const headers of [
  { "content-length": "16777217" },
  { "content-length": "0" },
  { "content-length": "1, 1" },
  { "content-encoding": "gzip" },
  { "transfer-encoding": "chunked" },
  { "content-type": "text/html" },
]) {
  test(`private attachment rejects invalid metadata ${JSON.stringify(headers)}`, () => {
    const state = fixture([bytes("a")], 1, headers);
    assert.throws(() => state.create(), /Private export unavailable/);
    assert.equal(state.reads(), 0);
    assert.equal(state.abort.signal.aborted, true);
  });
}

test("downstream cancellation aborts upstream and closes its reader", async () => {
  const state = fixture([bytes("abc"), bytes("def")], 6);
  const reader = state.create().body.getReader();
  assert.equal(new TextDecoder().decode((await reader.read()).value), "abc");
  await reader.cancel();
  assert.equal(state.cancelled(), true);
  assert.equal(state.abort.signal.aborted, true);
});

test("request disconnect and whole-transfer deadline cancel stalled upstream reads", async (t) => {
  for (const mode of ["disconnect", "deadline"]) {
    await t.test(mode, async () => {
      let cancelled = false;
      const request = new AbortController();
      const abort = new AbortController();
      const upstream = new Response(
        new ReadableStream({
          cancel() {
            cancelled = true;
          },
        }),
        {
          headers: {
            "content-length": "5",
            "content-type": "application/json",
          },
        },
      );
      const result = exportStream({
        upstream,
        target: randomUUID(),
        requestId: randomUUID(),
        abort,
        requestSignal: request.signal,
        timeoutMs: 20,
      });
      const completion = assert.rejects(
        result.text(),
        /Private export transfer incomplete/,
      );
      if (mode === "disconnect") request.abort();
      await completion;
      assert.equal(abort.signal.aborted, true);
      assert.equal(cancelled, true);
    });
  }
});
