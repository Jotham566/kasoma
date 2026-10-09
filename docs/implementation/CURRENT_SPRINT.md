# Current Sprint: remaining MVP operational and grading gates

Updated 9 October 2026. Main implementation is `8c14590`. Work remains synthetic/local.

## Verified and promoted

Hosted CI [37918757085](https://github.com/Jotham566/kasoma/actions/runs/37918757085)
passed at `8c14590`: 427 unit/contract plus 184 integration tests (611 Python), five tooling tests,
63 real-API browser executions and one isolated editor test. Clean setup/migrations/seed, focused
rubric/role checks, lint/format/types/contracts/build, security/source/image scans and container smoke
passed. Recovery restored 54 tables/272 synthetic rows in 385 ms with pgvector/immutable guards and
no cleanup failures. Cold transfer was 191501/194260/193634 bytes, below 250000 for all engines.
The implementation is on main and its completed branch is removed locally and remotely.

The preceding reviewed-rubric/telemetry release passed CI 37914864557 at `ed7d7d5`
(609 Python, 63 browser, one isolated UI and five tooling tests). ADR-044 authoring/review is verified
with learner delivery disabled; minimized model telemetry and the Next.js/Sharp/source-map-js
security refresh are verified. All completed branches through export projection have been removed.

Evidence: [rubrics](E2_REVIEWED_RUBRICS_VERIFICATION.md),
[telemetry](E8_MODEL_TELEMETRY_VERIFICATION.md),
[dependencies](E9_DEPENDENCY_REFRESH_2026_10_09.md),
[export projection](E8_EXPORT_PROJECTION_VERIFICATION.md).
Earlier verified E0–E9 slices and their individual evidence remain in the requirements register.

## Local environment recovery

Native Docker is available (29.8.2). The documented CLI PATH adjustment and
`make services-db migrate test-reviewed-rubrics test-data-exports` passed: PostgreSQL/Redis healthy,
eight rubric and eleven export cases verified. Full native `make lint test` passed 427 unit/contract
and 183 integration cases; its storage/Mailpit case failed because MinIO was not running. Separate
contract, recovery (54 tables/272 rows, 221 ms), restricted-role and security checks passed, with no
known vulnerabilities reported. This is not a full native acceptance pass.

The MinIO source download passed its checksum, but `go mod download` later failed with unexpected
EOFs in four module downloads. Native Playwright installed Chromium/FFmpeg; the headless-shell
transfer encountered timeout/connection resets and is retrying. No data or volumes were reset.

Next address NFR-MNT-001 build resilience: bounded retries and a verified module cache for the
same pinned MinIO source build. Preserve checksum verification, fail on exhausted attempts and
verify real container health/storage once dependencies arrive. Do not replace the approved release
or weaken network/security checks to make setup pass.

## Next MVP delivery slice

FR-ID-006 large-history delivery needs the explicit asynchronous worker/artifact/download contract
in the [readiness assessment](E8_LARGE_HISTORY_EXPORT_READINESS.md). The accepted projection
refactor bounds ORM hydration but retains synchronous row/byte caps and current transaction policy.
The next design must resolve snapshot authorization, leases/retries, atomic publication, orphan
cleanup, encryption binding, resource limits and owner-only streaming delivery before enablement.

The [short-text assessment](E4_SHORT_TEXT_INTEGRATION_READINESS.md) tracks pending/neutral results,
worker/fallback/mastery integration and academic calibration. Automatic scoring remains disabled.
Aggregate telemetry/load evidence, remaining hold coverage, large-history fulfillment, accountability
expiry and the reviewed anonymization/recovery proposal remain incomplete.

The [release register](RELEASE_GATES.md) tracks required kickoff/capacity, academic mappings/rights/
approved inventory and benchmark, privacy/guardian/DPIA, Week 8 provider, production OTP/MFA/roles,
PITR/RPO/RTO, branded/mobile browser and pilot approvals. The 12-week deadline and all acceptance
thresholds remain unchanged; the MVP is not complete.

NFR-MNT-001 build resilience is implemented on `codex/minio-download-recovery`: three download
attempts, terminal module verification and locked build caches for the unchanged MinIO source.
Four deterministic helper regressions pass (431 total unit/contract tests); native final-image and
hosted acceptance are pending. [Evidence](E0_MINIO_DOWNLOAD_RECOVERY.md).

While storage dependencies download, FR-ID-006/BR-010 accountability preservation is implemented
under ADR-045 on `codex/accountability-holds`, based on the pending MinIO resilience commit.
FLAG_HISTORY and DATA_REQUEST_REVIEW use exact immutable parent ownership with existing controls;
deletion execution remains disabled. Native migration and 19 focused hold cases pass. Full native
regression/recovery and hosted browser acceptance remain pending.
[Evidence](E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md).

NFR-ACC-001/NFR-COMP-001 narrow learner regression is being added on `codex/mobile-reflow`.
It exercises a 320-pixel touch viewport through registration, practice, saved resume and history,
checking reflow and key 44-pixel targets. Lint/types and inventory pass; runtime acceptance remains
pending. [Evidence](E9_MOBILE_REFLOW_VERIFICATION.md). Physical mobile and branded browser gates stay open.

Native accountability regression passed 431 unit/contract and 189 integration cases, with the one
storage/Mailpit case still failing because MinIO is not available. Host-native Ollama connectivity
now passes after starting the prescribed loopback service with cloud access disabled; no inference,
model download or Gemini evaluation ran.
