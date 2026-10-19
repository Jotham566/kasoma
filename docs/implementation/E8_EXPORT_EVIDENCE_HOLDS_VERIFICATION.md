# E8 exact export evidence preservation foundation

Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
Status: implementation candidate; complete acceptance pending.

## Authorization and boundary

[ADR-060](../decisions/ADR/060-completed-export-accountability-retirement-proposal.md)
received explicit user approval on 19 October 2026 for bounded synthetic implementation.
This first additive increment supplies preservation prerequisites only. No retirement
routine, maintenance login, scheduler, DELETE bypass or account erasure exists here.
Creation defaults false through `EXPORT_EVIDENCE_HOLDS_ENABLED`; the Docker review
stack stays disabled. Read/release of existing holds remains independent of creation.

## Implementation

Migration 0039 adds generated unique immutable receipt UUIDs and a request/UUID index.
The existing actor/key primary key and exact retry hashes remain unchanged.
Forward migration 0040 corrects receipt ownership to follow the EXPORT subject,
including receipts whose actor is an independent administrator claiming review.
The locally applied 0039 is preserved; the correction is additive. Deferred
ORM loading/default fetching preserves historical migration fixtures until upgrade.
Existing append-only UPDATE/DELETE guards remain; exact active-hold DELETE guards
run first and evaluate database wall clock.

DATA_REQUEST_RECEIPT names one original receipt UUID whose EXPORT parent
owner matches the deletion requester. EXPORT_JOB_RECEIPT names one EXPIRED job by its
request UUID, with no authentication grant, current generation or remaining generation
row. Active jobs are excluded, preserving grant/worker transitions. API and SQL
independently enforce ownership, original independent ADMIN claim and finite decisions.
For these targets, source locking orders EXPORT parent before exact leaf; future
retirement must take the same locks. No hold/delete race acceptance is claimed before
the deletion capability exists and is tested.

The claimed pending DELETE case exposes a bounded exact-EXPORT source lookup,
sharing the 60/minute hold-read pool. At most 50 ordered receipt UUIDs/page and an
optional cleared job UUID are returned; no keys, hashes, grants, contacts or bodies.
Lookup is available to the independent recent-OTP claimant even with creation off;
it grants no new hold or delete permission. Missing/foreign/non-EXPORT sources are
absent. Reads have minimized case-level audit evidence and no-store responses.

Accessible controls advertise the two options only when creation is enabled. An
operator can select a paginated exact reference into the existing decision form.
Presentation-only browser interception tests this gated UI; PostgreSQL integration
and actual restricted logins separately exercise the authorization boundary.

## Verification record

Initial focused run: four pass; one fails because a CASE expression resolves a
receipt-only OLD.id field for a job trigger. Replaced with explicit PL/pgSQL IF
branches; corrected five cases pass. Initial formatting/type checks catch overlong
SQL and a missing helper return annotation; both corrected. The first browser run
finds a duplicate test variable; it is renamed. The next catches an ambiguous status
selector after adding the nested lookup. Label the main status and scope its tests.
A stale production build then correctly fails to find the new label; rebuilding
resolves it without changing assertions, timeouts or authorization gates.

Final focused verification passes ten integration cases, including real restricted
LOGIN creation/release and denied source/schema/role rewrites, exact ownership and
SQL rejection, staff-claim receipt ownership, rollback, sibling scope, pagination,
release with creation disabled, retained DELETE guards and populated upgrades from
both 0038 and 0039. Clean schema migration is exercised by the other focused fixtures.
`make test-unit openapi-check build` passes 1,094 unit/contract and 35 tooling cases
plus generated contracts and production build; final types/lint/security are
rechecked after the added recovery evidence.

`make build test-web-privacy` passes six executions (two existing complete privacy
journeys per engine) in Chromium/Firefox/WebKit. The expanded operator journey
checks advertised options, paginated reference replacement, exact selection into
the decision form, existing retry/release behavior, keyboard/native controls, axe,
320-pixel reflow and 200-percent text. [Synthetic reference controls](evidence/E8_EXPORT_HOLD_REFERENCES_2026_10_19.png)
show the actual WebKit operator form; this is presentation evidence, not branded
or physical-device acceptance.

`make migrate seed recovery-drill security` passes. A final recovery recheck adds
the actual exact receipt hold: 68 tables/685 synthetic rows restore in 365 ms, with
UUID identity/evidence hashes preserved and immutable/held guards effective. This
is logical database recovery; object-storage and production PITR/RPO/RTO remain
unverified. The review stack is additively migrated through 0040, all eight services
remain healthy and creation remains false. No review-stack data is purged.

Full integration and hosted acceptance remain pending. Documentation checks alone do not accept application behavior.

## Remaining work

The restricted six-year processor, DB-enforced policy/limits, leaf/parent races,
atomic batch audit, finite retry retirement, bounded scheduling and health are next.
Review-stack purge, real-data processing and account erasure remain excluded. Full
preservation, investigation/audit retention and production release gates remain open.
