# E8 deletion-impact preview verification

Date: 29 September 2026. Synthetic local development only.

Owned exports `d20c344` are pushed to main; completed branch removed and
[hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36529147185). Deletion-impact
preview is local on `codex/deletion-readiness`, uncommitted for review.

## Scope and decisions

FR-ID-006/BR-010 deletion-review prerequisite, supporting FR-OPS-003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. [ADR-029](../decisions/ADR/029-deletion-impact-preview.md)
records a non-destructive read-only review journey. It adds no migration, provider,
retention period or exception to immutable records. Execution remains disabled.

## Verification

| Command | Result |
| --- | --- |
| `make setup migrate seed` | Pinned/frozen dependencies and additive migration head 0015 verified; synthetic seed and private local storage setup passed. No new migration. |
| `make openapi format lint typecheck` | Generated contracts, formatting, Python/TypeScript lint/types passed. |
| `make test openapi-check` | 214 unit/contract/property and 107 integration tests passed (321 total); generated API/client contracts match. |
| `make build e2e` | Production web build and all 17 browser tests passed (9 + 8 shards). |
| `make security security-source` | Bandit, dependency audits, secret and source scans passed. |
| `make containers security-containers container-smoke` | Final images including the export correction built; HIGH/CRITICAL scans and API/database/Redis/worker/web smoke passed. |
| `make check-docs` | Links in 65 Markdown files, coverage of 61 requirements and whitespace passed. |

Tests cover fresh ADMIN authorization, independent claim ownership, wrong kind, missing
request, stale/revoked credentials, count-only output, no decryption, no modification of
domain records, continued learning access, bounded counts and unknown/bound guardian
challenge attribution. Staff provenance remains visible after role revocation. Failed
inventory/audit operations return no partial report; preview access is audited and
rate-limited. Fresh isolated schemas migrate through head without resets.

Browser coverage includes unavailable pre-claim preview, lost-response recovery,
explicit execution blockers, keyboard disclosure/table access, axe checks, clearing a
stale preview on reload and absence of learner preview controls.

A related export correction decrypts the owner's stored display name; profiled exports
previously returned ciphertext. A regression now requires the readable synthetic name.
Already-generated immutable copies remain frozen; a new explicit export captures the
correction. Deletion previews still never decrypt any personal payload.

Failures corrected: duplicate test basenames caused pytest collection failure; the
contract test now has a distinct name. The no-decryption test sentinel initially also
blocked the separate learning-resume assertion; it is now scoped to the preview before
restoring normal learning behaviour. Formatting issues were corrected with repository
commands. Existing deprecation/network-guard warnings remain, with external sockets
blocked in tests. No model, Gemini, external delivery or production cloud calls.

## Remaining gates

This does not implement erasure/anonymization or legal holds. Counts are advisory and
bounded, related staff categories overlap, and unmodelled payload references, logs,
backups and shared rate buckets need separate review. WhatsApp/channel links do not
exist yet. A zero count never establishes that erasure is safe or complete. Record-specific
holds, execution state, narrow reviewed transforms/migration and recovery plan come next.
Production privacy/legal and re-identification review remain independent gates.

## Files changed

- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [README.md](../../README.md)
- [apps/api/data_requests.py](../../apps/api/data_requests.py)
- [apps/web/app/api/v1/[...path]/route.ts](../../apps/web/app/api/v1/[...path]/route.ts)
- [apps/web/app/privacy/deletion-impact.tsx](../../apps/web/app/privacy/deletion-impact.tsx)
- [apps/web/app/privacy/requests.tsx](../../apps/web/app/privacy/requests.tsx)
- [docs/decisions/ADR/029-deletion-impact-preview.md](../../docs/decisions/ADR/029-deletion-impact-preview.md)
- [docs/decisions/ADR/README.md](../../docs/decisions/ADR/README.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md](../../docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md)
- [docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md](../../docs/implementation/E8_DELETION_PREVIEW_VERIFICATION.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/03_Domain_and_Data_Model.md](../../docs/specifications/03_Domain_and_Data_Model.md)
- [docs/specifications/04_API_and_Integration_Contract.md](../../docs/specifications/04_API_and_Integration_Contract.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [services/data_export_projection.py](../../services/data_export_projection.py)
- [services/data_request_contracts.py](../../services/data_request_contracts.py)
- [services/deletion_preview.py](../../services/deletion_preview.py)
- [tests/contract/test_deletion_preview_contract.py](../../tests/contract/test_deletion_preview_contract.py)
- [tests/e2e/data-requests.spec.ts](../../tests/e2e/data-requests.spec.ts)
- [tests/integration/test_data_exports.py](../../tests/integration/test_data_exports.py)
- [tests/integration/test_deletion_preview.py](../../tests/integration/test_deletion_preview.py)
