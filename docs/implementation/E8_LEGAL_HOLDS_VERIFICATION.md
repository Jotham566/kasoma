# E8 specific-record legal holds verification

Date: 30 September 2026. Synthetic local development only.

Deletion-impact preview `6f7f210` is committed and pushed to main; completed branch
`codex/deletion-readiness` was removed. [Hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36726790587). Legal holds were committed on 3 October as `ec53ac4`. Publication is tracked in the
[current sprint](CURRENT_SPRINT.md); the evidence below was executed on 30 September.

## Scope and decisions

FR-ID-006/BR-010 preservation prerequisite, supporting FR-OPS-003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. [ADR-030](../decisions/ADR/030-record-legal-holds.md)
records finite holds on individual owned consent, attempt, content-flag and data-request
records. Only the independent recent-OTP ADMIN claimant can list/create/release.
Opaque references and enum reasons avoid personal narratives. Scope and expiry are
immutable; release is one-time and audited. Multiple decisions remain independent.
Evidence follows the parent request's six-year-after-completion obligation.

The additive 0016 migration includes SQL ownership/role/scope/time guards, receipt
immutability, key-share target locking, active-hold predicate and BEFORE DELETE guards.
Existing immutability remains intact. No erasure state, transform or production provider
is introduced. Preview counts are bounded, coverage incomplete and execution disabled.
Owner exports exclude internal hold metadata and hold outbox events.

## Verification

| Command | Result |
| --- | --- |
| `make setup services migrate seed` | Pinned/frozen setup preserved .env; local services, additive head 0016 and synthetic/private storage seeds passed. |
| `make openapi format lint typecheck openapi-check` | Generated API/client match; formatting, Python/TypeScript lint/types and docs checks passed. |
| `make test` | 223 unit/contract/property and 114 integration tests passed (337 total). |
| `PYTEST_ADDOPTS='-k "legal_hold or deletion_preview"' make test` | 10 contract and 12 integration tests passed after the staff-provenance inventory correction. |
| `make build e2e` | Final production web build and all 17 browser tests passed (9 + 8 shards). |
| `make check-docs` | Links in 67 Markdown files, coverage of 61 requirements and whitespace passed. |
| `make security security-source` | Bandit, dependency audits, secret/source scans passed. |
| `make containers security-containers container-smoke` | Final reviewed images built; HIGH/CRITICAL scans and API/database/Redis/worker/web smoke passed. |

Local logs are retained under ignored `.local/legal-holds-*.log`. The full suite precedes
the final staff-provenance inventory correction; the focused hold/preview suite verifies
that correction. The browser run includes the final confirmation reset and onboarding fix.

Test coverage includes strict scoped metadata, independent claimant/fresh/revoked
access, all four supported records, cross-owner rejection, exact-body/path retries,
timezone normalization, expiry boundaries, multiple holds, pagination, write/read limits,
SQL ownership/finite-date/immutable-evidence guards, concurrent receipt deduplication,
transaction rollback and exclusion from learner exports. Supported target DELETE guards
are exercised using active holds under the database clock. Existing preview no-decryption
and domain-nonmutation regressions still apply. Staff hold/receipt provenance remains
in the inventory after role revocation; it is separate from requester-owned counts.
Browser tests cover lost create/release
acknowledgements, pagination forwarding, explicit confirmation, preview count refresh,
reload and accessibility. Fresh isolated schemas migrate through 0016 without resets.

A pre-existing FR-ID-001 onboarding race was exposed by the full browser suite: the
initial session/catalog check could overwrite an offline-action error. Actions now stay
disabled until initialization settles. A controlled delayed catalog response verifies
that ordering, followed by offline-error recovery. This is a synchronization fix, not
an authentication or architecture change.

Initial failures corrected: SQL-line formatting, an accidental tuple insertion in the
preview inventory and the onboarding race above. Existing Starlette deprecation and
intentional network-guard warnings
remain; automated tests block external sockets.

## Remaining gates

Four record types are supported, not universal hold coverage. Embedded references,
other source tables, representative requests, logs/backups and accountability expiry
remain pending. Future erasure requires compatible transaction locking, revalidation,
reviewed transforms/constraints and a recovery plan. A zero active count is never
clearance. Production legal/privacy, guardian verification and anonymity reviews remain
separate gates. No real learner data, Gemini, model inference, external delivery or
production cloud calls are part of this slice.

## Files changed

- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [README.md](../../README.md)
- [apps/api/data_requests.py](../../apps/api/data_requests.py)
- [apps/api/migrations/versions/0016_legal_holds.py](../../apps/api/migrations/versions/0016_legal_holds.py)
- [apps/web/app/api/v1/[...path]/route.ts](../../apps/web/app/api/v1/[...path]/route.ts)
- [apps/web/app/onboarding/page.tsx](../../apps/web/app/onboarding/page.tsx)
- [apps/web/app/privacy/deletion-impact.tsx](../../apps/web/app/privacy/deletion-impact.tsx)
- [apps/web/app/privacy/legal-holds.tsx](../../apps/web/app/privacy/legal-holds.tsx)
- [apps/web/app/privacy/requests.tsx](../../apps/web/app/privacy/requests.tsx)
- [docs/decisions/ADR/030-record-legal-holds.md](../../docs/decisions/ADR/030-record-legal-holds.md)
- [docs/decisions/ADR/README.md](../../docs/decisions/ADR/README.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md](../../docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md)
- [docs/implementation/E8_LEGAL_HOLDS_VERIFICATION.md](../../docs/implementation/E8_LEGAL_HOLDS_VERIFICATION.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/03_Domain_and_Data_Model.md](../../docs/specifications/03_Domain_and_Data_Model.md)
- [docs/specifications/04_API_and_Integration_Contract.md](../../docs/specifications/04_API_and_Integration_Contract.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [packages/analytics-schema/identity-event.schema.json](../../packages/analytics-schema/identity-event.schema.json)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [services/data_export_projection.py](../../services/data_export_projection.py)
- [services/data_request_contracts.py](../../services/data_request_contracts.py)
- [services/deletion_preview.py](../../services/deletion_preview.py)
- [services/domain/data_requests.py](../../services/domain/data_requests.py)
- [services/legal_hold_contracts.py](../../services/legal_hold_contracts.py)
- [services/legal_holds.py](../../services/legal_holds.py)
- [tests/contract/test_legal_hold_contracts.py](../../tests/contract/test_legal_hold_contracts.py)
- [tests/e2e/data-requests.spec.ts](../../tests/e2e/data-requests.spec.ts)
- [tests/e2e/identity.spec.ts](../../tests/e2e/identity.spec.ts)
- [tests/integration/test_legal_holds.py](../../tests/integration/test_legal_holds.py)
