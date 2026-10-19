"use client";

import Link from "next/link";
import { FlagForm } from "../flag-form";
import { useCallback, useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";
import { SavedProgress, Status } from "@kasoma/ui";
import { Hints } from "./hints";
import { PendingFeedback } from "./pending-feedback";

type Schema = components["schemas"];
const button = "ui-button ui-button-secondary";
const input = "ui-input";
function client() {
  return apiClient("", crypto.randomUUID());
}
function value<T>(result: {
  data?: T;
  error?: Schema["ErrorEnvelope"];
  response: Response;
}): T {
  if (!result.response.ok || result.data === undefined)
    throw new Error(result.error?.error.code ?? "SERVICE_UNAVAILABLE");
  return result.data;
}
const messages: Record<string, string> = {
  REASSESSMENT_UNAVAILABLE:
    "No unseen suitable question is available yet. Continue your practice or try later.",
  REASSESSMENT_NOT_ALLOWED: "Reassessment starts from revision feedback.",
  VALIDATION_FAILED:
    "Check the number, unit and accepted form, then submit again. Your answer has not been saved.",
  AUTH_REQUIRED: "Sign in again to continue. Your saved answers are retained.",
  CONSENT_REQUIRED:
    "Learning access is paused. Complete your profile and required consent first.",
  FORBIDDEN: "This subject is not selected in your profile.",
  INSUFFICIENT_CONTENT:
    "There are not enough available questions for a new session in this topic. Choose another topic or try later.",
  CONTENT_NOT_APPROVED:
    "This question has been withdrawn. End this session and choose another topic.",
  RESOURCE_NOT_FOUND:
    "This session or question is unavailable. Reload your saved progress.",
  SESSION_NOT_ACTIVE:
    "This session has ended or expired. Reload your saved progress.",
  ITEM_ALREADY_ANSWERED:
    "This answer is already saved. Reload your saved progress.",
  IDEMPOTENCY_CONFLICT:
    "This submission changed after a retry. Reload your saved progress.",
};

export default function Revise() {
  const [subjects, setSubjects] = useState<Schema["SubjectView"][]>([]);
  const [topics, setTopics] = useState<Schema["TopicView"][]>([]);
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [active, setActive] = useState<Schema["SessionView"][]>([]);
  const [session, setRevisionSession] = useState<Schema["SessionView"] | null>(
    null,
  );
  function setSession(
    state: Schema["SessionView"] | Schema["DiagnosticView"] | null,
  ) {
    if (state && !("answers" in state)) throw new Error("FORBIDDEN");
    setRevisionSession(state);
  }
  const [item, setItem] = useState<Schema["LearnerItem"] | null>(null);
  const [grade, setGrade] = useState<Schema["AnsweredItem"]["grade"] | null>(
    null,
  );
  const [shortText, setShortText] = useState("");
  const [solution, setSolution] = useState("");
  const [choice, setChoice] = useState("");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [numericValue, setNumericValue] = useState("");
  const [unit, setUnit] = useState("");
  const [busy, setBusy] = useState(true);
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState("Loading your practice options…");
  const retry = useRef<{ fingerprint: string; key: string } | null>(null);
  const pollingError = useCallback((code: string) => {
    setStatus(
      code === "USAGE_LIMIT_REACHED"
        ? "Please wait a minute before checking feedback again. Your answer is saved."
        : (messages[code] ??
            "Feedback could not be checked. Your saved answer is retained."),
    );
    if (["AUTH_REQUIRED", "CONSENT_REQUIRED", "FORBIDDEN"].includes(code)) {
      setReady(false);
      setItem(null);
      setGrade(null);
      setSession(null);
      setSolution("");
    }
  }, []);
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
          "Check your connection, then retry. Saved answers are safe.",
      );
      if (["AUTH_REQUIRED", "CONSENT_REQUIRED", "FORBIDDEN"].includes(code)) {
        setReady(false);
        setItem(null);
        setGrade(null);
        setSolution("");
        setSession(null);
      }
    } finally {
      setBusy(false);
    }
  }
  async function loadTopics(id: string) {
    setSubject(id);
    setTopic("");
    setTopics([]);
    const result = value(
      await client().GET("/api/v1/curriculum/subjects/{subject_id}/topics", {
        params: { path: { subject_id: id } },
      }),
    );
    setTopics(result);
    setTopic(result[0]?.id ?? "");
  }
  async function loadSession(id: string, showLast = true) {
    setItem(null);
    setGrade(null);
    setSolution("");
    setChoice("");
    setSelectedIds([]);
    setNumericValue("");
    setShortText("");
    setUnit("");
    const state = value(
      await client().GET("/api/v1/sessions/{session_id}", {
        params: { path: { session_id: id } },
      }),
    );
    if (!("answers" in state)) throw new Error("FORBIDDEN");
    setSession(state);
    window.history.replaceState(null, "", `/revise?session=${state.id}`);
    const last = state.answers.at(-1);
    if (showLast && last) setGrade(last.grade);
    else if (state.status === "ACTIVE") {
      const next = value(
        await client().GET("/api/v1/sessions/{session_id}/next-item", {
          params: { path: { session_id: id } },
        }),
      );
      setItem(next);
      if (next.response_spec.type === "NUMERIC")
        setUnit(next.response_spec.unit_options[0] ?? "");
    }
  }
  async function initialize() {
    const profile = value(await client().GET("/api/v1/me"));
    if (!profile.learning_allowed) throw new Error("CONSENT_REQUIRED");
    const all = value(await client().GET("/api/v1/curriculum/subjects"));
    const selected = all.filter((s) => profile.subject_ids.includes(s.id));
    setSubjects(selected);
    setReady(true);
    const query = new URLSearchParams(window.location.search);
    const requested =
      selected.find((s) => s.id === query.get("subject")) ?? selected[0];
    if (requested) {
      await loadTopics(requested.id);
      if (query.get("topic")) setTopic(query.get("topic")!);
    }
    setActive(value(await client().GET("/api/v1/sessions/active")));
    const id = new URLSearchParams(window.location.search).get("session");
    if (id) await loadSession(id);
  }
  useEffect(() => {
    let cancelled = false;
    async function boot() {
      try {
        if (!cancelled) await initialize();
        if (!cancelled) setStatus("");
      } catch (error) {
        if (!cancelled)
          setStatus(
            messages[error instanceof Error ? error.message : ""] ??
              "Check your connection, then reload.",
          );
      } finally {
        if (!cancelled) setBusy(false);
      }
    }
    void boot();
    return () => {
      cancelled = true;
    };
    // Initialization runs once; actions explicitly reload authoritative state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main className="learning-page practice-page">
      <p className="eyebrow">Your learning · One question at a time</p>
      <h1 className="text-3xl font-semibold">
        {session?.kind === "REASSESSMENT"
          ? "Check your understanding"
          : "Practise a topic"}
      </h1>
      <p>
        Synthetic development questions only. Answers contribute to an evolving
        mastery estimate, not a certified grade.
      </p>
      <Status>{status}</Status>
      <Link
        className="inline-flex min-h-11 items-center underline"
        href="/onboarding"
      >
        Profile, consent and sign in
      </Link>
      <button
        className={button}
        disabled={busy}
        onClick={() => void run(initialize)}
      >
        Reload saved progress
      </button>
      {ready && !session && (
        <>
          {active.length > 0 && (
            <section className="space-y-3" aria-label="Interrupted sessions">
              <h2 className="text-xl font-semibold">Continue practice</h2>
              {active.map((s) => (
                <button
                  className={button}
                  key={s.id}
                  disabled={busy}
                  onClick={() => void run(() => loadSession(s.id))}
                >
                  Resume {s.answered_count} of {s.item_count} answered
                </button>
              ))}
            </section>
          )}
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              void run(async () => {
                const body: Schema["StartRevision"] = {
                  subject_id: subject,
                  topic_id: topic,
                  mode: "TOPIC",
                  desired_item_count: 5,
                  channel: "WEB",
                };
                const state = value(
                  await client().POST("/api/v1/revision-sessions", {
                    body,
                    params: { header: { "Idempotency-Key": key(body) } },
                  }),
                );
                retry.current = null;
                await loadSession(state.id);
              });
            }}
          >
            <label className="block">
              Subject
              <select
                className={input}
                value={subject}
                disabled={busy}
                onChange={(e) => void run(() => loadTopics(e.target.value))}
              >
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              Topic
              <select
                className={input}
                value={topic}
                disabled={busy}
                onChange={(e) => setTopic(e.target.value)}
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </label>
            <p>
              Five questions from your selected topic. Feedback uses the
              approved answer for each question.
            </p>
            <button
              className="ui-button ui-button-primary"
              disabled={busy || !topic}
            >
              Start five-question practice
            </button>
          </form>
        </>
      )}
      {session && (
        <section className="space-y-5" aria-label="Practice session">
          <p>{session.recommendation_reason}</p>
          {session.kind === "REASSESSMENT" && (
            <p>
              Try this question independently. Your original score stays
              unchanged.
            </p>
          )}
          {session.original_session_id && (
            <button
              className={button}
              disabled={busy}
              onClick={() =>
                void run(() => loadSession(session.original_session_id!))
              }
            >
              Return to original practice
            </button>
          )}
          <SavedProgress
            answered={session.answered_count}
            total={session.item_count}
          />
          {session.status === "COMPLETED" && (
            <h2 className="text-xl font-semibold">
              {session.answers.some(
                (answer) => answer.grade.status === "PENDING",
              )
                ? "All answers saved; feedback pending"
                : "Practice complete"}
            </h2>
          )}
          {!item &&
            session.answers.some(
              (answer) => answer.grade.status !== "GRADED",
            ) && (
              <section className="space-y-2" aria-label="Saved feedback">
                {session.answers
                  .filter((answer) => answer.grade.status !== "GRADED")
                  .map((answer) => (
                    <button
                      className={button}
                      key={answer.session_item_id}
                      disabled={busy}
                      onClick={() =>
                        void run(async () => {
                          setGrade(
                            value(
                              await client().GET(
                                "/api/v1/attempts/{attempt_id}/grade",
                                {
                                  params: {
                                    path: {
                                      attempt_id: answer.grade.attempt_id,
                                    },
                                  },
                                },
                              ),
                            ),
                          );
                        })
                      }
                    >
                      Check saved feedback for question {answer.position}
                    </button>
                  ))}
              </section>
            )}
          {["ABANDONED", "EXPIRED"].includes(session.status) && (
            <p>This session has ended. Your submitted answers are retained.</p>
          )}
          {item && !grade && (
            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                void run(async () => {
                  const body: Schema["SubmitAnswer"] = {
                    session_item_id: item.session_item_id,
                    response:
                      item.response_spec.type === "SHORT_TEXT"
                        ? { type: "SHORT_TEXT", text: shortText }
                        : item.response_spec.type === "NUMERIC"
                          ? { type: "NUMERIC", value: numericValue, unit }
                          : item.response_spec.type === "MULTIPLE_CHOICE"
                            ? {
                                type: "MULTIPLE_CHOICE",
                                choice_ids: selectedIds,
                              }
                            : { type: "SINGLE_CHOICE", choice_id: choice },
                  };
                  const result = value(
                    await client().POST(
                      "/api/v1/sessions/{session_id}/attempts",
                      {
                        body,
                        params: {
                          path: { session_id: session.id },
                          header: {
                            "Idempotency-Key": key({
                              session: session.id,
                              ...body,
                            }),
                          },
                        },
                      },
                    ),
                  );
                  if (result.status === "SAVED") throw new Error("FORBIDDEN");
                  setGrade(result);
                  setItem(null);
                  retry.current = null;
                  setSession(
                    value(
                      await client().GET("/api/v1/sessions/{session_id}", {
                        params: { path: { session_id: session.id } },
                      }),
                    ),
                  );
                });
              }}
            >
              <h2 className="text-xl font-semibold">
                Question {item.position} of {session.item_count}
              </h2>
              {item.prompt_blocks.map((p, i) => (
                <p className="whitespace-pre-wrap" key={i}>
                  {p.content}
                </p>
              ))}
              {session.kind !== "REASSESSMENT" && (
                <Hints
                  key={item.session_item_id}
                  sessionId={session.id}
                  item={item}
                  disabled={busy}
                />
              )}
              {item.response_spec.type === "SHORT_TEXT" ? (
                <>
                  <label htmlFor="written-answer">Your written answer</label>
                  <textarea
                    id="written-answer"
                    className={input}
                    value={shortText}
                    required
                    autoComplete="off"
                    maxLength={4000}
                    rows={5}
                    aria-describedby="short-text-help"
                    onChange={(event) => setShortText(event.target.value)}
                  />
                  <span id="short-text-help">
                    {Array.from(shortText).length} of 2000 characters. Your
                    answer is saved when you submit it.
                  </span>
                </>
              ) : item.response_spec.type === "NUMERIC" ? (
                <fieldset disabled={busy} className="space-y-3">
                  <legend>Enter a numeric answer</legend>
                  <label>
                    Numeric value
                    <input
                      className={input}
                      value={numericValue}
                      onChange={(e) => setNumericValue(e.target.value)}
                      maxLength={64}
                      autoComplete="off"
                      required
                      aria-describedby="numeric-help"
                    />
                  </label>
                  <label>
                    Answer unit
                    <select
                      className={input}
                      value={unit}
                      onChange={(e) => setUnit(e.target.value)}
                    >
                      {item.response_spec.unit_options.map((u) => (
                        <option key={u} value={u}>
                          {u || "No unit (dimensionless)"}
                        </option>
                      ))}
                    </select>
                  </label>
                  <p id="numeric-help">
                    Accepted forms:{" "}
                    {item.response_spec.accepted_forms
                      .map((f) =>
                        f === "DECIMAL"
                          ? "decimal (e.g. 1.25)"
                          : f === "SCIENTIFIC"
                            ? "scientific (e.g. 1.25e2)"
                            : "fraction (e.g. 1/2)",
                      )
                      .join(", ")}
                    . Use a decimal point; do not include units in the value.
                  </p>
                  {item.response_spec.significant_figures_policy ===
                    "EXACT" && (
                    <p>
                      Use exactly {item.response_spec.significant_figures}{" "}
                      significant figures. Trailing zeros count after a decimal
                      point or in scientific notation; integer trailing zeros do
                      not. For zero, decimal places count, with a minimum of
                      one.
                    </p>
                  )}
                </fieldset>
              ) : (
                <>
                  <fieldset disabled={busy}>
                    <legend>
                      {item.response_spec.type === "MULTIPLE_CHOICE"
                        ? "Select all that apply"
                        : "Choose one answer"}
                    </legend>
                    {item.response_spec.type === "MULTIPLE_CHOICE" && (
                      <p>
                        Full credit requires every correct option and no others.
                      </p>
                    )}
                    {item.response_spec.choices.map((c) => (
                      <label className="answer-choice" key={c.id}>
                        <input
                          type={
                            item.response_spec.type === "MULTIPLE_CHOICE"
                              ? "checkbox"
                              : "radio"
                          }
                          name="answer"
                          value={c.id}
                          checked={
                            item.response_spec.type === "MULTIPLE_CHOICE"
                              ? selectedIds.includes(c.id)
                              : choice === c.id
                          }
                          onChange={() =>
                            item.response_spec.type === "MULTIPLE_CHOICE"
                              ? setSelectedIds((ids) =>
                                  ids.includes(c.id)
                                    ? ids.filter((id) => id !== c.id)
                                    : [...ids, c.id].sort(),
                                )
                              : setChoice(c.id)
                          }
                        />
                        {c.text}
                      </label>
                    ))}
                  </fieldset>
                </>
              )}
              <button
                className="ui-button ui-button-primary"
                disabled={
                  busy ||
                  (item.response_spec.type === "SHORT_TEXT"
                    ? !shortText.trim() || Array.from(shortText).length > 2000
                    : item.response_spec.type === "NUMERIC"
                      ? !numericValue.trim()
                      : item.response_spec.type === "MULTIPLE_CHOICE"
                        ? selectedIds.length === 0
                        : !choice)
                }
              >
                Submit answer
              </button>
            </form>
          )}
          {grade && grade.status !== "GRADED" && (
            <PendingFeedback
              key={grade.attempt_id}
              grade={grade}
              busy={busy}
              onResult={setGrade}
              onError={pollingError}
              onNext={
                session.status === "ACTIVE"
                  ? () => void run(() => loadSession(session.id, false))
                  : undefined
              }
              onEquivalent={(id) => void run(() => loadSession(id))}
            />
          )}
          {grade && grade.status === "GRADED" && (
            <section
              className="space-y-3"
              aria-label="Answer feedback"
              aria-live="polite"
            >
              <h2 className="text-xl font-semibold">Answer saved</h2>
              <p>
                {grade.points_awarded} of {grade.points_possible} points
              </p>
              {[
                ...grade.feedback.correct_elements,
                ...grade.feedback.missing_elements,
              ].map((text, i) => (
                <p key={i}>{text}</p>
              ))}
              <p>{grade.feedback.next_action}</p>
              {"criterion_results" in grade && (
                <ul className="space-y-2">
                  {grade.criterion_results.map((criterion) => (
                    <li key={criterion.criterion_id}>
                      <p>
                        {criterion.criterion_id}: {criterion.points_awarded}{" "}
                        points
                      </p>
                      {criterion.evidence_excerpt && (
                        <blockquote className="whitespace-pre-wrap break-words">
                          {criterion.evidence_excerpt}
                        </blockquote>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              <FlagForm
                key={`flag-${grade.attempt_id}`}
                attemptId={grade.attempt_id}
              />
              <button
                className={button}
                disabled={busy}
                onClick={() =>
                  void run(async () => {
                    setSolution(
                      value(
                        await client().GET(
                          "/api/v1/attempts/{attempt_id}/solution",
                          {
                            params: { path: { attempt_id: grade.attempt_id } },
                          },
                        ),
                      ).worked_solution,
                    );
                  })
                }
              >
                Show worked solution
              </button>
              {solution && <p className="whitespace-pre-wrap">{solution}</p>}
              {session.kind !== "REASSESSMENT" && (
                <button
                  className={button}
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      const result = value(
                        await client().POST(
                          "/api/v1/attempts/{attempt_id}/reassessment",
                          {
                            params: {
                              path: { attempt_id: grade.attempt_id },
                              header: {
                                "Idempotency-Key": key({
                                  reassessment: grade.attempt_id,
                                }),
                              },
                            },
                          },
                        ),
                      );
                      retry.current = null;
                      await loadSession(result.id);
                    })
                  }
                >
                  Try an unseen reassessment
                </button>
              )}
              {session.status === "ACTIVE" && (
                <button
                  className={button}
                  disabled={busy}
                  onClick={() => void run(() => loadSession(session.id, false))}
                >
                  Next question
                </button>
              )}
              {session.kind !== "REASSESSMENT" && (
                <Hints
                  key={`hints-${grade.attempt_id}`}
                  sessionId={session.id}
                  attemptId={grade.attempt_id}
                  disabled={busy}
                />
              )}
            </section>
          )}
          {session.status === "ACTIVE" && (
            <button
              className={button}
              disabled={busy}
              onClick={() =>
                void run(async () => {
                  setSession(
                    value(
                      await client().POST(
                        "/api/v1/sessions/{session_id}/abandon",
                        { params: { path: { session_id: session.id } } },
                      ),
                    ),
                  );
                  setItem(null);
                })
              }
            >
              End this session
            </button>
          )}
          {session.status !== "ACTIVE" && (
            <button
              className={button}
              disabled={busy}
              onClick={() =>
                void run(async () => {
                  window.history.replaceState(null, "", "/revise");
                  setSession(null);
                  setGrade(null);
                  setSolution("");
                  await initialize();
                })
              }
            >
              Choose another topic
            </button>
          )}
        </section>
      )}
    </main>
  );
}
