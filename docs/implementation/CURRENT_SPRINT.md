# Current Sprint: E2 first content review slice

E0 foundation (`4faf65a`) and E1 identity/consent (`9dfe726`) are on main.
Both passed hosted CI. E2 work is on `codex/e2-content-review` and remains
uncommitted for review. See [E2 verification](E2_VERIFICATION.md).

## Current slice

FR-CNT-001–005: text-only single-choice draft authoring, independent review,
return/correction, approval, retirement and new versions; FR-OPS-003 content/role
audit; supporting NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

Partial scope is explicit: bulk import, other response formats, media, full curriculum
graph, real NCDC outcome mappings, rubric entities, historical attempt pinning and
learner flags are not completed by this slice. Synthetic APPROVED versions are
workflow test evidence, excluded from production content counts and selection.

## Next vertical slice

E3: a consented learner starts a short session, receives an approved synthetic
single-choice item without its answer key, submits one immutable answer and receives
a deterministic grade. Pin the item version, make retries idempotent and emit the
transactional result event. Extend numeric content/grading next; do not invent
academic outcomes or claim the full diagnostic/mastery loop.

## Remaining release gates

- Real academic mapping, source rights review and production content inventory.
- Approved consent/assent notices, guardian-verification procedures and legal review.
- Production OTP providers, staff MFA/role governance and separate restricted database roles.
- Long-term retention jobs, analytics dispatch, data-subject requests and provider selection.
- All future learning/WhatsApp routes must enforce current consent and approved-content selection.
- Week 5/6 short-text benchmark sequencing question E0-01 remains open for the grading slice.
- No calendar kickoff or named delivery owners have been supplied; horizon remains 12 weeks.

Prior evidence: [E0](E0_VERIFICATION.md), [E1](E1_VERIFICATION.md),
[Phase 0 assessment](PHASE_0_ASSESSMENT.md), [traceability](REQUIREMENTS_TRACEABILITY.md).
