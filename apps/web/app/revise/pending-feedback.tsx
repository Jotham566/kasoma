"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";
import { FlagForm } from "../flag-form";

type Schema = components["schemas"];
type Outcome = Schema["AnsweredItem"]["grade"];
type Unresolved =
  | Schema["PendingShortTextGrade"]
  | Schema["LowConfidenceShortTextGrade"];

export function PendingFeedback({
  grade,
  busy,
  onResult,
  onError,
  onNext,
  onEquivalent,
}: {
  grade: Unresolved;
  busy: boolean;
  onResult: (result: Outcome) => void;
  onError: (code: string) => void;
  onNext?: () => void;
  onEquivalent: (id: string) => void;
}) {
  const [checking, setChecking] = useState(false);
  const active = useRef<AbortController | null>(null);
  const mounted = useRef(true);
  const polls = useRef(0);
  const check = useCallback(async () => {
    if (busy || active.current !== null) return;
    const controller = new AbortController();
    active.current = controller;
    setChecking(true);
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/attempts/{attempt_id}/grade",
        {
          params: { path: { attempt_id: grade.attempt_id } },
          signal: controller.signal,
        },
      );
      if (controller.signal.aborted) return;
      if (result.response.ok && result.data) onResult(result.data);
      else onError(result.error?.error.code ?? "SERVICE_UNAVAILABLE");
    } catch {
      if (!controller.signal.aborted) onError("SERVICE_UNAVAILABLE");
    } finally {
      if (active.current === controller) active.current = null;
      if (mounted.current) setChecking(false);
    }
  }, [busy, grade.attempt_id, onResult, onError]);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      active.current?.abort();
      active.current = null;
    };
  }, []);
  useEffect(() => {
    if (grade.status !== "PENDING" || busy) return;
    const timer = window.setInterval(() => {
      if (polls.current >= 12 || active.current !== null) return;
      polls.current += 1;
      void check();
    }, 3000);
    return () => window.clearInterval(timer);
  }, [grade.status, busy, check]);

  return (
    <section
      className="space-y-3"
      aria-label="Answer feedback"
      aria-live="polite"
    >
      <h2 className="text-xl font-semibold">Answer saved</h2>
      {grade.status === "PENDING" ? (
        <>
          <p>
            Your feedback is being prepared. Your answer is saved; no score or
            mastery update has been produced yet.
          </p>
          <button
            className="ui-button ui-button-secondary"
            disabled={busy || checking}
            onClick={() => void check()}
          >
            {checking ? "Checking feedback…" : "Check feedback"}
          </button>
          <p>
            You can continue practice and check this saved answer again later.
          </p>
        </>
      ) : (
        <>
          <p>
            We could not provide a reliable automated grade. No score or mastery
            update was produced for this answer.
          </p>
          {grade.fallback.kind === "OBJECTIVE_EQUIVALENT" ? (
            <button
              className="ui-button ui-button-secondary"
              disabled={busy}
              onClick={() => {
                if (grade.fallback.kind === "OBJECTIVE_EQUIVALENT")
                  onEquivalent(grade.fallback.session_id);
              }}
            >
              Try an equivalent question
            </button>
          ) : (
            <>
              <p>You can use the report form to request a review.</p>
              <FlagForm attemptId={grade.attempt_id} reviewRequest />
            </>
          )}
        </>
      )}
      {onNext && (
        <button
          className="ui-button ui-button-secondary"
          disabled={busy}
          onClick={onNext}
        >
          Next question
        </button>
      )}
    </section>
  );
}
