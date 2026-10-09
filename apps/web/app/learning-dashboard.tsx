"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
const button = "ui-button ui-button-secondary";
const states: Record<Schema["ProgressSummary"]["display_state"], string> = {
  NOT_ENOUGH_EVIDENCE: "Not enough evidence",
  DEVELOPING_ESTIMATE: "Developing estimate",
  NEEDS_ATTENTION: "Needs attention",
  DEVELOPING: "Developing",
  STRONG: "Strong estimate",
};
const changes: Record<Schema["ProgressSummary"]["change"], string> = {
  NOT_ENOUGH_EVIDENCE: "Not enough evidence to compare recent change.",
  HIGHER: "The estimate is higher after your latest answer.",
  LOWER: "The estimate is lower after your latest answer.",
  UNCHANGED: "The estimate is unchanged after your latest answer.",
};
function date(value: string) {
  return new Intl.DateTimeFormat("en-UG", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Africa/Kampala",
  }).format(new Date(value));
}
function Summary({ summary }: { summary: Schema["ProgressSummary"] }) {
  return (
    <article
      className="surface-card progress-summary"
      aria-label={summary.name}
    >
      <h3 className="text-lg font-semibold">{summary.name}</h3>
      <p className="evidence-label">{states[summary.display_state]}</p>
      {summary.confidence >= 0.25 && summary.mastery !== null && (
        <p className="mastery-estimate">
          Estimated mastery: {Math.round(summary.mastery * 100)}%
        </p>
      )}
      <p>Evidence confidence: {Math.round(summary.confidence * 100)}%.</p>
      <p>
        {summary.evidence_count} recorded answers across{" "}
        {summary.assessed_skill_count} of {summary.mapped_skill_count} mapped
        skills.
      </p>
      <p>{changes[summary.change]}</p>
      {summary.last_evidence_at && (
        <p>
          Latest evidence:{" "}
          <time dateTime={summary.last_evidence_at}>
            {date(summary.last_evidence_at)}
          </time>{" "}
          (Kampala).
        </p>
      )}
    </article>
  );
}

