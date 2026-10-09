# Short-text learner integration readiness

Reviewed 10 October 2026. Requirements: FR-GRD-003/004/005, FR-CNT-003/004,
FR-MST-001, FR-ID-003/006. This assessment grants no academic enablement.

## Current boundary

ADR-040 validates synthetic output and ADR-041 rehearses independent fake passes and bounded
repair. Neither is connected to learner routes, database grades or mastery. ADR-044 adds SHORT_TEXT authoring/review to `DraftDocument`, while learner selection and
submission remain limited to choice/multiple-choice/numeric. `GradeView` admits only definitive deterministic
results. `AssessmentService.view`, `grade` and `result`, and `mastery.record`, deserialize that
same contract. A LOW_CONFIDENCE result must not be disguised as a zero-point GradeView.

Migration 0023 implements version-pinned `rubrics` and `rubric_criteria`, with independent content
review and SQL immutability/projection guards. Hosted acceptance passed in CI 37914864557; see
[the rubric report](E2_REVIEWED_RUBRICS_VERIFICATION.md). The rehearsal requires explicit criterion
text, acceptable evidence, common errors and prohibited inference, in addition to IDs/maxima.
Synthetic fixtures and v2 prompts remain without benchmark or production academic approval.

## Next complete learner slice

1. Build on the verified independently reviewed rubric/criterion persistence, including acceptable
   evidence, common errors and prohibited inference, pinned to immutable item versions. Preserve
   author/reviewer separation, rights/mapping checks, retirement and audit controls.
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

## Inspected implementation dependencies

- `services/assessment_contracts.py`: `SubmitAnswer` excludes short text; `GradeView`
  requires a definitive deterministic score and confidence 1. `AnsweredItem` embeds it.
  Add explicit pending/neutral projections without optional fields that admit a score
  in an unresolved outcome. Update session resume, polling and history consumers together.
- `services/assessment.py`: submission atomically creates the attempt, grade, receipt
  and mastery today. An asynchronous receipt must replay the original owned attempt
  safely while its outcome changes, without dispatching another grading job.
- `services/mastery.py`: only definitive grades may reach `record`; its current
  deserialization assumes `GradeView`. Pending, low-confidence and review-required
  attempts must contribute no zero score or synthetic mastery evidence.
- Migration 0004 and subsequent guards retain immutable attempts/grades; migration
  0006 binds mastery evidence to an existing grade. Keep unresolved workflow state
  separate from definitive immutable grades. Any new persistence must receive export,
  exact-record hold, retention and restricted-runtime-role coverage in the same slice.
- ADR-044's service and SQL assignment exclusions remain effective until their explicit
  replacement ADR and complete learner-path acceptance. Approved rubric authoring alone
  cannot bypass eligibility or authorize real automatic scores.
- `services/short_text_orchestration.py` remains a synthetic rehearsal, with a
  caller-supplied flag and a synchronous adapter boundary. It does not implement the
  required injection/safety/out-of-domain detectors or hard worker cancellation.
  Agreeing fake candidates are not an eligible learner grade.

## Calibration, beta audit and disablement gates

The Week 5 >=85% benchmark criterion and automatic-scoring >=90% exact agreement
criterion are separate. An enabled band must identify the approved subject/topic,
response length, language and model/prompt/configuration versions, with held-out
expert evidence and no material harmful subgroup error pattern. Self-reported model
confidence cannot stand in for that evidence.

Production-pilot specification section 7 also requires at least 10% of automatically
returned short-text grades to receive blinded expert audit during beta. Rolling exact
agreement below 90% or a critical error must automatically disable the affected band.
Implement audit assignment, independent expert access, minimized retained evidence,
rolling evaluation and atomic disablement with synthetic fixtures before enablement.
The affected band must be rechecked before publication, including jobs already in flight.
An unavailable or disabled band returns the neutral fallback without a mastery update.
No benchmark, subgroup approval, audit result or enabled production band is fabricated.
The rolling-window definition is not supplied by the cited rule: record the chosen
versioned policy and its rationale in the eligibility ADR and obtain academic approval
before production enablement; do not silently interpret missing evidence as agreement.

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
Native Docker and isolated logical recovery now work; current evidence includes 54 tables and
272 synthetic rows. See [recovery verification](E9_RECOVERY_VERIFICATION.md) and the current
sprint for subsequent runs. A logical synthetic restore does not prove managed 35-day PITR, encryption,
production RPO ≤24 hours or RTO ≤8 hours; those remain Week 8/provider and pre-beta gates.

Sources: [domain model](../specifications/03_Domain_and_Data_Model.md),
[API](../specifications/04_API_and_Integration_Contract.md),
[AI guardrails](../specifications/06_AI_RAG_and_Grading_Guardrails.md),
[privacy](../specifications/09_Security_Privacy_and_Safeguarding.md),
[release acceptance](../specifications/10_Testing_Acceptance_and_Release.md),
[production-pilot grading rule](../specifications/16_Production_Pilot_Decisions.md).

The [ADR-050 proposal](../decisions/ADR/050-short-text-pending-and-eligibility.md) now
records the full integration boundary. Internal pending/neutral contracts are under
verification; no generated HTTP contract changes or learner assignment are enabled.

Contract preparation verification: `make format lint test-unit openapi-check` passes
699 unit/contract and 35 tooling cases; OpenAPI/client remain unchanged. New tests reject
unsupported scores, confidence, hidden rubric/model/error fields and false mastery
claims; verify bounded exact-text preservation, a bound relative polling URL and a
required typed fallback. Log: `.local/short-text-contracts-checks.log`. Database, worker,
HTTP and browser acceptance remain pending; these contracts are not a deployed feature.

Answer-protection preparation uses the existing authenticated encryption interface and
an explicit five-ID envelope binding. The planned attempt response representation must
be coordinated with migration 0013's bounded-structure guard and the existing owned export
projection. Migration 0023's assignment exclusion remains unchanged. Format tests do not
prove persistence, export or legal-hold acceptance. Verification is in progress.

Answer-format verification now passes `make format lint test-unit openapi-check
security-source`: 730 unit/contract cases, including 31 new answer-protection cases,
and 35 tooling cases. Logs: `.local/short-text-answer-protection-final.log`. No HTTP
schema, database migration, provider call or running service changed in this preparation.
Next integrate durable grading and eligibility atomically with encrypted attempts,
owned export decryption and the full privacy inventory; do not relax assignment guards
until that path has complete acceptance evidence.

FR-GRD-003/004/005 and NFR-SEC-002: `services/short_text_workflow.py` adds the proposed
one-claim transition policy, inclusive queue/lease expiry, clock/state validation and
immutable terminal replay. A crashed claim cannot reset the global model-call budget.
Verification passes: `make format lint test-unit openapi-check security-source`,
including 747 unit/contract cases (17 new transitions) and 35 tooling checks. Log:
`.local/short-text-workflow-checks.log`. This is a transition component only; durable SQL locking,
worker wiring, eligibility, grade/mastery publication and privacy coverage are unimplemented.
