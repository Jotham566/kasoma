# ADR-077: Closed guardian-consent and local role consumers

Date: 20 October 2026 (Africa/Kampala)
Status: Accepted technical extension under approved ADR-061/070/075; complete own hosted39380895685 verified at source1597a68; main publication pending
Requirements: FR-ID-003/005/006, BR-010, NFR-SEC-002, NFR-MNT-001

For a new guardian grant, pre-read only the exact actor-owned GUARDIAN challenge's
identifier type/hash and current verified recipient binding. Coordinate a distinct
known recipient with the existing shared subject gate before locking the challenge.
Do not acquire a second account HMAC lock. Under the challenge and identifier locks,
recheck that exact binding and fresh recipient closure before consuming the code or
recording evidence. A changed binding requires fresh verification; do not adopt a
new subject after the identifier lock. Unbound contacts still require no account.
Refusal uses the existing generic OTP_INVALID error without changing the challenge.
Current actor authentication, accepted idempotent replay, consent withdrawal, policy,
own-contact refusal and ordinary incorrect-code attempt accounting remain unchanged.

Local synthetic staff provisioning refuses closed subjects for both grant and revoke,
before role/audit writes. A temporarily disabled, nonclosed account can still have
privileges revoked. This grants no authority to close a staff identity or erase shared
provenance. Existing account coordination protects both operations through commit.

No migration, public contract, retention/ownership policy, real-data authority, normal
review activation or erasure execution is added. Future-state fixtures use only the
registered exact-owned source factory. Application guards do not replace permanent
SQL write guards, full preservation, authorization/closure or quarantined recovery.
