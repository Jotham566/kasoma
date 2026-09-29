# E8 owned data exports verification

Date: 29 September 2026. Synthetic local development only.

Intake `68146b9` is pushed to main; completed branch removed and
[hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/36523648234). Exports are local on
`codex/data-exports`, uncommitted for review.

Requirements: FR-ID-006 (export/completion portion), FR-OPS-001/003,
NFR-SEC-001/002, NFR-OBS-001, NFR-ACC-001, NFR-MNT-001.
Decision: [ADR-028](../decisions/ADR/028-owned-data-exports.md).

## Verification

| Command | Result |
| --- | --- |
| `make setup` | Pinned runtimes and frozen dependencies verified; existing environment preserved. |
| `make migrate seed` | Additive migration 0015 and synthetic catalog/private storage setup passed. |
| `make openapi openapi-check` | Generated API/TypeScript contracts match. |
| `make format lint typecheck` | Formatting, Python/TypeScript lint/types and documentation links passed. |
| `make test` | 213 unit/contract/property and 102 integration tests passed (315 total). |
| `make build e2e` | Production web build and all 17 browser tests passed (9 + 8 isolated shards). |
| `make expire-exports` | Passed, zero expired copies in the default synthetic database; nonempty cleanup and repeat sweeps pass in isolated integration tests. |
| `make security security-source` | Bandit, dependency audits, secret/source scans passed. |
| `make containers security-containers container-smoke` | Final images built, HIGH/CRITICAL vulnerability scans and API/database/Redis/worker/web smoke passed. |
| `make check-docs` | Links in 63 Markdown files, coverage of 61 requirements and whitespace passed. |

Coverage includes own-account/fresh-OTP access without profile or after withdrawal;
other-owner/admin denial; retry/conflict, new request after completion, atomic rollback
and concurrent retrieval; bounds without truncation; 24-hour expiry and idempotent sweep;
revoked sessions; SQL guards against early deletion, artifact mutation, orphan artifacts
and unsupported completion; six-year calendar arithmetic and worker registration.
Guardian evidence is never decrypted. Released grades and mastery remain available;
unfinished/abandoned diagnostics and mixed mastery snapshots remain sealed. Frozen
copies do not gain newly released results; a new explicit request is required.
Fresh isolated schemas migrate through head twice without destructive resets.

Browser coverage extends intake/review with owner download, a deliberately lost first
response, retry to a JSON file, safe attachment headers, completion visibility, absent
admin download controls, keyboard access and axe checks. No external inference/delivery.

Failures corrected during implementation: Python query-union typing, fixture-import
lint and formatting failures were corrected before the application checks. Terminal
export errors now clear the pending download so an expired copy does not block a new
request. Existing socket-block/deprecation warnings remain; they do not indicate a
provider call or failed test. No runtime pin or accepted provider architecture changed.

## Remaining gates

Deletion/anonymization, large-history export, exceptional disclosure review and
six-year accountability expiry/legal holds remain pending. Production legal/guardian,
academic calibration, real delivery and Week 8 provider decisions remain separate gates.
The JSON manifest deliberately excludes credentials, guardian/staff details, content
keys/solutions, future assignments and sealed diagnostic-derived results. No external
model, messaging or cloud calls; synthetic records and deterministic provider fakes only.

## Files changed

- [ADR index](../decisions/ADR/README.md)

- [AGENTS.md](../../AGENTS.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [Makefile](../../Makefile)
- [README.md](../../README.md)
- [apps/api/data_requests.py](../../apps/api/data_requests.py)
- [apps/api/migrations/versions/0015_data_exports.py](../../apps/api/migrations/versions/0015_data_exports.py)
- [apps/web/app/api/v1/[...path]/route.ts](../../apps/web/app/api/v1/[...path]/route.ts)
- [apps/web/app/privacy/requests.tsx](../../apps/web/app/privacy/requests.tsx)
- [apps/worker/main.py](../../apps/worker/main.py)
- [docker-compose.yml](../../docker-compose.yml)
- [docs/decisions/ADR/028-owned-data-exports.md](../../docs/decisions/ADR/028-owned-data-exports.md)
- [docs/implementation/CURRENT_SPRINT.md](../../docs/implementation/CURRENT_SPRINT.md)
- [docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md](../../docs/implementation/E8_DATA_EXPORTS_VERIFICATION.md)
- [docs/implementation/E8_DATA_REQUESTS_VERIFICATION.md](../../docs/implementation/E8_DATA_REQUESTS_VERIFICATION.md)
- [docs/implementation/REQUIREMENTS_TRACEABILITY.md](../../docs/implementation/REQUIREMENTS_TRACEABILITY.md)
- [docs/runbooks/LOCAL_DEVELOPMENT.md](../../docs/runbooks/LOCAL_DEVELOPMENT.md)
- [docs/specifications/03_Domain_and_Data_Model.md](../../docs/specifications/03_Domain_and_Data_Model.md)
- [docs/specifications/04_API_and_Integration_Contract.md](../../docs/specifications/04_API_and_Integration_Contract.md)
- [docs/specifications/13_ADR_and_Decision_Log.md](../../docs/specifications/13_ADR_and_Decision_Log.md)
- [packages/analytics-schema/identity-event.schema.json](../../packages/analytics-schema/identity-event.schema.json)
- [packages/api-client/openapi.json](../../packages/api-client/openapi.json)
- [packages/api-client/src/schema.d.ts](../../packages/api-client/src/schema.d.ts)
- [scripts/dev.py](../../scripts/dev.py)
- [scripts/expire_exports.py](../../scripts/expire_exports.py)
- [services/data_export_projection.py](../../services/data_export_projection.py)
- [services/data_exports.py](../../services/data_exports.py)
- [services/data_request_contracts.py](../../services/data_request_contracts.py)
- [services/data_requests.py](../../services/data_requests.py)
- [services/domain/data_requests.py](../../services/domain/data_requests.py)
- [tests/contract/test_data_request_contract.py](../../tests/contract/test_data_request_contract.py)
- [tests/contract/test_export_retention.py](../../tests/contract/test_export_retention.py)
- [tests/e2e/data-requests.spec.ts](../../tests/e2e/data-requests.spec.ts)
- [tests/integration/test_data_exports.py](../../tests/integration/test_data_exports.py)
