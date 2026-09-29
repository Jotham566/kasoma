# E8 data-request intake verification

Date: 29 September 2026. Synthetic local development only.

Multiple-choice support is committed and pushed to main as `02f96bc`; its completed
branch was removed. [Hosted main CI](https://github.com/Jotham566/kasoma/actions/runs/36487637477).
Hosted CI for that multiple-choice commit passed. Data-request intake is now committed
and pushed as `68146b9`; its completed branch was removed.
[Hosted intake CI passed](https://github.com/Jotham566/kasoma/actions/runs/36523648234).
Subsequent export work is recorded in [export verification](E8_DATA_EXPORTS_VERIFICATION.md).

## Requirements and boundary

FR-ID-006 intake/review portion, supporting FR-OPS-001/003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. [ADR-027](../decisions/ADR/027-data-request-intake.md)
records recent-OTP verification, privacy rights independent of learning consent,
minimal data collection, atomic audit/outbox, canonical retry identity, independent
administrator claims and the six-year-after-completion retention obligation.
No architectural replacement or weakening of privacy/retention controls.

The local slice acknowledges and tracks pending export/deletion requests. It cannot
fulfill or mark them completed. FR-ID-006 remains partial until machine-readable export,
verified retrieval, deletion/anonymization, completion evidence and retention processing
are implemented. Production/legal/guardian procedures remain separately gated.

## Verification

| Command | Result |
| --- | --- |
| `make setup` | Pinned runtimes/frozen dependencies verified; existing environment preserved. |
| `make migrate seed` | Additive migration 0014, synthetic catalog and private local object-storage setup passed. |
| `make openapi openapi-check` | Generated API and TypeScript contracts match. |
| `make format lint` | Python/TypeScript formatting, lint, type checks and documentation links passed. |
| `make test` | 212 unit/contract/property and 93 integration tests passed (305 total). |
| `make build e2e` | Production web build and all 17 browser tests passed (9 + 8 isolated shards). |
| `make security security-source` | Bandit, dependency audits and secret/source scanning passed. |
| `make containers security-containers container-smoke` | Images, HIGH/CRITICAL scans and API/database/Redis/worker/web smoke passed. |

Coverage: explicit intent and unknown-field rejection; intake before profile completion
and after minor learning-consent withdrawal; ownership, role and fresh-auth boundaries;
key replay/conflict and new-key deduplication; concurrent request/claim delivery;
atomic audit/outbox/receipt rollback; queue pagination; own-request claim denial;
immutable SQL evidence; administrator claim guards; rate limits and revoked sessions.
Fresh isolated integration schemas migrate through head and upgrade again, without reset.

Browser coverage: unconsented learner intake, acknowledgement loss and retry, reload,
separate export/deletion references, forbidden learner admin access, independent admin
claim/retry, status recovery, keyboard and axe accessibility. Provider fakes and synthetic
data only; no model/Gemini, real learner data, external delivery or cloud deployment.

Failures corrected: API routes initially omitted standard error-response metadata and
explicit Idempotency-Key casing, caught by generated-client type checking. These now
match existing transport conventions. The initial loading effect was adjusted to satisfy
React linting without changing authorization or retry behavior. Pre-commit review also found the web gateway omitted data-request pagination query
parameters; both lists now forward cursor/limit, with browser regression checks.
A later global pnpm installation exposed nested task resolution outside Corepack;
setup now installs local shims and retains the pinned version without changing global tools.
No unresolved local check failures remain. Existing non-failing dependency and test-tool warnings remain.

Ignored logs: `.local/data-requests-tests.log`, `.local/data-requests-web.log`,
`.local/data-requests-web-final.log`, `.local/data-requests-security.log`,
`.local/data-requests-containers.log`, `.local/data-requests-final-checks.log`.

## Files

- Identity: services/data_requests.py, services/data_request_contracts.py,
  services/domain/data_requests.py, apps/api/data_requests.py and router registration.
- Persistence: migration 0014 and migration model registration.
- Web: privacy and administrator request screens, onboarding/home links, API proxy allowlist.
- Contracts: generated OpenAPI/TypeScript and identity analytics event allowlist.
- Tests: contract, integration and browser request suites; synthetic E2E administrator fixture.
- Docs: AGENTS, README, changelog, ADR-027/indexes, API/data/runbook, sprint,
  traceability and prior/current verification reports.

## Remaining work

Build the retention-aware fulfillment processor before real learner data. Pending requests
have no fabricated completion timestamp or expiry deadline. No manual completed toggle,
external notification, data erasure, learning-record rewrite or impersonation is exposed.
Next: owned machine-readable export, verified retrieval and durable completion evidence;
then narrowly scoped deletion/anonymization and retention jobs with legal-hold controls.
