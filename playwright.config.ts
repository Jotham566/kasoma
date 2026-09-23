import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/e2e",
  use: { baseURL: "http://127.0.0.1:3000" },
  webServer: [
    {
      command:
        "uv run --frozen uvicorn apps.api.main:app --host 127.0.0.1 --no-access-log",
      url: "http://127.0.0.1:8000/api/v1/live",
      reuseExistingServer: false,
    },
    {
      command: "corepack pnpm --filter @kasoma/web start",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: false,
    },
  ],
});
