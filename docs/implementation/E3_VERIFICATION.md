# E3 first assessment slice: verification

Date: 23 September 2026. Active branch: `codex/e3-assessment`; changes uncommitted.
E2 was committed as `b5cfd75` and pushed to main at the owner's request.
[Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/35901725404).
Completed E1/E2 local branches were deleted after merge. Origin has only main;
the only local work branch is the active E3 slice.

## Requirements and result

- FR-REV-002: topic-selected 5–10-item plans (UI uses five); mastery remains pending.
- FR-REV-003/004: approved local synthetic versions, selected subject/S4, channel
  eligibility, deterministic ordering and recent stable-item exclusion across versions.
- FR-REV-005: durable assignments, active-session lookup and cross-browser resume.
- FR-GRD-001: exact single-choice grading; multiple-choice remains pending.
- FR-GRD-005/007: typed feedback, authored remediation and post-submission solution gate.
- FR-CNT-004: immutable attempt/grade records pin the exact item/answer version and hash;
  later retirement or successor drafts do not rewrite scores or historical solutions.
- FR-OPS-001: safe transactional session/served/grade/completion/abandon events.
- FR-ID-003, NFR-SEC-002: current consent/assent, policy, enrollment and ownership
  enforced on reads, writes and replay, serialized with withdrawal/revocation.
- Supporting NFR-ACC-001 and NFR-MNT-001: keyboard/axe, generated client, migration,
  repeatable local fixture command and requirements traceability.

[ADR-016](../decisions/ADR/016-assessment-choice.md) records delegated implementation
choices and additive endpoints/schema. No accepted architecture or release gate changes.
Mastery status is explicitly NOT_IMPLEMENTED; no diagnostic or recommended-session
claims are made. This is a complete thin choice path, not full E3/E4 acceptance.

## Checks executed

| Command | Result |
|---|---|
| `make setup services migrate seed` | Passed; existing local configuration/data preserved |
| `make seed-assessment` (twice) | Passed; 30 explicit synthetic workflow fixtures, repeat run no-op |
| `make format lint typecheck` | Ruff, mypy, ESLint, Prettier and TypeScript passed |
| `make test` | 83 passed: 53 unit/contract and 30 PostgreSQL/Redis integration |
| `make openapi openapi-check` | OpenAPI and generated TypeScript agree |
| `make build e2e` | Production build and all eight browser tests passed |
| `make security security-source` | Bandit, dependency audits, local boundaries and Gitleaks passed |
| `make containers security-containers container-smoke` | Images built; HIGH/CRITICAL scans and API/worker/web runtime smoke passed |
| `make check-docs` | Links in 41 Markdown files, coverage of 61 requirements and whitespace passed |

Tests include exact correct/incorrect scores at multiple point maxima, invalid
answer/authority injection, consent withdrawal, changed policy, child assent without
guardian, cross-learner access, retired/draft/non-web exclusion, insufficient
inventory, stale/expired plans, version history, concurrent replay and rollback
when event persistence fails. Database tests reject mutation/deletion of answers,
grades and assignment identity. Migration tests upgrade fresh isolated schemas from
0001 through 0004 and repeat upgrade without destroying existing catalog data.

The browser test deliberately saves an answer at the server and drops its response,
then retries and verifies only one answer is saved. A separate authenticated browser
resumes the same session and finishes with keyboard submission. Answer keys/solutions
are absent before submission, feedback survives reload, and withdrawal blocks resume.
This is synthetic correctness evidence, not the teacher-approved academic benchmark
or the production load/accessibility certification.

## Failures corrected

- Initial formatting checks caught long migration/fixture lines and a missing test import.
- A floating-point Literal annotation was replaced by a bounded numeric field for mypy.
- The new consent test initially used `affirmed`; the real contract is `affirmative`.
  The server correctly rejected the malformed fixture; the test was corrected.
