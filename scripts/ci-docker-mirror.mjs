import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

export function withPublicMirror(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("Docker configuration must be an object");
  }
  const mirrors = config["registry-mirrors"] ?? [];
  if (
    !Array.isArray(mirrors) ||
    mirrors.some((value) => typeof value !== "string")
  ) {
    throw new Error("Invalid Docker registry mirrors");
  }
  return {
    ...config,
    "registry-mirrors": [...new Set(["https://mirror.gcr.io", ...mirrors])],
  };
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href
) {
  if (
    process.env.GITHUB_ACTIONS !== "true" ||
    process.env.RUNNER_OS !== "Linux"
  ) {
    throw new Error("This command requires a Linux GitHub Actions runner");
  }
  const path = process.env.CI_DOCKER_CONFIG;
  if (!path) throw new Error("CI_DOCKER_CONFIG is required");
  const config = withPublicMirror(JSON.parse(readFileSync(path, "utf8")));
  writeFileSync(path, `${JSON.stringify(config, null, 2)}\n`);
}
