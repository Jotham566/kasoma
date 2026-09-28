"use client";

import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
const button =
  "min-h-11 rounded border border-slate-500 px-4 py-2 disabled:opacity-50";
const categories: Record<Schema["FlagInput"]["category"], string> = {
  QUESTION_ERROR: "Question or answer key error",
  GRADE_DISPUTE: "Grade concern",
  UNCLEAR: "Unclear wording",
  ACCESSIBILITY: "Accessibility problem",
  UNSAFE_CONTENT: "Unsafe content",
  OTHER: "Other question issue",
};
const api = () => apiClient("", crypto.randomUUID());
export function FlagForm({ attemptId }: { attemptId: string }) {
  const [open, setOpen] = useState(false);
  const [category, setCategory] =
    useState<Schema["FlagInput"]["category"]>("QUESTION_ERROR");
  const [comment, setComment] = useState("");
  const [reports, setReports] = useState<Schema["FlagReceipt"][]>([]);
  const [busy, setBusy] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [pending, setPending] = useState<{
    key: string;
    body: Schema["FlagInput"];
  } | null>(null);
  const [status, setStatus] = useState("");
  function fail(code?: string) {
    setStatus(
      code === "CONSENT_REQUIRED" || code === "FORBIDDEN"
        ? "Current learning consent and subject access are required. Check your profile."
        : code === "AUTH_REQUIRED"
          ? "Sign in again to report this issue."
          : code === "USAGE_LIMIT_REACHED"
            ? "The reporting limit was reached. Please try later."
            : code === "FLAG_ALREADY_REPORTED"
              ? "This category is already reported. Reload recorded reports."
              : "Could not confirm the report. Retry the same report or reload recorded reports; your answer is safe.",
    );
  }
  async function load() {
    setBusy(true);
    setStatus("Loading recorded reports…");
    try {
      const result = await api().GET("/api/v1/attempts/{attempt_id}/flag", {
        params: { path: { attempt_id: attemptId } },
      });
      if (!result.data) {
        fail(result.error?.error.code);
        return;
      }
      setReports(result.data);
      setLoaded(true);
      setPending(null);
      setComment("");
      setStatus(
        result.data.length
          ? "Previously recorded categories are shown below."
          : "No reports recorded for this answer.",
      );
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }
  async function submit() {
    const request = pending ?? {
      key: crypto.randomUUID(),
      body: { category, comment: comment.trim() },
    };
    setPending(request);
    setBusy(true);
    setStatus("Recording your report…");
    try {
      const result = await api().POST("/api/v1/attempts/{attempt_id}/flag", {
        params: {
          path: { attempt_id: attemptId },
          header: { "Idempotency-Key": request.key },
        },
        body: request.body,
      });
      if (!result.data) {
        fail(result.error?.error.code);
        return;
      }
      const receipt = result.data;
      setReports((old) => [...old.filter((r) => r.id !== receipt.id), receipt]);
      setPending(null);
      setComment("");
      setStatus(
        "Report recorded. Your saved answer and grade have not changed.",
      );
    } catch {
      fail();
    } finally {
      setBusy(false);
    }
  }
  if (!open)
    return (
      <button
        type="button"
        className={button}
        onClick={() => {
          setOpen(true);
          void load();
        }}
      >
        Report question or grade
      </button>
    );
  return (
    <section
      aria-label="Report question or grade"
      className="space-y-3 rounded border border-slate-300 p-4"
    >
      <h3 className="font-semibold">Report question or grade</h3>
      <p>
        Describe the question issue only. Do not include names, contact details
        or other personal information. This development queue is not a live
        support service.
      </p>
      <p role="status" aria-live="polite">
        {status}
      </p>
      <button
        type="button"
        className={button}
        disabled={busy}
        onClick={() => void load()}
      >
        Reload recorded reports
      </button>
      {reports.length > 0 && (
        <ul>
          {reports.map((r) => (
            <li key={r.id}>Recorded: {categories[r.category]}</li>
          ))}
        </ul>
      )}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void submit();
        }}
        className="space-y-3"
      >
        <fieldset disabled={busy || !!pending || !loaded} className="space-y-3">
          <label className="block">
            Issue category
            <select
              className="block min-h-11 border border-slate-500 p-2"
              value={category}
              onChange={(e) =>
                setCategory(e.target.value as Schema["FlagInput"]["category"])
              }
            >
              {Object.entries(categories).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            Optional issue comment
            <textarea
              className="block w-full rounded border border-slate-500 p-2"
              maxLength={1000}
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
          </label>
        </fieldset>
        <button
          className={button}
          disabled={
            busy ||
            !loaded ||
            (!pending && reports.some((r) => r.category === category))
          }
        >
          {pending ? "Retry report" : "Send report"}
        </button>
      </form>
    </section>
  );
}
