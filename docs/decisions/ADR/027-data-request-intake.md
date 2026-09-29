# ADR-027: Minimized data-request intake and independent review

Date: 29 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-ID-006, FR-OPS-001/003, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001

## Decision and scope

Implement the specified export/deletion request endpoint with durable acknowledgement,
owned status and an administrator review queue. This is the first FR-ID-006 vertical
slice, not export delivery or deletion/anonymization. No API/UI can mark a request
completed, dismiss it, claim fulfillment or silently discard it. Queued and in-review
requests remain visible. Production remains disabled until retention-aware fulfillment
and the existing privacy/legal gates are implemented and verified.

Privacy rights are not conditional on learning consent, a completed profile, subject
enrollment or guardian learning consent. A signed-in requester uses the existing recent
OTP boundary (under ten minutes) for intake. Owned status reads need an active session;
admin queue reads and claims need recent authentication and ADMIN. No new role or
production MFA exception is introduced. Staff may not review their own requests.
A revoked session cannot create/read a request. Accounts already closed and guardian
representative requests require a future verified support process; this slice does not
invent an impersonation path or collect identity-document uploads.

Input is only kind EXPORT/DELETE and explicit affirmative confirmation. Store server-derived
user ID, OTP authentication time, verification method, creation time and retention-policy
code. No reason, free-text notes, contact details, raw credentials or learner answers are
collected. Return only opaque request ID, kind, QUEUED/IN_REVIEW status, timestamps and
retention-policy code. Administrator listings also omit requester identity and staff IDs.
Request creation, review start and queue reads are audited; safe identity-outbox events
contain only the existing correlation request ID. No email or messaging is sent.

## State, retries and persistence

Migration 0014 adds append-only data_subject_requests, data_request_reviews and
actor-scoped data_request_receipts. Requests are unique per account/kind while this
intake-only workflow has no terminal states. Repeated same-kind intake, including a
new key after reload, returns the same request; key reuse for another kind/action conflicts.
A single independent administrator claims review; a different claimant conflicts.
Status derives from the existence of that immutable review record. No completion
state, manual fulfillment toggle, arbitrary transition or reassignment is exposed.
A later fulfillment migration must support subsequent requests after completion.

Existing identity locks serialize account-scoped intake and receipts; request row locks
serialize claims across administrators. Audit/outbox/receipt/evidence changes commit
atomically. SQL guards enforce kinds, verification window, retention policy, immutable
records and independent ADMIN ownership. Read pages use bounded UUID cursor pagination.
Limit new intake keys to ten per account/hour and reads/claims to sixty per minute;
authenticated exact-key retries recover existing results. These operational limits are
implementation defaults, not a legal request quota or promised processing deadline.

## Retention and fulfillment boundary

The controlling security/production-pilot schedule requires minimized data-request
accountability evidence for six years after completion. Persist that policy explicitly;
there is no completion timestamp yet and therefore no fabricated expiry date. Before
real learner data, implement observable fulfillment, completion evidence, exact retention
deadlines, specific legal holds and testable erasure of expired evidence. Pending queues
require operational monitoring; this design does not authorize indefinite retention.

Export must produce an understandable machine-readable artifact under verified ownership
and safe retrieval, with third-party information and assessment secrets treated under
approved policy. Deletion must revoke sessions/channel links early in actual processing,
remove direct identifiers and anonymize only permitted evidence. Existing immutable
learning/audit guards must be reconciled using a narrow reviewed processor and migration;
never bypass them with a general deletion endpoint. An in-review intake receipt does not
start destructive processing or revoke learning access. The UI explains this and links
to existing consent withdrawal. The 30-day inactive-account grace period is not silently
applied as a data-request deadline.

This sequencing preserves the approved security/retention rules; it does not change them.
Synthetic tests cover identity/consent independence, ownership, administrator roles,
concurrent retry/claim, rollback, SQL guards, rate limits, audit, browser acknowledgement
recovery, keyboard and accessibility. No real data, external providers or cloud changes.
