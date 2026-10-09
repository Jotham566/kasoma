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

## Answer-protection format under implementation

The internal envelope uses the existing IdentityService authenticated encryption
interface. Its encrypted, versioned body binds learner, attempt, session-item,
item-version and rubric-version IDs to the exact response. ADR-044 requires the rubric
ID to equal its owning item-version ID. Validate that binding before releasing text;
reject unknown/noncanonical formats, duplicate fields, malformed input, ciphertext
corruption and cross-record replay with closed errors. Bound plaintext envelopes at
16 KiB and ASCII ciphertext at 24 KiB, accommodating the 2,000-character input limit
including four-byte Unicode and JSON escapes. These are format limits, not retention
or academic policies. The caller must still enforce authorization before decryption.

The proposed database representation is an encrypted response within the existing
immutable attempt, preserving its exact-record ATTEMPT hold and ownership. Migration
0013 currently rejects that response format; migration 0023 prevents its assignment.
Both remain unchanged during format verification. Update structured-response checks,
attempt guards and export decryption together with durable job/receipt integration;
never allow the current generic export projection to disclose ciphertext or raw rubric
material as a learner response. New grading jobs and audit evidence still require
separate inventory/hold/retention treatment. No new table or persisted answer is added
by the format component alone.

## Durable-work transition policy

A grading command gets at most one model-execution claim. Redelivered broker tasks
may claim only QUEUED work; they must not renew a RUNNING lease or restart the
three-request/one-repair budget. A crash after dispatch may leave model usage unknown.
Conservatively expire that claim to neutral fallback instead of assuming no calls
occurred and dispatching again. The learner can follow the reviewed equivalent or
independent review path; resubmitting the same idempotency key remains the same attempt.

The internal transition component bounds queue age at five minutes and a claim at
30 seconds, further capped by the absolute queue deadline. These are local failure
recovery ceilings, not a change to model-call budgets or latency SLOs. The worker's
hard execution limit must expire before the lease. At the deadline, stale workers
cannot publish. Terminal replays preserve the original timestamp and outcome; a
conflicting outcome is rejected. Persist each transition atomically under the attempt/
command lock and preserve immutable transition evidence with privacy/hold coverage.

The transition function's GRADED outcome is not academic or ownership authorization.
The publication transaction must independently recheck consent, content, calibrated
band, validation and audit-disablement state and store grade/mastery atomically. The
current component has no database adapter, broker registration or learner delivery.
Those remain the next integration work; transition tests do not establish durable
queue, concurrency, model execution or application acceptance.
