import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

// Configuration is global within a schema. Give its deliberate mutations an
// independent fresh fake-provider API, rather than racing unrelated warning tests.
export default defineConfig({
  ...base,
  testIgnore: [],
  testMatch: "**/operations-configuration.spec.ts",
});
