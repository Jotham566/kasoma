# ADR-026: Exact-set deterministic multiple-choice answers

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-GRD-001/005/007, FR-CNT-001/003/004/005, FR-REV-003/005,
FR-DIAG-004, FR-MST-001/003, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001

## Decision

Extend the reviewed content and shared assessment paths with MULTIPLE_CHOICE.
Retain the explicitly authored ALL_OR_NOTHING policy: selected IDs must exactly
match the pinned answer-key set. Award all maximum points or zero, without inferred
partial credit, negative marking or parsing correctness from prose. The grader version
is multiple-choice-set-v1. This implements SRD exact answer-key matching; it does not
change the existing academic policy or approve any production questions.

Content has 2–8 unique options with nonempty text and a nonempty correct_choice_ids
list drawn from those IDs. One or all options may be correct if independently reviewed
as academically appropriate. No key cardinality is disclosed to learners. Keys and
responses are sorted canonically; duplicate IDs are rejected, not silently removed.
The answer DTO is {type: MULTIPLE_CHOICE, choice_ids: [A, C]}; accept 1–8 unique
single-uppercase-letter IDs, rejecting IDs absent from the served item. Selection
order is irrelevant to grading, storage and idempotency fingerprints.

The learner response_spec contains only the MULTIPLE_CHOICE discriminator and options.
Checkbox players say “Select all that apply” and “Full credit requires every correct
option and no others.” Submission requires at least one selection. Existing
saved-attempt/retry, feedback, hint, worked-solution, flag, diagnostic seal, reassessment
and mastery controls apply. No future-item key, correct-count or option-level key hints
are disclosed. Diagnostic and practice use the same grader.

The staff editor supports 2–8 options and explicit key checkboxes; the reviewer preview
shows the entire key and exact-set policy. Single-choice and numeric fields must remain
empty when irrelevant, enforced again at publication. Existing approved versions and
historical grades/hashes are never backfilled or rewritten; missing new key fields
parse as an empty default for older formats. Corrections still require successor review.

## Persistence and compatibility

Add migration 0013 to extend the existing response JSON representation to a bounded,
canonical MULTIPLE_CHOICE object. Preserve legacy choice_id and numeric rows unchanged.
Database shape, assignment, format and option-membership guards reject invalid sets;
existing immutability, hint bindings and atomic grade/mastery/outbox constraints remain.
No provider or architecture replacement. Deploy new contracts, readers and players
together; after multiple-choice content exists, use forward fixes or keep compatible
readers. Do not downgrade by deleting learning evidence.

Synthetic opt-in fixture command and tests cover exact/permuted/subset/superset/wrong
sets, duplicate/unknown/empty inputs, publication/review, immutable pinned history,
response-type mismatch, concurrent/retry/rollback behavior, mastery replay, sealed
diagnostics, reassessment and browser authoring/recovery/keyboard/accessibility.
No model inference, Gemini, real learner data, cloud dependency or expert benchmark
acceptance is implied. Production content validity and release gates remain pending.

Browser checks run in two fresh isolated shards, retaining the unchanged peer OTP
limit. This is test isolation, not a change to production authentication policy.
