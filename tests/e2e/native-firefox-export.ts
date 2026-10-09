import { spawn } from "node:child_process";
import type { BrowserContext } from "@playwright/test";

/** Native manager bypasses the pinned Firefox download interceptor only. */
export async function nativeFirefoxExport(
  context: BrowserContext,
  target: string,
) {
  const cookies = (await context.cookies("http://127.0.0.1:13000"))
    .filter((cookie) =>
      ["kasoma_access", "kasoma_refresh"].includes(cookie.name),
    )
    .map(({ name, value }) => ({ name, value }));
  return new Promise<{
    corrupt_rejected: boolean;
    reader_closed: boolean;
    size: number;
    sha256: string;
  }>((resolve, reject) => {
    const child = spawn(
      "uv",
      ["run", "--frozen", "python", "-m", "scripts.firefox_native_export"],
      {
        stdio: ["pipe", "pipe", "pipe"],
      },
    );
    let output = "";
    let diagnostic = "";
    child.stderr.on("data", (chunk: Buffer) => {
      const code = chunk.toString().trim();
      if (/^NATIVE_EXPORT_[A-Z]+_[A-Za-z]+$/.test(code)) diagnostic = code;
    });
    const timer = setTimeout(() => child.kill("SIGTERM"), 25000);
    child.on("error", () => {
      clearTimeout(timer);
      reject(new Error("Native Firefox export helper failed"));
    });
    child.stdout.on("data", (chunk: Buffer) => {
      if (output.length + chunk.length > 4096) {
        child.kill("SIGTERM");
        return;
      }
      output += chunk.toString();
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (code !== 0)
        return reject(
          new Error(`Native Firefox export verification failed ${diagnostic}`),
        );
      try {
        resolve(JSON.parse(output));
      } catch {
        reject(new Error("Invalid native Firefox result"));
      }
    });
    child.stdin.on("error", () => undefined);
    // Synthetic credentials travel over stdin, never command arguments or test output.
    child.stdin.end(JSON.stringify({ target, cookies }));
  });
}
