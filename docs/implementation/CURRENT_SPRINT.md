# Current Sprint: remaining MVP operational and grading gates

Updated 9 October 2026. Main implementation is `ed7d7d5`. Completed branches through rubric context, restricted
login, learning-record holds and ephemeral expiry have been removed. Work remains synthetic/local.

## Verified implementation

| Slice | Commit / hosted CI | Evidence |
| --- | --- | --- |
| Signed five-question WhatsApp practice | `5063528` / 37220225176 | 469 Python, 20 browser, five tooling checks; [report](E7_CONVERSATION_VERIFICATION.md) |
| Minimized channel operations | `34950b0` / 37221185319 | 479 Python, 20 browser, five tooling checks; [report](E8_CHANNEL_OPERATIONS_VERIFICATION.md) |
| Strict synthetic rubric candidate validation | `3b74f5b` / 37221835579 | 519 Python, 20 browser, five tooling checks; [report](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md) |
| Fake dual-pass/budgeted rehearsal | `2ce14c3` / 37222368566 | 534 Python, 20 browser, five tooling checks; [report](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md) |
| Isolated logical recovery | `42a6e08` / 37223872075 | 550 Python, 20 browser, five tooling checks; 52 tables/270 rows restored; [report](E9_RECOVERY_VERIFICATION.md) |
| API response-start timing | `74a4a8f` / 37226011029 | 556 Python, 60 browser, five tooling checks; [report](E8_REQUEST_TIMING_VERIFICATION.md) |
| Three-engine journeys and cold transfer | `96a16d0` / 37224172033 | 550 Python, 60 browser, five tooling checks; 191389–194127 bytes; [report](E9_BROWSER_COVERAGE_VERIFICATION.md) |

Each run also passed clean setup/migrations/seed, lint/types/contracts/build, security scans/audits
and container smoke. Earlier native database/browser attempts failed before assertions while Docker was unavailable.
Hosted evidence does not substitute for native application acceptance. The first
recovery run failed on a table-name check; it was fixed and the complete pipeline rerun.

Restricted-login verification, learning-record holds and bounded identity expiry passed CI
37228338121 (574 Python, 60 browser, five tooling checks). Explicit rubric context passed CI
37228984415 (587 Python, 60 browser, five tooling checks), including all preceding changes and
clean migrations/recovery/security/container checks. See [permissions](E9_RUNTIME_ROLE_VERIFICATION.md),
[holds](E8_LEARNING_HOLDS_VERIFICATION.md), [expiry](E1_EPHEMERAL_EXPIRY_VERIFICATION.md) and
[rehearsal](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md). Production credentials remain unchanged.

## Newly verified and promoted

Hosted CI [37914864557](https://github.com/Jotham566/kasoma/actions/runs/37914864557)
passed at `ed7d7d5`: 427 unit/contract and 182 integration tests (609 Python total), five tooling
tests, 63 real-API browser journeys across Chromium/Firefox/WebKit and one isolated editor UI test.
Clean setup/migrations/seed, eight focused rubric cases, restricted-login verification,
lint/format/types/contracts/build, dependency/source/image security checks and container smoke all
passed. The isolated logical recovery restored 54 tables/272 synthetic rows in 455 ms and verified
pgvector/immutable guards; this is not production PITR/RPO/RTO evidence. Cold question transfers
were 191529/194251/193635 bytes, each below 250000. Commit `ed7d7d5` is on main; both completed
rubric/telemetry branches were deleted locally and remotely.

FR-CNT-001/002/003/004, FR-GRD-003/004 and NFR-SEC-002: version-pinned reviewed rubrics under
ADR-044 are verified with learner assignment disabled. [Rubric evidence](E2_REVIEWED_RUBRICS_VERIFICATION.md).
NFR-OBS-001/FR-OPS-002: minimized fake gateway call/outcome telemetry is verified; durable
aggregation remains pending. [Telemetry evidence](E8_MODEL_TELEMETRY_VERIFICATION.md).
NFR-MNT-001: Next.js/Sharp/source-map-js dependency remediation passes the complete pipeline.
[Dependency evidence](E9_DEPENDENCY_REFRESH_2026_10_09.md).

## Active local verification and next slice

Docker Desktop now responds (29.8.2). The installed CLI needed the macOS PATH adjustment documented
in the runbook. Approved service image builds and isolated browser downloads are running; native
migration/seed/database/browser assertions remain pending. Earlier native failures remain historical.

Next implement the FR-ID-006 personal-export read projection in bounded batches, preserving the v1
privacy allowlist, sealed diagnostic rules and existing all-or-nothing synchronous limits. Then add
verified asynchronous large-history delivery under an explicit ADR. The
[readiness assessment](E8_LARGE_HISTORY_EXPORT_READINESS.md) records snapshot/authorization,
resource, privacy, expiry and atomic-publication requirements; it is not implementation acceptance.

## Dependencies and remaining MVP gates

The [short-text integration assessment](E4_SHORT_TEXT_INTEGRATION_READINESS.md) identifies pending/
neutral results, idempotent worker, fallback and mastery boundaries. Automatic scoring remains
disabled; academic truth and benchmark/calibration approval cannot be inferred from fake agreement.
Complete aggregate telemetry/load evidence, remaining hold coverage, large-history exports and
accountability expiry. Prepare the concrete anonymization/recovery proposal before destructive
execution. Current slices do not rewrite immutable evidence.

The [release register](RELEASE_GATES.md) tracks missing kickoff/capacity, exact NCDC mappings, rights
and approved inventory, expert benchmarks, privacy/guardian/DPIA, Week 8 provider choice, production
OTP/MFA/restricted roles, managed PITR/RPO/RTO, branded/mobile/versioned browser and pilot sign-offs.
The approved 12-week deadline and acceptance thresholds remain unchanged. The MVP is not complete.
