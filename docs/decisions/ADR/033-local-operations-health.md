# ADR-033: Local operational health and threshold alerts

Date: 3 October 2026
Status: Accepted within delegated MVP implementation discretion
Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-MNT-001

## Decision and scope

Add an ADMIN-only read-only operational snapshot and web dashboard for the implemented
local services. Recheck current authorization on every request, rate-limit reads and
return no learner, author, document, answer, flag-comment or exception details.

Show PostgreSQL/Redis health, monitoring-worker heartbeat, queued import count/oldest age,
failed imports in the last 24 hours, unresolved flags and high-priority unresolved flags.
Counts cap at 10,000 with an explicit lower-bound indicator. Operational snapshots are
transient and never used as learning or privacy-deletion decisions.

A Celery operations task samples every 60 seconds and emits allowlisted structured alerts
with correlation ID, code, severity and numeric threshold/value. Store its heartbeat only
in local Redis with a 180-second TTL, namespaced by a keyed database-name/search-path digest. Native/Compose host aliases
share heartbeat identity; isolated test schemas remain separate. Manual checks do not
write a worker heartbeat.
No new database table, external notification or cloud monitoring dependency is introduced.
Redis is disposable; missing heartbeat means unavailable, never proof that a worker is up.
The monitoring task cannot alert during its own total outage: the dashboard and existing
health probes expose that absence; independent production monitoring remains required.

Initial configurable local thresholds: one failed import in 24 hours; oldest queued import
300 seconds; 20 unresolved flags. Any high-priority unresolved flag or unavailable core
dependency is critical. Missing monitoring heartbeat is a warning. These are operational
engineering defaults, not a safeguarding response policy or production SLO approval.
Threshold checks use inclusive boundaries. Resolved conditions disappear from the current
snapshot; periodic alert logs remain bounded by the one-minute sampler cadence.

AI usage, messaging usage, grading-failure rates, latency distributions, mastery lag and
WhatsApp failures are explicitly unavailable until their paths/telemetry are implemented.
Do not report zero as measured evidence for an uninstrumented capability. This is a thin
FR-OPS-002 slice, not complete production observability or release acceptance.

Task registrations are application-local (`shared=False`) so constructing another Celery
application cannot reuse a different database/configuration closure. Regression tests cover
monitoring, imports and export expiry without connecting to external services.

## Verification

Test authorized/unauthorized/revoked roles, snapshot minimization, capped counts, healthy/
degraded dependencies, heartbeat expiry, exact threshold boundaries and recovery, safe log
fields, worker registration, and browser refresh/accessibility. Update generated contracts,
configuration example, runbook, changelog, sprint and traceability. Existing read-only
health remains compatible. Rollback disables this sampler/UI route and lets Redis TTL expire.
