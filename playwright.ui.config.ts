import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "**/*.ui.spec.ts",
  use: { baseURL: "http://127.0.0.1:13001", browserName: "chromium" },
  webServer: {
    command: "corepack pnpm --filter @kasoma/web start",
    env: { PORT: "13001", API_INTERNAL_URL: "http://127.0.0.1:18001" },
    url: "http://127.0.0.1:13001",
    reuseExistingServer: false,
  },
});
