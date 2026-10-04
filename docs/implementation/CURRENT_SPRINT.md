# Current Sprint: remaining MVP operational and grading gates

Updated 4 October 2026. Main is `74a4a8f`. Completed conversation, channel operations, short-text
foundation, recovery, browser and request-timing branches have been removed. Work remains synthetic/local.

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
and container smoke. Native database/browser attempts failed before assertions because Docker.app
is unavailable. Hosted evidence does not claim that native installation has recovered. The first
recovery run failed on a table-name check; it was fixed and the complete pipeline rerun.

## Active implementation

NFR-SEC-002: a temporary restricted database login now exercises objective assessment, idempotency,
mastery evidence and explicit permission denials. Hosted database execution is pending; the native
fixture cannot connect. Default application credentials are unchanged.
[Permission evidence](E9_RUNTIME_ROLE_VERIFICATION.md).

FR-ID-006/BR-010: ADR-043 adds exact grade/mastery evidence/history hold targets with ownership
locks and unchanged immutable protections. Local 397 unit/contract checks pass; hosted migration/
application acceptance is pending. [Learning hold evidence](E8_LEARNING_HOLDS_VERIFICATION.md).

FR-ID-001/NFR-OBS-001: bounded worker expiry replaces request-triggered bulk removal of expired
OTP/rate records. Row locks protect rate refresh against cleanup. Local 400 unit/contract checks pass; hosted
acceptance is pending;
[expiry evidence](E1_EPHEMERAL_EXPIRY_VERIFICATION.md).

FR-GRD-003/004: the synthetic criterion context now carries required rubric text/evidence/error/
inference material, with v2 rehearsal prompts and 13 additional boundary/privacy cases. Local
413 unit/contract checks pass; persisted approved rubrics and learner scoring remain unavailable.

## Next dependencies and acceptance work

The [short-text integration assessment](E4_SHORT_TEXT_INTEGRATION_READINESS.md) identifies the
required versioned rubric/criteria, pending/neutral result, idempotent worker, fallback and mastery
boundaries. Automatic scoring remains disabled. Academic truth and benchmark/calibration approval
cannot be inferred from fake output agreement.

Continue remaining AI/usage/domain telemetry and the agreed latency/load profile. Complete remaining
hold coverage, large-history exports and accountability expiry. Prepare the concrete anonymization
transform/recovery proposal before seeking destructive-execution approval. No immutable evidence
is rewritten by the current slices.

The [release register](RELEASE_GATES.md) tracks missing kickoff/capacity, exact NCDC mappings, rights
and approved inventory, expert benchmarks, privacy/guardian/DPIA, Week 8 provider choice, production
OTP/MFA/restricted roles, managed PITR/RPO/RTO, branded/mobile/versioned browser and pilot sign-offs.
The approved 12-week deadline and all acceptance thresholds remain unchanged.

Runtime-role verification follow-up: hosted CI 37227070209 exposed the existing users-row lock in
attempt_hint_guard. The test profile adds only the mutable display_name column grant and verifies
identity/status/birth-date remain denied. All 162 existing integration cases passed; the corrected
restricted-login case and full pipeline are pending rerun. No production credential change.
