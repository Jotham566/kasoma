# Current Sprint: remaining MVP operational and grading gates

Updated 9 October 2026. Main implementation is `83c6102`. Work remains synthetic/local.

## Verified and promoted

Narrow touch learner coverage passed hosted CI 37925290651 at `83c6102`: 66 real-API browser
executions, one isolated UI, 621 Python and five tooling cases, plus the full setup/recovery/role/
security/container pipeline. Recovery restored 54 tables/272 rows in 454 ms. Cold transfers were
192785/194253/193654 bytes, all below 250000. Promoted to main and removed its branch locally/remotely.
[Evidence](E9_MOBILE_REFLOW_VERIFICATION.md). Physical/branded/mobile acceptance remains open.

Recent merged slices include ADR-045 exact accountability holds (`ce9d9f3`, CI 37924489562),
MinIO download resilience (`04de7ea`, CI 37923437046), batched export projection (`8c14590`,
CI 37918757085), and reviewed rubrics/telemetry/security refresh (`ed7d7d5`, CI 37914864557).
All completed branches are removed. ADR-044 learner short-text delivery and deletion execution
remain disabled. Earlier E0–E9 evidence is preserved in the requirements register.

Evidence: [holds](E8_ACCOUNTABILITY_HOLDS_VERIFICATION.md),
[MinIO](E0_MINIO_DOWNLOAD_RECOVERY.md), [export projection](E8_EXPORT_PROJECTION_VERIFICATION.md),
[rubrics](E2_REVIEWED_RUBRICS_VERIFICATION.md), [telemetry](E8_MODEL_TELEMETRY_VERIFICATION.md),
[dependency refresh](E9_DEPENDENCY_REFRESH_2026_10_09.md).

## Active slice: objective load and assessment concurrency

NFR-PERF-001/002 and NFR-SCL-001 are being addressed on `codex/objective-load-profile`.
The isolated real-HTTP baseline creates 2,000 synthetic registrations, 500 active learners and
288 original reviewed fixtures. Fifty concurrent journeys submit objective answers at a 20/s target.
No application limits, thresholds or providers are changed.

The first profile exposed START p95 652.530 ms despite a mixed p95 of 30.115 ms. Per-operation
gates now prevent masking. ADR-046 shares immutable content read locks while still excluding
retirement, limits manual candidate work and batches final plan eligibility checks. Ordering,
permission, consent, content, grading/mastery and channel rules remain intact.

Final local baseline: 7,000 HTTP requests, 500 completed sessions, 2,500 grades, zero errors,
50 peak in-flight and successful owned-database cleanup. START p95 is 440.633 ms and objective
answer p95 27.221 ms; actual dispatch 19.996/s. Startup p99 remains about one second and is a
risk signal. This is not production or representative long-history/provider acceptance.
[Full metrics and limitations](E9_OBJECTIVE_LOAD_VERIFICATION.md).

Nineteen deterministic harness cases and six PostgreSQL lock/filter cases pass. Full native
`make format lint test` passed 450 unit/contract and 195 integration cases, including channel
parity, rubric exclusion and restricted-role checks; only storage/Mailpit failed because MinIO
is unavailable. Contract/build/security checks pass with no known dependency vulnerabilities.
Migration/recovery passes (54 tables/272 rows, 238 ms, pgvector/immutable guards, no cleanup failure).
Hosted full-stack regression is required before promotion.

## Native environment

Docker 29.8.2 and PostgreSQL/Redis work using the documented Docker CLI PATH. The pinned MinIO
source checksum passed, but module downloads encountered EOFs; the final cache/retry build is
still running. Native Playwright has Chromium/FFmpeg; headless-shell download continues after
network timeouts/resets. Native storage/browser acceptance remains incomplete. No volumes or
developer data were reset. Host-native Ollama connectivity passes with cloud disabled; no inference,
model download or Gemini evaluation ran.

## Next MVP delivery and release gates

FR-ID-006 large-history delivery needs the asynchronous worker/artifact/download contract in the
[readiness assessment](E8_LARGE_HISTORY_EXPORT_READINESS.md). Resolve snapshot authorization,
leases/retries, atomic publication, orphan cleanup, encryption binding, resource ceilings and
owner-only streaming before enablement. Existing synchronous row/byte caps remain unchanged.

The [short-text assessment](E4_SHORT_TEXT_INTEGRATION_READINESS.md) tracks pending/neutral results,
worker/fallback/mastery integration and academic calibration. Automatic scoring remains disabled.
Aggregate telemetry, representative load evidence, remaining hold coverage, accountability expiry
and the reviewed anonymization/recovery proposal remain incomplete.

The [release register](RELEASE_GATES.md) tracks kickoff/capacity, academic mappings/rights/approved
inventory and benchmark, privacy/guardian/DPIA, Week 8 provider, production OTP/MFA/roles,
PITR/RPO/RTO, branded/physical-mobile browser and pilot approvals. The 12-week deadline and all
acceptance thresholds remain unchanged; the MVP is not complete.
