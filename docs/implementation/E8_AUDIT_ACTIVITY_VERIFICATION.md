# ADMIN audit activity verification — verified and merged

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
No cleanup failure is reported. Complete exact-source hosted acceptance subsequently passes at 5d95f9d in
39171302022; the source is on main and merged branches are removed. This index/summary changes no retained record or retention policy and
provides no learner-level support permission, full audit coverage or production approval.

Logs: `.local/audit-activity-*.log`. The stack remains available at localhost:3000;
no existing volume was removed and no external model/messaging/Gemini call was made.

The first candidate push omitted the new service module from its explicit staging
list. A clean-tree review caught the untracked file before hosted acceptance; a normal
follow-up commit includes it. No force push or hook bypass. Hosted acceptance must be
for the corrected complete source, not the incomplete first push.

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

## Full navigation regression and CI capacity follow-up

The extra full-Chromium target initially passes 29/31 cases; two existing parameterized
learner/staff navigation cases still assert that the formerly unimplemented Audit link
is absent. Replace that obsolete guard with its exact /admin/audit target, keeping
learner/staff separation and authorization checks. All 105 ordinary three-engine/short-text
journeys subsequently pass. Failure traces are retained under .local/audit-navigation-failure.
The corrected full Chromium target separately passes all 31 cases.

The older hold-clock hosted run fails on disposable-runner disk exhaustion, not a
completed acceptance gate. The bounded CI profile correction is recorded in
[ADR-059](../decisions/ADR/059-disposable-ci-runner-storage.md) and
[CI evidence](E0_CI_STORAGE_VERIFICATION.md). Existing local application gates pass;
complete corrected-source hosted verification remains required.

## Exact-source hosted acceptance

Source `5d95f9d7cc2fe37a9a2f8624ea6b6960f8e5f497` passes the complete
[39171302022 pipeline](https://github.com/Jotham566/kasoma/actions/runs/39171302022). It includes 940 unit/contract,
378 integration, 35 tooling, 105 ordinary browser executions, three UI harness and
three native WebKit transport-control cases, setup/migrations/restricted login/restore,
source/dependency/image security and owned service smoke. The full Chromium target
additionally passes 31 cases locally. This supersedes candidate/pending status above;
failed/cancelled runs retain their original status. Main contains the source and merged
branches are removed. No real-data, full audit coverage or production approval.
