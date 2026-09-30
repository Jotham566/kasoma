"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

import { DeletionImpact } from "./deletion-impact";

type Schema = components["schemas"];
const api = () => apiClient("", crypto.randomUUID());
const button =
  "min-h-11 rounded border border-slate-500 px-4 py-2 disabled:opacity-50";
function check<T>(result: { data?: T; error?: Schema["ErrorEnvelope"] }): T {
  if (!result.data) throw new Error(result.error?.error.code ?? "UNAVAILABLE");
  return result.data;
}
export function Requests({ staff = false }: { staff?: boolean }) {
  const [preview, setPreview] = useState<Schema["DeletionPreview"] | null>(
    null,
  );
  const [rows, setRows] = useState<Schema["DataRequestView"][]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [kind, setKind] =
    useState<Schema["DataRequestInput"]["kind"]>("EXPORT");
  const [affirmative, setAffirmative] = useState(false);
  const [pending, setPending] = useState<{
    key: string;
    kind: Schema["DataRequestInput"]["kind"];
    target?: string;
  } | null>(null);
  const [downloadPending, setDownloadPending] = useState<{
    key: string;
    target: string;
  } | null>(null);
  const [busy, setBusy] = useState(true);
  const [status, setStatus] = useState("Loading requests…");
  const mounted = useRef(true);
  async function load(next?: string) {
    const page = check(
      await api().GET(
        staff ? "/api/v1/admin/data-requests" : "/api/v1/me/data-requests",
        { params: { query: { cursor: next, limit: 20 } } },
      ),
    );
    if (mounted.current) {
      setRows((old) => (next ? [...old, ...page.data] : page.data));
      setCursor(page.next_cursor);
    }
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setPreview(null);
    setStatus("Saving or loading…");
    try {
      await action();
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      if (["AUTH_REQUIRED", "REAUTH_REQUIRED", "FORBIDDEN"].includes(code)) {
        setRows([]);
        setCursor(null);
        setPending(null);
        setDownloadPending(null);
      }
      if (
        [
          "EXPORT_EXPIRED",
          "EXPORT_LIMIT_REACHED",
          "RESOURCE_NOT_FOUND",
          "IDEMPOTENCY_CONFLICT",
        ].includes(code)
      ) {
        setDownloadPending(null);
      }
      setStatus(
        code === "AUTH_REQUIRED" || code === "REAUTH_REQUIRED"
          ? "Sign in again to verify your identity. Saved requests remain available."
          : code === "FORBIDDEN"
            ? "Administrator access is required."
            : code === "SELF_REVIEW_FORBIDDEN"
              ? "Another administrator must review your request."
              : code === "REVIEW_OWNERSHIP_REQUIRED"
                ? "Only the administrator who claimed this request can preview it."
                : code === "ALREADY_CLAIMED"
                  ? "Another administrator is reviewing this request. Reload the list."
                  : code === "EXPORT_EXPIRED"
                    ? "This copy has expired. Submit a new export request."
                    : code === "EXPORT_LIMIT_REACHED"
                      ? "This account exceeds the self-service export limit. Your request remains pending for review."
                      : code === "RATE_LIMITED"
                        ? "Too many requests. Wait before trying again; saved requests are retained."
                        : "Could not confirm the operation. Retry the same request or reload the list.",
      );
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  useEffect(() => {
    mounted.current = true;
    void Promise.resolve().then(() =>
      run(async () => {
        await load();
        setStatus("Requests loaded.");
      }),
    );
    return () => {
      mounted.current = false;
    };
    // The workspace mode is fixed by its route; all subsequent loads are explicit.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  async function send(target?: string) {
    const operation = pending ?? { key: crypto.randomUUID(), kind, target };
    setPending(operation);
    await run(async () => {
      if (staff && operation.target) {
        check(
          await api().POST("/api/v1/admin/data-requests/{target}/claim", {
            params: {
              path: { target: operation.target },
              header: { "Idempotency-Key": operation.key },
            },
            body: {},
          }),
        );
      } else {
        check(
          await api().POST("/api/v1/me/data-requests", {
            params: { header: { "Idempotency-Key": operation.key } },
            body: { kind: operation.kind, affirmative: true },
          }),
        );
      }
      setPending(null);
      setAffirmative(false);
      await load();
      setStatus(
        staff
          ? "Review recorded. Fulfillment remains pending."
          : "Request received. Export or deletion has not been completed.",
      );
    });
  }
  async function download(target: string) {
    const operation = downloadPending ?? { key: crypto.randomUUID(), target };
    setDownloadPending(operation);
    await run(async () => {
      const bundle = check(
        await api().POST("/api/v1/me/data-requests/{target}/export", {
          params: {
            path: { target: operation.target },
            header: { "Idempotency-Key": operation.key },
          },
          body: {},
        }),
      );
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(bundle, null, 2)], {
          type: "application/json",
        }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.download = `kasoma-export-${bundle.request_id}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setDownloadPending(null);
      await load();
      setStatus(
        "Export made available. The same copy is available for 24 hours.",
      );
    });
  }
  return (
    <main className="mx-auto max-w-2xl p-6 space-y-5">
      <Link className="inline-flex min-h-11 items-center underline" href="/">
        Home
      </Link>
      <h1 className="text-3xl font-semibold">
        {staff ? "Data request review" : "Your data requests"}
      </h1>
      <p>
        {staff
          ? "Administrators can claim requests for review. Only the account owner can download an export. Deletion processing remains pending."
          : "Request a copy of your data or ask for deletion. Learning consent is not required to make or track a request."}
      </p>
      <p>
        Exports require a recent sign-in. Downloads include your account and
        released learning records, with exclusions listed in the file. Deletion
        requests remain pending.
      </p>
      {!staff && (
        <>
          <Link
            className="inline-flex min-h-11 items-center underline"
            href="/onboarding"
          >
            Sign in or manage consent
          </Link>
          <p>
            Submitting a deletion request does not pause learning. You can
            withdraw learning consent on the profile page.
          </p>
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              void send();
            }}
          >
            <fieldset
              disabled={busy || !!pending || !!downloadPending}
              className="space-y-3"
            >
              <legend>Request type</legend>
              {(["EXPORT", "DELETE"] as const).map((value) => (
                <label className="flex min-h-11 items-center gap-3" key={value}>
                  <input
                    type="radio"
                    name="kind"
                    value={value}
                    checked={kind === value}
                    onChange={() => {
                      setKind(value);
                      setAffirmative(false);
                    }}
                  />
                  {value === "EXPORT"
                    ? "Export a copy of my data"
                    : "Request deletion of my data"}
                </label>
              ))}
              <label className="flex min-h-11 items-center gap-3">
                <input
                  type="checkbox"
                  checked={affirmative}
                  onChange={(event) => setAffirmative(event.target.checked)}
                />
                I confirm this request for my account.
              </label>
            </fieldset>
            <button
              className={button}
              disabled={busy || !!downloadPending || (!pending && !affirmative)}
            >
              {pending ? "Retry request" : "Submit request"}
            </button>
          </form>
        </>
      )}
      <p role="status" aria-live="polite">
        {status}
      </p>
      {staff && preview && <DeletionImpact preview={preview} />}
      <button
        className={button}
        disabled={busy}
        onClick={() =>
          void run(async () => {
            await load();
            setPending(null);
            setDownloadPending(null);
            setStatus("Requests loaded.");
          })
        }
      >
        Reload requests
      </button>
      {!staff && downloadPending && (
        <button
          className={button}
          disabled={busy}
          onClick={() => void download(downloadPending.target)}
        >
          Retry download
        </button>
      )}
      {staff && pending?.target && (
        <button
          className={button}
          disabled={busy}
          onClick={() => void send(pending.target)}
        >
          Retry review
        </button>
      )}
      <ul className="space-y-4">
        {rows.map((row) => (
          <li
            className="rounded border border-slate-400 p-4 space-y-2"
            key={row.id}
          >
            <h2 className="font-semibold">
              {row.kind === "EXPORT" ? "Export request" : "Deletion request"}
            </h2>
            <p>Reference: {row.id}</p>
            <p>
              {row.status === "COMPLETED"
                ? "Export made available"
                : row.status === "QUEUED"
                  ? "Queued for review"
                  : "In review"}
            </p>
            <p>
              Received:{" "}
              {new Date(row.created_at).toLocaleString("en-GB", {
                timeZone: "Africa/Kampala",
              })}{" "}
              (Kampala)
            </p>
            {row.download_expires_at && (
              <p>
                Copy expires:{" "}
                {new Date(row.download_expires_at).toLocaleString("en-GB", {
                  timeZone: "Africa/Kampala",
                })}{" "}
                (Kampala)
              </p>
            )}
            {!staff && row.kind === "EXPORT" && (
              <button
                className={button}
                disabled={busy || !!pending || !!downloadPending}
                onClick={() => void download(row.id)}
              >
                Download export
              </button>
            )}
            {staff && row.kind === "DELETE" && row.status === "IN_REVIEW" && (
              <button
                className={button}
                disabled={busy || !!pending}
                onClick={() =>
                  void run(async () => {
                    const result = check(
                      await api().GET(
                        "/api/v1/admin/data-requests/{target}/deletion-preview",
                        { params: { path: { target: row.id } } },
                      ),
                    );
                    setPreview(result);
                    setStatus(
                      "Deletion impact loaded. No account data was changed.",
                    );
                  })
                }
              >
                Preview deletion impact
              </button>
            )}
            {staff && row.status === "QUEUED" && (
              <button
                className={button}
                disabled={busy || !!pending || !!downloadPending}
                onClick={() => void send(row.id)}
              >
                Claim for review
              </button>
            )}
          </li>
        ))}
      </ul>
      {!busy && rows.length === 0 && (
        <p>No requests displayed. Sign in and reload if needed.</p>
      )}
      {cursor && (
        <button
          className={button}
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await load(cursor);
              setStatus("More requests loaded.");
            })
          }
        >
          Load more requests
        </button>
      )}
      <p>
        Minimized request evidence is retained for six years after completion
        under the approved retention policy.
      </p>
    </main>
  );
}
