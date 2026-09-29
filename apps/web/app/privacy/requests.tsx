"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
const api = () => apiClient("", crypto.randomUUID());
const button =
  "min-h-11 rounded border border-slate-500 px-4 py-2 disabled:opacity-50";
function check<T>(result: { data?: T; error?: Schema["ErrorEnvelope"] }): T {
  if (!result.data) throw new Error(result.error?.error.code ?? "UNAVAILABLE");
  return result.data;
}
export function Requests({ staff = false }: { staff?: boolean }) {
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
    setStatus("Saving or loading…");
    try {
      await action();
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      if (["AUTH_REQUIRED", "REAUTH_REQUIRED", "FORBIDDEN"].includes(code)) {
        setRows([]);
        setCursor(null);
        setPending(null);
      }
      setStatus(
        code === "AUTH_REQUIRED" || code === "REAUTH_REQUIRED"
          ? "Sign in again to verify your identity. Saved requests remain available."
          : code === "FORBIDDEN"
            ? "Administrator access is required."
            : code === "SELF_REVIEW_FORBIDDEN"
              ? "Another administrator must review your request."
              : code === "ALREADY_CLAIMED"
                ? "Another administrator is reviewing this request. Reload the list."
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
          ? "Administrators can claim requests for review. Export generation and deletion processing are not yet available."
          : "Request a copy of your data or ask for deletion. Learning consent is not required to make or track a request."}
      </p>
      <p>
        Requests remain pending until processed. This development service does
        not yet export or delete account data.
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
            <fieldset disabled={busy || !!pending} className="space-y-3">
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
              disabled={busy || (!pending && !affirmative)}
            >
              {pending ? "Retry request" : "Submit request"}
            </button>
          </form>
        </>
      )}
      <p role="status" aria-live="polite">
        {status}
      </p>
      <button
        className={button}
        disabled={busy}
        onClick={() =>
          void run(async () => {
            await load();
            setPending(null);
            setStatus("Requests loaded.");
          })
        }
      >
        Reload requests
      </button>
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
            <p>{row.status === "QUEUED" ? "Queued for review" : "In review"}</p>
            <p>
              Received:{" "}
              {new Date(row.created_at).toLocaleString("en-GB", {
                timeZone: "Africa/Kampala",
              })}{" "}
              (Kampala)
            </p>
            {staff && row.status === "QUEUED" && (
              <button
                className={button}
                disabled={busy || !!pending}
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
