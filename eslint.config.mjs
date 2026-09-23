import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

export default defineConfig([
  ...nextVitals,
  ...nextTypescript,
  {
    settings: { next: { rootDir: "apps/web/" }, react: { version: "19.3.0" } },
  },
  globalIgnores([
    "**/.next/**",
    "**/next-env.d.ts",
    "packages/api-client/src/schema.d.ts",
  ]),
]);
