# ADR-047: Bounded private export artifact format

Date: 9 October 2026
Status: Accepted within delegated implementation discretion; delivery remains disabled
Requirements: FR-ID-006, NFR-SEC-001/002, NFR-MNT-001

## Decision

Prepare the private artifact boundary required by the large-history export plan. Keep ADR-028's
existing synchronous limits, encrypted PostgreSQL copies and every disclosure/authorization rule.
This decision defines an internal format, not a new HTTP route, database completion path, worker
job, retention period or production provider. Only synthetic in-memory storage tests consume it
until the separately verified publication and owner-delivery lifecycle exists.

Use the existing authenticated identity cipher behind a small protocol. Each encrypted envelope
binds a request UUID, unpredictable generation UUID, zero-based chunk ordinal, fixed format label
and base64 payload. Fresh unpredictable object UUIDs contain no account identifiers. A trusted
manifest records those references, exact plaintext sizes, SHA-256 digests and a whole-file digest.
Digests alone are not authorization or authentication; the envelope must decrypt and match all
trusted binding fields before any plaintext from that chunk is returned. Hide payloads in object
representations and convert validation/storage/cipher errors to closed errors without diagnostics.

Resource limits for this format are 64 KiB plaintext per chunk, at most 256 chunks (16 MiB total),
128 KiB encrypted object size and a 64 KiB serialized manifest. Reject empty chunks/artifacts,
duplicate object references, gaps/reordering, inconsistent byte totals and unknown format fields.
Accept only bounded input chunks; do not silently split an arbitrarily large source allocation.
These are engineering ceilings, not new synchronous limits, legal deadlines or pilot SLOs.
The producer must supply the verified allowlisted JSON stream; this codec does not approve fields,
parse a complete JSON file or make arbitrary input safe for disclosure.

The writer returns a manifest only after every chunk is stored successfully. Failure produces no
manifest. Uploaded but unpublished objects still require the future generation/lease-aware orphan
cleanup; this codec must not delete an object based on age or assume an upload failure wrote nothing.
The caller owns publication and cleanup. Storage callbacks must bound reads before returning bytes;
post-read size validation is a second check, not proof of bounded adapter allocation.

The reader checks the trusted manifest and request/generation binding before reading objects. It
checks each authenticated chunk's identity, ordinal, size and digest before yielding bytes. It checks
the whole-file digest before yielding the final chunk. A late failure may follow previously emitted
chunks; the future HTTP/proxy path must abort and enforce Content-Length so an incomplete response
cannot be accepted as a complete file. The codec never asserts successful delivery or completion.
Generator cancellation closes the producer; storage callbacks retain their own connection cleanup.

## Gates unchanged

Do not expose this artifact through learner routes until durable jobs, consistent authorized snapshot,
leases/retries, atomic completion, private approved storage, recent-OTP owner download, expiry and
orphan cleanup are implemented together. No public/presigned URL, external service, token persistence,
new learner data, real data, or whole-file unbounded collection is introduced here. ADR-028's 24-hour
availability and six-year minimized request accountability will control the eventual lifecycle.

Verify boundary sizes, multi-chunk and empty input, ciphertext privacy, wrong key/binding, swapped,
missing, truncated and corrupt chunks, manifest tampering, unknown fields, callback failures,
cancellation and failure-before-final-byte behavior using synthetic fake storage. No migration or
public contract change is needed. Rollback removes the unused internal format; existing exports
remain usable. The delivery decision must resolve worker/proxy timeouts before enablement.
