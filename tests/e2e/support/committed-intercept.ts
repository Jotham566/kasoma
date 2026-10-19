import type { APIResponse, Route } from "@playwright/test";

export const interceptionUnavailable =
  "Synthetic commit interception unavailable; request diagnostics withheld.";

export async function fetchCommitted(route: Route): Promise<APIResponse> {
  try {
    const request = route.request();
    const url = new URL(request.url());
    const key = request.headers()["idempotency-key"];
    if (
      url.protocol !== "http:" ||
      url.hostname !== "127.0.0.1" ||
      url.username ||
      url.password ||
      !url.pathname.startsWith("/api/v1/") ||
      !["POST", "DELETE"].includes(request.method()) ||
      !/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(key ?? "")
    )
      throw new Error("Invalid synthetic interception");
    // The pinned transport retries ECONNRESET only, with identical body/headers.
    // No test retry or HTTP-error retry; never follow a redirect outside loopback.
    return await route.fetch({ maxRetries: 1, maxRedirects: 0 });
  } catch {
    // Playwright's raw error includes Cookie/Authorization headers. Withhold it.
    throw new Error(interceptionUnavailable);
  }
}
