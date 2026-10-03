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
    <main className="mx-auto max-w-2xl p-8">
      <p className="text-sm font-semibold tracking-wide">KASOMA</p>
      <h1 className="mt-8 text-4xl font-semibold">Know what to revise next.</h1>
      <p className="mt-6">Revision for Senior 4 Mathematics and Physics.</p>
      <p className="mt-4">
        Synthetic practice is available for development. Diagnostic estimates
        are available with synthetic fixtures. Academic approval remains
        pending.
      </p>
      <div className="mt-8 rounded-xl border border-slate-300 p-5">
        <Status>
          {available
            ? "Services are ready."
            : "Services are temporarily unavailable. Please try again."}
        </Status>
        {/* Full navigation deliberately refreshes server readiness. */}
        {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
        <a
          className="mt-4 inline-flex min-h-11 items-center underline"
          href="/"
        >
          Check again
        </a>
      </div>
      <Link
        href="/onboarding"
        className="mt-6 inline-flex min-h-11 items-center underline"
      >
        Set up a synthetic learner profile
      </Link>
      <Link
        href="/revise"
        className="mt-6 inline-flex min-h-11 items-center underline"
      >
        Practise a topic
      </Link>
      <Link
        href="/diagnostic"
        className="mt-6 inline-flex min-h-11 items-center underline"
      >
        Start a subject diagnostic
      </Link>
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
        className="inline-flex min-h-11 items-center underline"
        href="/privacy"
      >
        Your data requests
      </Link>
      <Link
        className="inline-flex min-h-11 items-center underline"
        href="/channels/whatsapp"
      >
        WhatsApp channel
      </Link>
      <RecommendationCard />
      <small className="mt-6 block text-slate-600">
        Support reference: {requestId}
      </small>
    </main>
  );
}
