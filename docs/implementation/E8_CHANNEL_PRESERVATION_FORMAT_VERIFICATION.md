# ADR-057 private channel preservation format

Date: 19 October 2026. Requirements advanced: FR-ID-006, FR-WA-006, FR-OPS-003,
BR-010, NFR-SEC-002, NFR-MNT-001. These requirements are not newly closed by this
increment. Follow [ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md).

## Authority and implementation boundary

The human user explicitly approved the bounded synthetic implementation. This clears
the engineering design question only; it does not approve real-data processing,
production privacy/legal policy, raw-message retention or account erasure.

The first reviewable increment implements strict frozen internal evidence models,
canonical UTC timestamps, bounded authenticated encryption and closed diagnostics in
`services/channel_preservation_format.py`. Evidence accepts exactly the approved
link or conversation allowlist. Capture binding is separate and includes the new
snapshot UUID, request/owner, actual source link UUID, revision, source kind and opaque
observed-version value. The future transaction must produce and revalidate that
version. This format cannot assert ownership, authorization or source freshness.

Fernet is the existing approved primitive. HKDF-SHA256 derives a distinct key from
the existing identity encryption key with the fixed versioned purpose, zero separator
and canonical binding as info. Plaintext repeats the binding and format. Bounds are
2,048 plaintext and 4,096 ciphertext bytes; unknown/missing/duplicate/noncanonical
fields are rejected. Fernet's timestamp does not implement a retention decision.
Private representations omit identifiers/timestamps; ciphertext uses SecretStr.
All operational codec errors are closed fixed codes with suppressed input context.

No runtime imports/capture/storage/migration/flag/API/UI/permission are added. Existing
receipt kinds, learner export, deletion preview, STOP/unlink, expiry and dispatch remain
unchanged. Internal decoding supports integrity/recovery checks, not authorized human
retrieval. Production key management/rotation remains governed by the existing gates.

## Verification

`make test-channel-preservation-format` passes 82 socket-disabled synthetic cases:

- Both allowlists round-trip; ciphertext is randomized and within bounds.
- Every binding field rejects ciphertext substitution, including request/owner,
  source link/revision, observed version, kind and snapshot UUID.
- Wrong root key, identity-purpose ciphertext and ciphertext bit corruption fail closed.
- Unknown confidential fields, malformed revisions, naive dates, invalid instance
  copies, mutation of frozen values and wrong source/revision are rejected.
- Authenticated faulty producers cannot introduce another format, extra/missing or
  duplicate fields, wrong kind, noncanonical encoding or oversized plaintext.
- UTC normalization preserves microseconds and equivalent instants; representations
  and error messages omit payloads and keys.

The first focused lint run caught an overlong test assertion; formatting corrected it.
`make lint` passes Python/TypeScript lint, formatting and type checks (177 mypy source
files), all 156 Markdown link checks, 61-requirement coverage and whitespace checks.
`make test` passes all 1,022 unit/contract, 378 integration (992.69 seconds) and 35 tooling
cases. Existing Starlette and tooling module-type warnings remain;
the socket-guard warnings come from intentional network-denial tests.

`make openapi-check` passes with no generated contract diff. `make security
security-source` passes Bandit, local secret checks, Python/JavaScript dependency
audits and Gitleaks. `make containers`, application-profile Compose up with `--wait`,
and `make container-smoke security-containers` pass; all eight services are healthy,
synthetic worker/export/metrics smoke passes and API/web images have zero HIGH/CRITICAL
findings. No real model or messaging provider is called.

Exact source `25b44b1` passes complete hosted
[39176205670](https://github.com/Jotham566/kasoma/actions/runs/39176205670), including
the full backend/browser/security/recovery/image/service pipeline. This verifies the
private format increment; no usable capture or full ADR-057 application acceptance is
claimed. The documentation-only closeout preserves the exact application tree.

Subsequent capture development exposed an existing conversation timestamp defect with
an advancing clock: updated_at and its exact 24-hour expiry used different clock reads.
Two deterministic regressions fail on this source; the correction and real-time
conversation browser coverage remain under separate capture-branch verification. Prior
fixed-clock fixture acceptance does not prove real-time channel acceptance.

## Next complete application slice

Implement default-disabled exact source inspection/capture with independent recent-OTP
ADMIN claim checks, request-owner lock then channel lock, exact version validation,
atomic immutable metadata/encrypted body/finite decision/audit/safe outbox and exact
idempotency. The identity transaction helper intentionally commits IdentityError for
rate/OTP accounting; capture must use an explicit rollback/savepoint boundary so a
late failure cannot commit partial evidence. Add independent SQL ownership/immutability and finite disposal guards,
multi-decision release/expiry cleanup without starvation, safe capability discovery,
preview inventory and accessible operator controls. Preserve all STOP/unlink/relink,
withdrawal and expiry paths. Verify clean/upgrade/restricted-login/populated recovery
and full channel/hold/browser/security suites before claiming usable preservation.

Full preservation coverage, accountability expiry, legal sufficiency of omitted raw
material, destructive erasure authority and production release gates remain open.
