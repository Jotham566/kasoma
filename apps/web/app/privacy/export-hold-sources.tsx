"use client";

import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type Sources = components["schemas"]["ExportHoldSources"];
export function ExportHoldSources({
  target,
  disabled,
  onSelect,
}: {
  target: string;
  disabled: boolean;
  onSelect: (
    kind: "DATA_REQUEST_RECEIPT" | "EXPORT_JOB_RECEIPT",
    id: string,
  ) => void;
}) {
  const [page, setPage] = useState<Sources | null>(null);
  const [source, setSource] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  async function load(reference: string, cursor?: string) {
    setBusy(true);
    setPage(null);
    setStatus("Looking up export evidence…");
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/admin/data-requests/{target}/holds/export-sources/{source}",
        {
          params: {
            path: { target, source: reference },
            query: { cursor, limit: 50 },
          },
        },
      );
      if (!result.data) throw new Error("UNAVAILABLE");
      setSource(reference);
      setPage(result.data);
      setStatus("Export evidence references loaded.");
    } catch {
      setSource("");
      setStatus(
        "Could not load references. Check the export request and your recent administrator sign-in and claim.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      aria-label="Find exact export evidence"
      className="space-y-3 rounded-xl border p-4"
    >
      <h4 className="font-semibold">Find exact export evidence</h4>
      <p>
        Enter an export request reference for this requester. Choose one receipt
        or a cleared expired job, then record its authorized hold decision
        below. This lookup returns references only.
      </p>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          void load(String(data.get("export_request")));
        }}
      >
        <fieldset disabled={disabled || busy} className="space-y-3">
          <legend className="sr-only">Export evidence lookup</legend>
          <label className="block">
            Export request reference
            <input
              name="export_request"
              required
              className="ui-input"
              pattern="[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"
            />
          </label>
          <button className="ui-button ui-button-secondary">
            Find export evidence
          </button>
        </fieldset>
      </form>
      {status && <p role="status">{status}</p>}
      {page && (
        <div className="space-y-3">
          <p>
            Export request: <span className="break-all">{source}</span>
          </p>
          {page.receipt_ids.length === 0 && (
            <p>No receipt references on this page.</p>
          )}
          <ul className="space-y-2">
            {page.receipt_ids.map((id) => (
              <li key={id}>
                <button
                  className="ui-button ui-button-secondary break-all text-left"
                  disabled={disabled || busy}
                  onClick={() => {
                    onSelect("DATA_REQUEST_RECEIPT", id);
                    setStatus(
                      "Receipt selected. Complete the authorized hold decision below.",
                    );
                  }}
                >
                  Use receipt {id}
                </button>
              </li>
            ))}
          </ul>
          {page.export_job_id ? (
            <button
              className="ui-button ui-button-secondary break-all text-left"
              disabled={disabled || busy}
              onClick={() => {
                onSelect("EXPORT_JOB_RECEIPT", page.export_job_id!);
                setStatus(
                  "Expired job selected. Complete the authorized hold decision below.",
                );
              }}
            >
              Use expired job {page.export_job_id}
            </button>
          ) : (
            <p>No cleared expired job is available.</p>
          )}
          {page.next_cursor && (
            <button
              className="ui-button ui-button-secondary"
              disabled={disabled || busy}
              onClick={() => void load(source, page.next_cursor!)}
            >
              Next receipt references
            </button>
          )}
        </div>
      )}
    </section>
  );
}