- Bandit rejected two defensive assertions. Replaced them with explicit safe errors
  that remain active in optimized Python execution.
- Existing staff browser test now follows pagination when the larger fixture catalog
  places its newly authored item beyond the first page.

No outstanding executed-check failures. Provider fakes only; no external model,
email, messaging or cloud service calls, real learner data or Gemini evaluation.

## Limits, open questions and next slice

Only synthetic single-choice WEB practice is implemented. Numeric/multiple-choice/
short-text grading, diagnostic planning, hints, mastery evidence/projections,
recommendations, reassessment, flags and WhatsApp remain scheduled work. Outbox
publication/retention/anonymization and restricted production database roles are E8
and launch gates. Production startup is still blocked.

A retired question makes an existing plan unavailable for new answers; the learner
can end it and choose another topic. Inventory shortage never silently shortens a
plan or repeats recently served items. Session and repetition windows are configured
separately from the approved retention policy. The local fixtures contain software
labels, not approved NCDC content, and never count toward academic release inventory.

OPEN-QUESTION E3-01: content has STANDARD/CHALLENGING difficulty labels while engine
specification 05 uses CORE/STRETCH. Before E5, either approve a versioned mapping
(recommended, preserves immutable content and current API values) or approve a
compatible content-contract migration. Do not silently assign weights. This affects
FR-MST-001/003/006 and adaptive selection, not the current exact choice grader.
E0-01 (Week 5/6 short-text sequencing) also remains unresolved.

Next: approved numeric answer specification and editor/player support, deterministic
units/tolerance/equivalence grading with boundary fixtures and pinned results;
then diagnostic planning and initial mastery evidence. No new provider is needed.

## Files created or changed

- [.env.example](../../.env.example)
- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [Makefile](../../Makefile)
- [README.md](../../README.md)
- [apps/api/assessment.py](../../apps/api/assessment.py)
- [apps/api/main.py](../../apps/api/main.py)
- [apps/api/migrations/env.py](../../apps/api/migrations/env.py)
- [apps/api/migrations/versions/0004_assessment.py](../../apps/api/migrations/versions/0004_assessment.py)
- [apps/web/app/api/v1/[...path]/route.ts](../../apps/web/app/api/v1/[...path]/route.ts)
- [apps/web/app/page.tsx](../../apps/web/app/page.tsx)
- [apps/web/app/revise/page.tsx](../../apps/web/app/revise/page.tsx)
- [docs/decisions/ADR/016-assessment-choice.md](../../docs/decisions/ADR/016-assessment-choice.md)
- [docs/decisions/ADR/README.md](../../docs/decisions/ADR/README.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E2_VERIFICATION.md](../../docs/implementation/E2_VERIFICATION.md)
- [docs/implementation/E3_VERIFICATION.md](../../docs/implementation/E3_VERIFICATION.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [packages/analytics-schema/assessment-event.schema.json](../../packages/analytics-schema/assessment-event.schema.json)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [scripts/assessment_fixtures.py](../../scripts/assessment_fixtures.py)
- [scripts/e2e_api.py](../../scripts/e2e_api.py)
- [services/assessment.py](../../services/assessment.py)
- [services/assessment_contracts.py](../../services/assessment_contracts.py)
- [services/config.py](../../services/config.py)
- [services/content.py](../../services/content.py)
- [services/domain/assessment.py](../../services/domain/assessment.py)
- [services/grading.py](../../services/grading.py)
- [tests/contract/test_assessment_contract.py](../../tests/contract/test_assessment_contract.py)
- [tests/e2e/assessment.spec.ts](../../tests/e2e/assessment.spec.ts)
- [tests/e2e/content.spec.ts](../../tests/e2e/content.spec.ts)
- [tests/integration/conftest.py](../../tests/integration/conftest.py)
- [tests/integration/test_assessment.py](../../tests/integration/test_assessment.py)
- [tests/integration/test_content.py](../../tests/integration/test_content.py)
