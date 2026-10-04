# Current Sprint: E7 shared WhatsApp practice

Updated 4 October 2026. Main is `c0b5b55`; all completed foundation branches have been removed.

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

## Active implementation

[ADR-038](../decisions/ADR/038-local-whatsapp-practice.md) and migration 0020 implement signed
five-question conversations, exact menu/question reply binding, minimized transient encrypted
answers, safe dynamic fake delivery, STOP/unlink invalidation and local queue wake-up. Commit
`a440182` is undergoing hosted verification. Follow-up concurrency coverage and aligned web/runbook
instructions are being checked. No end-to-end conversation acceptance is claimed yet.

Native `make format lint openapi-check test-unit` passes 310 unit/contract and five tooling tests.
Security audits pass. Docker has no running socket; migration and focused database checks fail at
connection/setup, before application assertions. No volumes were reset. Hosted clean-schema checks
must pass for the final snapshot before promotion. See [conversation evidence](E7_CONVERSATION_VERIFICATION.md).

## Next implementation and gates

Finish conversation regression, retry/out-of-order and delivery authorization checks, then publish
verified work and remove its branch. Measure deterministic feedback latency under the normal worker;
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
