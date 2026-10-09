# E8 private export storage boundary

Requirements: FR-ID-006, NFR-SEC-001/002, NFR-MNT-001.
Architecture: approved local MinIO adapter plus
[ADR-047](../decisions/ADR/047-private-export-artifact-format.md).
Status: fake-adapter checks pass; actual local-service acceptance pending.

`services/export_storage.py` binds operations to a fixed private export prefix and UUID generation/
object references. It reuses the approved local settings, private container and bounded provider
connection/read timeouts with retries disabled. Uploads require bounded ciphertext and close their
in-memory stream. Reads require a valid Content-Length within 128 KiB before reading at most the
announced size plus one byte; short/overlong bodies fail. Responses always close and release their
connection, including malformed headers, read failure and cleanup exceptions. All failures expose
closed codes; provider diagnostics, object locations and payloads are not logged or returned.

The adapter creates no bucket, lists no objects and exposes no public URL. Removal accepts only
an exact UUID key; its caller must authorize lifecycle cleanup. Neither the adapter nor format is
registered in learner routes or workers. Read-time expiry, authorization, publication, orphan
sweeps and retries remain future lifecycle policy. Socket timeouts do not establish a complete
worker or download wall-clock deadline; those remain explicit in the
[ADR-048 proposal](../decisions/ADR/048-asynchronous-owned-export-delivery.md).

## Checks

Twenty-four fake-provider cases verify exact maximum sizes, bounded read amounts, invalid/missing/
negative/oversized/Unicode lengths, truncation/extra bytes, cleanup on read/close/release failure,
write bounds, UUID-only keys and redacted provider errors. The integration case creates two
synthetic encrypted objects with fresh random references, verifies the complete codec round trip,
anonymous denial and cross-generation failure, then removes only its own objects and verifies
absence. It never lists/deletes a bucket or touches pre-existing developer objects.

`make format lint test-unit` passed 520 unit/contract plus five tooling cases, Python/TypeScript
checks and documentation links/whitespace. `make test-export-storage` passed 24 fake cases but
failed the actual MinIO case because native port 9000 is unavailable after dependency downloads
exhausted their retries. This is not accepted as an actual-storage pass. Hosted full-stack CI
must pass the real case before promotion. Initial duplicate test-module names were corrected;
no test was skipped or disabled.

No public API or migration changes. Existing generated contracts must remain identical and
security checks must pass. Update this report with actual CI evidence before promotion.


Final `make format lint test-unit` passed all 520 unit/contract and five tooling cases.
`make openapi-check security` passed unchanged generated contracts, Bandit, secret-boundary
checks and both dependency audits, with no known vulnerabilities. The actual MinIO test remains
an explicit native failure; no application acceptance is claimed from these static/fake checks.
