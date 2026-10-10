"use client";

import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type S = components["schemas"];
type Operation = { key: string } & (
  | { kind: "create"; body: S["HoldInput"] }
  | { kind: "release"; hold: string; body: S["HoldRelease"] }
);
const button =
  "min-h-11 rounded border border-slate-500 px-4 py-2 disabled:opacity-50";
const api = () => apiClient("", crypto.randomUUID());
function check<T>(result: { data?: T; error?: S["ErrorEnvelope"] }): T {
  if (!result.data) throw new Error(result.error?.error.code ?? "UNAVAILABLE");
  return result.data;
}
const date = (value: string) =>
  new Date(value).toLocaleString("en-GB", { timeZone: "Africa/Kampala" });

export function LegalHolds({
  target,
  onChange,
}: {
  target: string;
  onChange: () => void;
}) {
  const [opened, setOpened] = useState(false);
  const [rows, setRows] = useState<S["HoldView"][]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [pending, setPending] = useState<Operation | null>(null);
  const [release, setRelease] = useState<string | null>(null);
  const [formVersion, setFormVersion] = useState(0);
  async function load(next?: string) {
    const page = check(
      await api().GET("/api/v1/admin/data-requests/{target}/holds", {
        params: { path: { target }, query: { cursor: next, limit: 20 } },
      }),
    );
    setRows((old) => (next ? [...old, ...page.data] : page.data));
    setCursor(page.next_cursor);
    setOpened(true);
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setStatus("Saving or loading holds…");
    try {
      await action();
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      if (
        [
          "AUTH_REQUIRED",
          "REAUTH_REQUIRED",
          "FORBIDDEN",
          "REVIEW_OWNERSHIP_REQUIRED",
          "SELF_REVIEW_FORBIDDEN",
        ].includes(code)
      ) {
        setRows([]);
        setCursor(null);
        setOpened(false);
        setPending(null);
        setStatus(
          "A recent sign-in by the independent administrator who claimed this request is required.",
        );
      } else if (
        [
          "HOLD_NOT_ACTIVE",
          "HOLD_END_REQUIRED",
          "RESOURCE_NOT_FOUND",
          "IDEMPOTENCY_CONFLICT",
          "VALIDATION_ERROR",
        ].includes(code)
      ) {
        setPending(null);
        setStatus(
          "The record or hold could not be accepted. Reload holds and check the record reference and future end date.",
        );
      } else if (code === "RATE_LIMITED") {
        setStatus(
          "Too many requests. Wait before retrying the same operation.",
        );
      } else
        setStatus(
          "Could not confirm the operation. Retry the same hold operation or reload holds.",
        );
    } finally {
      setBusy(false);
    }
  }
  async function send(operation: Operation) {
    setPending(operation);
    onChange();
    await run(async () => {
      if (operation.kind === "create")
        check(
          await api().POST("/api/v1/admin/data-requests/{target}/holds", {
            params: {
              path: { target },
              header: { "Idempotency-Key": operation.key },
            },
            body: operation.body,
          }),
        );
      else
        check(
          await api().POST(
            "/api/v1/admin/data-requests/{target}/holds/{hold}/release",
            {
              params: {
                path: { target, hold: operation.hold },
                header: { "Idempotency-Key": operation.key },
              },
              body: operation.body,
            },
          ),
        );
      setPending(null);
      setRelease(null);
      if (operation.kind === "create") setFormVersion((value) => value + 1);
      await load();
      setStatus("Hold decision recorded. Deletion remains disabled.");
    });
  }
  return (
    <section aria-label="Record legal holds" className="space-y-3">
      <button
        className={button}
        disabled={busy}
        onClick={() =>
          void run(async () => {
            await load();
            setPending(null);
            setRelease(null);
            setStatus("Holds loaded.");
          })
        }
      >
        {opened ? "Reload holds" : "Manage record holds"}
      </button>
      {status && <p role="status">{status}</p>}
      {pending && (
        <button
          className={button}
          disabled={busy}
          onClick={() => void send(pending)}
        >
          Retry hold operation
        </button>
      )}
      {opened && (
        <>
          <h3 className="font-semibold">Record legal holds</h3>
          <p>
            Record an already authorized preservation decision for one record.
            Other record types still require review. Expiry or release does not
            delete data. Decision references must be opaque UUIDs; do not enter
            names or legal narratives. For a grade, use its attempt reference;
            for a data request review, use its request reference. Other types
            use their own record reference. Each hold covers only the named
            record.
          </p>
          <form
            key={formVersion}
            onSubmit={(event) => {
              event.preventDefault();
              const form = new FormData(event.currentTarget);
              void send({
                kind: "create",
                key: crypto.randomUUID(),
                body: {
                  record_type: String(
                    form.get("record_type"),
                  ) as S["HoldInput"]["record_type"],
                  record_id: String(form.get("record_id")),
                  decision_reference: String(form.get("decision_reference")),
                  reason: String(
                    form.get("reason"),
                  ) as S["HoldInput"]["reason"],
                  expires_at: new Date(
                    String(form.get("expires_at")),
                  ).toISOString(),
                  affirmative: true,
                },
              });
            }}
          >
            <fieldset disabled={busy || !!pending} className="space-y-3">
              <legend>Create a record hold</legend>
              <label className="block">
                Record type
                <select
                  name="record_type"
                  defaultValue="DATA_REQUEST"
                  className="block min-h-11 border"
                >
                  <option value="DATA_REQUEST">Data request</option>
                  <option value="CONSENT">Consent</option>
                  <option value="ATTEMPT">Attempt</option>
                  <option value="CONTENT_FLAG">Content flag</option>
                  <option value="GRADE">Grade (attempt reference)</option>
                  <option value="MASTERY_EVIDENCE">Mastery evidence</option>
                  <option value="MASTERY_HISTORY">Mastery history</option>
                  <option value="FLAG_HISTORY">Flag history</option>
                  <option value="GRADING_HISTORY">Grading history</option>
                  <option value="DATA_REQUEST_REVIEW">
                    Data request review (request reference)
                  </option>
                </select>
              </label>
              <label className="block">
                Record reference
                <input
                  name="record_id"
                  defaultValue={target}
                  required
                  pattern="[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
                  className="block min-h-11 w-full border"
                />
              </label>
              <label className="block">
                Decision reference
                <input
                  name="decision_reference"
                  required
                  pattern="[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
                  className="block min-h-11 w-full border"
                />
              </label>
              <label className="block">
                Reason
                <select name="reason" className="block min-h-11 border">
                  <option value="LEGAL_OBLIGATION">Legal obligation</option>
                  <option value="SECURITY_INVESTIGATION">
                    Security investigation
                  </option>
                </select>
              </label>
              <label className="block">
                Hold ends (your device time)
                <input
                  name="expires_at"
                  type="datetime-local"
                  required
                  className="block min-h-11 border"
                />
              </label>
              <label className="flex min-h-11 items-center gap-3">
                <input type="checkbox" required />I confirm an authorized
                preservation decision for this record and period.
              </label>
              <button className={button}>Create hold</button>
            </fieldset>
          </form>
          {rows.length === 0 && <p>No registered holds for this request.</p>}
          <ul className="space-y-3">
            {rows.map((row) => (
              <li key={row.id} className="border p-3 space-y-2">
                <p>
                  Hold: {row.id} — {row.status}
                </p>
                <p>
                  Record: {row.record_type} / {row.record_id}
                </p>
                <p>
                  Decision: {row.decision_reference} ({row.reason})
                </p>
                <p>
                  Created: {date(row.created_at)} (Kampala). Ends:{" "}
                  {date(row.expires_at)} (Kampala).
                </p>
                {row.released_at && (
                  <p>
                    Released: {date(row.released_at)} (Kampala). Decision:{" "}
                    {row.release_reference}
                  </p>
                )}
                {row.status === "ACTIVE" && (
                  <button
                    className={button}
                    disabled={busy || !!pending}
                    onClick={() => setRelease(row.id)}
                  >
                    Release hold {row.id}
                  </button>
                )}
              </li>
            ))}
          </ul>
          {cursor && (
            <button
              className={button}
              disabled={busy || !!pending}
              onClick={() =>
                void run(async () => {
                  await load(cursor);
                  setStatus("More holds loaded.");
                })
              }
            >
              Load more holds
            </button>
          )}
          {release && (
            <form
              key={release}
              onSubmit={(event) => {
                event.preventDefault();
                const form = new FormData(event.currentTarget);
                void send({
                  kind: "release",
                  key: crypto.randomUUID(),
                  hold: release,
                  body: {
                    decision_reference: String(form.get("reference")),
                    affirmative: true,
                  },
                });
              }}
            >
              <fieldset disabled={busy || !!pending} className="space-y-3">
                <legend>Release hold {release}</legend>
                <label className="block">
                  Release decision reference
                  <input
                    name="reference"
                    required
                    pattern="[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
                    className="block min-h-11 w-full border"
                  />
                </label>
                <label className="flex min-h-11 items-center gap-3">
                  <input type="checkbox" required />I confirm an authorized
                  release decision for this hold.
                </label>
                <button className={button}>Confirm release</button>
              </fieldset>
            </form>
          )}
          <p>
            Minimized hold evidence is retained for six years after request
            completion. All timestamps above use Kampala time.
          </p>
        </>
      )}
    </section>
  );
}
