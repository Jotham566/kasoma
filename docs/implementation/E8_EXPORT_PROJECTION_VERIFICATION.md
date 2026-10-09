# E8 bounded personal-export projection verification

Requirements: FR-ID-006, NFR-SEC-001/002, NFR-MNT-001.
Status: verified synthetic regression and promoted to main.

The synchronous ADR-028 export now reads related rows through server-side cursors in batches of
100, closing cursors on success, row-limit failure and consumer exceptions. Owner-filtered SQL
joins/subqueries replace retained session/attempt/version maps, global released-attempt sets and
expanded ID lists. Distinct assignment/version references still count toward the existing related
row budget. Stable ordering is explicit for each section, including mastery projections.

Sealed mastery exclusion checks every snapshot input attempt against owned released attempts in
SQL; snapshot validation and the original accounting of withheld rows remain. No raw ORM object is
serialized. Guardian evidence, hidden content keys/rubrics and staff internals remain excluded.

The complete output bundle is still assembled under the existing 10,000-related-row and 2 MiB
limits. This bounds ORM hydration, not total JSON memory or arbitrary per-record size. Authorization,
transaction isolation, encrypted PostgreSQL retry copies, atomic completion, recent OTP, six-year
accountability and 24-hour availability are unchanged. This is an internal query refactor under
ADR-028, requiring no new architecture decision, migration or API contract. It does not implement
large-history delivery or claim a stronger concurrent snapshot guarantee.

## Checks

`make services-db migrate test-data-exports` starts only approved PostgreSQL/Redis and runs the
focused real-database suite. It permits focused database work while the full MinIO image build is
pending; `make services seed` remains necessary for full setup/object storage. On macOS use the
installed Docker CLI PATH adjustment in the local runbook if needed.

Existing export cases cover owner/recent-auth/revocation, exact frozen retry, atomic rollback,
concurrent commands, expired copies, complete/exceeded byte and row bounds, withdrawn consent,
sealed/mixed diagnostic histories, guardian non-decryption and database completion/retention guards.
New cases exercise 350 synthetic account events across small cursor batches while measuring peak
ORM identity-map size, exact related-row budget accounting, and cursor closure after limit failure.
All tests remain synthetic with deterministic providers.

Run `make lint openapi-check test test-data-exports` plus the existing hosted browser/security/
container gates before promotion. The [large-history readiness](E8_LARGE_HISTORY_EXPORT_READINESS.md)
records the remaining asynchronous snapshot, artifact, resource and owner-delivery work.

## Acceptance results

Hosted CI [37918757085](https://github.com/Jotham566/kasoma/actions/runs/37918757085)
passed at `8c14590`: 427 unit/contract plus 184 integration tests (611 Python), five tooling tests,
63 real-API browser executions and one isolated editor test. Clean setup/migrations/seed, focused
rubric/role checks, lint/format/types/contracts/build, security/source/image scans and container smoke
passed. Recovery restored 54 tables/272 synthetic rows in 385 ms with pgvector/immutable guards and
no cleanup failures. Cold transfer was 191501/194260/193634 bytes, below 250000 for all engines.
The implementation is on main and its completed branch is removed locally and remotely.

Native Docker is available (29.8.2). The documented CLI PATH adjustment and
`make services-db migrate test-reviewed-rubrics test-data-exports` passed: PostgreSQL/Redis healthy,
eight rubric and eleven export cases verified. Full native `make lint test` passed 427 unit/contract
and 183 integration cases; its storage/Mailpit case failed because MinIO was not running. Separate
contract, recovery (54 tables/272 rows, 221 ms), restricted-role and security checks passed, with no
known vulnerabilities reported. This is not a full native acceptance pass.

The MinIO source download passed its checksum, but `go mod download` later failed with unexpected
EOFs in four module downloads. Native Playwright installed Chromium/FFmpeg; the headless-shell
transfer encountered timeout/connection resets and is retrying. No data or volumes were reset.


Follow-on [incremental encoding](E8_EXPORT_ENCODING_VERIFICATION.md) enforces the existing byte
limit during projection, before full-history collection. Successful synchronous output remains
bounded and decoded for delivery; this does not enable large-history fulfillment.
