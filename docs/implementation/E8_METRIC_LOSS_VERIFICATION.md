# Known metric-export loss - candidate verification

Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-064](../decisions/ADR/064-known-metric-export-loss-windows.md).
Status: local targeted and engineering checks pass; own full hosted acceptance pending.

## Reproduced defect

Two actual SDK/Redis regressions fail against parent source ceee401: request and model
collectors return a fresh empty aggregate after an unacknowledged nonempty export.
The request sample_size becomes zero and the six model counts become zero. These
are measured-state assertions, not inferred from static inspection. Both failures
are retained in ignored .local/metric-loss-red.log (two failed in 0.14s).

The initial correction passes both cases in 0.11s. Expand coverage to all three kinds,
remaining-window publication before recovered freshness, finite/max-preserving TTL,
known subsequent frames remaining hidden, forced marker expiry and stopped collection.
Actual namespace-isolation tests ensure a request marker does not poison model/OTP.
Seven invalid durations fail before Redis; two controlled-clock SDK cases cover a
failed marker write, retry before freshness and withheld diagnostic canaries.
The final focused target passes 13 cases in 0.15s (nine contract, four integration).

## Correction boundary

The bounded store owns the existing fixed incomplete marker operation, previously
OTP-only. Request/model collectors retain a monotonic remaining-window deadline and
republish uncertainty before any pulse/export. All current readers test their own
marker atomically. No observation or personal data enters this marker. Payload bytes,
codecs, HMAC purpose scopes, frame absolute expiry, capping and skew bounds are unchanged.
No API schema, database migration, dependency, authentication, grading, model/messaging
call, quota or retention policy change. The new behavior only makes existing operational
projections unavailable while their data is known incomplete. Frames may continue to
arrive with their original expiry; unavailable data is not silently rewritten as zero.

This does not detect arbitrary process crashes, establish fleet completeness, billing
or production SLOs. All API/operations-worker readers must support the marker; payload
compatibility does not prove mixed-reader deployment behavior. On rollback preserve
unavailable projections while markers remain live. No production approval is inferred.

## Initial broader verification

The first test-file editing script fails a text anchor before writing the integration
file; no application file is changed by that failed script. The subsequent run covers
nine then-existing cases, 51 request, 43 model and 35 OTP/identity cases. The corrected
expanded file subsequently supplies the 13 focused passes above. These are phased
results, not acceptance of an unexecuted test expansion.

Final local checks all exit zero:

- make lint openapi-check build: formatting, lint, 200 typed Python source files,
  TypeScript checks, contract drift and production build pass.
- make test-unit: 1,180 unit/contract and 35 tooling cases; 502 integration cases
  deselected. Three existing TestClient/network-block warnings remain.
- make test-metric-loss: 13 cases in 0.15s.
- make test-request-metrics: 51 cases in 0.79s.
- make test-model-metrics: 43 cases in 0.38s.
- make test-otp-observations: 35 cases in 40.83s.
- make test-operations: 24 cases in 28.99s.
- make test-web-otp-observations: six executions across Chromium, Firefox and WebKit
  (two per engine, 21.8/18.3/14.8s). These do not replace native or physical review.
- make security security-source and make containers security-containers container-smoke:
  dependency/source/image checks and owned export/request/model/service probes pass.
  Docker remains running with default-disabled OTP and retirement configuration.

These targeted integration passes do not claim the complete 502-case integration
suite or full browser suite. Complete own hosted execution remains pending. The live parent OTP run
39304052749 at ceee401 must stay unchanged; it cannot accept this newer collector/store
and test/Make tree. Main remains87a93d7. Normal Docker services stay running, with OTP
collection/retirement disabled. No caches, images, volumes or unrelated data are swept.

## Files and next gate

Bounded interval store, request/model collectors and OTP store method inheritance;
new contract/actual Redis regressions and Make target; ADR-064/049/054/index, API and
runbook, changelog/sprint/traceability. No UI or generated contract change. Publish a separate source candidate for its own full hosted
run. Do not infer application acceptance from documentation checks.
