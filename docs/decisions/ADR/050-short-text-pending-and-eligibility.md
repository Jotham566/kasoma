# ADR-050: Short-text pending outcomes, eligibility and neutral fallback

Date: 10 October 2026
Status: Accepted for disabled synthetic engineering; actual learner enablement remains gated
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

### Proposed versioned calibration/audit policy

#### Next audit persistence boundary

The next slice must bind each automatic grade to its immutable band and allocate a
monotonic publication ordinal under that band's lock. Persist a separate aggregate
counter so future personal-data retention cannot reset sampling ordinals. Grade,
mastery evidence, publication binding, counter increment and any required audit
assignment must commit together; retries must reuse the original ordinal and audit.
Do not infer successful publication from a completed provider call or workflow state.

Audit review stores criterion points and closed critical-error categories, with the
reviewer's identity and completion time retained as restricted accountability evidence.
It references the existing encrypted attempt and pinned rubric rather than copying
learner answers into another table. Blinded expert projections must omit learner
identity, model points/confidence/feedback, prior audit decisions and sampling ordinals.
Use existing independent staff-review constraints, including excluding the item author;
review ownership and authorization must be enforced by the service and SQL constraints.

An immutable completed review updates the completed count and rolling window under the
same band lock. Persist any critical-error/below-threshold disablement in that transaction,
so publication cannot race past an already committed disablement. Concurrent reviews,
claims, duplicates, rollback and stale publication require PostgreSQL tests. Review
does not mutate the original grade; correction/contest behavior needs its additive
contract and separate acceptance.

These new per-grade records require owned minimized export projection, diagnostic
sealing, deletion-impact inventory, exact-record legal holds, and preservation of
attempt/rubric linkage before runtime wiring. Holding an immutable review must not
freeze unrelated work or the entire account. Apply the existing privacy retention
schedule; do not use audit accountability as permission to retain raw answers forever.
Publication/audit persistence is under verification; expert projections remain unimplemented. This design
does not broaden enabled answer formats or authorize academic/production use.

Durable preparation: migration 0028 stores immutable global report projections and
scope bindings, with disabled initial state and exact SQL-generated history. Migration
0029 adds a composite topic/subject FK to retain scope through future curriculum updates;
insertion-time validation alone proved insufficient in a regression test. Activation
requires a separately controlled timestamp column; worker grants cover only disablement
fields and history insertion. No activation application command or genuine approval
resolver exists yet. A band may activate once and disable once; disablement cannot be
reset by updating report metadata or the feature flag. A future approved replacement
must resolve new authority evidence, not merely allocate new IDs. Runtime publication
must hold the refreshed band row lock until grade/mastery/audit commit. Metadata contains
no learner answers or reviewer identities; per-grade audits still require their own
privacy/hold/retention design and acceptance. See
[storage evidence](../../implementation/E4_BAND_STORAGE_VERIFICATION.md).

`short-text-calibration-v1` binds subject, topic, English language, response-length
range and model/prompt/configuration versions to an immutable report digest, frozen
benchmark identifier and approval reference. Exact integer counts enforce the separate
85% overall within-tolerance and 90% held-out exact-agreement requirements. An approved
subgroup review and zero critical errors are required. No default enabled band exists;
schema-valid identifiers are not evidence that an approval exists. Persistence must
resolve the actual authorized report and approval before passing a projection to the gate.

Propose the latest 100 completed expert audits per band as the rolling window, ordered
by completion. Until 100 exist, use all completed audits. This is a bounded, responsive
engineering policy requiring academic approval before production, not an already
approved statistical sample-size claim. Below 90% exact agreement or any critical error
must persist sticky band disablement; later good results or window eviction cannot
silently re-enable it. A newly approved report/configuration is required for enablement.
Pending assignments never count as completed or correct. Stored completed counts must
agree with the projected window, preventing missing reviews from becoming an empty,
implicitly passing window. No completed audits initially means no observed rolling
agreement; it does not replace the required approved held-out calibration.

