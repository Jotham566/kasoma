"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Job = components["schemas"]["ImportView"];
type Input = components["schemas"]["ImportInput"];
const api = () => apiClient("", crypto.randomUUID());
const button = "rounded border px-4 py-3 my-2 disabled:opacity-50";

export default function Imports() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [status, setStatus] = useState(
    "Choose an original synthetic JSON draft batch.",
  );
  const [busy, setBusy] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const retry = useRef<{ body: string; key: string } | null>(null);
  async function run(action: () => Promise<void>) {
    setBusy(true);
    try {
      await action();
    } catch {
      setStatus("Connection interrupted. Retry with the same file.");
    } finally {
      setBusy(false);
    }
  }
  async function load(more: boolean) {
    await run(async () => {
      const result = await api().GET("/api/v1/admin/content-imports", {
        params: { query: { limit: 20, ...(more && cursor ? { cursor } : {}) } },
      });
      if (!result.data) {
        setJobs([]);
        setCursor(null);
        setStatus("Author access required. Sign in again or retry later.");
        return;
      }
      setJobs((old) =>
        more ? [...old, ...result.data.data] : result.data.data,
      );
      setCursor(result.data.next_cursor);
      setStatus("Import status refreshed.");
    });
  }
  async function enqueue() {
    if (
      !file ||
      file.size > 65536 ||
      !file.name.toLowerCase().endsWith(".json")
    ) {
      setStatus("Choose a JSON file no larger than 64 KiB.");
      return;
    }
    await run(async () => {
      const raw = await file.text();
      let body: Input;
      try {
        body = JSON.parse(raw) as Input;
      } catch {
        setStatus("The file is not valid JSON.");
        return;
      }
      if (retry.current?.body !== raw)
        retry.current = { body: raw, key: crypto.randomUUID() };
      const result = await api().POST("/api/v1/admin/content-imports", {
        body,
        params: { header: { "Idempotency-Key": retry.current.key } },
      });
      if (!result.data) {
        setStatus(
          result.response.status === 422
            ? "Batch rejected. Check its schema, provenance, taxonomy and duplicate candidates. No drafts were queued."
            : "Import denied. Check author access, recent sign-in, file size or rate limit.",
        );
        return;
      }
      setJobs((old) => [
        result.data,
        ...old.filter((job) => job.id !== result.data.id),
      ]);
      setStatus(
        "Import accepted. Refresh status after the worker processes it. Retry preserves this job.",
      );
    });
  }
  return (
    <main className="mx-auto max-w-3xl p-6 space-y-4">
      <Link className="underline" href="/admin/content">
        Back to content workspace
      </Link>
      <h1 className="text-3xl font-semibold">Import synthetic draft items</h1>
      <p>
        Original Kasoma synthetic content only. JSON batches contain 1–20
        records and must be at most 64 KiB. Include source, source locator and
        rights evidence for each item. Imported drafts require independent
        review before publication.
      </p>
      <p>
        No real learner data, confidential sources, documents, archives or media
        files.
      </p>
      <label className="block">
        Draft JSON file{" "}
        <input
          className="block py-3"
          type="file"
          accept=".json,application/json"
          disabled={busy}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
      </label>
      <button
        className={button}
        disabled={busy || !file}
        onClick={() => void enqueue()}
      >
        Queue draft import
      </button>
      <p role="status">{status}</p>
      <button
        className={button}
        disabled={busy}
        onClick={() => void load(false)}
      >
        Refresh import status
      </button>
      <ul className="space-y-4">
        {jobs.map((job) => (
          <li key={job.id} className="rounded border p-4">
            <p>
              Import {job.id}: {job.status}
            </p>
            <p>Processing attempts: {job.attempts}</p>
            {job.error_code && (
              <p>
                {job.status === "FAILED"
                  ? "Import failed. No partial drafts were saved."
                  : "Processing will retry."}{" "}
                Code: {job.error_code}
              </p>
            )}
            <ul>
              {job.results.map((row) => (
                <li key={row.position}>
                  <Link
                    className="underline"
                    href={`/admin/content?version=${row.version_id}`}
                  >
                    Record {row.position}:{" "}
                    {row.outcome === "CREATED"
                      ? "Open draft"
                      : "Open existing duplicate"}
                  </Link>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
      {cursor && (
        <button
          className={button}
          disabled={busy}
          onClick={() => void load(true)}
        >
          Load more imports
        </button>
      )}
    </main>
  );
}
