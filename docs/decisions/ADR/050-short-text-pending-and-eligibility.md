# ADR-050: Short-text pending outcomes, eligibility and neutral fallback

Date: 10 October 2026
Status: Proposed; contracts only, learner integration and acceptance pending
Requirements: FR-GRD-003/004/005, FR-MST-001, FR-ID-003/006, NFR-SEC-002

## Context and proposed decision

ADR-044 permits reviewed rubric authoring but explicitly excludes SHORT_TEXT from
learner assignment. ADR-040/041 validate and rehearse synthetic candidates without
academic eligibility. The current assessment transaction assumes immediate definitive
grading; immutable grades feed mastery. These constraints must be respected while
implementing the approved asynchronous short-text experience.

Introduce distinct pending and low-confidence result contracts. Neither admits a
score, points, confidence, rubric evidence, model output or error details. PENDING
provides a relative poll URL bound to its attempt ID. LOW_CONFIDENCE requires a typed
objective-equivalent or request-review action. A review action does not imply a review
has been submitted, assigned or completed. Services must authorize the action and
establish an owned equivalent session before returning its ID. Schema validity does
not establish ownership or academic suitability.

Bound submitted answers to 2,000 characters, matching the existing rehearsal limit;
reject whitespace-only answers, preserve exact text for evidence validation, and omit
text from representations and formatted validation errors. This is a resource limit,
not an academically approved response-length band. HTTP validation must continue to
use minimized error projection; never log Pydantic's raw input-bearing error objects.

## Complete integration required before enabling learner assignment

1. Pin reviewed item/rubric/context and versioned eligibility evidence. Scoring bands
   need held-out >=90% exact agreement, supported subject/topic/length/language/model/
   prompt versions, no material harmful subgroup error pattern and explicit enablement.
   The separate >=85% overall benchmark gate still applies. No synthetic test or
   self-reported confidence substitutes for academic approval.
2. Atomically persist the immutable attempt, encrypted answer, idempotent receipt and
   durable grading command. Keep unresolved workflow state separate from definitive
   immutable grades. Duplicate submissions replay the same attempt; retrying the
   command cannot create a second grade or mastery contribution.
3. Claim work with finite leases and hard execution bounds. Perform model work outside
   database locks; recheck consent, ownership, content status, privacy restrictions and
   the enabled band before publication. Use the existing two independent passes and
   one shared repair budget, with actual injection/safety/domain checks. Fake providers
   remain mandatory for automated tests. No external model call is authorized here.
4. Publish either a validated eligible definitive grade or neutral fallback. No pending,
   disabled-band, low-confidence or failed outcome may create mastery evidence. Select
   a reviewed objective equivalent or provide the independent review action; do not
   reuse a reassessment path that requires a prior definitive score without adapting
   its invariants. Preserve sealed diagnostic disclosures and shared channel state.
5. Audit at least 10% of automatic beta grades through blinded independent experts.
   Disable a band on rolling exact agreement below 90% or any critical error, including
   rechecking in-flight work. Version the rolling-window policy and obtain academic
   approval before production use; missing audit evidence is not a successful result.
6. Cover every new personal-data record in owned exports, exact-record legal holds,
   deletion inventory, retention and restricted database-role rules. Use additive
   migrations and forward recovery; retain protected immutable evidence. This proposal
   grants no destructive-migration or production-data authorization.
7. Update API/client schemas and web polling/resume/history/fallback flows together;
   preserve deterministic grading compatibility. Verify concurrency, crash/retry,
   consent withdrawal, retirement, band disablement, ciphertext handling, ownership,
   no-score/no-mastery fallback and all three browser engines before promotion.

## Alternatives and rollout

Making all grade fields optional would allow ambiguous or accidentally scored pending
responses. Storing low confidence as zero would misstate learning evidence. Mutating
existing grades would violate immutable-history rules. Separate typed results and
workflow state avoid those failures while allowing later definitive publication.

The first implementation adds only internal response/outcome contracts and validation
tests. Existing HTTP schemas, selectors, database guards, deterministic grades and
mastery remain unchanged. This proposal does not yet supersede ADR-044's disabled
assignment boundary. Acceptance requires the full integration above and recorded
verification; academic and production enablement remain separately approved.

Sources: [readiness assessment](../../implementation/E4_SHORT_TEXT_INTEGRATION_READINESS.md),
[API](../../specifications/04_API_and_Integration_Contract.md),
[AI guardrails](../../specifications/06_AI_RAG_and_Grading_Guardrails.md),
[production-pilot rules](../../specifications/16_Production_Pilot_Decisions.md).
