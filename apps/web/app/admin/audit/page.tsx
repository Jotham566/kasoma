"use client";

import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type View = components["schemas"]["AuditActivity"];
const labels: Record<
  components["schemas"]["AuditActivityCount"]["category"],
  string
> = {
  CONTENT: "Content authoring & review",
  FLAGS: "Content flag activity",
  IMPORTS: "Draft imports",
  PRIVACY: "Privacy requests & preservation",
  ROLES: "Staff role changes",
  GRADING_REVIEW: "Independent grading review",
  OTHER: "Other recorded actions",
};

export default function Audit() {
  const [view, setView] = useState<View | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(
    "Load audit activity. ADMIN access required.",
  );

  async function refresh() {
    if (busy) return;
    setBusy(true);
    setStatus("Loading audit activity…");
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/admin/audit",
      );
      if (!result.data) {
        setView(null);
        setStatus(
          "Activity unavailable. Check ADMIN access, sign-in or rate limit.",
        );
        return;
      }
      setView(result.data);
      setStatus("Audit activity refreshed.");
    } catch {
      setView(null);
      setStatus(
        "Connection interrupted. No current activity result is available; retry.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="staff-page operations-page">
      <section className="surface-card operations-section">
        <p className="eyebrow">Staff operations</p>
        <h1 className="text-3xl font-semibold">Audit activity</h1>
        <p>
          A private overview of recorded actions in the last 24 hours.
          Individual records and personal details are not shown.
        </p>
        <div>
          <button
            type="button"
            className="ui-button ui-button-primary"
            disabled={busy}
            onClick={refresh}
          >
            {busy ? "Loading activity…" : "Refresh audit activity"}
          </button>
        </div>
        <p role="status">{status}</p>
      </section>
      {view && (
        <section
          className="surface-card operations-section"
          aria-label="Audit activity sample"
        >
          <h2 className="text-xl font-semibold">Recorded activity</h2>
          <p>
            {view.sampled_count.toLocaleString("en-UG")} actions in this sample.
            Window:{" "}
            {new Date(view.window_start).toLocaleString("en-UG", {
              timeZone: "Africa/Kampala",
            })}
            {" to "}
            {new Date(view.window_end).toLocaleString("en-UG", {
              timeZone: "Africa/Kampala",
            })}
            {" (Africa/Kampala)."}
          </p>
          {view.capped && (
            <p>
              Sample limit reached. Only the newest 10,000 actions are included;
              category counts may omit older activity in this window.
            </p>
          )}
          {view.sampled_count === 0 && (
            <p>No recorded actions in this window.</p>
          )}
          <dl>
            {view.counts.map(({ category, count }) => (
              <div key={category}>
                <dt>{labels[category]}</dt>
                <dd>{count.toLocaleString("en-UG")}</dd>
              </div>
            ))}
          </dl>
          <p>
            Counts include audited reads and retries where recorded. They do not
            represent unique people, incidents or confirmed problems. This
            sample does not establish complete audit coverage or retention
            compliance.
          </p>
        </section>
      )}
    </main>
  );
}
