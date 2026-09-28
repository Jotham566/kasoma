# ADR-024: Evidence-derived learner progress and session history

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-MST-004/005, supporting FR-MST-002/003, FR-ID-003, FR-REV-005,
NFR-SEC-002, NFR-ACC-001, NFR-LOC-001, NFR-MNT-001

## Decision and boundaries

Implement the specified GET /me/progress?subject_id= and GET /me/session-history
with web Progress and History pages. Current consent, S4 and selected-subject access
apply on every request. Do not accept a learner ID. Reuse the versioned mastery
engine at one explicit read timestamp; no changes to grades, evidence or persisted
mastery projections. Normal correlation/access logging covers these reads; no gesture
analytics, raw answers or contact data are added.

Exclude all evidence from diagnostics until that diagnostic is COMPLETED, including
abandoned/expired diagnostics. This preserves ADR-020's sealed results through new
aggregate routes. History may show saved-answer counts/status but never scores,
answers, item IDs, hints or recommendations derived from an unfinished diagnostic.
Historical approved-version evidence remains valid when content is later retired;
retirement prevents new delivery, not a silent retrospective grade cancellation.

Skill scope comprises approved synthetic curriculum mappings plus eligible historical
evidence in the selected subject. Do not invent a concept/competency cross-product.
Use existing engine estimates (including neutral priors for mapped but unassessed
skills). Subject/topic/competency rollups are equal-weight means of those skill
estimates and confidence values, versioned as progress-rollup-v1. Neutral weights are
explicit synthetic display defaults, not academic calibration. Show assessed/total
mapped skill coverage and count unique attempts, not duplicated mappings. Empty scope
has null mastery, zero confidence and NOT_ENOUGH_EVIDENCE. A sparse rollup never
claims full subject mastery. No new stored aggregate is introduced.

For change text, recompute the same scope at the same timestamp with the latest visible
attempt removed (timestamp then stable ID). Only compare if both confidence values
are at least 0.25; otherwise say not enough evidence to compare. This isolates recent
answer evidence from clock decay and avoids claiming intervention-caused learning gain.
Use the existing display-state thresholds unchanged. UI omits numeric mastery below
0.25 confidence and always includes confidence, estimate wording and coverage.

History uses descending (started_at,id) keyset pagination with limit 1–50 (default 10).
The opaque cursor is authenticated and bound to learner and optional subject filter;
all authorization is rechecked on every page. Derive EXPIRED status at read time without
mutating sessions. Summaries expose safe kind/topic/timestamps/counts and existing
session IDs for resume/review. UTC remains on the wire; dates display in Africa/Kampala.
Newer sessions appear on reload, not as duplicate entries while paging backward.

## API, security and tests

Typed, generated DTOs include summary confidence, coverage, latest evidence time,
algorithm/aggregation versions and an input hash, without evidence payloads or answer
keys. Progress returns subject, topic and competency summaries and a safe next action:
continue an active diagnostic, gather diagnostic evidence, or open recommended practice.
It does not call recommendation selection during an unfinished diagnostic. Existing
recommendation UI remains on Home; this slice does not expand its ranking policy.

No migration is required: existing curriculum, immutable evidence and session indexes
supply these views. Rate-limit read projections; return safe failure for corrupt or
unsupported evidence rather than inventing values. Tests cover hand-calculated means,
coverage/deduplication, sparse/strong states, latest-evidence change, recency, completed
versus sealed diagnostic evidence, consent/IDOR/subject filtering, cursor tampering,
equal-time page boundaries, expiry, read-only evidence and browser retry/keyboard/axe.

No peers, rankings, streak system, inference, production data, cloud dependency or
mature-product feature is added. Academic calibration and production gates remain.
