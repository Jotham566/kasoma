# E8 minimized response-start timing

Requirements: NFR-OBS-001, FR-OPS-002, NFR-SEC-002; instrumentation toward NFR-PERF-001.
Status: local contract verification; hosted application regression pending.

`apps/api/main.py` measures elapsed monotonic time from outer correlation middleware entry until
the response headers are ready. Round up to integer milliseconds and emit optional `response_start_ms`
on the existing `api.request` event and trace span, alongside status/correlation/channel. This is
server processing to response start, not full body/network delivery or a p95-under-load result.

The additive numeric field is defined in `packages/analytics-schema/foundation-event.schema.json`.
Existing worker events remain valid without it. Logs/traces include no route URLs, query parameters,
request/response bodies, credentials or identity fields. The same timing applies to returned errors
and safely converted internal failures. No new datastore or cloud telemetry dependency is added.
This extends the approved logging design; no architectural decision is changed.

Six contract cases in `tests/contract/test_request_timing.py` check successful requests, unknown
paths, validation errors, disabled webhook verification, sanitized internal failures, exact timing
with an injected monotonic clock and compatibility with existing worker events. Canary values in
path/query/authorization/body/exception data must never appear in logs or traces.

The operations dashboard still reports REQUEST_LATENCY aggregation unavailable. A log field is
not an aggregated p95, load test, availability SLO, production alert channel or retention backend.
Those remain explicit gaps. Native database/browser acceptance remains unavailable until Docker
is restored; hosted full checks are required before promotion.

Local `make format lint openapi-check test-unit security` passes 394 unit/contract and five tooling
checks, including all six timing cases, plus types, event formatting, contract comparison, Bandit,
local secret checks and Python/JavaScript dependency audits. HTTP schemas are unchanged.
