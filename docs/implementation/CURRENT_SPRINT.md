# Current Sprint: E8 local operations visibility

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

## Active vertical slice

[ADR-033](../decisions/ADR/033-local-operations-health.md) and
[verification](E8_OPERATIONS_VERIFICATION.md) track
FR-OPS-002: ADMIN service/queue-failure visibility and configurable local alert thresholds,
with simulated breach/recovery tests and explicit unavailable metrics for unimplemented AI
and messaging paths. No external notification delivery is enabled. Native unit tests
now pass the cross-application worker-settings regression. Database/container acceptance
is pending fresh hosted CI while Docker awaits its OS administrator prompt.

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
