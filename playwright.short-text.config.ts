import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

const servers = base.webServer;
if (!Array.isArray(servers) || servers.length !== 2)
  throw new Error("Expected isolated API/web servers");

export default defineConfig({
  ...base,
  testIgnore: [],
  testMatch: "short-text.spec.ts",
  webServer: [
    {
      ...servers[0],
      command: "uv run --frozen python -m scripts.e2e_short_text_api",
    },
    servers[1],
  ],
});
