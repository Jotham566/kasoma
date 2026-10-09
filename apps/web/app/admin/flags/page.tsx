"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
const api = () => apiClient("", crypto.randomUUID());
const button = "ui-button ui-button-secondary";
const field = "ui-select";
export default function Flags() {
  const [rows, setRows] = useState<Schema["FlagSummary"][]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [selected, setSelected] = useState<Schema["FlagDetail"] | null>(null);
  const [filter, setFilter] = useState<Schema["FlagSummary"]["status"] | "">(
    "",
  );
  const [priority, setPriority] =
    useState<Schema["FlagUpdate"]["priority"]>("NORMAL");
  const [decision, setDecision] =
    useState<Schema["FlagUpdate"]["status"]>("IN_REVIEW");
  const [resolution, setResolution] = useState("");
  const [busy, setBusy] = useState(true);
  const [status, setStatus] = useState("Loading flag queue…");
  const [pending, setPending] = useState<{
    key: string;
    id: string;
    body: Schema["FlagUpdate"];
  } | null>(null);
  const mounted = useRef(true);
  function check<T>(result: { data?: T; error?: Schema["ErrorEnvelope"] }): T {
    if (!result.data)
      throw new Error(result.error?.error.code ?? "UNAVAILABLE");
    return result.data;
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setStatus("Saving or loading flags…");
    try {
      await action();
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      if (["FORBIDDEN", "AUTH_REQUIRED", "REAUTH_REQUIRED"].includes(code)) {
        setSelected(null);
        setRows([]);
        setCursor(null);
        setResolution("");
        setPending(null);
      }
      setStatus(
        code === "VERSION_CONFLICT"
          ? "Another reviewer changed this flag. Reload the selected flag before trying again."
          : code === "SELF_REVIEW_FORBIDDEN"
            ? "An independent reviewer must triage this content."
            : code === "AUTH_REQUIRED" || code === "REAUTH_REQUIRED"
              ? "Sign in again for staff access."
              : code === "FORBIDDEN"
                ? "Reviewer or administrator access is required."
                : "Could not confirm this operation. Retry the same decision or reload the flag queue.",
      );
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  async function load(next?: string, statusFilter = filter) {
    const page = check(
      await api().GET("/api/v1/admin/content-flags", {
        params: {
          query: { cursor: next, limit: 20, status: statusFilter || undefined },
        },
      }),
    );
    if (!mounted.current) return;
    setRows((old) =>
      next
        ? [...old, ...page.data.filter((r) => !old.some((o) => o.id === r.id))]
        : page.data,
    );
    setCursor(page.next_cursor);
    setStatus("Flag queue loaded.");
  }
  async function inspect(id: string) {
    const flag = check(
      await api().GET("/api/v1/admin/content-flags/{flag_id}", {
        params: { path: { flag_id: id } },
      }),
    );
    setSelected(flag);
    setPriority(flag.priority);
    setDecision("IN_REVIEW");
    setResolution("");
    setPending(null);
    setStatus("Flag loaded. Access is audited.");
  }
  useEffect(() => {
    mounted.current = true;
    // Fetch the protected queue on mount; loading state accompanies the external request.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void run(() => load());
    return () => {
      mounted.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  async function save() {
    if (!selected) return;
    const request = pending ?? {
      key: crypto.randomUUID(),
      id: selected.id,
      body: {
        expected_revision: selected.revision,
        status: decision,
        priority,
        claim: true,
        resolution: decision === "IN_REVIEW" ? "" : resolution.trim(),
      },
    };
    setPending(request);
    const flag = check(
      await api().PATCH("/api/v1/admin/content-flags/{flag_id}", {
        params: {
          path: { flag_id: request.id },
          header: { "Idempotency-Key": request.key },
        },
        body: request.body,
      }),
    );
    setSelected(flag);
    setPending(null);
    setResolution("");
    setDecision("IN_REVIEW");
    setRows((old) => old.map((r) => (r.id === flag.id ? flag : r)));
    setStatus("Triage decision saved and audited. Grades are unchanged.");
  }
  return (
    <main className="staff-page">
      <nav className="flex flex-wrap gap-4" aria-label="Staff navigation">
        <Link className={button} href="/admin/content">
          Content review
        </Link>
        <Link className={button} href="/onboarding">
          Profile and sign in
        </Link>
      </nav>
      <h1 className="text-3xl font-semibold">Learner flags</h1>
      <p>
        Confidential synthetic reports. Access is audited. Do not copy personal
        details into resolutions. This queue does not send messages or alter
        grades.
      </p>
      <p role="status" aria-live="polite">
        {status}
      </p>
      <button
        className={button}
        disabled={busy}
        onClick={() =>
          void run(async () => {
            setSelected(null);
            setPending(null);
            setResolution("");
            await load();
          })
        }
      >
        Reload flag queue
      </button>
      <label className="block">
        Filter status
        <select
          className={field}
          disabled={busy || !!pending}
          value={filter}
          onChange={(e) => {
            const value = e.target.value as typeof filter;
            setFilter(value);
            setSelected(null);
            void run(() => load(undefined, value));
          }}
        >
          <option value="">All statuses</option>
          {["OPEN", "IN_REVIEW", "RESOLVED", "DISMISSED"].map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <section aria-label="Flag queue" className="space-y-3">
        <h2 className="text-xl font-semibold">Reports</h2>
        {!rows.length && !busy && status === "Flag queue loaded." && (
          <p>No flags in this view.</p>
        )}
        {rows.map((row) => (
          <article key={row.id} className="surface-card staff-record">
            <p>
              {row.category} · {row.priority} · {row.status}
            </p>
            <p>{row.owner_id ? "Assigned to a reviewer" : "Unassigned"}</p>
            <button
              className={button}
              disabled={busy || !!pending}
              onClick={() => void run(() => inspect(row.id))}
            >
              Review report
            </button>
          </article>
        ))}
        {cursor && (
          <button
            className={button}
            disabled={busy || !!pending}
            onClick={() => void run(() => load(cursor))}
          >
            Load older reports
          </button>
        )}
      </section>
      {selected && (
        <section
          aria-label="Selected flag"
          className="surface-card staff-record"
        >
          <h2 className="text-xl font-semibold">Report details</h2>
          <p>
            Category: {selected.category}. Status: {selected.status}. Revision:{" "}
            {selected.revision}.
          </p>
          <p className="whitespace-pre-wrap">
            {selected.comment || "No comment provided."}
          </p>
          <Link
            className={button}
            href={`/admin/content?version=${selected.item_version_id}`}
          >
            Inspect reported content version
          </Link>
          <button
            className={button}
            disabled={busy}
            onClick={() => void run(() => inspect(selected.id))}
          >
            Reload selected flag
          </button>
          {selected.resolution && (
            <p className="whitespace-pre-wrap">
              Recorded resolution: {selected.resolution}
            </p>
          )}
          <form
            className="space-y-3"
            onSubmit={(e) => {
              e.preventDefault();
              void run(save);
            }}
          >
            <fieldset disabled={busy || !!pending} className="space-y-3">
              <legend>Claim and record a triage decision</legend>
              <label>
                Priority
                <select
                  className={field}
                  value={priority}
                  onChange={(e) =>
                    setPriority(e.target.value as typeof priority)
                  }
                >
                  <option>NORMAL</option>
                  <option>HIGH</option>
                </select>
              </label>
              <label>
                Decision
                <select
                  className={field}
                  aria-label="Decision"
                  value={decision}
                  onChange={(e) =>
                    setDecision(e.target.value as typeof decision)
                  }
                >
                  <option value="IN_REVIEW">Claim or reopen for review</option>
                  <option value="RESOLVED">Resolve</option>
                  <option value="DISMISSED">Dismiss</option>
                </select>
              </label>
              <label>
                Resolution note
                <textarea
                  className={field}
                  rows={3}
                  maxLength={1000}
                  required={decision !== "IN_REVIEW"}
                  disabled={decision === "IN_REVIEW"}
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                />
              </label>
            </fieldset>
            <button className={button} disabled={busy}>
              {pending ? "Retry triage decision" : "Save triage decision"}
            </button>
          </form>
          <h3 className="font-semibold">Decision history</h3>
          <ol>
            {selected.history.map((h) => (
              <li key={h.revision}>
                Revision {h.revision}: {h.status}, {h.priority} —{" "}
                {new Date(h.created_at).toLocaleString("en-UG", {
                  timeZone: "Africa/Kampala",
                })}{" "}
                (Kampala)
              </li>
            ))}
          </ol>
        </section>
      )}
    </main>
  );
}
