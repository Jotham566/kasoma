import { defineConfig } from "@playwright/test";

const browserName = process.env.KASOMA_E2E_BROWSER ?? "chromium";
if (
  browserName !== "chromium" &&
  browserName !== "firefox" &&
  browserName !== "webkit"
) {
  throw new Error("KASOMA_E2E_BROWSER must be chromium, firefox or webkit");
}

export default defineConfig({
  testDir: "./tests/e2e",
  use: { baseURL: "http://127.0.0.1:13000", browserName },
  webServer: [
    {
      command: "uv run --frozen python -m scripts.e2e_api",
      url: "http://127.0.0.1:18000/api/v1/live",
      reuseExistingServer: false,
    },
    {
      command: "corepack pnpm --filter @kasoma/web start",
      env: { PORT: "13000", API_INTERNAL_URL: "http://127.0.0.1:18000" },
      url: "http://127.0.0.1:13000",
      reuseExistingServer: false,
    },
  ],
});
