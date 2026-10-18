# ADMIN audit activity readiness

19 October 2026. FR-OPS-003, NFR-SEC-002, NFR-ACC-001, NFR-PERF-001, NFR-MNT-001.

Read the source-of-truth/SRD, API admin operations contract, security retention rules,
UX navigation/accessibility and accepted audit/identity decisions. Inspect AuditLog,
immutable SQL guards, existing authorization/rate controls and staff/browser tests.
[ADR-058](../decisions/ADR/058-bounded-admin-audit-activity.md) records the additive slice.

Assumption within implementation discretion: the unspecified audit response is a bounded
fixed-category aggregate because the API explicitly limits operations responses to
aggregates without separate learner support permission. No individual audit access is
invented. Include the sample window/cap and explain incomplete counts honestly.

Implement GET /api/v1/admin/audit, strict generated contracts, a time-window index and
an ADMIN activity page in existing navigation. Reuse authorization, rate limiting and
design components. No audit row, source history, retention, hold, provider or learner
behavior is changed. Verification must cover SQL/API minimization and real browser
accessibility/recovery, clean/upgrade, restricted login, restore, security and Docker.
