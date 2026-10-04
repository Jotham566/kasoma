# Short-text learner integration readiness

Reviewed 4 October 2026. Requirements: FR-GRD-003/004/005, FR-CNT-003/004,
FR-MST-001, FR-ID-003/006. This assessment grants no academic enablement.

## Current boundary

ADR-040 validates synthetic output and ADR-041 rehearses independent fake passes and bounded
repair. Neither is connected to learner routes, database grades or mastery. `DraftDocument`
supports only choice/multiple-choice/numeric. `GradeView` admits only definitive deterministic
results. `AssessmentService.view`, `grade` and `result`, and `mastery.record`, deserialize that
same contract. A LOW_CONFIDENCE result must not be disguised as a zero-point GradeView.

The specified `rubrics` and `rubric_criteria` entities do not yet exist. The rehearsal now requires
explicit criterion text, acceptable evidence, common errors and prohibited inference, in addition
to IDs/maxima. These remain original fixture material without academic approval or a persistence/
review workflow. Synthetic v2 prompt wording is not a benchmark-approved production prompt.

## Next complete learner slice

1. Add independently reviewed, versioned rubric/criterion persistence with acceptable evidence,
   common errors and prohibited inference; pin a rubric version to an immutable item version.
   Reuse author/reviewer separation, rights/mapping checks, retirement and audit controls.
2. Add an explicit short-text eligibility service. Require approved current item/rubric/context,
   supported subject/topic/language/length and versioned enablement evidence. Keep automatic scoring
   disabled until the frozen benchmark, calibrated bands and owner approvals exist.
3. Add encrypted bounded response persistence and an atomic idempotent grading command. Return a
   distinct pending/neutral result without points or predicted scores. Preserve the attempt through
   timeouts, retry exhaustion, provider failures and consent withdrawal.
4. Add grade retrieval/revision/history rendering for pending and LOW_CONFIDENCE. Route fallback to
   a reviewed objective equivalent or independent review, with approved neutral wording. No failed
   or unresolved model candidate may create mastery evidence or expose hidden rubrics before answer.
5. Add worker eligibility rechecks, budget/repair controls, privacy-safe gateway provenance and
   disabled-by-default adapter selection. Test duplicate/concurrent commands, rollback, content
   retirement, consent changes and exception redaction using FakeModelProvider.
6. Update owned exports, deletion inventory/holds and retention coverage for each new personal-data
   record; preserve existing immutable attempts/grades and forward recovery. Generate HTTP/client
   schemas and test browser pending/retry/fallback states before promotion.

Do not repurpose immutable deterministic grades, silently broaden selection, use model confidence
as calibration, or manufacture a passing academic report. No destructive migration is authorized
by this plan. A future migration must be additive or have its explicitly approved recovery plan.

## External dependencies and safe parallel work

The existing RELEASE-01 question in the [release register](RELEASE_GATES.md) already requests
academic mappings, rights and frozen benchmark evidence. No answer has been recorded; do not
repeat the question or infer approval. Rubric/context authoring infrastructure and synthetic tests
can proceed, while academic truth, production eligibility and real learner use remain gated.

NFR-REL-002 recovery preparation is independent. A safe local drill must create its own uniquely
named source and destination databases, migrate/seed only synthetic fixtures, back up that isolated
source, restore to the fresh destination, compare rows/schema and verify immutable/ownership
guards. It must never restore over or dump the configured developer database, reset Docker
volumes, or drop a database it did not create. Record elapsed time and cleanup failures separately.
Native execution currently requires restoration of the missing Docker installation; hosted CI can
verify isolated fixtures. A logical synthetic restore does not prove managed 35-day PITR, encryption,
production RPO ≤24 hours or RTO ≤8 hours; those remain Week 8/provider and pre-beta gates.

Sources: [domain model](../specifications/03_Domain_and_Data_Model.md),
[API](../specifications/04_API_and_Integration_Contract.md),
[AI guardrails](../specifications/06_AI_RAG_and_Grading_Guardrails.md),
[privacy](../specifications/09_Security_Privacy_and_Safeguarding.md),
[release acceptance](../specifications/10_Testing_Acceptance_and_Release.md).
