# E8 request aggregation — implementation in progress

Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-049 proposal](../decisions/ADR/049-local-request-histograms.md).

`services/request_metrics.py` starts the complete operations slice with an owned
OpenTelemetry provider, a fixed attribute-free histogram, disabled exemplars and
static resource metadata. Its percentile function returns a nearest-rank interval
and distinguishes empty, measured zero and overflow. Its canonical interval projection
retains only schema version, interval bounds and counts; it rejects cumulative data,
unexpected series/attributes, invalid counts and noncanonical or oversized stored JSON.
`services/request_metrics_store.py` adds local Redis storage with 256 intervals,
canonical bodies bounded to 1024 bytes, absolute five-minute expiry from interval start,
idempotent retries, distinct process streams, a finite capping marker and 15-second
collection freshness. Corrupt or missing unexpired data is unavailable. Redis server
time rejects stale publication and future timestamps beyond a one-second host/VM
clock tolerance. Actual key lifetime remains capped at five minutes even within
that tolerance. The real collector integration test exposed this clock boundary;
the initial strict-future check was corrected rather than disabling the test.
No shared database is flushed and no production
key scan is used.

`services/request_metrics_collector.py` owns an SDK delta reader and five-second
background thread, a scoped Redis client with finite I/O and no automatic retries,
and bounded shutdown. Exceptions are not logged with endpoint/payload details.
Collection is best effort, not an authoritative ledger. Candidate API lifespan now
owns the collector; middleware records the existing response-start duration. The
ADMIN snapshot/monitoring task reads the scoped aggregate and removes REQUEST_LATENCY
from unavailable metrics only when the store is valid/fresh. Dashboard presentation
shows empty/unavailable/overflow/capped states and p95 ranges. Runtime wiring is under
verification and has not been deployed to the review stack.

`tests/contract/test_request_metrics.py` uses the installed SDK and in-memory readers
with external sockets disabled. It checks delta collections under active trace
context, environment metadata canaries, exact bucket boundaries, invalid counts,
invalid measurements and percentile containment against exact sorted samples.

Native `make format lint test-unit openapi-check security-source` passes: 650
unit/contract cases, 32 tooling checks, Python/TypeScript types, formatting/lint,
unchanged generated contracts and source secret scanning. Evidence is retained in
`.local/request-metrics-projection-checks.log`. Documentation checks cover 119
Markdown files and 61 requirements. No database or HTTP schema changed; this
unconnected component has not been deployed or claimed as application acceptance.

Subsequent storage/collector checks pass 655 unit/contract cases, 32 tooling checks
and 42 focused component/local Redis cases. Format/lint/types, OpenAPI comparison,
source scanning and security audits pass. Evidence: `.local/request-metrics-clock-verified.log`
and `.local/request-metrics-security.log`. The initial real collector run exposed
host/VM clock skew; bounded tolerance and unchanged TTL limits now have regression tests.

New API/dashboard checks cover lifecycle/failure isolation, conservative alert boundaries,
ADMIN access and malformed-store unavailability. The first unit run caught a missing
new alert enum in the analytics schema; the schema is corrected, preserving its strict
contract test. Runtime/API/browser verification is still in progress.

API checks pass 664 unit/contract, 32 tooling, 51 focused telemetry and 20 operations
cases, lint/types and generated-contract comparison. Full regressions are running.
Initial Chromium runs exposed a consent-success substring also matching the paused
sentence, allowing navigation to cancel the consent POST. A retained diagnostic trace
proves the cancellation and subsequent profile without SELF consent. All 14 success
locators now use an anchored prefix. A separate export alert assertion also matched
Next's route announcer; it now selects main content. No application consent rule or
expected error was weakened. The corrected full matrix remains required; failed runs
are not counted as successful evidence.

The corrected `make e2e` run passes all 90 native browser executions: Chromium
15+15, Firefox 15+15 and WebKit 15+15. Evidence is in
`.local/request-metrics-corrected-browser-matrix.log`. New operations presentation
states, mobile reflow and axe checks pass; the 320-pixel operations capture was
visually reviewed without clipping. This is not physical-device or pilot acceptance.
Full `make migrate test` remains active. `make containers security-containers` passes
for API/web with no HIGH/CRITICAL findings. `make container-smoke` refreshed all eight
healthy services and verified the scheduled owned export/frozen retry.

`make smoke-request-metrics` additionally verifies fresh observations from the running
API through its real collector into scoped local Redis, without creating a learner or
granting a role. It makes 20 loopback liveness requests, requires a newer nonempty
collection and fails after a finite wait. Two fake-store/HTTP tests check fresh versus
stale acceptance. The unit total is now 666 (the active full backend run collected
664 before these two smoke tests were added). Container smoke now includes this probe;
its combined final check is running. The updated operations UI is deployed locally.

Final local acceptance on 10 October: `make migrate test` passes all 259 integration
cases (592.31 seconds), with 664 unit/contract cases at collection time. The later
`make format lint test-unit container-smoke security-source` passes 666 unit/contract
cases, 32 tooling checks, both live container probes and source scanning after adding
the two smoke tests. All eight services remain running. Logs:
`.local/request-metrics-full-backend.log` and `.local/request-metrics-final-local-smoke.log`.
The candidate is on `codex/request-timing`, based on export head `ac4e10f`.

Remaining acceptance: final-head hosted checks and main promotion. This
component alone satisfies neither FR-OPS-002 nor the NFR-PERF-001 load requirement.
