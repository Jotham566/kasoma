"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Schema = components["schemas"];
const button = "ui-button ui-button-secondary";

export function RecommendationCard() {
  const router = useRouter();
  const [subjects, setSubjects] = useState<Schema["SubjectView"][]>([]);
  const [subject, setSubject] = useState("");
  const [recommendation, setRecommendation] = useState<
    Schema["RecommendationView"] | null
  >(null);
  const [busy, setBusy] = useState(true);
  const [status, setStatus] = useState("Loading your next activity…");
  const retry = useRef<{ subject: string; key: string } | null>(null);
  const api = () => apiClient("", crypto.randomUUID());
  function failure(code?: string) {
    setRecommendation(null);
    setStatus(
      code === "CONSENT_REQUIRED"
        ? "Complete your profile and consent before practice."
        : code === "AUTH_REQUIRED"
          ? "Sign in to see your next activity."
          : code === "INSUFFICIENT_CONTENT" || code === "CONTENT_NOT_APPROVED"
            ? "There are not enough reviewed questions available. Choose a topic or try again later."
            : "Check your connection and try again. Saved sessions are safe.",
    );
  }
  async function load(id: string) {
    setBusy(true);
    setSubject(id);
    setRecommendation(null);
    setStatus("Loading your next activity…");
    try {
      const result = await api().GET("/api/v1/me/recommendations/next", {
        params: { query: { subject_id: id } },
      });
      if (!result.data) {
        failure(result.error?.error.code);
        return;
      }
      setRecommendation(result.data);
      setStatus("");
    } catch {
      failure();
    } finally {
      setBusy(false);
    }
  }
  async function initialize() {
    try {
      const profile = await api().GET("/api/v1/me");
      if (!profile.response.ok || !profile.data) {
        failure(profile.response.status === 401 ? "AUTH_REQUIRED" : undefined);
        return;
      }
      if (!profile.data.learning_allowed) {
        failure("CONSENT_REQUIRED");
        return;
      }
      const catalog = await api().GET("/api/v1/curriculum/subjects");
      if (!catalog.response.ok || !catalog.data) {
        failure();
        return;
      }
      const selected = catalog.data.filter((s) =>
        profile.data!.subject_ids.includes(s.id),
      );
      setSubjects(selected);
      const requested =
        selected.find(
          (s) =>
            s.id === new URLSearchParams(window.location.search).get("subject"),
        ) ?? selected[0];
      if (requested) await load(requested.id);
      else failure("CONSENT_REQUIRED");
    } catch {
      failure();
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    async function boot() {
      await initialize();
    }
    void boot();
    // Refresh and subject selection explicitly reload authorized server state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <section
      aria-label="Recommended practice"
      id="recommendations"
      className="recommendation-card surface-card"
    >
      <p className="eyebrow">One useful next step</p>
      <h2>Your next activity</h2>
      <p role="status" aria-live="polite">
        {status}
      </p>
      {subjects.length > 0 && (
        <label className="block">
          Recommendation subject
          <select
            className="ui-select"
            value={subject}
            disabled={busy}
            onChange={(e) => void load(e.target.value)}
          >
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
      )}
      {recommendation && (
        <>
          {recommendation.topic && (
            <h3 className="recommendation-topic">{recommendation.topic}</h3>
          )}
          <p>{recommendation.learner_text}</p>
          {recommendation.topic_id && (
            <>
              <p>
                Five synthetic questions · About{" "}
                {recommendation.estimated_minutes} minutes
              </p>
              <button
                className="ui-button ui-button-primary"
                disabled={busy}
                onClick={() => {
                  setBusy(true);
                  setStatus("Preparing your practice…");
                  if (retry.current?.subject !== subject)
                    retry.current = { subject, key: crypto.randomUUID() };
                  void api()
                    .POST("/api/v1/revision-sessions", {
                      body: {
                        subject_id: subject,
                        mode: "RECOMMENDED",
                        topic_id: null,
                        desired_item_count: 5,
                        channel: "WEB",
                      },
                      params: {
                        header: { "Idempotency-Key": retry.current.key },
                      },
                    })
                    .then((result) => {
                      if (!result.data) {
                        failure(result.error?.error.code);
                        return;
                      }
                      router.push(`/revise?session=${result.data.id}`);
                    })
                    .catch(() => failure())
                    .finally(() => setBusy(false));
                }}
              >
                Start recommended practice
              </button>
            </>
          )}
          {recommendation.diagnostic_suggested && (
            <p>
              <Link
                className="ui-text-link"
                href="/diagnostic"
                prefetch={false}
              >
                Gather broader evidence with a diagnostic
              </Link>
            </p>
          )}
        </>
      )}
      <button
        className={button}
        disabled={busy}
        onClick={() => void (subject ? load(subject) : initialize())}
      >
        Refresh recommendation
      </button>
      <p>
        <Link className="ui-text-link" href="/onboarding" prefetch={false}>
          Profile and sign in
        </Link>
      </p>
    </section>
  );
}
