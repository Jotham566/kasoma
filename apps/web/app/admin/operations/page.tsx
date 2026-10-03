"use client";

import Link from "next/link";
import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type View = components["schemas"]["OperationsView"];
const messages: Record<
  components["schemas"]["OperationAlert"]["code"],
  string
> = {
  DATABASE_DOWN: "Database unavailable",
  REDIS_DOWN: "Redis unavailable",
  WORKER_HEARTBEAT_MISSING: "Monitoring worker heartbeat unavailable",
  IMPORT_FAILED: "Failed draft imports need investigation",
  IMPORT_STALLED: "Queued imports have exceeded the age threshold",
  FLAG_BACKLOG: "Unresolved flag backlog exceeded its threshold",
  HIGH_PRIORITY_FLAGS: "High-priority flags need attention",
};

export default function Operations() {
  const [view, setView] = useState<View | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(
    "Load the current operational snapshot. ADMIN access required.",
  );
  async function refresh() {
    setBusy(true);
    setStatus("Loading operational snapshot…");
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/admin/operations",
      );
      if (!result.data) {
        setView(null);
        setStatus(
          "Snapshot unavailable. Check ADMIN access, sign-in or rate limit.",
        );
        return;
      }
      setView(result.data);
      setStatus("Operational snapshot refreshed.");
    } catch {
      setView(null);
      setStatus(
        "Connection interrupted. No current health result is available; retry.",
      );
    } finally {
      setBusy(false);
    }
  }
  const counters = view?.counts
    ? ([
        ["Queued imports", view.counts.queued_imports],
        ["Failed imports in the last 24 hours", view.counts.failed_imports_24h],
        ["Unresolved content flags", view.counts.unresolved_flags],
        ["High-priority unresolved flags", view.counts.high_priority_flags],
      ] as const)
    : [];
  return (
    <main className="mx-auto max-w-3xl p-6 space-y-4">
      <Link className="underline" href="/admin/content">
        Content workspace
      </Link>
      <h1 className="text-3xl font-semibold">Operations health</h1>
      <p>
        Local service and queue monitoring. Refresh for current values; this
        page does not refresh automatically.
      </p>
      <button
        className="rounded border px-4 py-3 disabled:opacity-50"
        disabled={busy}
        onClick={() => void refresh()}
      >
        Refresh operations
      </button>
      <p role="status">{status}</p>
      {view && (
        <>
          <p>
            Sampled{" "}
            {new Intl.DateTimeFormat("en-UG", {
              timeZone: "Africa/Kampala",
              dateStyle: "medium",
              timeStyle: "medium",
            }).format(new Date(view.generated_at))}{" "}
            (Africa/Kampala).
          </p>
          <h2 className="text-xl font-semibold">Service health</h2>
          <ul>
            <li>Database: {view.health.database}</li>
            <li>Redis: {view.health.redis}</li>
            <li>Monitoring worker: {view.worker}</li>
          </ul>
          <h2 className="text-xl font-semibold">Active alerts</h2>
          {view.alerts.length === 0 ? (
            <p>No configured thresholds breached in this snapshot.</p>
          ) : (
            <ul>
              {view.alerts.map((alert) => (
                <li key={alert.code}>
                  {alert.severity}: {messages[alert.code]} (observed{" "}
                  {alert.observed}, threshold {alert.threshold}).
                </li>
              ))}
            </ul>
          )}
          <h2 className="text-xl font-semibold">Queue and content workload</h2>
          {view.counts ? (
            <>
              <table className="w-full text-left">
                <thead>
                  <tr>
                    <th scope="col">Metric</th>
                    <th scope="col">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {counters.map(([label, count]) => (
                    <tr key={label}>
                      <th className="py-2 font-normal" scope="row">
                        {label}
                      </th>
                      <td>
                        {count.at_least ? "At least " : ""}
                        {count.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p>
                Oldest queued import: {view.counts.oldest_import_seconds}{" "}
                seconds. Alert threshold: {view.thresholds.import_age_seconds}{" "}
                seconds.
              </p>
              <p>
                Failed-import threshold: {view.thresholds.failed_imports}. Flag
                backlog threshold: {view.thresholds.unresolved_flags}.
              </p>
            </>
          ) : (
            <p>
              Workload counts unavailable. Do not interpret missing values as
              zero.
            </p>
          )}
          <Link className="underline" href="/admin/flags">
            Review content flags
          </Link>
          <h2 className="text-xl font-semibold">
            Instrumentation still pending
          </h2>
          <p>
            AI and messaging usage, grading-failure rates, latency
            distributions, mastery lag and WhatsApp failures are not yet
            measured here. No external notifications are sent.
          </p>
        </>
      )}
    </main>
  );
}
