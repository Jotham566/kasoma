/** ADR-048 attachment boundary. The gateway supplies its private upstream abort controller. */
export class ExportUnavailable extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string) {
    super("Private export unavailable");
    this.status = status;
    this.code = code;
  }
}

/** Cookie credentials have already been converted to a private authorization header. */
export async function fetchExport({
  url,
  headers,
  target,
  requestId,
  requestSignal,
  fetcher = fetch,
  initialTimeoutMs = 8000,
}: {
  url: string;
  headers: Record<string, string>;
  target: string;
  requestId: string;
  requestSignal: AbortSignal;
  fetcher?: typeof fetch;
  initialTimeoutMs?: number;
}): Promise<Response> {
  const abort = new AbortController();
  const disconnect = () => abort.abort();
  requestSignal.addEventListener("abort", disconnect, { once: true });
  if (requestSignal.aborted) disconnect();
  const timer = setTimeout(disconnect, initialTimeoutMs);
  try {
    const upstream = await fetcher(url, {
      method: "GET",
      headers: { ...headers, "Accept-Encoding": "identity" },
      cache: "no-store",
      redirect: "error",
      signal: abort.signal,
    });
    clearTimeout(timer);
    if (!upstream.ok) {
      abort.abort();
      void upstream.body?.cancel().catch(() => undefined);
      // Never forward free-form upstream diagnostics or arbitrary redirect destinations.
      const codes: Record<number, string> = {
        401: "REAUTH_REQUIRED",
        403: "FORBIDDEN",
        404: "RESOURCE_NOT_FOUND",
        409: "EXPORT_NOT_READY",
        410: "EXPORT_EXPIRED",
        429: "RATE_LIMITED",
      };
      throw new ExportUnavailable(
        codes[upstream.status] ? upstream.status : 503,
        codes[upstream.status] ?? "SERVICE_UNAVAILABLE",
      );
    }
    return exportStream({ upstream, target, requestId, abort, requestSignal });
  } catch (error) {
    abort.abort();
    if (error instanceof ExportUnavailable) throw error;
    throw new ExportUnavailable(503, "SERVICE_UNAVAILABLE");
  } finally {
    clearTimeout(timer);
    requestSignal.removeEventListener("abort", disconnect);
  }
}

export function exportStream({
  upstream,
  target,
  requestId,
  abort,
  requestSignal,
  timeoutMs = 300_000,
}: {
  upstream: Response;
  target: string;
  requestId: string;
  abort: AbortController;
  requestSignal?: AbortSignal;
  timeoutMs?: number;
}): Response {
  const uuid =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const header = upstream.headers.get("content-length") ?? "";
  const size = Number(header);
  if (
    upstream.status !== 200 ||
    !upstream.body ||
    upstream.body.locked ||
    !/^[0-9]{1,8}$/.test(header) ||
    size < 1 ||
    size > 16 * 1024 * 1024 ||
    upstream.headers.get("content-type")?.split(";")[0] !==
      "application/json" ||
    ![null, "identity"].includes(upstream.headers.get("content-encoding")) ||
    upstream.headers.has("transfer-encoding") ||
    target.length !== 36 ||
    !uuid.test(target) ||
    requestId.length !== 36 ||
    !uuid.test(requestId) ||
    abort.signal.aborted ||
    !Number.isInteger(timeoutMs) ||
    timeoutMs < 1 ||
    timeoutMs > 300_000
  ) {
    abort.abort();
    void upstream.body?.cancel().catch(() => undefined);
    throw new Error("Private export unavailable");
  }
  const reader = upstream.body.getReader();
  let settled = false;
  let received = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let controller: ReadableStreamDefaultController<Uint8Array>;

  function clear() {
    clearTimeout(timer);
    requestSignal?.removeEventListener("abort", fail);
  }
  async function cancelUpstream() {
    abort.abort();
    try {
      await reader.cancel();
    } catch {
      // The connection is already aborted; never expose upstream diagnostics.
    } finally {
      reader.releaseLock();
    }
  }
  function fail() {
    if (settled) return;
    settled = true;
    clear();
    controller.error(new Error("Private export transfer incomplete"));
    void cancelUpstream();
  }

  const body = new ReadableStream<Uint8Array>(
    {
      start(value) {
        controller = value;
        requestSignal?.addEventListener("abort", fail, { once: true });
        if (requestSignal?.aborted) fail();
        if (!settled) timer = setTimeout(fail, timeoutMs);
      },
      async pull() {
        try {
          const part = await reader.read();
          if (settled) return;
          if (
            part.done ||
            !(part.value instanceof Uint8Array) ||
            part.value.byteLength === 0
          )
            throw new Error("Incomplete export body");
          received += part.value.byteLength;
          if (received > size) throw new Error("Oversized export body");
          if (received === size) {
            // Do not release the final bytes until upstream completion has been observed.
            const end = await reader.read();
            if (settled) return;
            if (!end.done) throw new Error("Unexpected export body");
            settled = true;
            clear();
            reader.releaseLock();
            controller.enqueue(part.value);
            controller.close();
          } else {
            controller.enqueue(part.value);
          }
        } catch {
          fail();
        }
      },
      async cancel() {
        if (settled) return;
        settled = true;
        clear();
        await cancelUpstream();
      },
    },
    { highWaterMark: 0 },
  );
  return new Response(body, {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Content-Length": String(size),
      "Content-Disposition": `attachment; filename="kasoma-export-${target.toLowerCase()}.json"`,
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      request_id: requestId,
    },
  });
}
