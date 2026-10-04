# Current Sprint: remaining MVP operational and grading gates

Updated 4 October 2026. Main is `96a16d0`. Completed conversation, channel operations, short-text
foundation, recovery and browser branches have been removed. Work remains synthetic/local.

## Verified implementation

| Slice | Commit / hosted CI | Evidence |
| --- | --- | --- |
| Signed five-question WhatsApp practice | `5063528` / 37220225176 | 469 Python, 20 browser, five tooling checks; [report](E7_CONVERSATION_VERIFICATION.md) |
| Minimized channel operations | `34950b0` / 37221185319 | 479 Python, 20 browser, five tooling checks; [report](E8_CHANNEL_OPERATIONS_VERIFICATION.md) |
| Strict synthetic rubric candidate validation | `3b74f5b` / 37221835579 | 519 Python, 20 browser, five tooling checks; [report](E4_SHORT_TEXT_VALIDATION_VERIFICATION.md) |
| Fake dual-pass/budgeted rehearsal | `2ce14c3` / 37222368566 | 534 Python, 20 browser, five tooling checks; [report](E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md) |
| Isolated logical recovery | `42a6e08` / 37223872075 | 550 Python, 20 browser, five tooling checks; 52 tables/270 rows restored; [report](E9_RECOVERY_VERIFICATION.md) |
| Three-engine journeys and cold transfer | `96a16d0` / 37224172033 | 550 Python, 60 browser, five tooling checks; 191389–194127 bytes; [report](E9_BROWSER_COVERAGE_VERIFICATION.md) |

Each run also passed clean setup/migrations/seed, lint/types/contracts/build, security scans/audits
and container smoke. Native database/browser attempts failed before assertions because Docker.app
is unavailable. Hosted evidence does not claim that native installation has recovered. The first
recovery run failed on a table-name check; it was fixed and the complete pipeline rerun.

## Active implementation

NFR-OBS-001/FR-OPS-002: correlated API logs/spans now include additive response-start milliseconds
without URLs or payloads. Six deterministic timing/privacy cases pass; all 394 local unit/contract
and five tooling checks, lint/types/contracts and security pass. Hosted regression is pending.
This is server response-start instrumentation, not full network timing or an aggregated p95 gate.
[Timing evidence](E8_REQUEST_TIMING_VERIFICATION.md).

NFR-SEC-002: a temporary restricted database login now exercises objective assessment, idempotency,
mastery evidence and explicit permission denials. Hosted database execution is pending; the native
fixture cannot connect. Default application credentials are unchanged.
[Permission evidence](E9_RUNTIME_ROLE_VERIFICATION.md).

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
