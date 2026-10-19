# ADR-061: Retention-aware synthetic learner account erasure

Date: 19 October 2026
Status: Proposed — no implementation or execution approval
Owners: Product/technical owner; privacy/safeguarding and academic release owners
Requirements: FR-ID-003/005/006, FR-GRD-003/004/005, FR-WA-006, FR-OPS-003,
BR-010, NFR-SEC-002, NFR-OBS-001, NFR-MNT-001

## Context and requested decision

The [readiness assessment](../../implementation/E8_ERASURE_TRANSFORM_READINESS.md)
and [69-table source inventory](../../implementation/E8_ERASURE_SOURCE_INVENTORY.md)
identify immutable learning records, finite legal preservation, shared grading authority
and required identity references. Neither a changed UUID nor an empty preview is proof
of erasure or anonymity. ADR-057 excludes contacts/message bodies; ADR-060 excludes
account erasure and pending DELETE completion. Their approvals do not extend here.

The coding contract requires explicit human approval for destructive migrations and
changes affecting privacy. This proposal requests **bounded synthetic implementation**
of the following lifecycle, including the new preservation and custody permissions
specified below. It does not request processing real data, executing on the normal
Docker review database, enabling normal short-text scoring, or approving production.
Approval of this decision would authorize implementation and isolated synthetic tests,
not assert legal sufficiency, academic calibration or successful application acceptance.

## Recommendation and alternatives

1. Recommended: delete eligible owned learning records; retain only exact lawful
   originals/dependencies or explicitly authorized encrypted preservation; use a
   minimized disabled identity anchor while lawful references exist. Do not create a
   de-identified learning warehouse or claim the retained linkage is anonymous.
2. Retain pseudonymized learning history: rejected as the default. It introduces a
   new retained dataset and requires an independent re-identification/retention decision.
3. Cascading account deletion or a trigger-bypass setting: rejected. Either can destroy
   required evidence, other people's provenance or operational safety barriers.
4. Keep requests pending indefinitely: rejected as fulfillment. Unsupported cases may
   remain visibly blocked for review, but cannot be represented as completed.

## Explicit specification change being proposed

The [data model section 10](../../specifications/03_Domain_and_Data_Model.md) describes
anonymization through a non-reversible replacement identity. ADR-029 rejects treating
changed IDs as proof of anonymity, and SRD BR-010 permits removal or anonymization of
personal linkage while retaining only permitted aggregate evidence. No approved
re-identification review authorizes a retained learning aggregate today.

This proposal therefore explicitly requests replacing that data-model transform with
whole-row removal of eligible owned learning data in this lane. It retains no new
aggregate; it does not redefine a disabled reference as anonymous. If approved, this
higher-priority ADR governs that narrow conflict and the data-model text must be updated
alongside implementation. Until approval, do not silently choose either transform.
Existing append-only grading/override rules remain unchanged for ordinary operations;
only the proposed restricted retention-aware erasure capability could remove originals.

## Scope, activation and ownership

Implement in the existing modular monolith, PostgreSQL and Celery stack. Creation and
execution switches default false. Independently refuse the ordinary review public
schema and non-development/provider profiles. Explicitly provision an owned isolated
synthetic database/schema; no switch, environment variable or request body can turn a
normal review database into an authorized erasure target. Fixtures use fake providers.

Only the current independent, recently OTP-authenticated ADMIN claimant of a pending
verified DELETE request may authorize that exact request. Input is affirmative
confirmation, a server-issued version-bound plan reference, and an opaque decision
reference; request UUID and authenticated case determine the subject. No caller-supplied
subject, SQL, table, cutoff, completion time or retention override is accepted. Exact
UUID-key retry binding rechecks current role, authentication, ownership and plan state.
A stale inventory/policy/source version conflicts and requires a new reviewed plan.

A subject's learner ownership follows the explicit relationships in the disposition
manifest. Shared content/curriculum and another learner's records are never owned just
because the subject authored, reviewed or administered them. Genuine staff provenance
or ambiguous third-party/embedded references blocks this first automatic execution
lane before closure. A learner's original flag report/history/receipt alone is not
staff activity. Staff/representative/closed-account support fulfillment remains required
work, not an accepted exception to the complete MVP/privacy obligation.

