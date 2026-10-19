# ADR-067: Versioned operational warning configuration

Date:19 October2026
Status: Accepted within delegated MVP engineering discretion; implementation pending
Requirements: FR-OPS-002/003, NFR-SEC-002, NFR-OBS-001, NFR-ACC-001,
NFR-LOC-001, NFR-MNT-001; API contract section9, bootstrap configuration section4.

## Gap, assumptions and scope

The approved contract lists PATCH /admin/configuration/{key} with a version and audit
reason. The current implementation exposes only startup Settings warning thresholds.
Implement that route for the15 existing OperationThresholds fields. This closed
allowlist is the implementation assumption where the generic contract leaves key names
unspecified. These numeric warning thresholds are internal operational configuration,
not secrets, academic weights/calibration, usage ceilings, consent/retention controls,
provider settings or feature activation. Existing hard dependency/high-priority alerts
remain unconditional. No new production provider or learner-data access is granted.

Add ADMIN-only GET /admin/configuration and an Operations-linked editor. Reads recheck
role; writes require current ADMIN and recent OTP, validated integer/range/closed reason,
Idempotency-Key and exact current version reference. SQL and service independently
validate the full closed numeric map. Unknown keys/fields fail closed. Preserve every
existing Settings range/default, including the initial retirement-warning derivation.
Runtime/academic usage budgets remain governed by their existing separate controls.

## Data, concurrency and retries

Add a singleton current pointer with an immutable random nonce and immutable
nonpersonal version rows. A fresh schema receives a distinct nonce; recovery preserves
it without changing the separate export-object scope. Version0 means
startup defaults, with no imaginary stored change time. Its reference hashes the singleton
nonce, version and complete resolved numeric defaults, so changed
startup settings invalidate a stale form. First successful edit freezes all effective
values into version1; thereafter API and worker resolve the same stored snapshot.

Lock the singleton row, recheck the exact prior reference, append one complete version,
append the existing AuditLog entry and advance the pointer atomically. No historic row
can be rewritten/deleted; direct SQL cannot commit an orphan/unaudited version or move
the pointer backward. Use database time for the version/audit event. A revert is another
reviewed forward version, never deletion of history. Current reads do not list historic
administrative actions or expose actor/learner/database identities.

Reuse the existing immutable AuditLog as exact mutation-receipt authority. Its opaque
UUID is derived through a purpose/immutable-nonce/actor/key-bound HMAC; raw retry keys and
new actor fields are not stored. Link it to the version, old/new references and closed
reason. Store a hash of the canonical command on the version. Replays reauthorize the
current actor/recent auth and verify that command hash before returning the original
recorded version, even if newer versions exist. A reused key with changed intent conflicts.
The receipt remains existing material administrative audit evidence under its current
retention/hold obligations; no new personal-data retention schedule is invented.

Global version rows contain only numeric settings, revision/reference/hash, changed key,
closed reason and database timestamp. They have no user/learner/contact/answer/token
field or arbitrary note. Existing AuditLog actor linkage remains accountable staff
provenance; update inventory/disposition documentation and preserve the unapproved
ADR-061 boundary. These additions do not authorize staff/learner erasure or new support
access. They do not silently rewrite old audit rows or change their retention.

## Warning resolution and compatibility

The existing OperationsView.thresholds continues to contain values actually used for
that snapshot's warning evaluation. Resolve saved values inside the existing database
sampling boundary. If configuration cannot be loaded/validated, apply validated startup
warning defaults, expose an additive explicit UNAVAILABLE_DEFAULTS_APPLIED state and
configuration-unavailable warning. Never claim those defaults are the saved version.
Core database/dependency/high-priority alerts remain effective. The dedicated configuration
GET fails unavailable instead of offering an editable fake version. This fallback only
controls warnings, never grading, privacy, authorization, quotas or a processing decision.
The existing schema remains compatible; generated contracts describe the additive state.

## Acceptance and rollout

Tests cover every key/range and boolean/string rejection, denied/nonrecent/revoked roles,
exact/conflicting/concurrent retries, stale references including changed defaults, atomic
rollback/audit, immutable/deferred SQL guards, current-reader/worker parity, unavailable
fallback and unconditional alerts. Browser checks cover edit/retry/conflict/offline,
keyboard, narrow layouts and accessibility using deterministic fake providers.

Verify clean/additive migration, actual restricted logins, populated logical/object
recovery, generated contracts, quality/security/images/services and full own hosted
regression before main promotion. Do not infer acceptance from other live source heads.
Keep current Docker preview available through a forward additive rollout. Rollback
requires compatible readers or explicit startup-only warning mode with a visible source;
never delete stored versions/audit. No account closure, production or academic gate changes.

## Additional implementation boundaries

Require both configuration tables in current_schema before any ORM lookup, so a partially
migrated schema cannot read a trailing public configuration through search_path.
After the first stored version, SQL independently requires the exact prior reference
and allows only the declared setting to differ from the saved snapshot. Initial defaults
remain service-validated because the database has no authority over runtime Settings.

The local preview had already applied0043 before this additional guard was identified.
Use forward-only0044 to replace that function; never rewrite the applied0043 function.
No tables/columns/retention or scope changes are introduced by0044. Browser mutations run
in a separate fresh fake-provider schema so unrelated warning tests cannot race global
settings. make e2e includes that three-engine profile, preserving all existing profiles.
