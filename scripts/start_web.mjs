import { cpSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const web = path.join(root, "apps/web");
const standalone = path.join(web, ".next/standalone/apps/web");
cpSync(path.join(web, ".next/static"), path.join(standalone, ".next/static"), {
  recursive: true,
});
// Next's documented runtime bind setting; local production smoke stays on loopback.
process.env.HOSTNAME = "127.0.0.1";
await import(pathToFileURL(path.join(standalone, "server.js")).href);
