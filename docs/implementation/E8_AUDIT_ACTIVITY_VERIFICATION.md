# ADMIN audit activity verification — candidate

19 October 2026. FR-OPS-003, NFR-SEC-002, NFR-ACC-001, NFR-PERF-001, NFR-MNT-001.
See [readiness](E8_AUDIT_ACTIVITY_READINESS.md) and
[ADR-058](../decisions/ADR/058-bounded-admin-audit-activity.md).

## Local evidence

- `make test-audit-activity`: five integration cases pass. Real API checks cover
  anonymous/all non-ADMIN roles, immediate role revocation, twenty-read limit, no
  self-audit writes, inclusive window boundaries/future exclusion, all seven categories,
  escaped prefix matching, unknown text minimization, exact newest-10,000 cap/ties,
  fresh sign-in with an empty window, clean/0036 upgrade and repeated upgrade. Original
  audit UPDATE/DELETE guards remain effective. No individual audit fields are returned.
- `make format lint openapi-check build`: formatting, Python/TypeScript types, lint,
  generated contract consistency and production build pass. Initial type checking
  caught an incorrect client-factory call; corrected before browser acceptance.
- `make test-web-audit test-web-content`: three real authenticated journeys pass in
  Chromium, Firefox and WebKit, plus three UI harness/navigation cases. Verify keyboard,
  axe, role denial, real aggregates, cap/empty/denied/offline/retry, stale-result removal,
  seven-link navigation and 320-pixel/200% text reflow. Browser testing found a missing
  GET proxy allowlist entry; it was added without enabling other methods. Retained
  trace: `.local/audit-activity-missing-proxy-route.zip`.
- Desktop and large-text screenshots were visually inspected. Reusing the existing
  operations-page fixed narrow padding improves readable line lengths; initial cramped
  text is retained at `.local/audit-activity-initial-large-text.png`. Final visuals:
  `.local/ui-review/audit-desktop.png` and `audit-mobile-large-text.png`. Static overflow
  checks alone were not treated as visual acceptance. Physical/branded devices remain
  separate release gates.
- Rebuilt/migrated local Docker serves the new audit layout and schema 0037/index;
  receipt-hold creation remains false. Actual Docker proxy returns unauthenticated
  GET 401 and unsupported POST 404 with no-store. Eight running healthy services and
  owned async export/frozen retry, request aggregation and fixed fake model probe pass. API/web image security scans
  report no HIGH/CRITICAL findings.

`make test test-runtime-role recovery-drill security security-source` passes:
918 unit/contract cases, 35 tooling cases, all 378 integration cases, a separate actual
restricted-login check, dependency/source scans with no findings, and isolated populated
logical recovery of 65 tables/648 rows (287 ms), including the restored audit index.
No cleanup failure is reported. Complete exact-source hosted acceptance remains required
before main promotion. This index/summary changes no retained record or retention policy and
provides no learner-level support permission, full audit coverage or production approval.

Logs: `.local/audit-activity-*.log`. The stack remains available at localhost:3000;
no existing volume was removed and no external model/messaging/Gemini call was made.

## Files in this candidate

- API/data: `services/audit_activity.py`, `apps/api/operations.py`,
  `apps/api/migrations/versions/0037_audit_activity_index.py`.
- Web: `apps/web/app/admin/audit/page.tsx`, `apps/web/app/admin/navigation.tsx`,
  `apps/web/app/api/v1/[...path]/route.ts`.
- Generated contracts: `packages/api-client/openapi.json`, `packages/api-client/src/schema.d.ts`.
- Tests/tooling: `Makefile`, `scripts/e2e_api.py`, `scripts/recovery_drill.py`,
  `tests/integration/test_audit_activity.py`, `tests/e2e/audit.spec.ts`,
  `tests/e2e/audit.ui.spec.ts`, `tests/e2e/content-editor.ui.spec.ts`.
- Documentation: `AGENTS.md`, `CHANGELOG.md`, ADR-051 follow-up acceptance,
  ADR-055 acceptance, ADR-058 and ADR index, current sprint, requirements traceability,
  receipt/audit verification, audit readiness, local runbook, data model/API and
  canonical decision register. Older accepted-stage summaries are synchronized;
  no architectural decision body or release gate is weakened.
