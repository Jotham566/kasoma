import { defineConfig } from "@playwright/test";

const browserName = process.env.KASOMA_E2E_BROWSER ?? "chromium";
if (!["chromium", "firefox", "webkit"].includes(browserName)) {
  throw new Error("KASOMA_E2E_BROWSER must be chromium, firefox or webkit");
}

export default defineConfig({
  testDir: "./tests/browser-control",
  workers: 1,
  use: {
    browserName: browserName as "chromium" | "firefox" | "webkit",
    trace: "retain-on-failure",
  },
});
