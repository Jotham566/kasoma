# ADR-074: Closed-identity credential intake and dispatch

Date: 20 October 2026 (Africa/Kampala)
Status: Accepted technical implementation under approved ADR-061; verification pending
Requirements: FR-ID-001/002/005/006, BR-010, NFR-SEC-002, NFR-MNT-001

## Decision

For LOGIN issuance, pre-read the current identifier owner, then take its existing
HMAC account lock and ADR-070 shared subject gate before rate/identifier work. Under
the existing identifier lock re-read the binding and fresh user. A changed binding
requires fresh issuance; never acquire a new account lock after an identifier lock.
A retained closed identifier receives the normal generic acceptance without a code,
new challenge or provider call. Finite peer/device/identifier security rates remain.

For an already bound LOGIN, retain one idle session-shared subject gate through
provider dispatch, with a fresh short binding/closure check on that same owned
connection before the call; no second checkout or larger pool is required. No row,
HMAC lock or open transaction spans messaging. A nonblocking exclusive closure cannot
cross a live dispatch. Reuse the existing connection invalidation discipline on
uncertain gate cleanup. Suppressed dispatch and gate failure are not provider outcomes
and must not increment returned/failed OTP observations. Only the exact challenge
created by this invocation may be discarded on suppression/provider failure.

The originally unbound LOGIN case has no attributable subject gate. Recheck its
binding before dispatch and refuse a newly bound identifier rather than adopting it.
This does not authorize hash-based attribution, deletion or a permanent tombstone.
The full closure executor must still preserve current identifier ownership and drain
all pre-barrier unbound challenges under their original at-most-ten-minute clocks
before identifier removal. No unbound history is claimed as owned by these checks.

Reject a closed existing LOGIN before consuming or incrementing a retained challenge.
Reject closed refresh before family-wide reuse revocation, keeping ordinary active
and nonclosed-disabled reuse protection unchanged. Access authentication retains its
ACTIVE check, backed by SQL's immutable closed-implies-DISABLED constraint. ACTIVE
consumers need not lazy-load the new column in historical migration fixtures. Only
non-ACTIVE users require the marker check; there is no schema introspection or
missing-column fallback that could admit a closed identity.

## Scope and verification

No public migration, new closure permission, erasure capability activation, account
closure, physical revocation batch or completed DELETE is introduced. Normal review,
real data and production exclusions remain. This extends the approved early barrier
and ADR-070 dispatch protocol without changing consent, ownership or retention.

Tests use only exclusively created fake-provider sources. A future closed-row fixture
temporarily toggles the one named closure trigger inside its owned source/transaction,
then restores it before consumers run. That fixture is not authorization/closure or
SQL guard acceptance; no such toggle is exposed to application code or normal review.
Prove generic email/phone refusal, unchanged retained challenges/session families,
active reuse protection, changed-binding refusal, actual idle gate/exclusive conflict,
late closure refusal, failed dispatch cleanup, observation accuracy and exact cleanup.
Full installed SQL/source/payload/preservation/export/checkpoint enforcement remains
mandatory before the real closure/removal lane can be accepted.
