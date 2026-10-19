# ADR-057 capture implementation readiness

Date: 19 October 2026. Requirements: FR-ID-006, FR-WA-006, FR-OPS-003,
BR-010, NFR-SEC-002, NFR-MNT-001. Follow the approved bounded synthetic scope in
[ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md) and the
[private-format evidence](E8_CHANNEL_PRESERVATION_FORMAT_VERIFICATION.md).
This is the next implementation plan, not application acceptance or a new permission.

## Observed integration points

- `services/legal_holds.py`: independent recent-OTP ADMIN, pending DELETE-request
  claimant, exact actor/key/body receipts, finite decisions and release/listing already
  exist. New snapshots must be visibly distinct from original receipt targets.
- `services/identity.py`: IdentityError deliberately commits failed-guess/rate
  accounting. A capture must put all evidence writes inside an explicit rollback
  boundary; do not assume raising IdentityError rolls them back.
- `services/domain/messaging.py`: ChannelLink has one persistent UUID and a revision;
  ConversationState is keyed by that link UUID and has no independent source UUID or
  mutation counter. Neither updated_at alone nor link_revision alone proves an exact
  conversation state version: changes can share a timestamp or a link revision.
  The existing SQL channel_owner_guard already requires every link UPDATE to increment
  revision by exactly one; preserve that invariant rather than adding a redundant link
  counter. Conversation deletion/reinsertion can reuse the same link/revision, so a
  per-row counter reset to one would be insufficient for exact conversation versions.
- `services/whatsapp_linking.py:owned_view` treats a committed sender STOP barrier at
  or after linked_at as STOPPED even while the link row still says ACTIVE. Capture
  must recheck this effective barrier under the channel lock; checking only link.status
  or its mutation version could miss signed STOP intake before queued processing.
  Ownership still comes from the link/request owner, never the sender hash. The barrier
  is an eligibility input, not an extra captured evidence field.
- `services/whatsapp_retention.py`: transient expiry and bounded terminal cleanup run
  under the channel lock. Snapshot evidence must not create operational foreign keys
  that block conversation deletion, contact clearing, STOP, unlink or relink.
- `apps/api/data_requests.py`, `services/legal_hold_contracts.py` and
  `apps/web/app/privacy/legal-holds.tsx`: existing metadata-only route/contracts/operator
  controls. Discovery, capture and additional decisions must have explicit labels and
  preserve terminal receipt selection. No payload viewer is authorized.
- `services/deletion_preview.py`: owned inventory remains advisory, incomplete and
  execution-disabled. Snapshot metadata and disposable encrypted evidence need inventory;
  ordinary learner export must continue excluding internal preservation material.

## Exact source selection

Use a narrow authenticated source inspection under the existing claimant checks, not
account browsing or contact lookup. The operator supplies actual source link UUID,
source kind and link revision. Return only a bounded opaque observed-version value;
do not return contacts, conversation bodies, session/outbound references or source payload.
Inspection does not create a preservation decision or authorize later capture by itself.

The implementation must establish a database-enforced mutation version for the exact
current source. Preserve the link's existing monotonic revision. A noncycling database
sequence assigned to each conversation INSERT and UPDATE is one bounded option: it
copies no historical payload and distinguishes reinsertion, A→B→A changes and
same-timestamp writes. Never expose its raw global sequence value to clients. If used,
document its concrete trigger/overflow/upgrade behavior in ADR-057 alongside the
implementation. An opaque purpose-keyed version binds request,
owner, source kind/link, link revision and exact current state. Never expose an unkeyed
digest of low-entropy evidence. Test revision reuse, no-op updates, same-time changes
and stale source selection. Freeze the producer contract before wiring capture.

## Atomic capture and retention

1. Re-authorize the recent independent ADMIN and pending claimed DELETE request.
   Preserve account/request-before-channel lock ordering. Recheck the creation flag,
   mutation limit, exact retry binding and current database time.
2. Lock and validate the exact current owned source/version. Refuse absent, cleared,
   expired, cross-owner, ambiguous or relinked sources; never backfill guessed history.
   An exact successful retry returns the existing decision without recapturing state.
3. Generate the snapshot UUID only after validation. Atomically write immutable capture
   metadata, separately disposable encrypted evidence, the finite preservation decision,
   exact receipt, audit and safe outbox. Keep operational source IDs out of outbox/logs/
   metrics. Test rollback after every write boundary, including IdentityError conversion.
4. Add independent SQL ownership/claim/version/immutability guards and commit-time
   completeness checks. A metadata-only partial capture must not commit. Snapshot
   references must not become dispatch, authentication, grading or resume capabilities.
5. Support additional finite decisions on the same existing snapshot without copying
   changing state. Serialize adding a decision against ciphertext disposal, and test
   actual SQL transaction races as well as application advisory locks.
6. Remove encrypted evidence in bounded batches only after the last exact active decision
   ends at database wall clock. Exclude active evidence before LIMIT to avoid starvation.
   Prevent reinsertion/resurrection of disposed evidence. Release/expiry must not delete
   original operational rows or extend their ordinary retention.
7. Keep minimized immutable accountability metadata under the parent request's existing
   six-years-after-completion rule. Pending requests get no invented completion/expiry.
   The separately required accountability-expiry processor remains open.

## Delivery and acceptance order

Ship additive clean/upgrade migrations and ORM/contracts with the service and generated
client; creation defaults disabled. Capability discovery exposes only supported capture
and exact decision kinds. Turning creation off retains metadata readers and release.
Add accessible keyboard, 320-pixel and 200%-text controls with source-check, stale/retry,
failure and re-auth states. Display only opaque decision/snapshot references and lifecycle
metadata. There is no payload-read/download endpoint in this slice.

Focused acceptance covers authorization/freshness/ownership, exact replay, field
allowlists/redaction, SQL immutability and completeness, concurrent STOP/unlink/relink/
withdrawal/expiry, multi-decision release/disposal, safe export and incomplete preview.
Then verify restricted database login, isolated populated recovery (including bound
decryption after operational source disposal), all existing channel/hold/browser suites,
source/dependency/image security and healthy Docker smoke. Record failures truthfully;
default-disabled code and documentation checks alone are not application acceptance.

Full hold coverage, raw-message legal sufficiency, reviewed erasure authority and real
privacy/academic/provider/production gates remain separate.
