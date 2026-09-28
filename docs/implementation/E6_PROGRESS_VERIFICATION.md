# E6 progress and session history verification

Date: 28 September 2026. Synthetic local development only.

Unseen reassessment was committed and pushed to main as `73c1fba`; its completed
branch was removed. Progress/history is on `codex/e6-progress-history`, uncommitted
for review. [Hosted main CI passed](https://github.com/Jotham566/kasoma/actions/runs/36404562915). These local checks are not production acceptance.

## Requirements and decision

FR-MST-004/005: subject/topic/competency estimates with confidence, coverage and sparse
evidence language. Supporting FR-MST-002/003, FR-ID-003, FR-REV-005, NFR-SEC-002,
NFR-ACC-001, NFR-LOC-001 and NFR-MNT-001.
[ADR-024](../decisions/ADR/024-progress-history.md) documents equal-weight skill rollups,
prior coverage, confidence-gated latest-answer change, sealed diagnostic evidence and
actor/filter-bound history cursors. Existing grading/mastery algorithms are unchanged.
No migration, provider change or production dependency is introduced.

## Verification

| Command | Result |
| --- | --- |
| `make setup` | Pinned runtimes and locked dependencies verified; existing environment preserved. |
| `make migrate seed` | Existing schema upgraded through head 0010; idempotent synthetic catalog and local storage setup succeeded. |
| `make format lint` | Python/TypeScript lint/types, formatting, documentation links and whitespace passed. |
| `make test` | 187 unit/contract/property and 74 integration tests passed (261 total). |
| `make openapi openapi-check` | Generated OpenAPI and TypeScript client match. |
| `make build e2e` | Final production web build and all 14 browser tests passed. |
| `make security security-source` | Bandit, secret-boundary/Gitleaks and Python/JavaScript dependency audits passed. |
| `make containers security-containers container-smoke` | Final images built; HIGH/CRITICAL vulnerability gates and API/database/Redis/worker/web smoke passed. |

Coverage includes hand-calculated equal-weight means with unassessed priors, unique
attempt counts across multiple mappings, deterministic replay, confidence-gated change,
recency and corrupt/future evidence rejection. Integration exercises current consent,
authentication, subject/learner isolation, tied-timestamp cursor boundaries, cursor
signature/filter tampering, expiry without mutation, unchanged evidence/history, and
completed versus active/abandoned/expired diagnostic visibility. Isolated integration
schemas migrate from clean through head and repeat upgrade application; no destructive
reset or downgrade is used.

Browser journeys exercise empty/sparse progress, safe connection-failure retry, keyboard
navigation, 11-session cursor pagination, sealed diagnostic summaries, resume at the
next unanswered item, completed-practice history and axe checks. Synthetic providers
are deterministic; no inference, Gemini, external messaging or real learner data is used.

Corrections during verification: SQLAlchemy collection typing, an ambiguous history join,
React mount-effect lint annotation for initial authorization, long test SQL formatting,
an offline-message assertion and selected-subject precedence on reload. No acceptance
controls were weakened. No unresolved check failures remain. Existing non-failing Starlette/test-network-guard and ignored
optional dependency build-script warnings remain.

Ignored execution logs: `.local/progress-final-python.log`, `.local/progress-final-ui.log`,
`.local/progress-security-containers.log`, `.local/progress-final-containers.log`,
`.local/progress-contracts.log` and `.local/progress-docs.log`.

## Files

- Services: `services/progress.py`, `progress_contracts.py`, `progress_engine.py`.
- API/contracts: `apps/api/assessment.py`, generated OpenAPI and TypeScript client.
- Web: progress/history pages, shared learning dashboard, API proxy, home/revision/
  diagnostic navigation and subject-preserving recommendation/diagnostic links.
- Tests: progress engine and integration suites, progress browser journey and extended
  recommended-practice browser history checks.
- Documentation: AGENTS, README, changelog, ADR-024/indexes, API contract, local runbook,
  sprint, traceability, prior verification and this report.

## Remaining gates and next task

Synthetic aggregation weights and catalog coverage do not certify academic mastery.
The expert benchmark, short-text grading, calibrated equivalent-pair transfer, legal/
privacy approvals and Week 8 provider decision remain pending. Large-history performance
and the full browser/device accessibility matrix require release-stage validation.
Next slice: FR-GRD-009/FR-CNT-006 learner question/grade flags with owned immutable
item/attempt linkage, safe optional comments and auditable staff triage. No automated
regrading or retrospective evidence mutation is implied.
