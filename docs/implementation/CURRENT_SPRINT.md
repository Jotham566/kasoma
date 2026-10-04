# Current Sprint: E7 shared WhatsApp practice

Updated 4 October 2026. Main is `5063528`; the completed conversation and foundation branches have been removed.

## Latest verified slice

Internal channel assessment capability and three-format score/mastery parity passed
[hosted CI 37217857047](https://github.com/Jotham566/kasoma/actions/runs/37217857047):
437 Python tests, 20 browser tests and five tooling checks. Setup, clean migrations/seed,
lint/types/contracts/build, security and container smoke all passed. Migration 0019 admits
immutable WHATSAPP provenance while preserving public WEB-only contracts, existing evidence
guards and shared grading/mastery. See [transaction evidence](E7_SHARED_TRANSACTIONS_VERIFICATION.md).

Prior verified dependencies include local linking/intake/STOP (`23da19c`), shared transactions
(`50044d4`) and objective question/reply formatting (`dd1c8d8`). These are synthetic/local gates;
no production messaging or academic content approval follows from these tests.

## Conversation acceptance

Commit `5063528` passed full [CI 37220225176](https://github.com/Jotham566/kasoma/actions/runs/37220225176):
469 Python, 20 browser and five tooling checks, clean migrations and all security/container gates.
It is on main; the conversation branch has been removed. This verifies signed reply-bound practice,
shared grading/mastery, STOP/expiry, broker-outage recovery and channel-suitability enforcement.
Native database checks failed at setup because Docker/PostgreSQL is unavailable; hosted proof is
separate and does not claim native acceptance. See [conversation evidence](E7_CONVERSATION_VERIFICATION.md).

## Next implementation and gates

Finish pending channel operations hosted verification. Measure deterministic feedback latency under the normal worker;
functional tests alone do not establish NFR-PERF-002. Continue remaining telemetry/usage controls and
guarded short-text preparation within the synthetic profile.

Prepare the concrete deletion/anonymization transform and tested recovery plan before seeking the
required destructive-execution approval. Remaining channel/record hold coverage, large-history export
and six-year accountability expiry remain explicit gaps. Preserve immutable evidence meanwhile.

See the [release gate register](RELEASE_GATES.md) for required owner evidence: kickoff/capacity,
exact NCDC mappings, rights, approved inventory, expert benchmark/calibration, privacy/guardian/DPIA,
Week 8 provider choice, production OTP/MFA, restricted roles, restore/load and pilot sign-offs.
No elapsed time or synthetic test pass substitutes for those approvals.

Prior evidence: [imports](E2_IMPORTS_VERIFICATION.md), [linking](E7_LINKING_READINESS.md),
[legal holds](E8_LEGAL_HOLDS_VERIFICATION.md), [reassessment](E4_REASSESSMENT_VERIFICATION.md),
[progress](E6_PROGRESS_VERIFICATION.md), [traceability](REQUIREMENTS_TRACEABILITY.md).

## Independent channel operations follow-up

ADR-039 adds bounded channel queue/status/timing visibility to the existing ADMIN dashboard.
Migration 0021 contains indexes only. Generated contracts, typed thresholds, alert schemas and
unit/database/browser regressions accompany the implementation. Verification is pending; local
fake-dispatch percentiles cannot satisfy the release latency/load gate by themselves.

## Next short-text boundary

ADR-040 adds offline strict candidate validation for FR-GRD-003/004/005. Forty fixture cases pass;
357 unit/contract and five tooling checks pass with lint/types/contracts. No short-text learner
route or model execution is enabled. Next: budgeted fake gateway orchestration and dual independent
passes with bounded repair, retaining academic calibration and learner fallback gates.