## Durable lifecycle and early processing stop

Add an immutable database-clock `closed_at` to the identity and one execution record
per authorized request. An identity with closed_at cannot be reactivated or reused by
an old token, verification, link code, staff provisioning or worker. Keep existing
ACTIVE/DISABLED values; closure sets DISABLED. Never backfill a fictional closure date.

Internal phases: AUTHORIZED, BARRIER_APPLIED, PRESERVING, REMOVING, VERIFYING,
COMPLETED; retryable FAILED and explicit BLOCKED states retain the last durable phase.
A closed identity remains closed after a failure. No manual mark-complete/force/skip
endpoint exists. Before the barrier, revalidate the exact source/preservation plan,
true staff provenance and all prerequisites; an advisory preview is insufficient.

At actual processing start, atomically persist the closure barrier, making all sessions
and link codes unusable immediately, stopping new learning/model work and channel
delivery, and making queued work unable to publish. Physical revocation/cancellation
row updates then run in bounded batches; no unbounded all-history UPDATE is required. Apply compatible identity/channel/source locks. STOP/unlink
remain usable operational privacy barriers; a preservation decision must not freeze a
usable credential, delivery address or resumable conversation. Revocation is prompt;
physical row removal is subsequently bounded. Cancelled jobs cannot recreate records.

Drain pending EXPORT work through its existing verified lifecycle and copy cleanup
before authorizing closure; never mark an unfinished EXPORT completed or delete a
cleanup locator. Recheck this condition under the barrier lock. A concurrent newly
accepted export either precedes the barrier and blocks it, or is refused after closure.
No post-closure export generation, model publication or outbound dispatch may commit.

Before removing login identifiers, keep their current lookup ownership while the
closed-user barrier rejects verification and new OTP issuance for those identifiers
using existing generic responses. Serialize identifier lookup/verification with closure.
Let pre-barrier unbound challenges expire under their existing at-most-ten-minute
window; do not delete or claim them solely by hash. Do not remove identifiers until
that window is conclusively elapsed under database time. This prevents an old unbound
challenge being mistaken for fresh registration once its identifier row disappears.
A malformed future window blocks removal. Afterwards a genuinely fresh verification
may create a new empty identity, never reconnect to erased history or reactivate the
closed UUID. This bounded credential-drain gate is not the inactive-account grace
period or a promised data-request completion deadline.

## Exact disposition manifest

The [implementation manifest](../../implementation/E8_ERASURE_DISPOSITION_PROPOSAL.md)
is part of this proposed decision. It enumerates all 69 existing tables, exact ownership
paths and whole-row versus field transforms. Inventory unknowns, new columns/payload
versions or malformed/cross-owner dependencies fail closed. SQL constraints remain
active. Never infer permission from a COUNT limit, absence of an FK or expired hold.

Eligible learning records are removed, not shuffled to a replacement user. An exact
hold or approved retention root keeps only its necessary source/dependency closure;
no sibling session items, unrelated grades or whole-account history is retained merely
because one record is held. Held originals are not rewritten. Retention dependencies
are identified explicitly and expire when their last lawful root ends, not on a new
invented six-year clock. Original retained records remain confidential/linkable.

Consent/material administrative evidence keeps its existing closure/withdrawal rule;
request evidence keeps completion plus six calendar years; flags keep resolution plus
24 calendar months. Unresolved flags have no fabricated resolution deadline. Completed
EXPORT retirement stays within ADR-060. Security-batch audit stays a 12-month class;
unknown audit classifications block classification-dependent removal rather than
silently selecting a longer or shorter schedule. No inactive-account 30-day grace is
repurposed as a rights-request processing deadline.

## Complete exact-record preservation within this lane

Keep existing 19 original/snapshot hold kinds and their meaning. Add a **closed source
registry**, not arbitrary-table SQL, for currently uncovered owned identity/profile/learning projections, identity events,
accountability originals, channel mutation receipts and exact live channel evidence. Canonical
keys are the actual typed primary key or existing source UUID plus revision/version;
composite-key sources use strict typed components and an opaque generated source
reference returned only after case ownership validation. Do not expose receipt keys,
contact/hash lookups or permit account-wide/table-wide preservation.

