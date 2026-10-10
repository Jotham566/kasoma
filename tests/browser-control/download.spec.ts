import { expect, test } from "@playwright/test";
import { createServer, type ServerResponse } from "node:http";
import { readFile } from "node:fs/promises";

test("control complete attachment: native filename and exact bytes", async ({
  page,
}) => {
  const body = Buffer.from(JSON.stringify({ synthetic: "x".repeat(196608) }));
  const server = createServer((request, response) => {
    if (request.url !== "/file") {
      response.end('<a href="/file" download>Download control</a>');
      return;
    }
    response.writeHead(200, {
      "Content-Type": "application/json",
      "Content-Length": String(body.length),
      "Content-Disposition": 'attachment; filename="control.json"',
      "Cache-Control": "no-store",
    });
    response.end(body);
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    const address = server.address();
    if (!address || typeof address === "string")
      throw new Error("Missing loopback listener");
    await page.goto(`http://127.0.0.1:${address.port}`);
    const started = page.waitForEvent("download");
    await page.getByRole("link", { name: "Download control" }).click();
    const download = await started;
    expect(await download.failure()).toBeNull();
    expect(download.suggestedFilename()).toBe("control.json");
    expect(await readFile((await download.path())!)).toEqual(body);
  } finally {
    server.closeAllConnections();
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
});

// A loopback control separates native browser attachment behavior from the gateway.
for (const fault of ["stall", "corrupt"] as const) {
  test(`control mid-transfer ${fault}: native attachment failure and disconnect`, async ({
    page,
  }) => {
    let transfer: ServerResponse | undefined;
    let closed = false;
    let corrupt = false;
    let requests = 0;
    const server = createServer((request, response) => {
      if (request.url !== "/file") {
        response.end('<a href="/file" download>Download control</a>');
        return;
      }
      requests++;
      transfer = response;
      response.on("close", () => {
        closed = true;
      });
      response.writeHead(200, {
        "Content-Type": "application/json",
        "Content-Length": "196608",
        "Content-Disposition": 'attachment; filename="control.json"',
        "Cache-Control": "no-store",
      });
      response.write(Buffer.alloc(65536, 32));
      if (corrupt) setImmediate(() => response.destroy());
    });
    await new Promise<void>((resolve) =>
      server.listen(0, "127.0.0.1", resolve),
    );
    try {
      const address = server.address();
      if (!address || typeof address === "string")
        throw new Error("Missing loopback listener");
      await page.goto(`http://127.0.0.1:${address.port}`);
      const started = page.waitForEvent("download");
      await page.getByRole("link", { name: "Download control" }).click();
      const download = await started;
      if (fault === "stall") await download.cancel();
      else {
        corrupt = true;
        transfer!.destroy();
      }
      await test.step("native control reports failure", async () => {
        expect(await download.failure()).toBeTruthy();
      });
      await expect.poll(() => closed).toBe(true);
    } finally {
      await test.info().attach("native-transport-observations", {
        body: JSON.stringify({ requests, closed }),
        contentType: "application/json",
      });
      server.closeAllConnections();
      await new Promise<void>((resolve) => server.close(() => resolve()));
    }
  });
}
