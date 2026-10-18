"use client";

import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
type Task = Schema["BlindedReviewTask"];
type Input = Schema["AuditReviewInput"];
const api = () => apiClient("", crypto.randomUUID());
const issueLabels: Record<Input["critical_error"], string> = {
  NONE: "No critical issue identified",
  ACADEMIC_INTEGRITY: "Critical academic integrity issue",
  SAFEGUARDING: "Critical safeguarding issue",
  PRIVACY: "Critical privacy issue",
};

function errorMessage(code?: string) {
  if (["AUTH_REQUIRED", "REAUTH_REQUIRED", "FORBIDDEN"].includes(code ?? ""))
    return "Sign in again with academic reviewer access to continue.";
  if (code === "CONSENT_REQUIRED")
    return "This answer is no longer available for review. Refresh the queue.";
  if (code === "REVIEW_ALREADY_COMPLETED")
    return "This review is already completed. Refresh the queue for another task.";
  if (code === "USAGE_LIMIT_REACHED")
    return "Please wait a minute before trying again.";
  return "Could not confirm the request. Check your connection, then retry.";
}

export default function GradingReview() {
  const [queue, setQueue] = useState<Schema["AuditQueuePage"] | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [receipt, setReceipt] = useState<Schema["AuditReviewReceipt"] | null>(
    null,
  );
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(
    "Load the queue to find an answer. Academic reviewer access and a recent sign-in are required.",
  );

  function fail(code?: string) {
    setStatus(errorMessage(code));
    if (
      [
        "AUTH_REQUIRED",
        "REAUTH_REQUIRED",
        "FORBIDDEN",
        "CONSENT_REQUIRED",
        "REVIEW_ALREADY_COMPLETED",
        "RESOURCE_NOT_FOUND",
        "IDEMPOTENCY_CONFLICT",
      ].includes(code ?? "")
    ) {
      setTask(null);
      setQueue(null);
    }
  }
  async function load(cursor?: string) {
    setBusy(true);
    setStatus("Loading the review queue…");
    try {
      const result = await api().GET("/api/v1/admin/grading-audits", {
        params: { query: { limit: 20, ...(cursor ? { cursor } : {}) } },
      });
      if (!result.data) return fail(result.error?.error.code);
      setQueue(result.data);
      setStatus(
        result.data.data.length
          ? "Choose an answer to review."
          : "No available reviews in this queue.",
      );
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }
  async function open(id: string) {
    setBusy(true);
    setTask(null);
    setReceipt(null);
    setStatus("Loading the answer and approved rubric…");
    try {
      const result = await api().GET(
        "/api/v1/admin/grading-audits/{audit_id}",
        {
          params: { path: { audit_id: id } },
        },
      );
      if (!result.data) return fail(result.error?.error.code);
      setTask(result.data);
      setStatus(
        "Review each criterion independently. Automated results are hidden.",
      );
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="staff-page grading-review-page">
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-widest text-[#165b46]">
          Academic quality
        </p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Independent answer review
        </h1>
        <p className="max-w-2xl text-[#51635d]">
          Give every answer a fair reading. Use the pinned rubric to assess the
          saved response; the learner’s identity and automated result stay
          hidden.
        </p>
      </div>
      <p
        role="status"
        className="rounded-xl border border-[#d6dfd8] bg-white p-4"
      >
        {status}
      </p>
      {receipt && (
        <section
          className="surface-card border-l-4 border-l-[#165b46]"
          aria-label="Review confirmation"
        >
          <h2 className="text-xl font-semibold">Review saved</h2>
          <p>
            Your independent assessment is recorded. The original grade and
            mastery evidence have not changed.
          </p>
        </section>
      )}
      <div className="grid items-start gap-6 lg:grid-cols-[15rem_minmax(0,1fr)]">
        <section
          className={`surface-card space-y-4 ${task ? "hidden lg:block" : ""}`}
          aria-label="Review queue"
        >
          <div>
            <h2 className="text-xl font-semibold">Ready for review</h2>
            <p className="text-sm text-[#51635d]">
              Choose one saved answer at a time.
            </p>
          </div>
          <button
            className="ui-button ui-button-secondary w-full"
            disabled={busy || !!task}
            onClick={() => void load()}
          >
            {queue ? "Refresh queue" : "Load review queue"}
          </button>
          {queue?.data.length === 0 && (
            <p>
              The queue is clear. Check back when more reviews are available.
            </p>
          )}
          <ul className="space-y-2">
            {queue?.data.map((entry, index) => (
              <li key={entry.id}>
                <button
                  className={`ui-button w-full ${entry.id === task?.id ? "ui-button-primary" : "ui-button-secondary"}`}
                  aria-current={entry.id === task?.id ? "step" : undefined}
                  disabled={busy || !!task}
                  onClick={() => void open(entry.id)}
                >
                  Review answer {index + 1}
                </button>
              </li>
            ))}
          </ul>
          {queue?.next_cursor && (
            <button
              className="ui-button ui-button-secondary w-full"
              disabled={busy || !!task}
              onClick={() => void load(queue.next_cursor!)}
            >
              Next reviews
            </button>
          )}
        </section>
        {task ? (
          <ReviewForm
            key={task.id}
            task={task}
            onBack={() => {
              setTask(null);
              setStatus("Choose an answer to review.");
            }}
            onFailure={fail}
            onComplete={(saved) => {
              setReceipt(saved);
              setTask(null);
              void load();
            }}
          />
        ) : (
          <section
            className="surface-card space-y-3 py-10"
            aria-label="Review guidance"
          >
            <span className="inline-flex rounded-full bg-[#e9f0e9] px-3 py-1 text-sm font-semibold text-[#165b46]">
              Independent assessment
            </span>
            <h2 className="text-2xl font-semibold tracking-tight">
              Start with the evidence
            </h2>
            <p className="max-w-xl text-[#51635d]">
              Read the question and exact saved response, then record points for
              every rubric criterion. No automated score is shown to influence
              your assessment.
            </p>
            <p className="text-sm text-[#51635d]">
              Reviews support quality checks. They do not override a learner’s
              saved grade.
            </p>
          </section>
        )}
      </div>
    </main>
  );
}

function ReviewForm({
  task,
  onBack,
  onFailure,
  onComplete,
}: {
  task: Task;
  onBack: () => void;
  onFailure: (code?: string) => void;
  onComplete: (receipt: Schema["AuditReviewReceipt"]) => void;
}) {
  const [points, setPoints] = useState<Record<string, string>>({});
  const [critical, setCritical] = useState<Input["critical_error"] | "">("");
  const [affirmative, setAffirmative] = useState(false);
  const [busy, setBusy] = useState(false);
  const [retry, setRetry] = useState(false);
  const [pending, setPending] = useState<{ key: string; body: Input } | null>(
    null,
  );
  const assessed = task.criteria.filter(
    (criterion) =>
      points[criterion.criterion_id] !== undefined &&
      points[criterion.criterion_id] !== "",
  ).length;
  const complete =
    assessed === task.criteria.length && critical !== "" && affirmative;

  async function submit() {
    if (busy || !complete) return;
    const request = pending ?? {
      key: crypto.randomUUID(),
      body: {
        criterion_points: task.criteria.map((criterion) => ({
          criterion_id: criterion.criterion_id,
          points_awarded: Number(points[criterion.criterion_id]),
        })),
        critical_error: critical,
        affirmative: true as const,
      },
    };
    setPending(request);
    setBusy(true);
    try {
      const result = await api().POST(
        "/api/v1/admin/grading-audits/{audit_id}/review",
        {
          params: {
            path: { audit_id: task.id },
            header: { "Idempotency-Key": request.key },
          },
          body: request.body,
        },
      );
      if (!result.data) {
        setRetry(true);
        return onFailure(result.error?.error.code);
      }
      onComplete(result.data);
    } catch {
      setRetry(true);
      onFailure();
    } finally {
      setBusy(false);
    }
  }
  return (
    <form
      className="min-w-0 space-y-5 break-words"
      aria-label="Independent rubric review"
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <button
        className="ui-button ui-button-secondary"
        type="button"
        disabled={busy || !!pending}
        onClick={onBack}
      >
        Back to queue
      </button>
      <section className="surface-card space-y-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-[#51635d]">
            01 · Read the response
          </p>
          <h2 className="mt-2 text-xl font-semibold">
            Question and saved answer
          </h2>
        </div>
        <p className="whitespace-pre-wrap break-words">{task.prompt}</p>
        <div className="rounded-xl border border-[#d6dfd8] bg-[#f5f7f4] p-4">
          <h3 className="mb-2 text-sm font-semibold text-[#51635d]">
            Saved response · exact wording
          </h3>
          <blockquote className="whitespace-pre-wrap break-words">
            {task.response}
          </blockquote>
        </div>
      </section>
      <section className="surface-card space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-[#51635d]">
            02 · Apply the rubric
          </p>
          <h2 className="mt-2 text-xl font-semibold">Assess each criterion</h2>
        </div>
        <div className="saved-progress">
          <p>
            {assessed} of {task.criteria.length} criteria assessed
          </p>
          <progress
            aria-label="Criteria assessed"
            value={assessed}
            max={task.criteria.length}
          />
        </div>
        <fieldset disabled={busy || !!pending} className="space-y-6">
          <legend className="sr-only">Criterion points</legend>
          {task.criteria.map((criterion) => (
            <div
              key={criterion.criterion_id}
              className="space-y-3 border-t border-[#d6dfd8] pt-5"
            >
              <h3 className="font-semibold">
                {criterion.criterion_id} · {criterion.maximum_points} possible
                points
              </h3>
              <p>{criterion.criterion_text}</p>
              <details className="rounded-lg bg-[#f5f7f4] p-3 text-sm">
                <summary className="min-h-11 cursor-pointer py-2 font-semibold">
                  Approved evidence guide for {criterion.criterion_id}
                </summary>
                <div className="space-y-3 pt-3">
                  <div>
                    <h4 className="font-semibold">Acceptable evidence</h4>
                    <ul className="list-disc space-y-1 pl-5">
                      {criterion.acceptable_evidence.map((text, index) => (
                        <li key={index}>{text}</li>
                      ))}
                    </ul>
                  </div>
                  {criterion.common_errors.length > 0 && (
                    <div>
                      <h4 className="font-semibold">Common errors</h4>
                      <ul className="list-disc space-y-1 pl-5">
                        {criterion.common_errors.map((text, index) => (
                          <li key={index}>{text}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {criterion.prohibited_inferences.length > 0 && (
                    <div>
                      <h4 className="font-semibold">Do not infer</h4>
                      <ul className="list-disc space-y-1 pl-5">
                        {criterion.prohibited_inferences.map((text, index) => (
                          <li key={index}>{text}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </details>
              <div>
                <label
                  className="block font-medium"
                  htmlFor={`review-points-${criterion.criterion_id}`}
                >
                  Points for {criterion.criterion_id}
                </label>
                <select
                  id={`review-points-${criterion.criterion_id}`}
                  className="ui-select"
                  value={points[criterion.criterion_id] ?? ""}
                  required
                  onChange={(event) =>
                    setPoints((old) => ({
                      ...old,
                      [criterion.criterion_id]: event.target.value,
                    }))
                  }
                >
                  <option value="">Choose points</option>
                  {Array.from(
                    { length: criterion.maximum_points + 1 },
                    (_, value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ),
                  )}
                </select>
              </div>
            </div>
          ))}
          <div>
            <label
              className="block font-medium"
              htmlFor="review-critical-issue"
            >
              Critical issue
            </label>
            <select
              id="review-critical-issue"
              className="ui-select"
              value={critical}
              required
              onChange={(event) =>
                setCritical(event.target.value as Input["critical_error"])
              }
            >
              <option value="">Select an assessment</option>
              {Object.entries(issueLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <label className="flex min-h-11 items-start gap-3 rounded-xl border border-[#d6dfd8] p-4">
            <input
              className="mt-1 h-5 w-5 shrink-0 accent-[#165b46]"
              type="checkbox"
              checked={affirmative}
              required
              onChange={(event) => setAffirmative(event.target.checked)}
            />
            <span>I have independently reviewed every criterion.</span>
          </label>
        </fieldset>
        <button
          className="ui-button ui-button-primary w-full"
          disabled={busy || !complete}
          type="submit"
        >
          {busy
            ? "Saving review…"
            : retry
              ? "Retry same review"
              : "Save independent review"}
        </button>
        <p className="text-sm text-[#51635d]">
          Your review is recorded independently. The original grade is
          preserved.
        </p>
      </section>
    </form>
  );
}
