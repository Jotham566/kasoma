# ADR-028: Owned bounded data exports and accountable completion

Date: 29 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-ID-006, FR-OPS-001/003, NFR-SEC-001/002, NFR-OBS-001, NFR-MNT-001

## Decision

Extend ADR-027 for EXPORT only. A recently OTP-authenticated owner may generate and
retrieve an understandable versioned JSON snapshot. An administrator cannot download
it for another account. Learning consent and subject enrollment do not gate privacy
access. Admin review remains optional for this deterministic owner-verified export;
DELETE requests remain pending with no destructive account processor.

Completion means a validated snapshot was made available to the authenticated owner,
not proof that a browser saved or read it. Commit completion/audit/outbox/retry evidence
atomically with an encrypted retry copy. A lost acknowledgement returns the same
snapshot. Subsequent requests may capture a newer snapshot after completion. Completion
records carry the exact six-calendar-year retention deadline required by security policy.
Expiry of accountability evidence and legal-hold processing remain production gates.

## Disclosure policy and limits

Use explicit read-only field projections, never ORM dumps. Include own profile, verified
identifiers, consent metadata (not guardian names/contact/evidence), subject selection,
session metadata, submitted answers with attempted-question context, released grade
metadata, hint usage, visible mastery evidence/estimates/history, own reports/comments,
reassessment linkage, data requests and safe own identity-event metadata. References
include curriculum names. Credentials, lookup hashes, OTPs, staff notes/identities,
answer keys, rubrics, solutions, future assignments and recommendation candidate
internals are excluded. Never decrypt or export guardian evidence.

Unfinished/abandoned diagnostic scores and any estimates/history depending on that
sealed evidence stay excluded under ADR-020/024. Answers themselves remain included.
The manifest explains those exclusions; this is an application self-service export,
not a representation that every legally disclosable record has been adjudicated.
Third-party and exceptional disclosure requests still need the approved privacy process.
No score recomputation, consent change or historical evidence rewrite occurs.

Bound synchronous personal export generation to 10,000 related queried rows plus
the account profile, and 2 MiB of serialized JSON. This is not the architecture's asynchronous analytics/bulk export path.
Exceeding a bound returns EXPORT_LIMIT_REACHED with the request still pending; never
truncate silently. A future large-history worker requires its own verified delivery
path. These local bounds do not establish pilot latency or legal response deadlines.

## Storage, retrieval and expiry

Store the bounded retry copy encrypted with the existing identity encryption service in
PostgreSQL for exactly 24 hours, with SHA-256 integrity metadata. No new object-storage
provider, public URL, bearer download URL or cloud dependency is introduced. This
transactional short-lived document is not a media-storage architecture replacement.
Authentication/revocation/ownership and recent OTP are rechecked for every download.
The proxy preserves no-store and an attachment disposition with a server-generated
filename. The UI saves an explicitly requested JSON file and does not use browser storage.

Migration 0015 permits only EXPORT completion on otherwise immutable request evidence,
requires a matching artifact and six-year deadline, and replaces lifetime kind uniqueness
with uniqueness for pending requests. Artifact updates and early deletion are blocked;
expired copies can be removed without deleting completion evidence. Expired downloads
return 410 and never regenerate the same request. New requests are explicit.

The existing single local Celery worker runs Beat for an idempotent bounded expiry sweep
every five minutes; only one scheduler should operate per deployment. A repository command
runs the same sweep. Expiry is enforced at read time even if cleanup is delayed. Sweeps
log only aggregate counts and correlation IDs. Database backups follow the separate
approved 35-day retention policy; production encryption, legal holds and restoration
procedures remain required. Automated tests use synthetic data and provider fakes.
