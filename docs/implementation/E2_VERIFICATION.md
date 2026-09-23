# E2 first content review slice: evidence

Date: 23 September 2026. Branch: `codex/e2-content-review` (uncommitted).
E1 was committed as `9dfe726`, pushed to main at the owner's request, and
[passed hosted CI](https://github.com/Jotham566/kasoma/actions/runs/35896298632).

## Requirements and decisions

- FR-CNT-001: single-choice draft creation/editing; import and other formats pending.
- FR-CNT-002: independent review, including mixed author/reviewer roles.
- FR-CNT-003: returned corrections, approval, two-reviewer escalation and retirement.
- FR-CNT-004: immutable published payloads/mappings and explicit successor drafts;
  actual attempt/rubric pinning is deferred to assessment/grading.
- FR-CNT-005: safe field-specific validation at submission and approval.
- FR-OPS-003: atomic content and explicit local-role audit, append-only database guards.
- Supporting NFR-SEC-002, NFR-MNT-001 and NFR-ACC-001.

[ADR-015](../decisions/ADR/015-content-review.md) records implementation discretion,
additive API/schema details and exclusions. No prior ADR, safety gate or academic
requirement was weakened. No real academic content or curriculum mappings are claimed.

## Verification

| Commands | Result |
|---|---|
| `make setup services migrate seed` | Additive 0003 passed; synthetic catalog remains repeatable |
| `make format lint` | Ruff, mypy, ESLint, Prettier, TypeScript and documentation checks passed |
| `make test` | 59 passed: 36 unit/property/contract and 23 integration |
| `make openapi openapi-check` | Generated OpenAPI/client agree, including error envelopes |
| `make build e2e` | Production build and six browser tests passed |
| `make security security-source` | SAST, dependency audits, boundary checks and Gitleaks passed |
| `make containers security-containers container-smoke` | All images built; strict HIGH/CRITICAL scans and runtime smoke passed |

Tests cover: invalid publication fields/rights, stale curriculum references at
approval, role/ownership denial, role revocation, unsupported field injection,
self-review, duplicate review, escalation, optimistic concurrent edits, idempotent
creation, explicit new versions, retired/draft/cross-subject/synthetic selection,
DB-level history/mapping mutation, review comments, safe event shape and pagination.
Fresh independent schemas test the full migration chain and repeat upgrade; existing
identity and foundation tests also pass. No user database is reset or truncated.
Browser evidence covers the author/reviewer return-correct-approve-retire-new-version
journey, anonymous denial, keyboard approval and axe, alongside identity journeys.

## Failures corrected

- Initial PL/pgSQL CASE comparison required parentheses. Migration failed transactionally;
  corrected migration passed before new code used its tables.
- A Literal-list default needed a type-compatible Pydantic declaration.
- Initial browser test queried checkboxes before the reloaded review form appeared.
  The server correctly rejected its incomplete checklist. Test now waits for all 15.
- Error rendering consumes the typed error envelope returned by the generated client,
  avoiding a second read of the already-consumed response stream.

## Limits and next slice

All content is synthetic. Local APPROVED status is workflow evidence, excluded from
production selection and the 250-item academic release minimum. Staff provisioning
is explicit local CLI over verified .invalid identities; production MFA, role
administration and restricted database roles remain launch work. Audit retention and
outbox dispatch remain E8 operations work. No bulk import, media pipeline, additional
response formats, real NCDC mapping, full concept graph or learner flags are claimed.

Next: E3 single-choice assessment from consent authorization and approved version
selection through immutable answer, deterministic grade and idempotent result event.
Preserve the item-version pointer for later audit and mastery. Numeric grading follows.
The Week 5/6 short-text benchmark sequencing question remains outside this slice.

## File inventory

- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [Makefile](../../Makefile)
- [README.md](../../README.md)
- [apps/api/content.py](../../apps/api/content.py)
- [apps/api/main.py](../../apps/api/main.py)
- [apps/api/migrations/env.py](../../apps/api/migrations/env.py)
- [apps/api/migrations/versions/0003_content.py](../../apps/api/migrations/versions/0003_content.py)
- [apps/web/app/admin/content/editor.tsx](../../apps/web/app/admin/content/editor.tsx)
- [apps/web/app/admin/content/page.tsx](../../apps/web/app/admin/content/page.tsx)
- [apps/web/app/api/v1/[...path]/route.ts](../../apps/web/app/api/v1/[...path]/route.ts)
- [docs/decisions/ADR/015-content-review.md](../../docs/decisions/ADR/015-content-review.md)
- [docs/decisions/ADR/README.md](../../docs/decisions/ADR/README.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E1_VERIFICATION.md](../../docs/implementation/E1_VERIFICATION.md)
- [docs/implementation/E2_VERIFICATION.md](../../docs/implementation/E2_VERIFICATION.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [packages/analytics-schema/content-event.schema.json](../../packages/analytics-schema/content-event.schema.json)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [scripts/e2e_api.py](../../scripts/e2e_api.py)
- [services/content.py](../../services/content.py)
- [services/content_contracts.py](../../services/content_contracts.py)
- [services/domain/content.py](../../services/domain/content.py)
- [services/domain/curriculum.py](../../services/domain/curriculum.py)
- [services/domain/identity.py](../../services/domain/identity.py)
- [services/seed.py](../../services/seed.py)
- [services/staff.py](../../services/staff.py)
- [tests/contract/test_content_contract.py](../../tests/contract/test_content_contract.py)
- [tests/e2e/content.spec.ts](../../tests/e2e/content.spec.ts)
- [tests/integration/conftest.py](../../tests/integration/conftest.py)
- [tests/integration/test_content.py](../../tests/integration/test_content.py)
- [tests/integration/test_identity.py](../../tests/integration/test_identity.py)