For immutable records, a new exact hold retains the original and necessary dependencies
under compatible source locks. For mutable projections/live channel state, capture one
version only into a separate encrypted evidence body, with immutable minimized capture
metadata and an exact finite decision. No automatic history, bulk backfill or recapture
on retry. Missing, changed, cleared, unbound or cross-owner sources fail closed.

**New privacy choice requiring this approval:** exact live channel evidence may preserve
already-stored profile fields (including name/date of birth), encrypted contacts
and parsed learner replies, beyond ADR-057's minimized allowlist. The manifest specifies the exact fields. This is extra retained personal
material, not anonymous metadata or a raw-webhook archive. Arbitrary learner text may
itself contain personal information or secrets; encryption and strict non-disclosure
are mandatory, and no claim of content-level sanitization is made. Never capture OTP,
link-code material, access/refresh credentials, encryption keys or general raw webhooks.
A decision requiring excluded material is visibly unsupported; do not fabricate evidence.
Capture/registration occurs only when that exact decision is created, before erasure
mutates its source. Authorizing erasure does not create a blanket preservation copy.
The closure transaction rechecks all already-authorized captures and any source changes;
a concurrent new decision either commits with preserved evidence or safely conflicts.

Use authenticated encryption under a separate purpose and binding containing case,
subject, source kind/key/version and snapshot UUID. Source ciphertext is additionally
wrapped; no plaintext/hashes/body in logs, queues, metrics or audit. Snapshot bodies
have no delivery/authentication/model/resume consumer or payload-reading API. Existing
learner exports exclude internal preservation. Capture and hold/audit commit atomically.

Body retention ends after the last exact active decision releases/expires. Bounded
cleanup deletes bodies while retaining only the existing six-year case accountability
metadata. Release never deletes the source or changes an unrelated hold. Capture of
contacts/replies never extends their operational lifetime. This is not authorization
for production forensic retrieval or disclosure; those need separate reviewed access.

## Shared grading authority

Keep lifetime publication/review counters and all original ordinals monotonic. Before
removing an owned completed short-text review, permanently disable its affected band
under the existing exclusive band lock with a closed ERASURE_EVIDENCE_REMOVED reason.
Do the same where removing publication/audit evidence would invalidate that band's
review coverage. An already disabled band stays disabled; retain its existing earlier
critical/academic reason and record the erasure effect separately in minimized audit.

Do not recompute a more favorable rolling window, decrement counters, fill gaps,
invent reviews, change thresholds or automatically re-enable/recalibrate. A fresh
academic-approved band may later restore availability through the normal calibration
process. This sacrifices that band's automatic-scoring availability rather than claiming
incomplete quality evidence remains valid. Deterministic grading is unaffected; normal
short-text scoring stays disabled. No extra per-learner quality ledger is retained.

## Post-completion custody and finite accountability

**New permission requiring this approval:** after DELETE completion, allow the original
independent claimant with current ADMIN and recent OTP to list/release exact existing
holds and create a new finite hold **only on an existing retained source of that same
case**, with an explicit new authorized decision. Preserve original review, subject,
completion and deadline; no reopening, reassignment, evidence retrieval, recapture of
removed history or general closed-account support permission. Revoked/unavailable
claimants leave a visible operational escalation; no silent substitute claimant.

A new preservation decision cannot resurrect disposed material. After the original
case's six-year deadline, a case exists only for an active exact hold or necessary
structural dependency. New decisions then require a still-active decision on that
same source; no creation during a cleanup gap to revive otherwise expired evidence.
A disposable snapshot body additionally requires an existing active exact decision at
new-decision time even before that deadline; a cleanup gap never grants recapture or
revival authority. No automatic extension occurs. The original six-year deadline never moves. Hold and
capture metadata outlive that deadline only while needed for an active exact decision
and its necessary accountability chain; dispose when the last such dependency ends.
This proposed finite exception/custody rule must be explicit, not a new six-year clock
silently attached to every later staff action. Real-data legal sufficiency remains open.

