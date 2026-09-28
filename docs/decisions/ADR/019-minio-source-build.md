# ADR-019: Reproducible local MinIO source build

Date: 28 September 2026
Status: Accepted within delegated engineering-foundation discretion
Requirements: NFR-MNT-001, NFR-SEC-001

The E4 main CI run 36391189987 failed before migrations because the pinned Quay
MinIO image returned HTTP 401. Docker Hub also denied the same release. A cached
local image must not conceal broken clean setup. No registry credentials or
unreviewed third-party mirror are introduced.

Retain MinIO and the existing local S3 interface, ports, credentials and volume.
Build the official release source at immutable commit
`07c3a429bfed433e49018cb0f78a52145d4bedeb` (resolved from the official
`RELEASE.2025-09-07T16-13-09Z` tag), verifying the archive SHA-256. Pin builder and
runtime image digests; use Go 1.27.1, `go mod verify` and readonly dependency mode.
Include the upstream license and source/revision labels. The source-build suffix
makes it distinct from the unavailable vendor binary. No MinIO source is modified.

Compose builds this local image through the existing `make services` command.
First setup needs package/source downloads, as before; subsequent builds use Docker
cache. No external storage/model/message calls occur. The Go toolchain is confined
to the image builder and does not become an application runtime.

Verify fresh build, readiness, bucket creation and existing S3 integration tests.
Keep the previous local image available for rollback without deleting volumes.
This is a local/CI artifact repair, not a production storage or cloud decision.