Assign ordinal 1 and every tenth subsequent published grade to blinded expert audit.
This yields `ceil(N/10)` assignments in every publication prefix, satisfying at least
10% even for a partial batch. Allocate ordinal/assignment atomically with grade/mastery
publication under the band lock; expose neither ordinal nor model scores to the blinded
expert. This systematic sample has no claim of random representativeness; the academic
approval must cover this policy or a revised, versioned sampling rule before beta.

`services/short_text_eligibility.py` implements this necessary candidate gate only.
It neither authenticates an approval, writes an audit/grade, disables a database band,
nor authorizes learner delivery. Durable report/state/audit persistence, independent
expert access, exact-record privacy coverage and worker publication remain mandatory.
Recheck current locked band/audit state before dispatch and publication; consent,
approved content, injection/safety/domain checks and dual-pass validation are separate.

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

## Durable storage preparation

Migration 0026 adds assessment_grading_work and immutable assessment_grading_history.
Work binds to an existing attempt and original correlation ID; its revision and
triggered exact snapshots track QUEUED, one RUNNING claim, and one terminal outcome.
SQL enforces lease/time bounds, forbids claim renewal or terminal rewriting, requires
an actual grade for GRADED, and forbids grade insertion alongside an unresolved work
state at transaction commit. Concurrent claims use row locks with SKIP LOCKED; queue
replay locks the existing attempt, preserving the original command. Expiry is bounded
to at most 100 rows per transaction. Model dispatch must occur only after claim commit.

This is a format-independent storage substrate. The learner-facing service must still
validate short-text format/eligibility before enqueueing and authorize disclosure.
The substrate tests use valid synthetic ungraded objective attempts to exercise SQL
without bypassing ADR-044's short-text assignment guard. They are not short-text
submission or academic acceptance. No route, selector, assignment guard or worker
registration changes in this preparation. Inventory, owned exports, exact-record
holds and restricted-role coverage must be completed before runtime integration.
Deletion is currently refused to preserve evidence; the approved learning-data
retention policy still applies and a tested processor remains required.

The restricted-runtime test now grants INSERT/UPDATE on current work and INSERT on
history, with no history UPDATE/DELETE or schema privileges. Attempt row locking needs
UPDATE on one column: grant only immutable attempts.id and retain the trigger that
rejects edits. The real restricted-login test verifies queue/claim/neutral completion,
history write denial and inability to change attempt IDs. This does not grant worker
access to unreviewed grades or replace the future publication checks.

## Exact history preservation

Migration 0027 extends the existing independently reviewed hold workflow with
GRADING_HISTORY, identified by the immutable history row UUID. Ownership is derived
through the referenced attempt and checked in both service and SQL. The current work
row is a projection of these exact snapshots. Holding one snapshot preserves its
state and linkage while later transitions append new records; it does not freeze the
worker or create an account-wide hold. Existing history immutability survives hold
release. The foreign keys and current no-delete guards preserve the referenced work
and attempt; future retention processing must retain the context of held snapshots
before removing any projection or linkage. No deletion processor is enabled here.

## Publication ledger preparation

Migrations 0030/0031 implement publication bindings and audit assignments. The SQL
trigger locks the band, checks enabled state and grade scope, allocates the next ordinal,
creates a required audit for ordinals 1, 11, 21 and advances the aggregate counter in
one transaction. Counters cannot reset; duplicate service calls return the original
binding, including after disablement. A binding to another band is rejected.

The publication service is internal and does not establish grading authorization.
The future worker must call it inside the same transaction as grade/mastery creation
and current consent/content/eligibility checks. Objective fixtures verify this substrate
without bypassing the existing SHORT_TEXT assignment exclusion. No learner format is
enabled. Owned projection, exact holds and deletion inventory cover the new personal
records; preservation still needs the existing future retention processor.

## Definitive result representation under integration

The internal rubric result is distinct from deterministic `GradeView` and unresolved
outcomes. It pins rubric/item identity and uses the existing validated criterion-result
and authored-feedback shapes. Integer criterion totals must equal awarded points and
score must equal awarded/possible points; confidence is finite and never grants
eligibility. Do not place a zero-grade placeholder into unresolved workflows.

Criterion evidence contains confidential answer excerpts. The result formatter hides
these from representations, rechecks exact answer/context evidence, and grants no
persistence/disclosure authorization. The full path must encrypt answer-bearing result
material at rest and expose it only through current ownership/consent and diagnostic
sealing checks. No plaintext result writer or learner route is introduced by the
intermediate contract. Existing assignment exclusions remain until complete acceptance.

