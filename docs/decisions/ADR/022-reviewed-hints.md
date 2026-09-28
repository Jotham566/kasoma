# ADR-022: Reviewed hints and immutable independence evidence

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-GRD-006/007, FR-MST-001/003, FR-CNT-001/004, FR-OPS-001, FR-ID-003

## Decision

Add zero to three ordered, nonblank authored hints to the versioned content document.
Existing published documents remain unchanged and have no hints. Hints travel through
the existing independent content review and rights workflow. Reviewers must check
that hints scaffold thinking without disclosing the answer or worked solution.
No generated hints, inference, external calls or production content are introduced.

The existing attempt record is an immutable submitted answer. Preserve that accepted
model. Add POST /sessions/{session_id}/items/{session_item_id}/hint for the served,
current unanswered revision item. Implement the specified POST /attempts/{id}/hint
for post-answer remediation, with GET /attempts/{id}/hints to resume disclosed levels.
These are additive routes over one shared service;
there is no placeholder attempt, score rewrite or change to submitted-answer semantics.

Each request carries an idempotency key and expected highest revealed level, preventing
network retries/concurrent clicks from accidentally revealing multiple levels. Usage
is append-only, pinned to the assignment and exact approved version, with BEFORE_ANSWER
or AFTER_ANSWER phase. Reveal only the next authored level. No hints for unserved or
future items, diagnostics (even completed), withdrawn content or unauthorized learners.
Pre-answer requests require an active session; post-answer remediation may be read
for historical submitted revision attempts while that content remains approved.

At submission, freeze the count and highest level of BEFORE_ANSWER use into the
attempt, mastery source and mastery.updated event. Keep the specified independence
formula unchanged: max(0.5, 1 - 0.15 * hint_count). Grade correctness/points do not change.
Post-answer hints never revise that frozen independence or original score. A later
unseen reassessment will establish independent evidence; it is a separate slice.

Mastery input serialization omits the new optional highest-level field when absent
in legacy evidence, preserving prior input hashes and replay. New evidence includes
it explicitly. Add migration 0009 for usage, receipts, bounded hint metadata and
integrity guards. Keep old rows valid; use forward fixes and retain evidence on rollback.
New optional analytics fields preserve existing version-1 event compatibility.

## Alternatives, security and verification

Mutable ungraded attempts would alter accepted evidence semantics unnecessarily.
Browser-only hint counts would be forgeable and lose cross-device state. Retroactively
reducing a stored grade/mastery event after remediation would corrupt audit history.
Reject all three. Authoritative disclosure and submission share the learner/consent
lock; database guards bind the frozen counts to actual usage. No hint text or learner
answers appear in analytics/logs. Persist only safe version/level linkage for usage.

Test reviewed publication, old content/evidence replay, count/level binding, formula,
concurrent hint/submission and duplicate delivery, IDOR/consent, diagnostic/solution
leakage, retired/unserved items, failed-transaction rollback, browser recovery and axe.
Update changelog, contracts, current sprint, traceability and verification evidence.
