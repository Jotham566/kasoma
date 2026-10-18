# ADR-055: Exact terminal channel receipt holds

Date: 18 October 2026
Status: Proposed; implementation and acceptance pending
Requirements: FR-ID-006, FR-WA-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

## Decision and scope

Extend ADR-030's exact-record deletion holds to already-minimized, explicitly owned
terminal channel receipts. New target kinds are CHANNEL_INBOUND_RECEIPT and
CHANNEL_OUTBOUND_RECEIPT. They refer to original message UUIDs, not snapshots or
invented ownership inferred from a sender hash. Existing record kinds are unchanged.

Inbound eligibility requires a non-QUEUED row bound to the request owner, processed_at,
and cleared sender ciphertext, code hash and reply ciphertext. Outbound eligibility
requires a non-PENDING row bound to that owner and cleared recipient ciphertext.
These receipts still contain confidential lifecycle/correlation metadata and learning
references; they are not anonymous. No payload/contact/authentication capability is
copied, resurrected or retained past its existing minimization step by this change.
Queued/unbound/cross-owner messages, links, conversations, link codes and composite
mutation receipts remain unsupported. Full channel/account preservation remains open.

Use existing independent recent-OTP ADMIN claim, finite decision-reference/expiry,
exact replay, release, bounded pages/rates, audit and identity outbox. Metadata retains
the existing request-accountability schedule; held original receipts resume their
existing 30-day cleanup when no active hold remains. No new retention policy or
production approval. No deletion/anonymization processor is enabled.

## Mutation and concurrency boundary

Acquire the ordinary channel mutation advisory lock after existing authenticated
actor/request locks and before selecting a new channel hold target. Retention already
uses this lock and never acquires request locks, avoiding reverse lock order. Recheck
terminal state, clearing and exact owner inside the hold transaction. SQL insertion
also validates/locks the exact target; an API check alone cannot grant preservation.

Channel hold creation is capped at database time, preserving deliberately earlier
synthetic clocks. New channel DELETE guards evaluate active holds at database wall
clock, including when a deleting transaction began before the hold was created.
Receipt UUIDs remain immutable even without a hold, allowing narrowly granted
UPDATE(id) solely for PostgreSQL row locking. Verify new holds under a separate real
restricted privacy login; do not broaden the assessment login or grant payload/DDL/
role-rewrite privileges. Existing hold-kind behavior is unchanged. Retention hold exclusion also uses database
wall clock, avoiding a host clock ahead of the database granting deletion clearance. Add focused skew/concurrency regressions.

While held, inbound terminal receipts cannot be rewritten/requeued. Outbound receipt
core fields/ownership cannot change or regain a recipient. Existing delivery callbacks
may advance SENT to DELIVERED/READ/FAILED or DELIVERED to READ, with monotonic status
clock; same-state callbacks may advance only that clock. FAILED uses the existing
PROVIDER_FAILED reason. No callback can turn a terminal receipt into pending work or
change unrelated fields. STOP/unlink/cancellation and expiry continue to operate on
ordinary live state; a hold never authorizes transmission or session resumption.

Bounded ordinary cleanup excludes active held receipt IDs before LIMIT, so an old held
row does not fill a batch forever. Existing dependency checks retain an inbound/link
while a held outbound still references it; unrelated eligible rows continue to expire.
Multiple holds, release and exact expiry use the existing active predicate. Direct SQL
DELETE guards remain a final protection against races and unsupported cleanup paths.

## Rollout compatibility

A typed CHANNEL_RECEIPT_HOLDS_ENABLED flag defaults false. The existing ADMIN hold
page advertises its currently supported target kinds; new UI options appear only when
advertised. New-kind creation fails closed while disabled, including new-key retries;
listing/releasing already-registered holds continues so disablement cannot hide evidence.
Enable only after all API/worker readers have the new enum/guards, preserving one mixed
version deployment window. Local synthetic tests explicitly opt in; this is not a new
privacy/production approval. Rollback disables creation and keeps the new reader/guards;
old readers cannot safely parse newly created target kinds and require a forward fix.

## API, privacy and acceptance

Extend only existing hold enums/UI labels and generated contracts. Display that only
already-minimized terminal receipts qualify; no receipt body is exposed. Owned export
keeps its existing minimized channel projection and excludes internal hold decisions.
Deletion inventory remains advisory with LEGAL_HOLD_COVERAGE_INCOMPLETE and execution
disabled. Existing source identifiers are private metadata, never telemetry dimensions.

Require clean/0033-upgrade migrations with existing hold replay preserved; API/SQL
eligibility and independence/recent-role checks; immutable core and legal callback
transitions; multiple holds/release/expiry; bounded non-starvation and hold/cleanup
races; STOP/unlink and five-question channel regressions; real restricted database
login; export/preview minimization; accessible UI; populated restore and security.
Full local and hosted acceptance is required before promotion. Synthetic-only evidence
does not approve real learner processing, legal interpretation or production release.

Rollback disables the new target selection while retaining registered hold metadata
and database protection; use a forward fix. No destructive rollback or volume reset.

## Remaining design

[Channel readiness](../../implementation/E8_CHANNEL_HOLD_READINESS.md) still governs
mutable/live state, historical link revisions, already-cleared material, other logs and
backups. A separate reviewed snapshot/versioned-evidence design is required for those
cases. This limited extension does not silently redefine an active live-message hold
as a terminal receipt hold or claim universal preservation coverage.


## JSON menu comparison correction

Local candidate0034 is already applied with new creation disabled. A final real signed
practice-menu regression exposes PostgreSQL json equality failure on no-op record
comparison. Preserve that applied migration and add forward migration 0035, comparing full rows
through to_jsonb before accepting no-ops. Canonical JSONB preserves array order, and
held menu/core rewrites remain rejected. No row transform or policy change. Clean and
0034-upgrade/replay tests must verify the correction before acceptance.