Retire due unheld consent, material audit, resolved flags, DELETE accountability,
preservation metadata and execution records in bounded dependency order. An exact
held leaf retains its required parent, not siblings. Remove the disabled user anchor
only after all lawful references and finite execution/accountability dependencies
have retired. A still-referenced anchor is minimized and monitored, not labelled
anonymous or assigned an indefinite retention period. Removed retry keys have no
permanent tombstones; current rights intake must never resurrect an old identity.

## Restricted execution and failure behavior

Use a dedicated NOLOGIN owner and separately provisioned EXECUTE-only maintenance
login. Fixed-search-path SECURITY DEFINER functions accept only authorized durable job
identity, never arbitrary source/cutoff/SQL. Independent SQL guards validate activation,
isolated scope, policy version, ownership, closure phase, due dates and active exact
holds using clock_timestamp(). Revoke PUBLIC execution. API, grading and ordinary
worker logins cannot DELETE protected records, assume the owner or set a bypass GUC.
No CASCADE, DROP OWNED, general DELETE grants or audit suppression.

Use at most 100 removals / 200 examined records per transaction, a five-second cooperative
budget and database statement/lock timeouts. Stable cursors/wrap prevent held prefixes
starving eligible siblings. Durable state is PostgreSQL truth; Redis loss cannot lose
work. Clear per-record cursors on terminal completion; keep only minimized policy,
phase/time/count/reason evidence under the parent deadline, not a new deleted-ID ledger.

Transactions atomically commit each bounded mutation, phase/cursor and minimized batch
audit. Never catch a database failure and return partial clearance. Replays recover
committed progress; crash/timeout rolls back the current batch. Audit includes fixed
operation/policy, correlation UUID, time and counts/categories, without source payloads,
contacts, credential/hash values or removed source-ID lists. Failure health is count-only;
case-authorized status may show phase and fixed blocker codes, never source bodies.

Learner-facing existing request status stays IN_REVIEW until actual verification passes.
Administrator execution status distinguishes blocked/failed work from completion. Use
accessible confirmation, retry and stale-plan states; generate contracts from the API.
Closed accounts do not regain login to check status. Verified support/representative
access remains a separate required design; do not invent identity-document uploads.

## Proposed persistence and API boundary

Add account_erasure_plans (case FK, opaque plan UUID, policy/manifest version,
server-derived keyed inventory/version fingerprint, observed_at and expires_at). Plans
last at most ten minutes under database time and retain no payload/contact/credential
copies. Authorization transfers only plan reference/version into the job, not a FK
that prevents finite plan expiry. Recompute validity under closure locks; a fresh plan
does not grandfather stale roles, holds or source changes.

Add account_erasure_jobs (case primary key/FK, subject FK, policy/manifest version,
immutable authorized_by/decision/authorized_at, phase, fixed blocker/failure code,
closure/completion timestamps, bounded counters and private stable cursors). Its terminal
accountability deadline is the parent case deadline; clear source cursors at completion.
No free-text operator notes or duplicate contact/answer fields are collected.

Add erasure_source_refs for the closed registry (opaque UUID, case/subject, source kind,
private typed primary-key components, observed version and capture time); hold original
sources through an explicit OWNED_SOURCE target or bind the exact encrypted body.
Private source keys are accessible only to the narrow resolver/guard capability, never
returned from an API, logged or copied into aggregate audit. Body binding repeats the
opaque reference/version and policy, rather than exposing private retry keys.
Clear private source-key components one-way after the exact original source and its
active decisions no longer need resolution; keep only minimized capture accountability.
Never use the private map to retain removed receipt keys as a replacement retry ledger.
Add erasure_preservation_bodies (reference PK/FK, authenticated encrypted payload only).
Use existing legal_holds for finite decisions and extend explicit exact ownership guards;
metadata/dependency cleanup follows the parent deadline and active-decision exception.
No generic dynamic-table function or unrestricted SELECT/DELETE capability is granted.

