import Link from "next/link";
import { randomUUID } from "node:crypto";
import { apiClient } from "@kasoma/api-client";
import { Status } from "@kasoma/ui";
import { apiUrl } from "./config";
import { RecommendationCard } from "./recommendation-card";

export const dynamic = "force-dynamic";

export default async function Home() {
  const requestId = randomUUID();
  let available = false;
  try {
    const { data } = await apiClient(apiUrl(), requestId).GET(
      "/api/v1/health",
      {
        signal: AbortSignal.timeout(6000),
        cache: "no-store",
      },
    );
    available = data?.status === "ok";
  } catch {
    /* Render a safe, recoverable state without printing connection errors. */
  }
  return (
    <main className="home-page">
      <div className="development-banner">
        <span className="environment-tag">Development preview</span>
        <p>Synthetic practice only. Academic approval remains pending.</p>
      </div>
      <section className="home-intro" aria-labelledby="home-title">
        <p className="eyebrow">Senior 4 · Mathematics &amp; Physics</p>
        <h1 id="home-title">Know what to revise next.</h1>
        <p className="home-description">
          Find a starting point, practise a little, and build a clearer picture
          of your learning.
        </p>
      </section>
      <div className="home-grid">
        <RecommendationCard />
        <aside className="home-options" aria-label="Other ways to get started">
          <section className="surface-card">
            <span className="step-label">Find your starting point</span>
            <h2>Not sure where to begin?</h2>
            <p>
              A subject diagnostic helps identify what to practise. Your results
              include how much evidence supports each estimate.
            </p>
            <Link
              className="ui-button ui-button-secondary"
              href="/diagnostic"
              prefetch={false}
            >
              Start a subject diagnostic
            </Link>
          </section>
          <section className="surface-card">
            <span className="step-label">Make it your session</span>
            <h2>Have a topic in mind?</h2>
            <p>
              Choose a topic for focused practice, with reviewed hints and
              worked solutions after you answer.
            </p>
            <Link className="ui-text-link" href="/revise" prefetch={false}>
              Practise a topic <span aria-hidden="true">→</span>
            </Link>
          </section>
        </aside>
      </div>
      <section
        className="home-account surface-card"
        aria-labelledby="account-title"
      >
        <div>
          <p className="eyebrow">Your learning, your account</p>
          <h2 id="account-title">Pick up where you left off.</h2>
          <p>
            Sign in to keep your saved answers and learning history together.
          </p>
        </div>
        <Link
          className="ui-button ui-button-secondary"
          href="/onboarding"
          prefetch={false}
        >
          Set up a synthetic learner profile
        </Link>
      </section>
      <footer className="home-footer">
        <nav aria-label="Account and privacy" className="home-footer-links">
          <Link href="/privacy" prefetch={false}>
            Your data requests
          </Link>
          <Link href="/channels/whatsapp" prefetch={false}>
            WhatsApp channel
          </Link>
        </nav>
        <div className="service-status">
          <Status>
            {available
              ? "Services are ready."
              : "Services are temporarily unavailable. Please try again."}
          </Status>
          {/* A full navigation refreshes server readiness. */}
          {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
          <a href="/">Check again</a>
        </div>
        <small className="support-reference">
          Support reference: {requestId}
        </small>
      </footer>
    </main>
  );
}
