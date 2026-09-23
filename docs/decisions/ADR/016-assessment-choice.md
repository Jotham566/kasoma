# ADR-016: First assessment and deterministic choice slice

Date: 23 September 2026
Status: Accepted within delegated implementation discretion
Owners: Engineering
Requirements: FR-REV-002–005, FR-GRD-001/005/007, FR-CNT-004, FR-OPS-001,
FR-ID-003, NFR-SEC-002, NFR-MNT-001

## Decision

Implement the Week 3 vertical path using the accepted modular monolith and
transactional outbox. No accepted architecture or academic rule changes.
Start with topic-selected WEB revision of 5–10 single-choice items. Recommended
planning, diagnostics, numeric/multiple-choice grading, hints, mastery projections
and reassessment remain subsequent slices. Do not represent this as full E3/E4.

The existing production startup block remains. Only explicitly synthetic approved
content is eligible in this local slice; fixtures never count as academic inventory.
Require current consent/assent, S4 enrollment and selected subject on every session,
answer, grade and solution operation, including idempotent replay. Authorization
and mutations share the identity user lock so withdrawal cannot race a new answer.

Plans pin concrete versions and reasons. Select deterministically by stable item ID,
using the newest approved version of each item. Exclude all items served to this
learner during a configurable seven-day window, across versions. Fail explicitly
when fewer than the requested count are available; never silently shorten or repeat.
Resume an active plan for the same learner/topic/count. Session lifetime defaults to
seven days; it is not a retention period. These bounded local settings are exposed
in typed environment configuration. Adaptive ranking remains E5.

Persist immutable attempts, deterministic grade snapshots (including the pinned
answer-specification version/hash and grader version), and safe outbox events in
one transaction. Acknowledgement means all three are durable. A unique session-item
constraint and actor-scoped idempotency receipt handle concurrent/network retries.
A second answer requires an explicitly assigned retry item in a later slice, never
an edit. Client score, role, channel escalation and unknown fields are rejected.
No model call is involved. Mastery update status is honestly NOT_IMPLEMENTED.

Learner DTOs explicitly allow only prompt, choices, response format and maximum
points before submission. Feedback and solution require an owned, submitted attempt.
Retirement blocks new serving/submission immediately, even for an existing plan;
historical submitted grades and solutions remain pinned and readable. Lock content
rows during delivery/submission to serialize emergency retirement.

Use the specified session/attempt endpoints. Add GET /sessions/active for cross-device
resume and POST /sessions/{id}/abandon so unavailable/expired plans have a safe exit.
The latter is idempotent by state and never removes answers. Add the specified topic
catalog endpoint. Outbox dispatch, data-subject anonymization and retention jobs
remain E8; database immutability guards are not a production least-privilege claim.

## Alternatives and approval

A one-item revision API would weaken the 5–10 item boundary. Client-selected item
IDs could bypass selection. Browser-only progress would lose cross-device recovery.
These alternatives are rejected. The user authorized the next vertical slice and
best-practice implementation discretion; no new provider or scope change is made.

## Migration and verification

Add migration 0004 after 0003. Preserve existing tables; rollback code without
removing learning evidence. Destructive downgrade requires a separate recovery plan.
Test consent, IDOR, answer leakage, retired content, concurrent replay, transaction
rollback, exact scoring, immutable history, browser recovery and accessibility.

The content difficulty labels STANDARD/CHALLENGING differ from the adaptive engine's
CORE/STRETCH. No difficulty weighting or adaptive selection is implemented here;
resolve the mapping before E5 rather than silently changing existing content.
