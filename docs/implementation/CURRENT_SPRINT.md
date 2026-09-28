# Current Sprint: E4 numeric grading

E0–E3 are on main. E3 `22773fd` passed hosted CI and its completed branch was
removed. E4 numeric grading is verified locally as recorded below and authorized for merge;
28 September Docker-dependent rechecks await Docker Desktop authentication.

## Current slice

FR-GRD-002/005/007, FR-CNT-001/004/005 and supporting FR-REV-003, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001.

Authors define numeric answers, permitted units/conversions, absolute and relative
tolerance, accepted decimal/scientific/fraction forms and explicit precision policy.
Independent reviewers approve these rules. Learners receive only input instructions,
submit bounded numeric answers and get deterministic version-pinned feedback.
Migration 0005 preserves existing choice evidence and stores numeric responses
immutably. No model provider or production dependency is introduced.

## Resolved pending questions

[ADR-017](../decisions/ADR/017-readiness-resolutions.md) resolves:

- E3-01: preserve content labels and use versioned FOUNDATIONAL→FOUNDATIONAL,
  STANDARD→CORE, CHALLENGING→STRETCH mapping when implementing E5 evidence.
- E0-01: retain the Week 5 short-text benchmark gate; deliver its first supported
  grading/evaluation path in Weeks 3–5, then harden/broaden in Week 6.

[ADR-018](../decisions/ADR/018-numeric-grading.md) records exact numeric semantics.
Test servers now use dedicated loopback ports; container smoke preserves application
services that were already running.

## Next vertical slice

Diagnostic planning and initial mastery evidence: one active diagnostic per subject,
10–15 approved choice/numeric items, topic/competency coverage, no hints or solutions,
durable resume, immutable mapped evidence and initial score/confidence projection.
Use the approved difficulty mapping and engine formula with replay/idempotency tests.
The first recommendation must include an honest rationale and uncertainty.

## Remaining external dependencies and release gates

- Named delivery/academic/safeguarding owners, kickoff date and confirmed capacity.
- Exact NCDC mappings, source rights review, real item inventory and expert benchmark.
- Approved notices, guardian-verification procedure, DPIA and other privacy approvals.
- Week 8 production provider selection, production OTP/MFA and restricted DB roles.
- Other MVP implementation: diagnostic/mastery, recommended practice, multiple choice,
  short text, hints, reassessment, flags, progress, WhatsApp and operations.
- Outbox dispatch and approved retention/anonymization jobs remain E8 work.
- Current evidence remains synthetic and does not authorize production use.

Current evidence: [E4 numeric verification](E4_VERIFICATION.md).

Prior evidence: [E0](E0_VERIFICATION.md), [E1](E1_VERIFICATION.md),
[E2](E2_VERIFICATION.md), [E3](E3_VERIFICATION.md),
[traceability](REQUIREMENTS_TRACEABILITY.md).
