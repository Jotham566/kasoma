# Current Sprint: E7 WhatsApp linking

Legal holds (`ec53ac4`) and dependency remediation (`b766266`) are published to main.
[Hosted CI](https://github.com/Jotham566/kasoma/actions/runs/37126531374) passed setup,
clean migrations/seed, lint/types, full tests/contracts/build, browser journeys,
security audits, image builds/scans and container smoke on 3 October. Completed branches removed.
Docker recovered during verification; no volumes were reset.

## Latest completed slice

Bounded synthetic imports are published as `5bdd122`; the completed branch is removed.

FR-CNT-001/002/004/005 and bounded FR-OPS-001/002/003: original synthetic JSON draft
imports under [ADR-032](../decisions/ADR/032-bounded-draft-imports.md).
Author UI/API, durable command outbox, transactional worker, duplicates, retries,
role rechecks, source locators and draft-only review passed verification: 347 Python,
18 browser and five tooling tests; clean migrations, contracts, builds and security/container checks.
See [import evidence](E2_IMPORTS_VERIFICATION.md).
The import slice is independent of destructive data-request execution.

## Operations verification complete

[ADR-033](../decisions/ADR/033-local-operations-health.md) and
[verification](E8_OPERATIONS_VERIFICATION.md) track
FR-OPS-002: ADMIN service/queue-failure visibility and configurable local alert thresholds,
with simulated breach/recovery tests and explicit unavailable metrics for unimplemented AI
and messaging paths. No external notification delivery is enabled.
Commit `7218898` is published to main and its branch removed after
[full hosted CI passed](https://github.com/Jotham566/kasoma/actions/runs/37131981381):
360 Python tests, 19 browser tests, five tooling tests and all setup/migration/build/security/container gates.
Local Docker recovered without a reset; hosted evidence remains independent.

## Active implementation

[WhatsApp linking readiness](E7_LINKING_READINESS.md) defines FR-WA-001/004/006 and
the required privacy/consent gates under ADR-034. Migration 0018, owner code/status/unlink,
signed durable intake, STOP barriers, transactional processing, fake delivery, expiry and
owned export/inventory are implemented. 24 focused contract/integration tests passed.
All 20 browser journeys and an earlier full regression/container pass succeeded. Final
verification was interrupted by Docker Desktop stopping; exact-snapshot hosted CI is required
before promotion to main. Final lint/types/contracts pass; acceptance remains pending.
No external messaging is enabled.

Prepare the concrete deletion/anonymization transform and recovery plan for required
review before destructive execution; reconcile immutable learning/content records,
remaining legal holds, logs/backups and representative requests. Continue unaffected
MVP work while academic/privacy/production approvals are outstanding.
Large-history export and six-year evidence expiry remain explicit gaps.

## Remaining dependencies and release gates

See the [release evidence register](RELEASE_GATES.md) for responsible functions and required artifacts.

- Named owners, kickoff date, delivery and academic reviewer capacity.
- Exact NCDC mappings, content rights, balanced inventory, reviewed equivalent pairs
  and expert benchmark; semantic transfer validation and calibrated criterion thresholds.
- Approved privacy wording, verifiable guardian procedure, DPIA and legal approvals.
- Week 5 short-text benchmark and Week 8 production provider decision; no model
  evaluation, real learner data or cloud deployment is authorized by these local checks.
- Short-text, WhatsApp and remaining operations.
- Production OTP/MFA, restricted DB roles, outbox dispatch and retention/anonymization jobs.

Prior evidence: [reassessment](E4_REASSESSMENT_VERIFICATION.md),
[hints](E4_HINTS_VERIFICATION.md), [recommendations](E5_RECOMMENDATIONS_VERIFICATION.md),
[diagnostics](E5_VERIFICATION.md), [traceability](REQUIREMENTS_TRACEABILITY.md).
