import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import { withPublicMirror } from "./ci-docker-mirror.mjs";

test("NFR-MNT-001: mirror merge preserves daemon settings and is idempotent", () => {
  const original = {
    features: { "containerd-snapshotter": true },
    "registry-mirrors": ["https://existing.example"],
    "log-driver": "local",
  };
  const result = withPublicMirror(original);
  assert.deepEqual(result, {
    ...original,
    "registry-mirrors": ["https://mirror.gcr.io", "https://existing.example"],
  });
  assert.deepEqual(withPublicMirror(result), result);
  assert.deepEqual(original["registry-mirrors"], ["https://existing.example"]);
  assert.deepEqual(withPublicMirror({}), {
    "registry-mirrors": ["https://mirror.gcr.io"],
  });
});

test("Invalid configuration is rejected instead of replacing daemon settings", () => {
  for (const value of [
    null,
    [],
    false,
    { "registry-mirrors": "invalid" },
    { "registry-mirrors": [1] },
  ]) {
    assert.throws(() => withPublicMirror(value));
  }
});

test("The CI entry point refuses local execution before reading or writing files", () => {
  for (const environment of [
    { GITHUB_ACTIONS: "false", RUNNER_OS: "Linux" },
    { GITHUB_ACTIONS: "true", RUNNER_OS: "macOS" },
  ]) {
    const result = spawnSync(
      process.execPath,
      ["scripts/ci-docker-mirror.mjs"],
      {
        env: {
          ...process.env,
          ...environment,
          CI_DOCKER_CONFIG: "/does-not-exist",
        },
        encoding: "utf8",
      },
    );
    assert.equal(result.status, 1);
    assert.match(result.stderr, /requires a Linux GitHub Actions runner/);
    assert.doesNotMatch(result.stderr, /ENOENT/);
  }
});
