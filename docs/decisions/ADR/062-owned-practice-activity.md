# ADR-062: Owned recent practice-day indicator

Date: 19 October 2026
Status: Accepted within the user's approved MVP implementation discretion; verification pending
Requirements: FR-MST-004/005, FR-ID-003, FR-WA-003, NFR-SEC-002,
NFR-ACC-001, NFR-LOC-001, NFR-MNT-001

## Context and implementation discretion

[Roadmap section 3.5](../../product/PRODUCT_ROADMAP.md) includes a simple streak or
consistency indicator. [ADR-024](024-progress-history.md) implemented the progress/history
slice without a streak system. Add one read-only practice-day measure to the approved
MVP Progress view. This adds neither consecutive-day streak rules nor stored rewards,
rankings or a new mastery input. Existing access, sealed diagnostics, grading and
academic policy remain unchanged. It is independent of proposed ADR-061.

The user has authorized completing the approved MVP and making routine implementation
choices. The following seven-day display definition is such a choice, not a new
retention/consent/preservation permission, destructive action or architectural replacement.
No external academic, privacy, safeguarding or production approval is inferred.

## Decision and exact semantics

For the selected subject, show the number of distinct Africa/Kampala calendar dates
with visible graded practice in the seven dates ending today, inclusive. Use the same
explicit server read timestamp as mastery rollups. The first date begins at Kampala
midnight six dates earlier; this is a calendar window, not the last 168 hours or a
Monday-start week. Reject naive/future source timestamps rather than guessing a zone
or inventing activity. Source dates use the original attempt time already pinned in
mastery evidence, including when short-text grading completes later.

Reuse only the authenticated progress query's already visible GRADED evidence, after
its existing validation. Include web/WhatsApp and completed diagnostics/reassessment;
exclude other learners/subjects, pending/unresolved grading and every unfinished,
abandoned or expired diagnostic. Repeated attempts or skill mappings on one date
count that date once. Wrong answers with valid grading also count; this measures
activity, not attainment, confidence, effort duration or learning improvement.

Compute on reads without additional database queries, evidence replay, writes, cache,
new timestamps, stored aggregates, analytics events or retention classes. Corrupt
existing evidence still fails through the existing rollup validation. No global
leaderboard, notifications, penalties, lost-streak language or comparison is introduced.

## Additive contract and UI

Extend ProgressView with practice_activity: days_practised (0–7), window_start/window_end
as calendar dates, fixed window_days=7, time_zone=Africa/Kampala and version
practice-days-v1. Dates must span exactly seven inclusive days. The new server always
returns the object after authorized successful progress computation. Contract optionality
supports mixed reader/server rollout only; missing/null means unavailable, never zero.
Existing web readers can ignore the additional field; new web handles older responses safely.

Use the existing responsive card style, a text count and labelled non-interactive meter.
Explain the selected-subject, graded-practice and Kampala-date basis. Distinguish
activity from mastery. Keep zero and unavailable states neutral, with no invented counts.
Existing loading/error/offline/consent states govern the whole data-dependent view.
No contact, answer text, item/learner IDs or individual activity timestamps are added.

No migration is needed. Generate OpenAPI/client contracts with the API change and
update the data-model/API/UX descriptions, sprint, changelog and traceability.

## Acceptance and rollback

Verify local-midnight boundaries, inclusive first/last dates, duplicate mappings,
old/out-of-window dates, empty and all-seven-day windows, explicit timezone semantics,
naive/future rejection and strict DTO bounds. Integration must verify zero/one-day
progress, repeat-read immutability, cross-subject/learner/consent isolation, all three
unfinished diagnostic outcomes and web/WhatsApp parity. Preserve existing replay-call
budgets and mastery fields. No academic calibration is claimed from these tests.

Browser acceptance covers neutral zero and positive activity, incomplete-diagnostic
sealing, older-server absence, reload/offline, keyboard/axe and 320-pixel layout across
three engines. Verify lint/types/contracts/build, relevant integration/unit, full
hosted regression, security/images/service smoke and unchanged load thresholds before
claiming accepted implementation. Keep Docker services running for visual review.
Physical/branded-browser and production acceptance remain separate gates.

Rollback removes/hides the additive projection/card while preserving all original
evidence and API compatibility. No learner history or persistence is rewritten.
