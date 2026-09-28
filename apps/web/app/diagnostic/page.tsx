"use client";

import Link from "next/link";
import { FlagForm } from "../flag-form";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";
import { Status } from "@kasoma/ui";

type Schema = components["schemas"];
const button =
  "min-h-11 rounded border border-slate-500 px-4 py-2 disabled:opacity-50";
const field = "block w-full min-h-11 rounded border border-slate-500 p-2";
function client() {
  return apiClient("", crypto.randomUUID());
}
function value<T>(result: {
  data?: T;
  error?: Schema["ErrorEnvelope"];
  response: Response;
}): T {
  if (!result.response.ok || result.data === undefined)
    throw new Error(result.error?.error.code ?? "UNAVAILABLE");
  return result.data;
}
const messages: Record<string, string> = {
  CONSENT_REQUIRED:
    "Complete your profile and required consent before starting.",
  AUTH_REQUIRED: "Sign in again. Your saved answers are retained.",
  FORBIDDEN: "Learning access is unavailable. Check your profile and consent.",
  INSUFFICIENT_CONTENT:
    "There are not enough approved questions for this diagnostic. Please try later.",
  CONTENT_NOT_APPROVED:
    "A question was withdrawn. End this diagnostic and try again later.",
  VALIDATION_FAILED:
    "Check your answer's format and unit. It has not been saved.",
  ITEM_ALREADY_ANSWERED:
    "This answer is already saved. Reload your diagnostic.",
  SESSION_NOT_ACTIVE: "This diagnostic has ended. Reload your saved progress.",
};
export default function Diagnostic() {
  const [subjects, setSubjects] = useState<Schema["SubjectView"][]>([]);
  const [subject, setSubject] = useState("");
  const [session, setSession] = useState<Schema["DiagnosticView"] | null>(null);
  const [item, setItem] = useState<Schema["LearnerItem"] | null>(null);
  const [flagAttempt, setFlagAttempt] = useState("");
  const [choice, setChoice] = useState("");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [number, setNumber] = useState("");
  const [unit, setUnit] = useState("");
  const [busy, setBusy] = useState(true);
  const [status, setStatus] = useState("Loading diagnostic options…");
  const retry = useRef<{ fingerprint: string; key: string } | null>(null);
  function key(body: unknown) {
    const fingerprint = JSON.stringify(body);
    if (retry.current?.fingerprint !== fingerprint)
      retry.current = { fingerprint, key: crypto.randomUUID() };
    return retry.current.key;
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setStatus("Saving or loading…");
    try {
      await action();
      setStatus("");
    } catch (error) {
      const code = error instanceof Error ? error.message : "";
      setStatus(
        messages[code] ??
          "Check your connection, then retry or reload. Saved answers are safe.",
      );
      if (["AUTH_REQUIRED", "CONSENT_REQUIRED", "FORBIDDEN"].includes(code)) {
        setItem(null);
        setSession(null);
        setSubjects([]);
      }
    } finally {
      setBusy(false);
    }
  }
  async function load(id: string) {
    setItem(null);
    const state = value(
      await client().GET("/api/v1/diagnostics/{session_id}", {
        params: { path: { session_id: id } },
      }),
    );
    setSession(state);
    window.history.replaceState(null, "", `/diagnostic?session=${state.id}`);
    if (state.status === "ACTIVE") {
      const next = value(
        await client().GET("/api/v1/sessions/{session_id}/next-item", {
          params: { path: { session_id: id } },
        }),
      );
      setChoice("");
      setSelectedIds([]);
      setNumber("");
      setUnit(
        next.response_spec.type === "NUMERIC"
          ? (next.response_spec.unit_options[0] ?? "")
          : "",
      );
      setItem(next);
    }
  }
  async function initialize() {
    const profile = value(await client().GET("/api/v1/me"));
    if (!profile.learning_allowed) throw new Error("CONSENT_REQUIRED");
    const all = value(await client().GET("/api/v1/curriculum/subjects"));
    const selected = all.filter((s) => profile.subject_ids.includes(s.id));
    setSubjects(selected);
    const requested =
      selected.find(
        (s) =>
          s.id === new URLSearchParams(window.location.search).get("subject"),
      ) ?? selected[0];
    setSubject(requested?.id ?? "");
    const id = new URLSearchParams(window.location.search).get("session");
    if (id) await load(id);
  }
  useEffect(() => {
    async function boot() {
      try {
        await initialize();
        setStatus("");
      } catch (error) {
        setStatus(
          messages[error instanceof Error ? error.message : ""] ??
            "Check your connection, then reload.",
        );
      } finally {
        setBusy(false);
      }
    }
    void boot();
    // Initialization is once; actions explicitly reload durable server state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <Link href="/" className="inline-flex min-h-11 items-center underline">
        Kasoma home
      </Link>
      <h1 className="text-3xl font-semibold">Subject diagnostic</h1>
      <p>
        Synthetic development questions only. Gather initial evidence across
        your subject. This is an estimate, not a certified grade.
      </p>
      <p>
        15 questions, untimed and resumable. No hints, solutions or corrective
        feedback during the diagnostic.
      </p>
      <Status>{status}</Status>
      <nav
        aria-label="Learning history and progress"
        className="flex flex-wrap gap-4"
      >
        <Link
          className="inline-flex min-h-11 items-center underline"
          href="/progress"
        >
          Progress
        </Link>
        <Link
          className="inline-flex min-h-11 items-center underline"
          href="/history"
        >
          History
        </Link>
      </nav>
      <Link
        href="/onboarding"
        className="inline-flex min-h-11 items-center underline"
      >
        Profile, consent and sign in
      </Link>
      <button
        className={button}
        disabled={busy}
        onClick={() => void run(initialize)}
      >
        Reload saved diagnostic
      </button>
      {!session && subjects.length > 0 && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void run(async () => {
              const body: Schema["StartDiagnostic"] = {
                subject_id: subject,
                channel: "WEB",
              };
              const plan = value(
                await client().POST("/api/v1/diagnostics", {
                  body,
                  params: { header: { "Idempotency-Key": key(body) } },
                }),
              );
              await load(plan.id);
            });
          }}
        >
          <label>
            Subject
            <select
              className={field}
              value={subject}
              disabled={busy}
              onChange={(event) => setSubject(event.target.value)}
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <button className={button} disabled={busy || !subject}>
            Start or resume diagnostic
          </button>
        </form>
      )}
      {session && (
        <p>
          {session.answered_count} of {session.item_count} answers saved
        </p>
      )}
      {item && session && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void run(async () => {
              const body: Schema["SubmitAnswer"] = {
                session_item_id: item.session_item_id,
                response:
                  item.response_spec.type === "NUMERIC"
                    ? { type: "NUMERIC", value: number, unit }
                    : item.response_spec.type === "MULTIPLE_CHOICE"
                      ? { type: "MULTIPLE_CHOICE", choice_ids: selectedIds }
                      : { type: "SINGLE_CHOICE", choice_id: choice },
              };
              const saved = value(
                await client().POST("/api/v1/sessions/{session_id}/attempts", {
                  params: {
                    path: { session_id: session.id },
                    header: { "Idempotency-Key": key(body) },
                  },
                  body,
                }),
              );
              if (saved.status !== "SAVED") throw new Error("UNAVAILABLE");
              await load(session.id);
            });
          }}
        >
          <fieldset disabled={busy} className="space-y-4">
            <legend className="font-semibold">Question {item.position}</legend>
            {item.prompt_blocks.map((block, index) => (
              <p key={index}>{block.content}</p>
            ))}
            {item.response_spec.type === "MULTIPLE_CHOICE" && (
              <p>
                Select all that apply. Full credit requires every correct option
                and no others.
              </p>
            )}
            {item.response_spec.type !== "NUMERIC" ? (
              item.response_spec.choices.map((option) => (
                <label
                  key={option.id}
                  className="flex min-h-11 items-center gap-3"
                >
                  <input
                    type={
                      item.response_spec.type === "MULTIPLE_CHOICE"
                        ? "checkbox"
                        : "radio"
                    }
                    name="answer"
                    value={option.id}
                    checked={
                      item.response_spec.type === "MULTIPLE_CHOICE"
                        ? selectedIds.includes(option.id)
                        : choice === option.id
                    }
                    onChange={() =>
                      item.response_spec.type === "MULTIPLE_CHOICE"
                        ? setSelectedIds((ids) =>
                            ids.includes(option.id)
                              ? ids.filter((id) => id !== option.id)
                              : [...ids, option.id].sort(),
                          )
                        : setChoice(option.id)
                    }
                    required={item.response_spec.type === "SINGLE_CHOICE"}
                  />
                  {option.text}
                </label>
              ))
            ) : (
              <>
                <p>
                  Accepted forms: {item.response_spec.accepted_forms.join(", ")}
                  .{" "}
                  {item.response_spec.significant_figures_policy === "EXACT"
                    ? `Use ${item.response_spec.significant_figures} significant figures. Trailing zeros count after a decimal point or in a scientific mantissa.`
                    : "No significant-figure restriction."}
                </p>
                <label>
                  Numeric value
                  <input
                    className={field}
                    value={number}
                    maxLength={64}
                    required
                    onChange={(event) => setNumber(event.target.value)}
                  />
                </label>
                <label>
                  Answer unit
                  <select
                    className={field}
                    value={unit}
                    onChange={(event) => setUnit(event.target.value)}
                  >
                    {item.response_spec.unit_options.map((u) => (
                      <option key={u} value={u}>
                        {u || "No unit"}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            )}
            <button
              className={button}
              disabled={
                item.response_spec.type === "MULTIPLE_CHOICE" &&
                selectedIds.length === 0
              }
            >
              Save answer and continue
            </button>
          </fieldset>
        </form>
      )}
      {!!session?.answered_attempts.length && (
        <section
          aria-label="Report a diagnostic question"
          className="space-y-3"
        >
          <h2 className="text-xl font-semibold">Report a saved question</h2>
          <label>
            Saved question
            <select
              className={field}
              value={
                flagAttempt || session.answered_attempts.at(-1)!.attempt_id
              }
              onChange={(e) => setFlagAttempt(e.target.value)}
            >
              {session.answered_attempts.map((a) => (
                <option key={a.attempt_id} value={a.attempt_id}>
                  Question {a.position}
                </option>
              ))}
            </select>
          </label>
          <FlagForm
            key={flagAttempt || session.answered_attempts.at(-1)!.attempt_id}
            attemptId={
              flagAttempt || session.answered_attempts.at(-1)!.attempt_id
            }
          />
        </section>
      )}
      {session?.result && (
        <section aria-label="Diagnostic results" className="space-y-4">
          <h2 className="text-2xl font-semibold">Your initial evidence</h2>
          <p>
            These estimates can change with more independent answers. They are
            not examination marks.
          </p>
          <ul className="space-y-3">
            {session.result.skills.map((skill) => (
              <li key={`${skill.concept_id}/${skill.competency_id}`}>
                <h3 className="font-semibold">
                  {skill.topic} — {skill.competency}
                </h3>
                <p>
                  {skill.display_state === "NOT_ENOUGH_EVIDENCE"
                    ? "Not enough evidence"
                    : skill.display_state === "DEVELOPING_ESTIMATE"
                      ? "Developing estimate"
                      : skill.display_state.replaceAll("_", " ").toLowerCase()}
                </p>
                <p>
                  Estimate: {Math.round(skill.mastery * 100)}%. Evidence
                  confidence: {Math.round(skill.confidence * 100)}%. Based on{" "}
                  {skill.evidence_count} answers.
                </p>
              </li>
            ))}
          </ul>
          <h2 className="text-xl font-semibold">What to do next</h2>
          <p>{session.result.recommendation.learner_text}</p>
          {session.result.recommendation.topic_id && (
            <Link
              className="inline-flex min-h-11 items-center underline"
              href={`/revise?topic=${session.result.recommendation.topic_id}&subject=${session.subject_id}`}
            >
              Practise this topic
            </Link>
          )}
        </section>
      )}
      {session?.status === "ACTIVE" && (
        <button
          className={button}
          disabled={busy}
          onClick={() =>
            void run(async () => {
              value(
                await client().POST("/api/v1/sessions/{session_id}/abandon", {
                  params: { path: { session_id: session.id } },
                }),
              );
              await load(session.id);
            })
          }
        >
          End diagnostic
        </button>
      )}
      {session && ["ABANDONED", "EXPIRED"].includes(session.status) && (
        <p>This diagnostic has ended. Your saved answers are retained.</p>
      )}
    </main>
  );
}
