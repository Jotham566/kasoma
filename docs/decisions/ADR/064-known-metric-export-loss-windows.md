# ADR-064: Known metric export loss remains unavailable

Date: 19 October 2026
Status: Accepted within delegated MVP engineering discretion; complete hosted39308594889 verified
Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-MNT-001

## Context and decision

ADRs 049/054 require missing observations to remain distinguishable from measured zero.
Two real Redis regressions show the request/model collectors can lose a nonempty SDK
interval during export and retain or refresh a fresh empty aggregate. Best-effort
collection is not a complete ledger, but known failure must not appear healthy zero.
Apply the finite uncertainty rule introduced in ADR-063 consistently to these existing
collectors. This changes no grading, authentication, latency definition or provider call.

After a collection/export failure, remember only a local monotonic deadline and publish
one namespace-wide incomplete marker with at most 300 seconds remaining. A failed attempt
to publish it is retried before subsequent export/freshness, using the remaining window.
The shared Redis READ checks the marker atomically. A successful empty pulse during the
window cannot make the aggregate available. Another producer cannot shorten an existing
window. Stop collectors cannot publish new freshness. No raw exception is logged.

Share only the existing bounded store's marker operation; keep histogram, model and OTP
payload codecs, static instruments and purpose hashes separate. Stored frame bytes,
absolute observation expiry, immutable retries, 256-frame cap, clock-skew limits and
API schemas stay unchanged. The marker contains only the fixed value 1, not a source,
request, actor, route, timestamp or payload. No new database, provider or dependency.
Conservative temporary unavailability is intentional; it is not a new production SLO.

This detects known SDK/export failures, not arbitrary process crashes or complete fleet
coverage. Intentional capacity eviction remains explicitly capped lower-bound data.
Existing ADMIN authorization, unavailable UI states and warning suppression already
handle missing observations. Real learner use, privacy/provider and release gates remain.

Roll out the current API and operations-worker readers together before claiming this
known-loss guarantee. Older server readers do not honor request/model markers; payload
compatibility alone does not prove mixed-reader behavior. No mixed-version or production
rollout acceptance is inferred from the local synthetic suite.

## Verification and rollback

Preserve the two failing real-SDK/Redis cases. Verify write rejection/exception, empty
recovery, finite/max-preserving TTL, source/kind isolation, forced marker expiry in owned
test namespaces, stopped collection and no secret diagnostics. Re-run original request,
model and OTP codec/store/lifecycle/ADMIN tests, quality/security/container and full hosted
gates. No timeout, assertion or provider/grading quota is relaxed. Rollback must keep affected projections unavailable while markers remain live; do not
reintroduce an older reader that ignores known loss. Disable affected observation
projections and let transient metadata expire. No history is changed.

Complete hosted39308594889 at b5557a3 passes1,180 unit/contract,502 integration,
35 tooling and114 full browser executions plus all engineering gates. Logical
restore69 tables/686 rows425ms cleans successfully. Only Markdown follows; all
production/mixed-reader, ledger, provider/privacy and erasure gates remain separate.
