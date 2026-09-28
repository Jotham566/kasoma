"use client";

import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
const button =
  "min-h-11 rounded-lg border border-slate-500 px-4 py-2 disabled:opacity-50";

export function Hints({
  sessionId,
  item,
  attemptId,
  disabled,
}: {
  sessionId: string;
  item?: Schema["LearnerItem"];
  attemptId?: string;
  disabled: boolean;
}) {
  const [state, setState] = useState<Schema["HintState"] | null>(
    item
      ? {
          session_item_id: item.session_item_id,
          hints: item.hints ?? [],
          has_more_hints: item.has_more_hints ?? false,
        }
      : null,
  );
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const retry = useRef<{ level: number; key: string } | null>(null);
  const api = () => apiClient("", crypto.randomUUID());
  function failed(code?: string) {
    setStatus(
      code === "CONSENT_REQUIRED" || code === "AUTH_REQUIRED"
        ? "Hint access is paused. Check your profile and sign in."
        : code === "HINT_UNAVAILABLE"
          ? "No more reviewed hints are available."
          : code === "CONTENT_NOT_APPROVED" || code === "RESOURCE_NOT_FOUND"
            ? "Hints for this question are unavailable."
            : code === "VERSION_CONFLICT"
              ? "A hint was revealed on another request. Reload saved progress."
              : "Check your connection and retry. Saved hint usage is retained.",
    );
  }
  useEffect(() => {
    if (!attemptId) return;
    let cancelled = false;
    void api()
      .GET("/api/v1/attempts/{attempt_id}/hints", {
        params: { path: { attempt_id: attemptId } },
      })
      .then((result) => {
        if (cancelled) return;
        if (result.data) setState(result.data);
        else failed(result.error?.error.code);
      })
      .catch(() => {
        if (!cancelled) failed();
      });
    return () => {
      cancelled = true;
    };
  }, [attemptId]);
  async function reveal() {
    if (!state) return;
    const level = state.hints.length;
    if (retry.current?.level !== level)
      retry.current = { level, key: crypto.randomUUID() };
    setBusy(true);
    setStatus("Loading reviewed hint…");
    try {
      const headers = { "Idempotency-Key": retry.current.key };
      const body = { expected_hint_level: level };
      const result = attemptId
        ? await api().POST("/api/v1/attempts/{attempt_id}/hint", {
            body,
            params: { path: { attempt_id: attemptId }, header: headers },
          })
        : await api().POST(
            "/api/v1/sessions/{session_id}/items/{item_id}/hint",
            {
              body,
              params: {
                path: { session_id: sessionId, item_id: state.session_item_id },
                header: headers,
              },
            },
          );
      if (!result.data) {
        failed(result.error?.error.code);
        return;
      }
      setState(result.data);
      retry.current = null;
      setStatus("Hint saved.");
    } catch {
      failed();
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      aria-label="Reviewed hints"
      className="space-y-3 rounded border border-slate-300 p-3"
    >
      <h3 className="font-semibold">Reviewed hints</h3>
      <p>
        {attemptId
          ? "These hints support review. Your submitted score and evidence stay unchanged."
          : "Hints can help you get started. They inform how independently you answered; they do not change your points."}
      </p>
      <p aria-live="polite">{status}</p>
      {state?.hints.map((hint) => (
        <p key={hint.level}>
          Hint {hint.level}: {hint.text}
        </p>
      ))}
      {state?.has_more_hints ? (
        <button
          type="button"
          className={button}
          disabled={disabled || busy}
          onClick={() => void reveal()}
        >
          Show next reviewed hint
        </button>
      ) : (
        state && <p>No more reviewed hints are available for this question.</p>
      )}
    </section>
  );
}
