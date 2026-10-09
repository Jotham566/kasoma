# E8 private export artifact boundary

Requirements: FR-ID-006, NFR-SEC-001/002, NFR-MNT-001.
Decision: [ADR-047](../decisions/ADR/047-private-export-artifact-format.md).
Status: native format/projection checks pass; hosted regression pending; delivery disabled.

`services/export_artifacts.py` accepts the allowlisted projection's bounded byte stream through
an existing identity-cipher protocol and storage callbacks. The writer uploads only encrypted
request/generation/ordinal-bound envelopes and returns a small manifest only after all uploads
succeed. Per-chunk size/digests and whole-file digest accompany unpredictable object references.
No account identity appears in object names and no raw payload appears in codec logs/errors.

The reader validates the trusted manifest's binding, closed schema, total size, contiguous order
and distinct references before accessing storage. It authenticates and checks each bounded chunk
before yielding it, and the full digest before yielding the last chunk. A failed late download
is still a partial stream; the future HTTP/proxy implementation must abort the transfer with
Content-Length enforcement. This module itself does not mark any request complete.

Ceilings: 64 KiB source/plaintext chunk, 256 chunks, 16 MiB total, 128 KiB ciphertext, 64 KiB
manifest. Smaller producer chunks can exhaust the chunk count earlier; the future worker must
coalesce at its chosen bounded size. A source chunk above the ceiling fails without upload, rather
than hiding a large source allocation through splitting. Cipher/storage errors are closed and
source generators close on failure. The storage adapter must itself enforce read bounds before
allocation; this module's post-read check cannot substitute for that control.

## Tests

Synthetic fake object storage and local authenticated encryption cover round trips, Unicode,
exact 16 MiB/256-chunk limits, empty/oversized sources and manifests, strict/required format fields,
foreign request/generation, duplicate/gapped references, size mismatch, swapped/missing/corrupt/
truncated ciphertext, wrong keys, invalid envelopes/base64, callback failures and cancellation.
Whole-file mismatch withholds the final chunk after an earlier verified chunk was consumed.
Failure after an upload returns no manifest and leaves unpublished cleanup to the caller.
An integration case streams the existing owned database projection through the format and verifies
complete equality without publishing an artifact or completing any request.

Run `make format lint test-unit test-data-exports openapi-check security`. No schema, migration,
HTTP/client contract or application registration changes; the existing API remains compatible.
Full hosted regression remains required before promotion.

## Pending lifecycle

The [large-history plan](E8_LARGE_HISTORY_EXPORT_READINESS.md) still needs durable jobs, snapshot
and lease correctness, private MinIO adapter bounds, atomic publication, orphan/expiry cleanup,
owner/recent-auth download, proxy cancellation/incomplete-transfer handling and browser acceptance.
No route or worker invokes this format yet. No new data retention, operational cost claim, privacy
approval, production provider or large-history acceptance is inferred from these tests.


## Native results — 9 October 2026

`make format lint test-unit test-data-exports openapi-check security` passed: 496 unit/contract
(including 38 artifact cases), five tooling and 15 PostgreSQL export cases. Generated contracts
remain unchanged. Python/TypeScript checks, documentation links/whitespace, Bandit, secret-boundary
and dependency audits pass, with no known vulnerabilities. Initial typing and required-format
constructor failures were fixed before this final run; no failing tests were disabled.

The preceding projection refactor's full native run passed 458 unit/contract and 198 integration
cases with one unavailable-MinIO failure. The artifact codec adds no registered runtime path;
full hosted regression, including actual services and browsers, remains required before promotion.
