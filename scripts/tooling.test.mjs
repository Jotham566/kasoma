import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join, resolve as resolvePath } from "node:path";
import { test } from "node:test";
import { ESLint } from "eslint";

const require = createRequire(import.meta.url);
const configRequire = createRequire(require.resolve("eslint-config-next"));
const pluginRequire = createRequire(
  configRequire.resolve("@next/eslint-plugin-next"),
);
const { getRootDirs } = pluginRequire("./utils/get-root-dirs.js");
const globRequire = createRequire(pluginRequire.resolve("fast-glob"));

test("NFR-MNT-001: only Next's glob dependency resolves to the pinned safe replacement", () => {
  const manifest = globRequire("../package.json");
  assert.equal(manifest.name, "tinyglobby");
  assert.equal(manifest.version, "0.2.17");
});

test("Next root discovery preserves defaults, directories, arrays and glob alternatives", (t) => {
  const root = mkdtempSync(join(tmpdir(), "kasoma-glob-"));
  t.after(() => rmSync(root, { recursive: true }));
  for (const name of ["web", "admin"]) mkdirSync(join(root, name));
  mkdirSync(join(root, "web", "nested"));
  writeFileSync(join(root, "not-a-directory"), "synthetic");
  const resolve = (rootDir) =>
    getRootDirs({ cwd: root, settings: { next: { rootDir } } })
      .map((path) => resolvePath(path))
      .sort();
  assert.deepEqual(resolve(undefined), [root]);
  assert.deepEqual(resolve(join(root, "web")), [join(root, "web")]);
  assert.deepEqual(resolve(join(root, "*")), [
    join(root, "admin"),
    join(root, "web"),
  ]);
  assert.deepEqual(resolve(join(root, "{web,admin}")), [
    join(root, "admin"),
    join(root, "web"),
  ]);
  assert.deepEqual(resolve([join(root, "web"), false, join(root, "admin")]), [
    join(root, "admin"),
    join(root, "web"),
  ]);
  assert.deepEqual(resolve(join(root, "absent*")), []);
});

test("Deep brace patterns do not exhaust the stack in the resolved Next helper", () => {
  const pattern = "{".repeat(3000) + "a,b" + "}".repeat(3000);
  try {
    getRootDirs({
      cwd: process.cwd(),
      settings: { next: { rootDir: pattern } },
    });
  } catch (error) {
    // Explicit parser/regex rejection is safe; unbounded recursive traversal is not.
    assert.doesNotMatch(String(error), /call stack|recursion/i);
    assert.ok(error instanceof SyntaxError || error instanceof TypeError);
  }
});

test("Next lint rules remain enabled through the normal repository config", async () => {
  const eslint = new ESLint();
  const [result] = await eslint.lintText(
    'export default function Example() { return <img src="/synthetic.png" alt="Synthetic" />; }',
    { filePath: "apps/web/app/tooling-fixture.tsx" },
  );
  assert.ok(
    result.messages.some(
      (message) => message.ruleId === "@next/next/no-img-element",
    ),
  );
});

test("Root-based Next link checks still find configured pages", async (t) => {
  const root = mkdtempSync(join(tmpdir(), "kasoma-next-rule-"));
  t.after(() => rmSync(root, { recursive: true }));
  mkdirSync(join(root, "pages"));
  writeFileSync(
    join(root, "pages", "synthetic-page.tsx"),
    "export default function Page() { return null; }",
  );
  const eslint = new ESLint({
    overrideConfig: { settings: { next: { rootDir: root } } },
  });
  const [result] = await eslint.lintText(
    'export default function Example() { return <a href="/synthetic-page">Synthetic</a>; }',
    { filePath: "apps/web/app/tooling-fixture.tsx" },
  );
  assert.ok(
    result.messages.some(
      (message) => message.ruleId === "@next/next/no-html-link-for-pages",
    ),
  );
});
