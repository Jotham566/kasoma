# E8 learner flags and independent triage verification

Date: 28 September 2026. Synthetic local development only.

Flags/triage is committed and pushed to main as `bd9dae3`; its completed branch
was removed. [Hosted main CI](https://github.com/Jotham566/kasoma/actions/runs/36411128242)
is tracked separately from the completed local evidence below.

## Requirements and decisions

FR-GRD-009/FR-CNT-006: owned immutable report linkage, bounded encrypted comments,
safe retry/reload, reviewer/admin queue, independent ownership, priority, resolution,
revision conflicts and auditable history. Supporting FR-CNT-003/004, FR-ID-003,
FR-OPS-001/003, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.
[ADR-025](../decisions/ADR/025-learner-flags.md) records categories/state transitions,
privacy minimization, disputed second review and the approved retention deadline.
Migrations 0011–0012 are additive. No published content, grade or mastery evidence is rewritten.

## Verification

| Command | Result |
| --- | --- |
| `make setup` | Pinned runtimes and frozen dependencies verified; existing environment preserved. |
| `make migrate seed` | Additive migrations 0011–0012 and idempotent synthetic catalog/local storage initialization passed. |
| `make format lint` | Python/TypeScript lint/types, formatting and documentation links/whitespace passed. |
| `make openapi openapi-check` | Generated OpenAPI and TypeScript contracts match. |
| `make test` | 198 unit/contract/property and 82 integration tests passed (280 total), including the final retention guard. |
| `make build e2e` | Production web build and all 15 browser tests passed. |
| `make security security-source` | Bandit, secret-boundary/Gitleaks and dependency audits passed. |
| `make containers security-containers container-smoke` | Final images built; HIGH/CRITICAL vulnerability gates and API/database/Redis/worker/web smoke passed. |

Tests cover strict inputs, text bounds, calendar retention, server-derived attempt/version
binding, current consent, IDOR and role denial, duplicate/idempotency conflicts, concurrent
report delivery and rollback, encrypted storage, audited reads, revision conflicts,
resolution/reopening, metadata immutability, pagination/filtering, new-report limits,
recent staff verification, diagnostic score sealing and two-reviewer successor approval.
The late-report case covers a draft created before the dispute. Integration schemas are
freshly migrated through head and upgraded again; no destructive database reset is used.

Browser verification covers report and triage retry after lost acknowledgement, receipt
recovery after reload, independent staff access, plain-text rendering of script-like
comments, queue/detail navigation, exact-version deep link, keyboard and axe checks.
Existing hint keyboard checks now wait for the asynchronous control to become enabled.
No model, messaging, cloud or Gemini calls and no real learner data were used.

Failures corrected: diagnostic answer-reference naming initially collided with the
revision player's type discriminator; the API now uses `answered_attempts`. Fresh-staff
authentication correctly returns 401, and its test expectation was corrected. A late
flag exposed premature SQLAlchemy autoflush of review escalation before revision
increment; reads now precede that mutation. The browser decision selector now has an
explicit accessible label, and a test cleanup no longer masks the original failure.
A local variable naming collision was caught and fixed by type checking. A final
database review found SQL CHECK null semantics could omit a terminal retention deadline;
forward migration 0012 and a constraint-specific rejection test close that gap without
rewriting locally applied migration 0011. No acceptance
or security gate was weakened. No unresolved check failures remain. Existing non-failing dependency/test-tool warnings remain.

Ignored logs: `.local/flags-final-verification.log`, `.local/flags-ui-verified.log`,
`.local/flags-foundation.log`, `.local/flags-release-checks.log`,
`.local/flags-first-check.log` and `.local/flags-docs.log`.

## Files

- Domain/API: `services/domain/flags.py`, `services/flag_contracts.py`, `services/flags.py`,
  `apps/api/flags.py`, router registration, migration env and migrations 0011–0012.
- Integration: content disputed-review policy, diagnostic safe attempt references,
  analytics content events, generated OpenAPI and TypeScript contracts.
- Web: shared flag form, revision/diagnostic players, staff flag queue, content-version
  deep link and navigation, authenticated API proxy.
- Tests: flag contract/integration/browser suites; isolated E2E reviewer fixture.
- Docs: instructions, README, changelog, ADR-025/indexes, API/data/content specs, runbook,
  sprint, traceability, previous progress verification and this report.

## Remaining gates and next task

Only synthetic development use is verified. Production MFA, approved safeguarding and
support procedures, legal/consent wording and retention/anonymization jobs remain gated.
The 24-month flag retention deadline is persisted; a scheduled erasure job is not claimed.
Triage has no automatic regrading, content withdrawal, notifications or learner contact.
Question reporting here requires a submitted attempt, matching the specified endpoint.
Academic calibration, expert short-text benchmark and Week 8 provider decisions remain.
Next: FR-GRD-001 deterministic multiple-choice content, grading and learner delivery.
