# ADR-021: Synthetic recommended practice and replay

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-MST-006, FR-REV-001/003/004/006, FR-ID-003, FR-OPS-001

## Decision

Extend the existing shared revision service with RECOMMENDED mode and a learner-safe
recommendation read endpoint. Preserve TOPIC requests. Persist the complete bounded
ranking input and result with the resulting session; immutable snapshots permit
read-only replay. Selection and session creation share the consent/learner lock and
transaction. Never accept a client-selected score, configuration or target in this mode.

Use specification 05's product and tie-break order unchanged. Synthetic configuration
uses neutral importance 1, a seven-day review interval, spacing linearly from 0.8 to
1.3 over that interval, repetition max(0.3, 1 - 0.1 * recent exposures), and readiness
0.4 + 0.6 * the minimum prerequisite mastery. Unseen skills have spacing 1.3.
These are explicit software-test defaults, not approved academic calibration.
Snapshot the entire configuration. Approved item prerequisite metadata supplies a
version-pinned synthetic graph; reject cyclic graphs. Unknown prerequisite evidence
is neutral/sparse, never asserted to be weakness. Confident prerequisite gaps redirect
before ranking dependents; lack of prerequisite inventory must not silently bypass
that gate. Full reviewed curriculum graph/importance administration remains a release
prerequisite before production. Existing synthetic-only content eligibility remains.

Eligible target plans require 5–10 unused approved items mapped to that skill. Rank
items by mapping weight, desired difficulty, format diversity, prompt-hash diversity
(the present text-only scenario proxy), exposure and stable ID. No randomness. All
plans exclude recent served identities and reservations in other active plans.
Recommended plans also exclude occupied revision topics to preserve uniqueness.
Start transactions expire stale revision reservations under the learner lock before
selection; an expired manual plan cannot retain the active-topic slot.
Low confidence uses evidence-gathering language and offers a diagnostic, without
claiming that a skill is weak. Every plan item retains its selection reason.

The recommendation endpoint previews current selection; the start transaction
recomputes and freezes it against current inventory/evidence. Preview and committed
plans retain immutable snapshots; preview returns version/hash/time
for comparison and does not reserve content. Deduplicate identical snapshots under the
learner lock and rate-limit reads. No analytics events are emitted from preview GET.

## Security, migration and boundaries

Migration 0008 adds immutable recommendation snapshots and a nullable copy on revision sessions;
old sessions remain valid. Snapshot contains skill estimates/hashes and safe content
metadata, never answer keys, raw answers or contact data. Public projections omit
candidate internals. Existing session.started outbox event covers recommended starts.
Use forward fixes; retain snapshots and compatible readers if disabling new starts.
No architecture replacement, external provider, calibration claim, real data, hints,
reassessment or progress dashboard is included. Teacher sanity review remains required.
