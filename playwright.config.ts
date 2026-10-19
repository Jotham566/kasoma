import { defineConfig } from "@playwright/test";

const browserName = process.env.KASOMA_E2E_BROWSER ?? "chromium";
const chromiumChannel = process.env.KASOMA_E2E_CHROMIUM_CHANNEL;
if (
  chromiumChannel !== undefined &&
  (chromiumChannel !== "chromium" || browserName !== "chromium")
) {
  throw new Error(
    "KASOMA_E2E_CHROMIUM_CHANNEL supports only chromium with the chromium engine",
  );
}
if (
  browserName !== "chromium" &&
  browserName !== "firefox" &&
  browserName !== "webkit"
) {
  throw new Error("KASOMA_E2E_BROWSER must be chromium, firefox or webkit");
}

export default defineConfig({
  testDir: "./tests/e2e",
  testIgnore: [
    "**/*.ui.spec.ts",
    "**/short-text.spec.ts",
    "**/operations-configuration.spec.ts",
  ],
  use: {
    baseURL: "http://127.0.0.1:13000",
    browserName,
    trace: "retain-on-failure",
    ...(chromiumChannel ? { channel: chromiumChannel } : {}),
  },
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
