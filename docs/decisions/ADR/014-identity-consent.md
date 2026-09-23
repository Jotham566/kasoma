# ADR-014: Local identity and consent implementation

Date: 23 September 2026
Status: Accepted within delegated implementation discretion
Owners: Engineering
Requirement IDs: FR-ID-001–005, FR-OPS-001, NFR-SEC-001/002

## Context and decision

Implement the approved application-managed OTP identity and consent model. No prior
ADR or consent policy is replaced. Add the specified identity endpoints and tables,
plus OTP challenges, rate buckets, consent evidence and registered outbox events.
Opaque random access/refresh credentials are hashed in PostgreSQL; access lasts
15 minutes, rotating refresh families 30 days. Every protected request checks
revocation. Sensitive actions require OTP authentication within ten minutes.

Use purpose-bound LOGIN, LINK and GUARDIAN challenges. Linking requires a recent
session and never merges two existing identities. Guardian verification is bound
to the learner, policy and a distinct verified contact. Guardian name, relationship
and affirmative declaration are collected separately from learner assent. Contact
verification establishes possession, not proof of legal guardianship; the approved
pilot verification procedure and legal notices remain launch gates.

Date of birth is immutable after first entry to prevent bypass by editing age.
Corrections need a future audited support flow. The existing profile endpoint only
accepts name, birth date and approved subject selection; it cannot accept roles or
consent state. Consent withdrawal stops authorization immediately. Policy changes
invalidate earlier grants. No learning routes are enabled by this slice.

PostgreSQL row/advisory locks serialize OTP consumption, rate counters and session
families. Request limits return the same generic 202; verification abuse returns
OTP_RATE_LIMITED. Default caps: one send/minute and five/hour per contact,
20/hour per network peer, ten/hour per device, five guesses/challenge. Forwarded
IP headers are not trusted. Web gateway traffic also shares a peer cap; production
proxy configuration must explicitly establish trust before rollout.

Use Fernet authenticated encryption for stored contact/name evidence and keyed
SHA-256 lookup/OTP digests with purpose separation. Separate local encryption and
lookup keys are generated into ignored .env. No fallback keys. Implementation uses
[PyCA Fernet](https://cryptography.io/en/stable/fernet/).

The web gateway retains credentials in HttpOnly SameSite=Strict cookies, never
browser storage or response JSON, with Origin checks for mutations. Secure cookies
are used on HTTPS; HTTP is local-only. The API accepts bearer credentials, never
ambient cookies. Generated OpenAPI types remain the UI contract.

Local authentication delivery is synchronous through existing fake/Mailpit adapters
(the architecture's synchronous authentication path). Tests inject deterministic
codes and capture messages in memory. Runtime codes are random; no debug-code API.
Registration/consent events are persisted atomically in an outbox with no PII.
External dispatch and long-term evidence retention jobs remain later operations work.

## Alternatives and consequences

JWTs would still require database revocation checks; opaque tokens reduce parsing
and signing complexity. Browser bearer storage would expose refresh credentials to
scripts. A guardian portal is explicitly excluded; a separate verified declaration
form fulfills the approved consent workflow without adding that product.

## Security and approval

The user authorized this vertical slice and best-practice implementation choices.
Synthetic notices are labeled development fixtures and are not legal policy. The
existing production startup rejection remains. No real learner/provider data or
external delivery is authorized. Approval of legal wording is not inferred.

## Migration and rollback

Migration 0002 is additive after 0001. Existing curriculum survives. Test both a
fresh schema and upgrade from the foundation. Roll back code while retaining new
tables; destructive downgrade requires a reviewed recovery plan. Local keys must
be backed up with local synthetic databases; rotation requires re-encryption and
lookup re-indexing and is a production-readiness gate.
