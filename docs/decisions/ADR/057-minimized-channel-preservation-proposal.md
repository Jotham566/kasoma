# ADR-057: Minimized channel preservation snapshots — proposal

Date: 19 October 2026
Status: Proposed; explicit privacy/product approval required before implementation
Owners: Product, privacy/safeguarding and technical owners; approval not recorded
Requirements: FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

## Context

[ADR-030](030-record-legal-holds.md) holds exact original records.
[ADR-055](055-terminal-channel-receipt-holds.md) extends that mechanism only to owned,
already-minimized terminal receipts. A live operational row cannot simply be frozen:
STOP/unlink must clear contacts and conversation state, authentication material must
expire, and a link row may represent a later revision or another sender.
[Channel readiness](../../implementation/E8_CHANNEL_HOLD_READINESS.md) requires a
separate decision. No implementation or approval is implied by this proposal.

The source-of-truth change protocol requires human approval before changing security,
data or learner-visible behavior. A snapshot changes the meaning of preservation from
an original-row guard to a captured evidence object, even if implementation is additive.
An engineering ADR cannot decide legal sufficiency or authorize extra personal data.

## Proposed first slice

OPEN-QUESTION PRESERVATION-01: approve or revise a narrowly minimized, encrypted,
immutable snapshot captured only for an already-authorized exact-record preservation
decision. Recommend this over continuous version history because it copies nothing
until a specific decision exists. This is a proposal for engineering implementation
with synthetic data, not permission for real-data processing or account erasure.

Start with an owned channel-link revision and an owned conversation revision, not raw
message bodies or authentication evidence. The operator names the existing source UUID
and its observed revision/version; mismatches fail closed rather than following a relink.
A conversation has no independent source UUID: identify its actual link UUID plus
link_revision and exact state version, never treat that composite as a global record ID.
The new snapshot gets its own UUID after validated capture. It is visibly a snapshot,
not a replacement CHANNEL_INBOUND_RECEIPT or original-record hold.

Proposed encrypted field allowlists, subject to owner review:

| Source | Captured evidence | Explicitly excluded |
| --- | --- | --- |
| Channel link revision | Source link UUID, revision, status, linked_at, opted_out_at, updated_at | Contact ciphertext, sender hash, provider identifier, token or code material |
| Conversation version | Source link UUID/revision, session UUID, expected outbound UUID, updated_at, expires_at | Answers, prompts, contact/hash, authentication material or resumable capability |

Ownership is verified against the parent request owner under lock; it is never inferred
from a sender hash. A snapshot remains confidential and linkable, not anonymous. Session
and outbound references cannot authorize retrieval, grading, sending or session resume.
If the source is absent, already cleared, cross-owner or ambiguous, refuse capture.
Never reconstruct deleted history or bulk-backfill guessed historical revisions.

This first slice intentionally does not preserve queued message contents, code issuance,
sender barriers, actor/key receipts, general logs, embedded references or backups. Those
need separately explicit source identities and field/retention decisions. In particular,
this proposal cannot be presented as adequate preservation of a raw-message dispute.
Full preservation coverage and deletion execution remain incomplete even if approved.

## Proposed transaction and access boundaries

Reuse the independent recent-OTP ADMIN claimant and pending DELETE-request checks.
Require an opaque authorized decision reference, finite future expiry, reason code and
exact-body/key retry binding. No automatic legal determination, account-wide capture,
free-text narrative or continuous recording. Apply existing mutation/page/rate bounds.

Acquire existing account/request locks before the channel mutation lock; lock and
revalidate the source version, ownership and current database time. Atomically create
the encrypted snapshot, exact finite preservation decision, immutable capture metadata,
audit and safe outbox event. A stale version conflicts; an unavailable source fails
closed. Concurrent unlink/STOP either precedes capture and changes eligibility, or follows
capture and freely clears operational state. Failure rolls back the whole capture.

Keep snapshot storage separate from operational channel models and all dispatch queries.
Use the existing approved authenticated-encryption primitive with a distinct purpose
and snapshot-bound context; no unkeyed low-entropy body digest or new cloud service.
No source payload or identifier enters logs/metrics/outbox attributes. Do not add a
payload-reading/export endpoint in the first slice. Existing hold pages may list only
opaque snapshot/decision references, lifecycle state and timestamps, with an explicit
snapshot label. The existing source selection must remain available for terminal receipts.

Keep ordinary learner exports within their existing minimized operational projection;
internal preservation decisions and snapshot ciphertext are excluded. Deletion preview
must inventory the new store, retain LEGAL_HOLD_COVERAGE_INCOMPLETE and keep execution
false. Production retrieval/disclosure, if later required, needs its own authorized,
audited access design; possession of a request or snapshot UUID is not authorization.

## Proposed finite retention

No snapshot extends an operational contact, code or conversation lifetime. STOP/unlink,
withdrawal, delivery cancellation and normal source cleanup continue immediately.
The encrypted evidence is retained only while at least one exact active decision covers
that same snapshot. Do not recapture changing state on retry or extend automatically.
After the last release/expiry, bounded cleanup deletes the disposable encrypted evidence;
release does not erase the operational source or existing original-record hold.

Keep only the minimized decision/capture accountability metadata under the parent
request's existing six-years-after-completion rule. Do not invent completion while the
request is pending or claim that ciphertext erasure anonymizes retained references.
The approved accountability expiry processor remains separately required. A policy
requiring different evidence fields or post-release retention must revise this proposal
before code; do not silently derive a new period from the raw-webhook upper bound.

## Alternatives and consequences

1. **Proposed bounded capture:** least additional collection, stable evidence independent
   of STOP/relink, but cannot recover prior revisions or prove omitted raw content.
2. **Continuous immutable version history:** better historical availability, but copies
   metadata for all users before a decision and adds expiry/ownership/disclosure costs.
   Not recommended for this MVP without a specific approved need.
3. **Freeze current operational rows:** reuses original-record guards but conflicts with
   STOP/unlink, contact clearing and revision reuse. Reject for live channel state.
4. **Keep only ADR-055 terminal holds:** safe current behavior; leaves the documented
   mutable-state coverage gap and cannot justify enabling account erasure.

## Acceptance before any implementation promotion

- Strict source/version contracts, generated clients and SQL ownership/immutability.
- Independent recent-role/re-auth checks, exact key replay and cross-owner/unbound denials.
- Simultaneous capture, relink, STOP, unlink, withdrawal, expiry and rollback regressions;
  no deadlock, dispatch, authentication or resume capability from the snapshot.
- Multiple decisions on one snapshot, exact wall-clock expiry/release, bounded cleanup
  without starvation, immutable metadata and no accidental source deletion.
- No encrypted field outside the approved allowlist; redaction and owned export/preview
  tests; accessible 320-pixel/large-text operator controls and stale-state recovery.
- Clean/additive upgrade, actual restricted database login, isolated populated recovery,
  full existing channel/hold/browser suites and source/dependency/container security.
- Default-disabled creation, explicit supported-capability discovery and all-reader
  rollout. Rollback keeps evidence/readers and disables creation; forward fix only.

## Approval and migration

Approval is not recorded. No migration, schema/API/UI behavior or runtime flag is added
by this proposal. Product/privacy/safeguarding owners must confirm source identities,
field allowlists, finite lifecycle and the fact that omitted raw material remains a gap.
Only then prepare the smallest additive synthetic implementation and record approval
here. Destructive erasure/anonymization still requires a separate exact transform,
full hold coverage, tested recovery and explicit human approval under the coding contract.