## Candidate cohesive implementation — 18 October 2026

Draft migration 0032 pins an assignment to a calibration band and permits only a
bounded encrypted SHORT_TEXT response, with generated rubric foreign keys. An enabled,
matching band and approved pinned rubric are necessary SQL conditions. Application
selection additionally requires a disabled-by-default flag and a trusted report authority;
the normal application has no report authority. Test authority exists only in isolated
synthetic fixtures. This candidate supersedes ADR-044's unconditional SQL exclusion only
on its working branch; complete learner-path acceptance is required before promotion.

The answer-bearing result is authenticated encrypted material bound to the five answer
identities plus band ID. A confidential quote-free summary retains points/confidence,
criterion points and version references for SQL consistency and mastery. Decryption
checks exact binding and summary equality. Use existing identity encryption; engineering
ceilings are 128 KiB plaintext and 192 KiB ASCII ciphertext, with failures closed rather
than truncating. Existing attempt/grade holds preserve their whole encrypted records.
Owned exports decrypt authorized answers/results and exclude internal band IDs/ciphertext.

Submission atomically commits attempt, receipt, work and `attempt.saved`; neutral state
transitions append `attempt.grade_unavailable` without points. A successful publication
requires matching rubric points, grade, terminal work, mastery and audit in the same
transaction. No unresolved outcome may use the deterministic grade placeholder.

The one-job task inherits the 15/20-second worker limits beneath the 30-second lease.
A bounded wake-up follows commit and periodic five-second drain recovers wake-up failure.
Every model pass rechecks current authority in a short transaction, releases locks,
then calls the provider within the remaining global five-second rehearsal budget.
The current implementation supports FakeModelProvider only and defaults to unavailable
report/safety gates. Human approvals, real detectors/adapters and independent blinded
expert review are not invented by these defaults. Rolling review integration remains
mandatory before scoring is enabled for actual learner use.

## Proposed staged adoption boundary

The cohesive branch may be accepted as a disabled synthetic engineering slice after
complete backend/browser, migration/recovery, restricted-login, contracts and security
verification. This does not accept the full automatic-grading capability. It replaces
ADR-044's unconditional SQL assignment exclusion with pinned-band constraints while
preserving the normal application's effective exclusion: flag false, no report authority,
no safety authority, fake-only processor and synthetic-only context/selection. No public
activation command or seeded enabled band is introduced. Worker grants cannot activate
reports. Test authorities are confined to isolated, explicitly synthetic fixtures.

All seven complete-integration requirements above remain gates before any actual
learner enablement. In particular, absent independent review/rolling disablement is an
unfinished feature, not an approved exemption; no real report, reviewer qualification,
safety detector or model adapter is inferred from tests. The earlier candidate statement
requiring complete acceptance before promotion applies to the complete enabled learner
path. Disabled-stage acceptance must explicitly state its narrower boundary and evidence.

Grading dispatch uses its own `grading` queue as required by production decision 16;
the local worker consumes it alongside existing operations/imports/messaging queues.
Beat and immediate wake-ups route explicitly, without mixing export-worker execution.
The owned feedback endpoint adds an account-bound engineering ceiling of 120 reads per
minute. Automatic web polling stops after twelve checks, three seconds apart, with
one request in flight; manual retry and durable result ownership remain unchanged.

## Disabled-stage acceptance — 18 October 2026

Commit `853f80af293ba5e78538534c7218beba7f50074e` passes complete hosted verification
[39143803289](https://github.com/Jotham566/kasoma/actions/runs/39143803289), including
backend, three-engine browser journeys, migration/recovery, restricted login, security,
rebuilt-image scanning and container smoke. It is promoted to main. This accepts only
the disabled synthetic stage described above under delegated implementation discretion.
No real calibration, reviewer qualification, privacy/safety approval or learner scoring
is accepted. Independent blinded review, rolling disablement and actual release-unit
audit coverage remain work before enablement; the next proposed decision records the
sampling edge case without rewriting this slice's immutable evidence.
