# E4 deterministic multiple-choice verification

Date: 28 September 2026. Synthetic local development only.

Flags/triage was committed and pushed to main as `bd9dae3`; its completed branch was
removed. [Hosted main CI](https://github.com/Jotham566/kasoma/actions/runs/36411128242).
Hosted CI for flags/triage passed. Multiple-choice support is now committed and pushed
to main as `02f96bc`; its completed branch was removed.
[Hosted multiple-choice CI](https://github.com/Jotham566/kasoma/actions/runs/36487637477)
is tracked separately from the completed local verification below.

## Requirements and decision

FR-GRD-001: independently reviewed nonempty keys, exact-set deterministic scoring,
canonical retry/storage and checkbox delivery. Supporting FR-GRD-005/007,
FR-CNT-001/003/004/005, FR-REV-003/005, FR-DIAG-004, FR-MST-001/003,
NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.
[ADR-026](../decisions/ADR/026-multiple-choice.md) records ALL_OR_NOTHING scoring,
1–8 submitted unique IDs, 2–8 authored options and migration compatibility.
No accepted architecture or provider changes.

## Verification status

| Command | Result |
| --- | --- |
| `make setup` | Pinned runtimes/frozen dependencies verified; local configuration preserved. |
| `make migrate seed seed-multiple-choice` | Additive 0013 migration and synthetic catalog/storage/choice fixtures passed; choice fixture rerun is idempotent. |
| `make format lint` | Formatting, Python/TypeScript lint/types and documentation checks passed. |
| `make openapi openapi-check` | Generated OpenAPI/TypeScript match the API. |
| `make test` | 206 unit/contract/property and 88 integration tests passed (294 total). |
| `make build e2e` | Production web build and 16 browser tests passed (8 per isolated shard). |
| `make security security-source` | Bandit, dependency audits, secret-boundary and source scanning passed. |
| `make containers security-containers container-smoke` | Images, HIGH/CRITICAL security checks and API/database/Redis/worker/web smoke passed. |
| `make replay-mastery replay-reassessments` | Commands passed against the empty local history (zero records); nonempty replay is verified by integration tests. |

Coverage includes every nonempty subset and permutation of a four-option set,
strict DTO bounds, independent publication checks, invalid/unknown/duplicate responses,
no answer-key leakage, canonical retries, concurrent delivery, transaction rollback,
hint metadata, immutable history, mastery replay, completed correct/incorrect sealed
diagnostics, unseen reassessment and database assignment/shape guards. Integration
fixtures migrate fresh isolated schemas to head twice; no destructive reset is used.

Browser coverage adds staff authoring/review, checkbox input, wrong-subset scoring,
exact-set scoring, lost acknowledgement with preserved selections, reload recovery,
worked solution, keyboard and axe checks. Existing journeys remain in the suite.
Tests use fake providers and synthetic data; no model/Gemini or external delivery calls.

Failures corrected during development: duplicate Python test basenames prevented initial
collection; the contract file now has a distinct name. The lost-ack browser assertion
initially expected the validation-error message; it now checks the connection message.
The expanded browser suite exceeded the shared peer OTP limit. `make e2e` now runs two
fresh isolated shards while retaining that security limit. No acceptance gate is weakened. No unresolved local check failures remain.
Existing non-failing dependency/test-tool warnings remain.

Ignored logs: `.local/multiple-tests.log`, `.local/multiple-web-final.log`,
`.local/multiple-web-checks.log`, `.local/multiple-security.log`,
`.local/multiple-containers.log` and `.local/multiple-final-checks.log`.

## Files changed

- Grading/content: services/grading.py, services/content.py, services/content_contracts.py.
- Assessment: services/assessment.py, services/assessment_contracts.py, migration 0013.
- Web: staff editor/reviewer, revision and diagnostic players; generated OpenAPI/TypeScript.
- Fixtures/checks: Makefile, scripts/assessment_fixtures.py, scripts/e2e_api.py;
  multiple-choice contract/integration/browser tests; shared assessment/diagnostic tests.
- Documentation: AGENTS, README, changelog, ADR-026/indexes, API/data/content specifications,
  local runbook, sprint, traceability and verification reports.

## Remaining gates and next task

Synthetic exact-set tests do not approve academic validity, curriculum alignment or
benchmark performance. Expert short-text grading, production privacy/MFA, retention,
WhatsApp, outbox dispatch and Week 8 provider/deployment decisions remain pending.
Next: FR-ID-006 export/deletion request intake and auditable processing, with retention
and immutable evidence rules resolved before destructive processing is implemented.
