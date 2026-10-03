# ADR-030: Specific-record legal holds

Date: 30 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002, NFR-MNT-001

## Decision and boundary

Extend ADR-029 with an audited hold register for four explicitly owned record types:
CONSENT, ATTEMPT, CONTENT_FLAG and DATA_REQUEST. Each hold names one existing record,
its pending DELETE review, an opaque decision-reference UUID, a reason code and a
finite future end time. No account-wide or table-wide hold, free-text legal narrative,
upload, automatic extension, new provider or blanket retention exception is introduced.
The operator must already have an authorized preservation decision; this UI records it,
not a legal determination. Production legal/privacy approval remains a launch gate.

Only the independent, recently OTP-authenticated ADMIN claimant can create, list or
release holds in that request. Recheck roles and claim ownership on every retry. Release
requires affirmative confirmation and a separate opaque decision-reference UUID. A hold
may be released once; extension requires a new explicit hold. Multiple decisions may
hold the same record; its hold effect ends only when all are released or expired.
Expiry is evaluated at access/check time, without relying on a scheduler. Expired hold
metadata remains evidence; expiry does not delete the underlying record.

Immutable scope, reason, decision reference, actor and timestamps plus single release
metadata form the evidence. Retain this minimized material under the parent request's
six-year-after-completion obligation. Do not invent a completion/expiry date while the
request is pending. Accountability expiry processing remains separately required.

## Contracts, concurrency and controls

Actor/key-scoped receipts bind create/release retries to their exact body and path;
reusing a key for a different action conflicts. Request-row locks serialize mutations.
Ten new mutations/admin/minute and sixty reads/admin/minute bound operational load;
exact-key retries still recheck authorization and recover current state.
List pages use UUID cursor and limit 1–50. API/UI expose opaque record/decision references,
status and lifecycle timestamps, never requester/staff identifiers or record payloads.
No personal record is decrypted. Audit and safe identity-outbox events commit atomically.

Migration 0016 is additive. SQL validates record ownership, independent ADMIN claim,
finite dates and immutable evidence. Supported target rows acquire key-share locks on
hold insertion; a BEFORE DELETE guard rejects active registered holds without weakening
existing immutable guards. A SQL active-hold predicate and domain predicate agree on
created_at <= time < expires_at and absent release. Synthetic tests inject clock values;
SQL DELETE guards use the database clock. Unsupported record types are rejected.
Future erasure/anonymization must check holds in the same transaction and use compatible
record locking; these guards do not authorize UPDATE anonymization or remove existing
immutability. A rolled-back/deadlocked transaction must never be treated as clearance.

## Preview and remaining work

The preview adds an active-hold count (bounded with a lower-bound marker), registered
hold/receipt inventory and ACTIVE_RECORD_HOLDS when relevant. Coverage is explicitly
partial: other record types, embedded references, logs, backups and representative
requests still need work. LEGAL_HOLD_COVERAGE_INCOMPLETE remains even with zero active
holds. execution_enabled stays false; learner status remains IN_REVIEW. Hold metadata
is excluded from learner exports under their existing internal-security review boundary.
A hold on request evidence does not hold its disposable export copy or unrelated rows.

No sessions are revoked, data erased, consent changed or retention deadline shortened
by this slice. Next implement the deletion execution state and reviewed transform,
remaining hold coverage and recovery plan before destructive execution. No migration
rewrites existing evidence; rollback should disable the new routes while preserving
hold protections and evidence, followed by a forward fix.
