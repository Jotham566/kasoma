"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";
import { Status } from "@kasoma/ui";

type Schema = components["schemas"];
const button =
  "min-h-11 rounded-lg border border-slate-500 px-4 py-2 disabled:opacity-50";
const input = "block min-h-11 w-full rounded border border-slate-500 p-2";
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
  const [session, setSession] = useState<Schema["SessionView"] | null>(null);
  const [item, setItem] = useState<Schema["LearnerItem"] | null>(null);
  const [grade, setGrade] = useState<Schema["GradeView"] | null>(null);
  const [solution, setSolution] = useState("");
  const [choice, setChoice] = useState("");
  const [busy, setBusy] = useState(true);
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState("Loading your practice options…");
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
    const state = value(
      await client().GET("/api/v1/sessions/{session_id}", {
        params: { path: { session_id: id } },
      }),
    );
    setSession(state);
    window.history.replaceState(null, "", `/revise?session=${state.id}`);
    const last = state.answers.at(-1);
    if (showLast && last) setGrade(last.grade);
    else if (state.status === "ACTIVE") {
      setItem(
        value(
          await client().GET("/api/v1/sessions/{session_id}/next-item", {
            params: { path: { session_id: id } },
          }),
        ),
      );
    }
  }
  async function initialize() {
    const profile = value(await client().GET("/api/v1/me"));
    if (!profile.learning_allowed) throw new Error("CONSENT_REQUIRED");
    const all = value(await client().GET("/api/v1/curriculum/subjects"));
    const selected = all.filter((s) => profile.subject_ids.includes(s.id));
    setSubjects(selected);
    setReady(true);
    if (selected[0]) await loadTopics(selected[0].id);
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
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <Link className="inline-flex min-h-11 items-center underline" href="/">
        Kasoma home
      </Link>
      <h1 className="text-3xl font-semibold">Practise a topic</h1>
      <p>
        Synthetic development questions only. These sessions do not yet estimate
        mastery.
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
            <button className={button} disabled={busy || !topic}>
              Start five-question practice
            </button>
          </form>
        </>
      )}
      {session && (
        <section className="space-y-5" aria-label="Practice session">
          <p>{session.recommendation_reason}</p>
          <p>
            {session.answered_count} of {session.item_count} answers saved
          </p>
          {session.status === "COMPLETED" && (
            <h2 className="text-xl font-semibold">Practice complete</h2>
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
                    response: { type: "SINGLE_CHOICE", choice_id: choice },
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
              <fieldset disabled={busy}>
                <legend>Choose one answer</legend>
                {item.response_spec.choices.map((c) => (
                  <label
                    className="flex min-h-11 items-center gap-3"
                    key={c.id}
                  >
                    <input
                      type="radio"
                      name="answer"
                      value={c.id}
                      checked={choice === c.id}
                      onChange={() => setChoice(c.id)}
                    />
                    {c.text}
                  </label>
                ))}
              </fieldset>
              <button className={button} disabled={busy || !choice}>
                Submit answer
              </button>
            </form>
          )}
          {grade && (
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
              {session.status === "ACTIVE" && (
                <button
                  className={button}
                  disabled={busy}
                  onClick={() => void run(() => loadSession(session.id, false))}
                >
                  Next question
                </button>
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
