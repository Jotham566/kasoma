# ADR-039: Minimized local channel operations

Date: 4 October 2026
Status: Accepted within delegated MVP implementation discretion; synthetic implementation verified in CI 37221185319
Requirements: FR-OPS-002/004, NFR-OBS-001, NFR-PERF-002, NFR-SEC-002

## Decision

Extend the existing ADMIN-only, rate-limited operations snapshot and sampler with local channel
queue depth/oldest age, terminal incoming failures/rejections, outgoing failures/cancellations and
fake transport acceptances. Preserve the 10,000-count cap with its explicit lower-bound indicator.
No identifiers, phone numbers, commands, message bodies, answers or exception diagnostics are returned.

Failure/rejection/cancellation counts describe the current status of messages received/created in
the preceding 24 hours, not the time of a later status transition. Pending depth/age includes all
pending messages. Sample at most the latest 1,000 successfully dispatched practice-feedback rows
sent in the preceding 24 hours, excluding invalid negative durations. Report nearest-rank p95
milliseconds from durable incoming receipt to fake transport acceptance, sample size and truncation.
No samples yields null, never measured zero. This measures local dispatch, not delivery to a learner,
AI latency, HTTP latency or performance under the agreed MVP load. It cannot establish release SLOs.

Add local numeric alerts: failed inbound/outbound recent cohorts (default one), oldest pending
message age (default 60 seconds), and dispatch p95 at or above 1,500 ms with at least 20 samples.
Thresholds are typed/configurable and bounded. Inclusive boundaries and recovery match ADR-033.
Cancelled/rejected messages alone do not alert because STOP, consent and validation are expected
causes. Alert logs contain only existing code/severity/numeric values/correlation metadata.

Migration 0021 adds operational indexes only. No new personal-data table or retention period is
introduced. Counts are rebuilt from PostgreSQL truth; Redis loss does not fabricate zero values.
Dependency/query failure remains unavailable under the existing snapshot behavior. SMS/email/AI
usage, ingress signature failures and production notifications remain explicitly uninstrumented.

## Verification

Test cohort/window boundaries, caps, nearest-rank sampling and empty state, exact thresholds and
recovery, queued/failed/cancelled states, permission/revocation, payload minimization and browser
empty/unavailable rendering. Regenerate OpenAPI/TypeScript, run clean migrations, full regressions,
security and container checks. Do not infer production or performance acceptance from fixtures.
