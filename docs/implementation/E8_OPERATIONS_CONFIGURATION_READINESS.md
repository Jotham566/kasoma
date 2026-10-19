# Versioned operations configuration readiness

19 October2026. FR-OPS-002/003,NFR-SEC-002/OBS-001/ACC-001/LOC-001/MNT-001.
[ADR-067](../decisions/ADR/067-versioned-operational-warning-configuration.md).

Read API section9, SRD administrator/operations scope, bootstrap configuration, security
and UX; inspect ADR-033/053, existing OperationThresholds/Settings bounds, staff/recent
OTP authorization, immutable AuditLog, request retry conventions and current staff UI.
The generic configuration route is absent. Existing warning values come from Settings.
No conflicting accepted decision requires them to remain startup-only forever.

Implement a closed15-key numeric warning configuration, version-reference checks and
existing-audit-backed exact retry authority. Keep secrets, academic controls, hard caps,
consent/retention, provider and activation outside this allowlist. Global version rows
hold no learner/actor/contact/answer or free text; AuditLog remains the existing staff
accountability authority. The current erasure proposal is not approval; refresh the
source inventory/disposition for the new shared configuration tables before its review.

Additive schema/API/service, existing worker snapshot integration and Operations-linked
UI form the complete slice. Configuration0 preserves environment defaults until the
first explicit administrative edit freezes the full resolved map. A changed environment
invalidates a stale version0 form. Exact retries return the original recorded version;
subsequent current configuration is loaded separately. Lost acknowledgement never silently
regenerates a key or overwrites a newer version.

On unavailable configuration, saved-state editing is unavailable; operational warning
sampling applies its explicitly labeled startup defaults and a warning, preserving core
unconditional alarms. No processing policy is inferred from a warning threshold.
Required gates: contracts/ranges, real PostgreSQL concurrency/SQL/rollback/role/worker,
three-engine browser/a11y/retry, clean/upgrade/restricted-login/populated recovery, normal
quality/security/images/service and own full hosted acceptance. No inference, external
model/messaging/cloud call, real data or destructive migration is needed or authorized.

## Verification in progress and retained failures

Initial30 focused cases pass23.50s; the expanded31-case rollback suite passes27.76s.
Initial logical restore at0043 passes71 tables/691 rows305ms; separate actual MinIO
restore passes71/691/one42,060-byte object179ms, sources stopped, integrity probes and
cleanup empty. Actual restricted-login test passes9.65s; initial quality/contracts/build,
source/dependency security and image/service smoke pass with eight healthy services.
Normal synthetic preview is advanced additively to0043 without cleanup or activation.
These checks precede0044 and do not accept that newer guard.

Retain failures: direct pytest invocation lacks the Make PATH for subprocess uv; a test
module name collision stops collection; test expectations initially use403 instead of
existing REAUTH_REQUIRED401, and literal JSON is parsed as a SQL bind. All corrected in
the focused tests. A worker-observation spy initially accepts four instead of seven
arguments; fix the spy without weakening the actual worker execution. The new upgrade
probe exposes trailing-public configuration fallback; require exact current-schema tables.
The first0044 draft accidentally includes0043 table creation and is refused by duplicate
relations in isolated upgrades; restrict0044 to CREATE OR REPLACE FUNCTION only. That
draft never advances the normal preview to0044.

Initial browser trials detect overflow at320px/200% text, including a WebKit-only residual
scroll extent after form bounds fit. Root/element geometry and screenshots are diagnostic;
no clipping of the document or relaxed reflow assertion is accepted. Final three-engine
acceptance remains pending. Keep original full-regression interruption explicit:1,277
unit/contract pass; integration is intentionally interrupted after47 passes/231.14s to
freeze corrected tests and SQL before restarting. It is not a full regression pass.
Two broad read-only catalog counts hit existing statement timeouts; indexed per-relation
inspection succeeds71 tables/501 columns/121 FKs/102 triggers, without timeout increases
or schema cleanup. Both parent candidates have since passed their own hosted runs;
none of that parent evidence accepts this configuration implementation.

## Frozen0044 candidate evidence

make test-operations-configuration passes34 contract/actual PostgreSQL cases in52.92s,
including every stored lower/upper range, stale/multi-key SQL rejection, independent
worker defaults, exact concurrent retries, recent/revoked roles, injected audit rollback,
chunked byte limits and populated0042→0044 preservation. Current-schema lookup is now
explicit; a pre0043 isolated schema cannot fall through to the review database.

The final dedicated browser journey passes once in each Chromium/Firefox/WebKit engine:
edit, actual committed lost response, same-key retry, stale conflict, offline/reload,
keyboard,320px/200% text and Axe. Native control overflow handling and two paint frames
preserve the strict document scroll-width assertion; document overflow is not hidden.
Initial broad runs and the invalid0044 draft remain failures above. The final candidate
uses a separate Playwright config/schema to avoid changing other suites' global warnings.

make format/lint, generated OpenAPI/client check, type checking (208 source files),
build, dependency/source security and final image scans pass. make migrate seed and
container-smoke advance the normal synthetic review DB to0044 and pass frozen export,
request/model probes; eight services remain healthy. No configuration edit or provider/
retirement/short-text activation is performed in that review database. Full frozen
backend/browser regression and own exact-source hosted run remain required before merge.

Final0044 source repeats both populated drills successfully: logical71 tables/691 rows
476ms, and actual database/MinIO71/691/one42,084-byte object173ms. Both report empty
cleanup, immutable guards and retirement denial. Actual restricted-login test passes
10.39s. The frozen full unit/contract suite passes1,277 cases6.03s with35 tooling checks;
512-case integration and full117-execution browser regression are running, not accepted.