Expose proposed /api/v1/admin/data-requests/{request_id}/erasure-plan (GET),
/erasure (POST/GET), with bounded case-only status; no learner/subject search endpoint.
POST accepts plan UUID/version, opaque decision UUID and affirmative confirmation,
plus the existing idempotency header. Use the existing ADMIN/recent/independence rules
and an explicit erasure switch. Preserve the existing advisory preview contract unchanged.
Exact source inspection/preservation extends case-only hold controls with a discriminated
source-kind contract; inputs never contain SQL or user-selected table/column names.
Post-completion custody uses those same exact hold routes with the separately specified
permission predicates. Generate OpenAPI/client types alongside implementation.

## First vertical slice and implementation sequence after approval

1. Strict disposition/preservation format and execution contracts; additive lifecycle
   schema, SQL ownership/closure barriers and denial tests. End-to-end first slice:
   an independent ADMIN authorizes a reviewed isolated synthetic case, all sessions/
   linking/learning/dispatch stop, and restart resumes the same durable job. No case
   completion until every subsequent acceptance condition is implemented.
2. Complete exact original/mutable-source preservation, custody permissions and finite
   body disposal with concurrency/ownership/STOP tests and accessible controls.
3. Restricted bounded learning/identity removal, shared-band disablement and retained
   dependency handling; no normal-stack execution. Cover all manifest sources.
4. Finite consent/flag/material-audit/DELETE-accountability retirement, stub disposal,
   crash/recovery/large-history tests, generated contracts and count-only operations.
5. Full native/hosted engineering verification before promotion/acceptance. Keep review
   activation false. Staff provenance, representative support, logs/backups, genuine
   external academic/privacy/provider/production gates remain explicitly outstanding.

The entire first automatic lane is accepted only after all applicable manifest actions,
preservation and finite retirement pass. Partial phase delivery is not MVP fulfillment.

## Acceptance, recovery and rollback

Use synthetic data and fake providers only. Verify cross-owner/stale/revoked/self-review
and direct restricted-login bypass denials; actual source/hold/closure/refresh/OTP/
relink/STOP/dispatch/grading/export races; exact active/expired/multiple holds; immutable
originals; minimal dependency closure; no collateral learner/staff/content changes;
calendar-year/month boundaries; classification failures; bounded fair scanning; rollback,
crash after commit, replay and Redis loss. Exercise large histories without truncation.

Prove the first barrier is prompt and no later protected operation commits on the
closed identity. Prove removal of audit evidence cannot improve/re-enable a band.
Verify all new sources appear in advisory inventory and cannot disappear behind an
old policy/format version. Validate no new payload-reading endpoint, answer leakage,
secret/logging path or snapshot consumption by an operational worker.

Before destructive tests, create and restore a populated isolated synthetic backup,
verify held originals and restricted-role guards, run erasure, then restore into a
quarantined target. A durable external-to-the-restored-database closure checkpoint is
required to reapply committed closure/erasure before serving; the test controller keeps
this finite synthetic checkpoint outside the backup, containing only case/subject/policy
and phase references, protected and expired with case accountability. No normal-stack
backup is restored or modified. Loss/ambiguity of checkpoint leaves the restore offline.
Production PITR, external checkpoint storage/retention, 35-day backup expiry and RPO/RTO
need their separate provider/recovery approval; a SQL-only pass cannot close those gates.

Rollback disables authorization/execution and preserves closed identities, evidence,
holds and committed progress. Do not downgrade destructive history or restore deleted
records into a serving system. Repairs are forward migrations. Extend recovery/load
role lifecycle tooling for every new exact owned capability; never sweep existing roles,
volumes, images or caches. Run setup, clean/additive migrations, seed, lint/types,
contracts, unit/integration/browser, security/source/images, service smoke and recovery.
Publish exact source/run evidence and docs before claiming bounded acceptance.

## Approval record

Not approved. The owner must explicitly approve this bounded synthetic proposal,
including exact profile/contact/reply preservation, restricted destructive execution,
post-completion custody and affected-band disablement. Existing generic continue/commit
instructions do not silently supersede the specific ADR-057/060 exclusions. Any
unsupported requirement remains a gap; neither approval nor tests waive real-data,
legal/privacy/safeguarding, academic, provider, device, pilot or release acceptance.
