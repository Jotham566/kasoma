"use client";

import Link from "next/link";
import { useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type View = components["schemas"]["OperationsView"];
const messages: Record<
  components["schemas"]["OperationAlert"]["code"],
  string
> = {
  REQUEST_RESPONSE_START_SLOW:
    "Observed API response-start timing exceeded its threshold",
  DATABASE_DOWN: "Database unavailable",
  REDIS_DOWN: "Redis unavailable",
  WORKER_HEARTBEAT_MISSING: "Monitoring worker heartbeat unavailable",
  IMPORT_FAILED: "Failed draft imports need investigation",
  IMPORT_STALLED: "Queued imports have exceeded the age threshold",
  FLAG_BACKLOG: "Unresolved flag backlog exceeded its threshold",
  HIGH_PRIORITY_FLAGS: "High-priority flags need attention",
  CHANNEL_INBOUND_FAILED: "Failed incoming channel messages need investigation",
  CHANNEL_OUTBOUND_FAILED:
    "Failed outgoing channel messages need investigation",
  CHANNEL_STALLED: "Pending channel messages exceeded the age threshold",
  CHANNEL_DISPATCH_SLOW:
    "Local feedback dispatch exceeded its timing threshold",
  OTP_ADAPTER_FAILURES: "Observed OTP adapter failures need investigation",
  MODEL_GATEWAY_VOLUME:
    "Observed local model attempts reached the volume threshold",
  GRADING_STALLED: "Pending grading work exceeded the age threshold",
  EXPORT_FAILED: "Failed personal exports need investigation",
  EXPORT_STALLED: "Pending personal exports exceeded the age threshold",
  RETIREMENT_FAILED:
    "Synthetic export evidence maintenance needs investigation",
  RETIREMENT_STALLED:
    "Synthetic export evidence maintenance heartbeat is overdue",
};

export default function Operations() {
  const [view, setView] = useState<View | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(
    "Load the current operational snapshot. ADMIN access required.",
  );
  async function refresh() {
    setBusy(true);
    setStatus("Loading operational snapshot…");
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/admin/operations",
      );
      if (!result.data) {
        setView(null);
        setStatus(
          "Snapshot unavailable. Check ADMIN access, sign-in or rate limit.",
        );
        return;
      }
      setView(result.data);
      setStatus("Operational snapshot refreshed.");
    } catch {
      setView(null);
      setStatus(
        "Connection interrupted. No current health result is available; retry.",
      );
    } finally {
      setBusy(false);
    }
  }
  const counters = view?.counts
    ? ([
        ["Queued imports", view.counts.queued_imports],
        ["Failed imports in the last 24 hours", view.counts.failed_imports_24h],
        ["Unresolved content flags", view.counts.unresolved_flags],
        ["High-priority unresolved flags", view.counts.high_priority_flags],
      ] as const)
    : [];
  const channel = view?.counts?.channel;
  const exports = view?.counts?.exports;
  const grading = view?.counts?.grading;
  const retirement = view?.counts?.retirement;
  const usage = view?.model_usage;
  const otp = view?.otp_dispatch;
  const channelCounters = channel
    ? ([
        ["Queued incoming messages", channel.queued_inbound],
        ["Queued outgoing messages", channel.queued_outbound],
        [
          "Failed incoming messages received in the last 24 hours",
          channel.failed_inbound_received_24h,
        ],
        [
          "Rejected incoming messages received in the last 24 hours",
          channel.rejected_inbound_received_24h,
        ],
        [
          "Failed outgoing messages created in the last 24 hours",
          channel.failed_outbound_created_24h,
        ],
        [
          "Cancelled outgoing messages created in the last 24 hours",
          channel.cancelled_outbound_created_24h,
        ],
        [
          "Transport-accepted outgoing messages created in the last 24 hours",
          channel.accepted_outbound_created_24h,
        ],
      ] as const)
    : [];
  return (
    <main className="staff-page operations-page">
      <Link className="ui-text-link" href="/admin/content">
        Content workspace
      </Link>
      <h1 className="text-3xl font-semibold">Operations health</h1>
      <p>
        Local service and queue monitoring. Refresh for current values; this
        page does not refresh automatically.
      </p>
      <button
        className="ui-button ui-button-primary"
        disabled={busy}
        onClick={() => void refresh()}
      >
        Refresh operations
      </button>
      <p role="status">{status}</p>
      {view && (
        <>
          <p>
            Sampled{" "}
            {new Intl.DateTimeFormat("en-UG", {
              timeZone: "Africa/Kampala",
              dateStyle: "medium",
              timeStyle: "medium",
            }).format(new Date(view.generated_at))}{" "}
            (Africa/Kampala).
          </p>
          {retirement && (
            <section
              className="surface-card operations-section"
              aria-label="Synthetic export evidence maintenance"
            >
              <h2 className="text-xl font-semibold">Export evidence</h2>
              <p>
                {retirement.scheduled &&
                retirement.database_enabled &&
                retirement.scope_allowed
                  ? "Enabled in an isolated synthetic scope"
                  : "Disabled"}
              </p>
              <p>
                Due completed exports:{" "}
                {retirement.due_requests.at_least ? "At least " : ""}
                {retirement.due_requests.value}. Exact holds and remaining
                copies can retain this evidence.
              </p>
              <p>
                Last database batch or activation:{" "}
                {retirement.last_db_progress_seconds} seconds ago.
              </p>
              <p>
                Last executor observation:{" "}
                {retirement.last_attempt_status ?? "Unavailable"}.
              </p>
              {retirement.last_removed !== null && (
                <p>
                  Last batch: {retirement.last_removed} rows removed;{" "}
                  {retirement.last_examined} examined.
                </p>
              )}
              <p>
                Failures in the current five-minute interval:{" "}
                {retirement.observation_available
                  ? `${retirement.failures_current_interval.at_least ? "At least " : ""}${retirement.failures_current_interval.value}`
                  : "Unavailable"}
                .
              </p>
              <p>
                Observations are best effort and expire within five minutes.
                Account deletion is not enabled.
              </p>
            </section>
          )}
          <section
            className="surface-card operations-section"
            aria-label="Service health"
          >
            <h2 className="text-xl font-semibold">Service health</h2>
            <ul>
              <li>Database: {view.health.database}</li>
              <li>Redis: {view.health.redis}</li>
              <li>Monitoring worker: {view.worker}</li>
            </ul>
          </section>
          <section
            className="surface-card operations-section"
            aria-label="Active alerts"
          >
            <h2 className="text-xl font-semibold">Active alerts</h2>
            {view.alerts.length === 0 ? (
              <p>No configured thresholds breached in this snapshot.</p>
            ) : (
              <ul>
                {view.alerts.map((alert) => (
                  <li key={alert.code}>
                    {alert.severity}: {messages[alert.code]} (observed{" "}
                    {alert.observed}, threshold {alert.threshold}).
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section
            className="surface-card operations-section"
            aria-label="Queue and content workload"
          >
            <h2 className="text-xl font-semibold">
              Queue and content workload
            </h2>
            {view.counts ? (
              <>
                <table className="w-full text-left">
                  <thead>
                    <tr>
                      <th scope="col">Metric</th>
                      <th scope="col">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {counters.map(([label, count]) => (
                      <tr key={label}>
                        <th className="py-2 font-normal" scope="row">
                          {label}
                        </th>
                        <td>
                          {count.at_least ? "At least " : ""}
                          {count.value}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p>
                  Oldest queued import: {view.counts.oldest_import_seconds}{" "}
                  seconds. Alert threshold: {view.thresholds.import_age_seconds}{" "}
                  seconds.
                </p>
                <p>
                  Failed-import threshold: {view.thresholds.failed_imports}.
                  Flag backlog threshold: {view.thresholds.unresolved_flags}.
                </p>
              </>
            ) : (
              <p>
                Workload counts unavailable. Do not interpret missing values as
                zero.
              </p>
            )}
          </section>
          <section
            aria-label="Local channel operations"
            className="surface-card operations-section"
          >
            <h2 className="text-xl font-semibold">Local channel delivery</h2>
            {channel ? (
              <>
                <table className="w-full text-left">
                  <thead>
                    <tr>
                      <th scope="col">Metric</th>
                      <th scope="col">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {channelCounters.map(([label, count]) => (
                      <tr key={label}>
                        <th className="py-2 font-normal" scope="row">
                          {label}
                        </th>
                        <td>
                          {count.at_least ? "At least " : ""}
                          {count.value}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p>
                  Oldest pending channel message:{" "}
                  {channel.oldest_pending_seconds} seconds. Alert threshold:{" "}
                  {view.thresholds.channel_queue_age_seconds} seconds.
                </p>
                <p>
                  Recent cohort counts show current message status, not the time
                  a failure or cancellation occurred.
                </p>
                {channel.feedback_dispatch.p95_ms === null ? (
                  <p>No feedback dispatch samples in the last 24 hours.</p>
                ) : (
                  <p>
                    Feedback dispatch p95: {channel.feedback_dispatch.p95_ms} ms
                    across {channel.feedback_dispatch.sample_size} samples.
                    {channel.feedback_dispatch.sample_capped
                      ? " Only the latest 1,000 samples are included."
                      : ""}
                  </p>
                )}
                <p>
                  Timing measures durable receipt to local fake transport
                  acceptance. It does not prove delivery to a learner or a
                  release latency target.
                </p>
                <p>
                  Dispatch alert: {view.thresholds.channel_dispatch_p95_ms} ms
                  with at least {view.thresholds.channel_dispatch_min_samples}{" "}
                  samples. Failure alert: {view.thresholds.channel_failures}{" "}
                  recent messages.
                </p>
              </>
            ) : (
              <p>
                Channel metrics unavailable. Missing values do not mean zero.
              </p>
            )}
          </section>
          <section
            aria-label="Local OTP adapter observations"
            className="surface-card operations-section"
          >
            <h2 className="text-xl font-semibold">OTP adapter outcomes</h2>
            {otp ? (
              <>
                <dl>
                  {(
                    [
                      ["Observed attempts", otp.observed_attempts],
                      ["Email adapter returned", otp.email_returned],
                      ["Email adapter failed", otp.email_failed],
                      ["SMS adapter returned", otp.sms_returned],
                      ["SMS adapter failed", otp.sms_failed],
                    ] as const
                  ).map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{value}</dd>
                    </div>
                  ))}
                </dl>
                <p>
                  Best-effort local API observations retained for up to five
                  minutes across {otp.interval_count} intervals.
                  {otp.capped
                    ? " The interval limit was reached; some observations were dropped."
                    : ""}
                </p>
                <p>
                  Includes fake and Mailpit adapters. A return is not delivery
                  or receipt. Suppressed sends are excluded; billing and
                  complete messaging usage remain unavailable.
                </p>
                <p>
                  Local warning threshold: {view.thresholds.otp_failures}{" "}
                  observed adapter failures. This does not enforce a quota.
                </p>
              </>
            ) : (
              <p>
                OTP adapter observations unavailable. Missing values do not mean
                zero.
              </p>
            )}
          </section>
          <section
            aria-label="Local model observations"
            className="surface-card operations-section"
          >
            <h2 className="text-xl font-semibold">Local model activity</h2>
            {usage ? (
              <>
                <dl>
                  {(
                    [
                      ["Observed provider attempts", usage.observed_attempts],
                      ["Returned candidates", usage.candidate_responses],
                      ["Returned fallbacks", usage.fallback_responses],
                      ["Attempts without a result", usage.no_result_attempts],
                      [
                        "Attempts with unknown token usage",
                        usage.usage_unknown_attempts,
                      ],
                      [
                        "Reported input-token subtotal",
                        usage.reported_input_tokens,
                      ],
                      [
                        "Reported output-token subtotal",
                        usage.reported_output_tokens,
                      ],
                      [
                        "Total input tokens",
                        usage.total_input_tokens ?? "Unknown",
                      ],
                      [
                        "Total output tokens",
                        usage.total_output_tokens ?? "Unknown",
                      ],
                    ] as const
                  ).map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{value}</dd>
                    </div>
                  ))}
                </dl>
                <p>
                  Best-effort observations retained for up to five minutes
                  across {usage.interval_count} intervals.
                  {usage.capped
                    ? " The interval limit was reached; some observations were dropped."
                    : ""}
                </p>
                <p>
                  Includes development fake-provider probes. Candidates are
                  awaiting validation. Missing token usage remains unknown;
                  reported subtotals exclude it. Billing and costs are
                  unavailable.
                </p>
                <p>
                  Local volume warning: {view.thresholds.model_gateway_attempts}{" "}
                  observed attempts. This does not enforce a quota or establish
                  grading accuracy, complete fleet usage or release acceptance.
                </p>
              </>
            ) : (
              <p>
                Model observations unavailable. Missing values do not mean zero.
              </p>
            )}
          </section>
          <section
            aria-label="Grading queue operations"
            className="surface-card operations-section"
          >
            <h2 className="text-xl font-semibold">Grading queue</h2>
            {grading ? (
              <>
                <dl>
                  {(
                    [
                      ["Queued grading work", grading.queued],
                      ["Running grading work", grading.running],
                      [
                        "Expired running leases",
                        grading.expired_running_leases,
                      ],
                      [
                        "Graded in the last 24 hours",
                        grading.graded_finished_24h,
                      ],
                      [
                        "Neutral outcomes in the last 24 hours",
                        grading.neutral_finished_24h,
                      ],
                      [
                        "Processing fallbacks in the last 24 hours",
                        grading.processing_fallback_finished_24h,
                      ],
                      ["Pending audit assignments", grading.pending_audits],
                      [
                        "Bands disabled after activation",
                        grading.disabled_bands,
                      ],
                    ] as const
                  ).map(([label, count]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>
                        {count.at_least ? "At least " : ""}
                        {count.value}
                      </dd>
                    </div>
                  ))}
                </dl>
                <p>
                  Oldest pending grading work: {grading.oldest_pending_seconds}{" "}
                  seconds. Alert threshold:{" "}
                  {view.thresholds.grading_age_seconds} seconds.
                </p>
                <p>
                  Processing fallbacks include provider refusals, budget and
                  validation failures; they do not measure academic errors.
                  Pending audits include sealed assignments that are not yet
                  available for expert review. Counts do not establish grading
                  accuracy, model spend or release latency acceptance.
                </p>
              </>
            ) : (
              <p>
                Grading queue metrics unavailable. Missing values do not mean
                zero.
              </p>
            )}
          </section>
          <section
            aria-label="Personal export operations"
            className="surface-card operations-section"
          >
            <h2 className="text-xl font-semibold">Personal exports</h2>
            {exports ? (
              <>
                <dl>
                  {(
                    [
                      ["Queued exports", exports.queued],
                      ["Running exports", exports.running],
                      [
                        "Failed exports finished in the last 24 hours",
                        exports.failed_finished_24h,
                      ],
                    ] as const
                  ).map(([label, count]) => (
                    <div key={label} className="py-2">
                      <dt>{label}</dt>
                      <dd>
                        {count.at_least ? "At least " : ""}
                        {count.value}
                      </dd>
                    </div>
                  ))}
                </dl>
                <p>
                  Oldest pending export: {exports.oldest_pending_seconds}{" "}
                  seconds. Alert threshold: {view.thresholds.export_age_seconds}{" "}
                  seconds. Failure threshold: {view.thresholds.export_failures}.
                </p>
                <p>
                  Counts show current job status. Explicit retry removes a job
                  from the failed count. Pending age runs from the latest owner
                  command, including automatic retries. These local alerts do
                  not measure legal fulfillment deadlines.
                </p>
              </>
            ) : (
              <p>
                Export metrics unavailable. Missing values do not mean zero.
              </p>
            )}
          </section>
          <Link className="ui-text-link" href="/admin/flags">
            Review content flags
          </Link>
          <section
            className="surface-card operations-section"
            aria-label="API response-start timing"
          >
            <h2 className="text-xl font-semibold">API response-start timing</h2>
            {view.request_timing ? (
              <>
                {view.request_timing.sample_size === 0 ? (
                  <p>
                    Collector available. No observed requests in the retained
                    window.
                  </p>
                ) : (
                  <p>
                    Observed p95:{" "}
                    {view.request_timing.p95_lower_exclusive_ms === null
                      ? "0"
                      : `greater than ${view.request_timing.p95_lower_exclusive_ms}`}{" "}
                    ms
                    {view.request_timing.p95_upper_inclusive_ms === null
                      ? ", with no finite upper bound"
                      : `, up to ${view.request_timing.p95_upper_inclusive_ms} ms`}
                    . {view.request_timing.sample_size} observations across{" "}
                    {view.request_timing.interval_count} collected intervals.
                  </p>
                )}
                {view.request_timing.capped && (
                  <p>
                    Storage capacity was reached; some intervals were removed.
                  </p>
                )}
              </>
            ) : (
              <p>
                Response-start metrics unavailable. Missing values do not mean
                zero.
              </p>
            )}
            <p>
              Best-effort measurements from the last five minutes, collected
              every five seconds. Outages or process exits can lose
              observations. Timing ends when API response headers are ready; it
              does not measure complete downloads, network delivery or release
              SLOs.
            </p>
            <p>
              Alert threshold: {view.thresholds.request_p95_ms} ms with at least{" "}
              {view.thresholds.request_min_samples} observations. An alert
              requires the histogram interval to prove the threshold was
              reached.
            </p>
          </section>
          <h2 className="text-xl font-semibold">
            Instrumentation still pending
          </h2>
          <p>
            AI, SMS and email usage, grading-failure rates, complete-response
            latency, mastery lag and webhook failures before durable intake
            remain unmeasured. No external notifications are sent.
          </p>
        </>
      )}
    </main>
  );
}
