# E5 diagnostic and initial mastery verification

Date: 28 September 2026. Synthetic local evidence only.

E4 numeric grading was committed and pushed as `7d2c8ed`. Clean hosted setup then
failed because the pinned MinIO image denied anonymous pulls. The official pinned
source-build repair was committed as `ee73741`; [main CI passed](https://github.com/Jotham566/kasoma/actions/runs/36392615242).
The completed E4 branch was deleted. The owner subsequently authorized committing
and merging this E5 slice to main and removing its completed branch. The pre-commit
repeat of `make lint test openapi-check security-source` passed (203 tests).

## Requirements and behavior

- FR-DIAG-001–005: one active diagnostic per learner/subject; durable resume;
  fifteen-item versioned plan; topic/competency coverage; response-dependent
  difficulty; atomic answer acknowledgement; completion estimates, uncertainty
  and an explained first topic practice action.
- FR-MST-001–003/005: immutable, unique attempt/skill evidence; specified weighted
  prior and confidence formula; full original inputs/configuration/hash; current
  projections and immutable history; reproducible read-only replay; sparse-evidence
  language. Deterministic revision and diagnostics share the same service.
- Supporting FR-ID-003, FR-REV-002/005/006, FR-GRD-007, FR-OPS-001,
  NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001: current consent/ownership, safe result
  projection, forbidden diagnostic solutions, typed contracts, registered events,
  keyboard and accessibility checks.

Diagnostics return SAVED acknowledgements rather than grades. The same-key replay
and shared session/grade routes cannot reveal scores or corrective feedback during
an active diagnostic. Solutions remain blocked after completion too. Completed
results are immutable snapshots. Initial recommendations seek evidence when sparse
and require enough currently eligible topic content for five-question practice.

This is not full E5 or general progress UX. Full prerequisite/importance/spacing/
repetition ranking, recommended session planning, hint independence in the learner
flow, unseen reassessment and academic calibration remain subsequent work.

## Decisions and data changes

[ADR-019](../decisions/ADR/019-minio-source-build.md) retains MinIO while repairing
unavailable images with official source, archive checksum and pinned image digests.
[ADR-020](../decisions/ADR/020-diagnostic-mastery.md) records diagnostic and mastery
choices, exclusions and rollback controls. Existing engine coefficients and
ADR-017's difficulty mapping are unchanged.

Migrations 0006 and 0007 add diagnostic session state, bounded counts, evidence,
projection/history tables, uniqueness and append-only guards. The second migration
tightens grade-to-evidence bindings and completed-result integrity without rewriting
learning data. Legacy grades reconcile lazily only after current consent; stored
grades are not edited. Forward-fix rollback retains all learning evidence.

Candidate discovery is read-only; the chosen item is locked and approval rechecked
before serving or submission. This avoids locking an entire inventory while another
learner completes grading. No production enablement, cloud integration, model or
Gemini evaluation, real identities or real learner data were introduced.

## Checks executed

| Command | Result |
| --- | --- |
| `make setup services migrate seed seed-diagnostic` | Passed; local source-built MinIO healthy, private bucket initialized, additive migrations and explicit synthetic fixtures ready. |
| `make format lint` / `make typecheck` | Python/TypeScript formatting, lint and types passed; final documentation check repeated after this report. |
| `make test` | 155 unit/contract/property and 48 integration tests passed (203 total), including legacy reconciliation after consent renewal. |
| `make openapi openapi-check build` | Generated contracts match; production web build passed. |
| `make e2e` | All 10 browser tests passed, including lost acknowledgement, diagnostic resume, keyboard use, uncertainty, first practice link and axe checks. |
| `make replay-mastery` | Passed read-only; default local database had zero learning projections. Integration tests replay nonempty current and historical projections. |
| `make security security-source` | Bandit, secret boundary, Python/JavaScript dependency audits and Gitleaks passed. |
| `make containers security-containers container-smoke` | Application images built, HIGH/CRITICAL scan gates passed, API/database/Redis/worker/web smoke passed. |

Final legacy-consent regression passed: withdrawal prevents reconciliation; renewed
consent creates one evidence/history record and leaves the original grade unchanged.

The suite covers strong/weak Mathematics and Physics trajectories, first CORE item
per topic, competency diversity, exact historical replay, duplicate start/answer,
failed-transaction rollback, expiry, withdrawal, overlapping active-plan exclusion,
invalid client fields, insufficient
inventory, retired questions and immutable records. Existing choice/numeric,
identity and content regressions remain green.

Failures corrected or resolved during this work: stopped Docker and macOS startup
authentication; unavailable public MinIO image; missing local Playwright browser
cache (restored with the documented install command); type/format checks during
implementation; withdrawal test using the wrong existing contract; one migration
setup test overlapping a development migration edit (rerun against stable files);
an assertion replaced by an explicit runtime integrity failure; missing draft
report links. No gate was suppressed. Existing Starlette/httpx deprecation and
intentional network-block-test warnings remain non-failing.

## File inventory

- Core: `services/mastery_engine.py`, `services/mastery.py`,
  `services/diagnostics.py`, `services/domain/mastery.py`,
  `services/assessment.py`, `services/assessment_contracts.py`,
  `services/domain/assessment.py`, `services/content.py`.
- API/data: `apps/api/assessment.py`, `apps/api/migrations/env.py`, migrations
  `0006_diagnostic_mastery.py` and `0007_mastery_bindings.py`.
- Web: `apps/web/app/diagnostic/page.tsx`, `apps/web/app/revise/page.tsx`,
  `apps/web/app/page.tsx`, `apps/web/app/api/v1/[...path]/route.ts`.
- Contracts: `packages/api-client/{openapi.json,src/schema.d.ts}` and
  `packages/analytics-schema/assessment-event.schema.json`.
- Tests: `tests/contract/test_mastery_engine.py`,
  `tests/integration/test_diagnostics.py`, `tests/integration/test_assessment.py`,
  `tests/e2e/diagnostic.spec.ts`, `tests/e2e/content.spec.ts`,
  `tests/e2e/numeric.spec.ts` (pagination with larger fixture inventory).
- Tooling: `Makefile`, `scripts/replay_mastery.py`,
  `scripts/assessment_fixtures.py`, `scripts/e2e_api.py`.
- Documentation: `AGENTS.md`, `README.md`, `CHANGELOG.md`, current sprint,
  traceability, this report, local runbook, ADR-020 and decision indexes.
- Separately committed CI repair: `docker-compose.yml`,
  `infra/containers/minio.Dockerfile`, ADR-019, E4 verification and runbook/index links.

## Remaining gates and next task

Teacher-approved curriculum mappings, item rights, content inventory, benchmark
quality/calibration, legal/privacy approvals, named owners and provider decisions
remain outstanding. Synthetic tests are not academic certification or pilot release
approval. Outbox dispatch, retention/anonymization and production least privilege
remain planned operations work.

Next: FR-MST-006 and FR-REV-001/006 full versioned recommendation ranking and
recommended practice, followed by hints and unseen reassessment. Preserve the
Week 5 short-text gate and the 12-week scope.
