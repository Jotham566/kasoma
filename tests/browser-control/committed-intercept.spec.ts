import { expect, test } from "@playwright/test";
import { createServer } from "node:http";
import { randomUUID } from "node:crypto";
import {
  fetchCommitted,
  interceptionUnavailable,
} from "../e2e/support/committed-intercept";

for (const mode of [
  "RESET_ONCE",
  "ALWAYS_RESET",
  "HTTP_503",
  "NO_KEY",
] as const) {
  test(`synthetic interception: ${mode}`, async ({ page }) => {
    const seen: { key: string | undefined; body: string }[] = [];
    const key = randomUUID();
    const body = JSON.stringify({ synthetic: true });
    const server = createServer((request, response) => {
      if (request.url === "/") {
        response.setHeader("Content-Type", "text/html");
        response.end(
          "<!doctype html><title>Synthetic interception control</title>",
        );
        return;
      }
      if (request.url !== "/api/v1/commit") {
        response.writeHead(404).end();
        return;
      }
      let received = "";
      request.on("data", (chunk) => {
        received += chunk;
      });
      request.on("end", () => {
        seen.push({
          key: request.headers["idempotency-key"] as string | undefined,
          body: received,
        });
        if (
          mode === "ALWAYS_RESET" ||
          (mode === "RESET_ONCE" && seen.length === 1)
        ) {
          request.socket.destroy();
        } else {
          response.writeHead(mode === "HTTP_503" ? 503 : 201, {
            "Content-Type": "application/json",
          });
          response.end('{"synthetic":true}');
        }
      });
    });
    await new Promise<void>((resolve) =>
      server.listen(0, "127.0.0.1", resolve),
    );
    try {
      const address = server.address();
      if (!address || typeof address === "string")
        throw new Error("Missing loopback listener");
      await page.goto(`http://127.0.0.1:${address.port}`);
      let failure: string | undefined;
      await page.route("**/api/v1/commit", async (route) => {
        try {
          const response = await fetchCommitted(route);
          await route.fulfill({ response });
        } catch (error) {
          failure =
            error instanceof Error ? error.message : "Unexpected diagnostic";
          await route.abort();
        }
      });
      const status = await page.evaluate(
        async ({ key, body, omit }) => {
          try {
            return (
              await fetch("/api/v1/commit", {
                method: "POST",
                body,
                headers: {
                  ...(omit ? {} : { "idempotency-key": key }),
                  Authorization: "Bearer synthetic-canary",
                },
              })
            ).status;
          } catch {
            return 0;
          }
        },
        { key, body, omit: mode === "NO_KEY" },
      );
      if (mode === "NO_KEY" || mode === "ALWAYS_RESET") {
        expect(status).toBe(0);
        expect(failure).toBe(interceptionUnavailable);
        expect(failure?.includes("synthetic-canary")).toBe(false);
      } else {
        expect(failure).toBeUndefined();
        expect(status).toBe(mode === "HTTP_503" ? 503 : 201);
      }
      expect(seen.length).toBe(
        mode === "NO_KEY" ? 0 : mode === "HTTP_503" ? 1 : 2,
      );
      expect(
        seen.every((request) => request.key === key && request.body === body),
      ).toBe(true);
    } finally {
      server.closeAllConnections();
      await new Promise<void>((resolve) => server.close(() => resolve()));
    }
  });
}
