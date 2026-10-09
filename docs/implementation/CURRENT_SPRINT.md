# Current Sprint: remaining MVP operational and grading gates

Updated 9 October 2026. Main is `64394ac`. Completed branches through rubric context, restricted
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
and container smoke. Native database/browser attempts failed before assertions because Docker.app
is unavailable. Hosted evidence does not claim that native installation has recovered. The first
recovery run failed on a table-name check; it was fixed and the complete pipeline rerun.

Restricted-login verification, learning-record holds and bounded identity expiry passed CI
37228338121 (574 Python, 60 browser, five tooling checks). Explicit rubric context passed CI
37228984415 (587 Python, 60 browser, five tooling checks), including all preceding changes and
clean migrations/recovery/security/container checks. See [permissions](E9_RUNTIME_ROLE_VERIFICATION.md),
[holds](E8_LEARNING_HOLDS_VERIFICATION.md), [expiry](E1_EPHEMERAL_EXPIRY_VERIFICATION.md) and
[rehearsal](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md). Production credentials remain unchanged.

## Active implementation

FR-CNT-001/002/003/004, FR-GRD-003/004, NFR-SEC-002: ADR-044 adds version-pinned reviewed
rubrics, staff authoring/review, SQL projection/immutability checks and disabled learner assignment.
Local 416 unit/contract checks pass; fresh/upgrade database and 63 browser executions await hosted
acceptance. [Rubric evidence](E2_REVIEWED_RUBRICS_VERIFICATION.md).

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

## Following slice: synthetic gateway telemetry

NFR-OBS-001/FR-OPS-002: model.call and model.rehearsal events now record minimized timing,
registered labels, reported usage and safe per-rehearsal fingerprints. 427 unit/contract checks pass; newly reported JavaScript dependency advisories block
promotion, and hosted regression is pending. [Evidence](E8_MODEL_TELEMETRY_VERIFICATION.md). Dashboard aggregation, production log
retention and provider accuracy/cost remain open; no inference adapter is enabled.

Rubric acceptance follow-up (9 October): CI 37909280438 passed clean migration/seed but failed
synthetic recovery population. `make test-reviewed-rubrics` now runs before recovery to expose
focused database diagnostics; the complete recovery and regression gates remain required. No
rubric acceptance or main promotion is claimed from this failed run.

The rubric SQL guard incorrectly treated the existing item_versions.document JSON column as JSONB.
Normalize a local comparison value to JSONB before equality/existence checks; retain the original
column, stored documents and hashes. Existing fresh/upgrade and projection tests cover this path;
complete hosted rerun remains required.

9 October dependency remediation (NFR-MNT-001/security gate): runtime Next.js is pinned to 16.3.8,
with affected Sharp/source-map-js versions resolved to 0.35.5/1.2.2. `make deps-lock setup` and
post-install lint/types/contracts/build, 427 unit/contract plus five tooling checks, and both audits
pass with no known vulnerabilities reported. Hosted application/container checks remain pending.

CI 37910416518 verifies the rubric SQL correction: eight focused rubric cases, all 182 integration
and 427 unit/contract tests pass, as do the restricted login and 54-table/272-row recovery drill.
The new Chromium rubric journey fails after save/reload. Add exact API round-trip assertions and
`make test-web-content`, an isolated deterministic HTTP-fixture browser regression, before full CI
services. It supplements, not replaces, the 63 real-API journeys. Main promotion remains blocked.
Browser binaries now use the repository-local .local/browsers cache to avoid shared-cache mutation.
