# ADR-043: Individual learning-record legal holds

Date: 4 October 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002

Extend ADR-030's explicitly incomplete target registry with GRADE, MASTERY_EVIDENCE and
MASTERY_HISTORY. These are existing immutable, learner-owned learning records. Preserve the
independent recent-OTP ADMIN claimant, finite authorized decision, exact-record scope, immutable
receipt/audit, expiry/release and six-year-after-request-completion evidence controls unchanged.
This expands preservation coverage without introducing an erasure permission or retention period.

GRADE uses its existing attempt_id primary key as record_id; it has no separate grade UUID.
Ownership follows the immutable attempt. MASTERY_EVIDENCE uses its own id and learner_id;
MASTERY_HISTORY uses its own id and follows its immutable evidence owner. Both API and SQL
check these relationships and acquire key-share locks on the target and joined ownership rows.
The grade DELETE guard reads attempt_id; the other two reuse the existing id-based guard.
Migration 0022 widens the target constraint and replaces only the ownership guard function while
retaining every existing validation. Existing rows and immutable learning evidence are unchanged.

A hold applies only to the named row. It does not silently hold the associated attempt, grade,
mastery history, rebuildable estimate or entire account. Future transforms must evaluate affected
references and all explicit holds under compatible transaction locks. Expiry/release never bypasses
existing immutable guards. Deletion stays disabled and LEGAL_HOLD_COVERAGE_INCOMPLETE remains,
including channel records, embedded references, remaining sources, logs and backups.

The administrator form labels all seven supported types and explains the grade key. API schemas
are generated from the expanded strict enum. No model, provider, learner export disclosure or
legal interpretation changes. Operators still need an already authorized preservation decision;
synthetic tests cannot supply production legal/privacy approval.

Verify exact ownership including missing/foreign targets through API and direct SQL, denied
DELETE under active holds, release/expiry with immutable evidence preserved, duplicate receipts,
preview counts and unchanged disabled execution. Rollback disables new options/routes and uses a
forward fix while retaining registered holds; downgrade must not drop protections or evidence.