export function LearningDashboard({ mode }: { mode: "progress" | "history" }) {
  const [subjects, setSubjects] = useState<Schema["SubjectView"][]>([]);
  const [subject, setSubject] = useState("");
  const [progress, setProgress] = useState<Schema["ProgressView"] | null>(null);
  const [entries, setEntries] = useState<Schema["SessionHistoryEntry"][]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState("Loading your learning record…");
  const generation = useRef(0);
  const api = () => apiClient("", crypto.randomUUID());
  function check<T>(result: { data?: T; error?: Schema["ErrorEnvelope"] }): T {
    if (!result.data)
      throw new Error(result.error?.error.code ?? "UNAVAILABLE");
    return result.data;
  }
  function fail(error: unknown) {
    const code = error instanceof Error ? error.message : "";
    if (["AUTH_REQUIRED", "CONSENT_REQUIRED", "FORBIDDEN"].includes(code)) {
      setReady(false);
      setProgress(null);
      setEntries([]);
      setCursor(null);
    }
    setStatus(
      code === "CONSENT_REQUIRED"
        ? "Complete your profile and consent to view your learning record."
        : code === "AUTH_REQUIRED"
          ? "Sign in to view your learning record."
          : code === "FORBIDDEN"
            ? "This subject is no longer selected in your profile. Reload your learning record."
            : "Could not load your learning record. Check your connection and retry; saved answers are safe.",
    );
  }
  async function load(
    id: string,
    next?: string,
    ticket = ++generation.current,
  ) {
    setBusy(true);
    setStatus("Loading your learning record…");
    if (!next) {
      setProgress(null);
      setEntries([]);
      setCursor(null);
      setSubject(id);
    }
    try {
      if (mode === "progress") {
        const data = check(
          await api().GET("/api/v1/me/progress", {
            params: { query: { subject_id: id } },
          }),
        );
        if (ticket !== generation.current) return;
        setProgress(data);
      } else {
        const data = check(
          await api().GET("/api/v1/me/session-history", {
            params: {
              query: { subject_id: id || undefined, cursor: next, limit: 10 },
            },
          }),
        );
        if (ticket !== generation.current) return;
        setEntries((old) =>
          next
            ? [
                ...old,
                ...data.data.filter(
                  (entry) => !old.some((v) => v.id === entry.id),
                ),
              ]
            : data.data,
        );
        setCursor(data.next_cursor);
      }
      setStatus("Learning record loaded.");
    } catch (error) {
      if (ticket === generation.current) fail(error);
    } finally {
      if (ticket === generation.current) setBusy(false);
    }
  }
  async function initialize() {
    const ticket = ++generation.current;
    setBusy(true);
    setReady(false);
    setProgress(null);
    setEntries([]);
    setCursor(null);
    setStatus("Loading your learning record…");
    try {
      const profile = check(await api().GET("/api/v1/me"));
      if (!profile.learning_allowed) throw new Error("CONSENT_REQUIRED");
      const catalog = check(await api().GET("/api/v1/curriculum/subjects"));
      if (ticket !== generation.current) return;
      const selected = catalog.filter((s) =>
        profile.subject_ids.includes(s.id),
      );
      setSubjects(selected);
      setReady(true);
      const requested =
        selected.find((s) => s.id === subject) ??
        selected.find(
          (s) =>
            s.id === new URLSearchParams(window.location.search).get("subject"),
        );
      await load(
        requested?.id ?? (mode === "history" ? "" : (selected[0]?.id ?? "")),
        undefined,
        ticket,
      );
    } catch (error) {
      if (ticket === generation.current) fail(error);
    } finally {
      if (ticket === generation.current) setBusy(false);
    }
  }
  useEffect(() => {
    // Fetch authorization on mount; loading state accompanies this external request.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void initialize();
    return () => {
      generation.current += 1;
    };
    // Initial authorization; reload and subject selection explicitly refresh server state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const action = progress?.next_action;
  const actionHref =
    action?.kind === "CONTINUE_DIAGNOSTIC"
      ? `/diagnostic?session=${action.session_id}`
      : action?.kind === "START_DIAGNOSTIC"
        ? `/diagnostic?subject=${subject}`
        : `/?subject=${subject}#recommendations`;
  return (
    <main className="learning-record-page">
      <header className="learning-record-intro">
        <p className="eyebrow">Your learning record</p>
        <h1 className="text-3xl font-semibold">
          {mode === "progress" ? "Your progress" : "Your session history"}
        </h1>
        <p>
          These are estimates from your recorded answers, not certified grades
          or comparisons with other learners. Synthetic development data only.
        </p>
      </header>
      <section
        className="surface-card record-controls"
        aria-label="Learning record controls"
      >
        <p role="status" aria-live="polite">
          {status}
        </p>
        <button
          className={button}
          disabled={busy}
          onClick={() => void initialize()}
        >
          Reload learning record
        </button>
        {ready && (
          <label className="record-subject">
            Subject
            <select
              className="ui-select"
              value={subject}
              disabled={busy}
              onChange={(event) => void load(event.target.value)}
            >
              {mode === "history" && (
                <option value="">All selected subjects</option>
              )}
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
        )}
        {!ready && !busy && (
          <Link className="ui-text-link" href="/onboarding" prefetch={false}>
            Open profile and sign in
          </Link>
        )}
      </section>
      {ready && progress && (
        <>
          <section aria-label="Subject progress" className="space-y-3">
            <h2 className="text-xl font-semibold">Subject overview</h2>
            <Summary summary={progress.subject} />
          </section>
          <p>
            Coverage is limited to mapped skills in this development catalog.
            More answers and broader coverage improve confidence.
          </p>
          <Link
            className="ui-button ui-button-primary"
            href={actionHref}
            prefetch={false}
          >
            {action?.label}
          </Link>
          <section aria-label="Topic progress" className="space-y-3">
            <h2 className="text-xl font-semibold">Topics</h2>
            <div className="progress-grid">
              {progress.topics.map((t) => (
                <Summary key={t.id} summary={t} />
              ))}
            </div>
          </section>
          <section aria-label="Competency progress" className="space-y-3">
            <h2 className="text-xl font-semibold">Competencies</h2>
            {progress.competencies.length ? (
              <div className="progress-grid">
                {progress.competencies.map((c) => (
                  <Summary key={c.id} summary={c} />
                ))}
              </div>
            ) : (
              <p>No reviewed competency mappings are available yet.</p>
            )}
          </section>
        </>
      )}
      {ready && mode === "history" && (
        <section aria-label="Session history" className="space-y-4">
          <h2 className="text-xl font-semibold">Recent sessions</h2>
          {!busy && !entries.length && status === "Learning record loaded." && (
            <div className="surface-card record-empty">
              <p>No sessions yet. Start a diagnostic or practise a topic.</p>
              <Link
                className="ui-button ui-button-primary"
                href="/diagnostic"
                prefetch={false}
              >
                Find your starting point
              </Link>
            </div>
          )}
          <p>
            Times shown in Kampala. Diagnostic scores stay hidden until
            completion.
          </p>
          {entries.map((entry) => (
            <article key={entry.id} className="surface-card history-entry">
              <h3 className="font-semibold">
                {entry.subject} —{" "}
                {entry.kind === "DIAGNOSTIC"
                  ? "Diagnostic"
                  : entry.kind === "REASSESSMENT"
                    ? "Reassessment"
                    : "Revision"}
              </h3>
              {entry.topic && <p>{entry.topic}</p>}
              <p>
                Status: {entry.status.toLowerCase()}. {entry.answered_count} of{" "}
                {entry.item_count} answers saved.
              </p>
              <p>
                Started:{" "}
                <time dateTime={entry.started_at}>
                  {date(entry.started_at)}
                </time>
              </p>
              {entry.completed_at && (
                <p>
                  Completed:{" "}
                  <time dateTime={entry.completed_at}>
                    {date(entry.completed_at)}
                  </time>
                </p>
              )}
              <Link
                className={button}
                prefetch={false}
                href={`${entry.kind === "DIAGNOSTIC" ? "/diagnostic" : "/revise"}?session=${entry.id}`}
              >
                {entry.status === "ACTIVE"
                  ? "Resume session"
                  : "Review session"}
              </Link>
            </article>
          ))}
          {cursor && (
            <button
              className={button}
              disabled={busy}
              onClick={() => void load(subject, cursor)}
            >
              Load older sessions
            </button>
          )}
        </section>
      )}
    </main>
  );
}
