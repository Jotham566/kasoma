# ADR-068: Fresh owned PostgreSQL services for synthetic browsers

Date:20 October2026 (Africa/Kampala)
Status: Accepted within delegated local engineering discretion; local browser/resource checks pass; full combined/hosted verification pending
Requirements: NFR-MNT-001, NFR-PERF-001/002, NFR-SEC-002 and NFR-OBS-001

## Evidence and decision

Catalog statistics for the configured local database estimate10842 namespaces. Read-only catalog estimates
include3,226,840 pg_class rows,15,456,539 pg_attribute rows and22,997,306 pg_depend
rows; five system catalogs occupy11,307,737,088 bytes including their indexes/TOAST.
These are metadata observations, not learner records or proof of a failure's cause.
The existing browser API adds another retained schema to this shared database each run.
Local Firefox reproduces a QUERY_CANCELLED/HTTP500, while exact source3e6175b passes
complete hosted39322035839. A separate numeric pointer transition also remains open.

Move the standard synthetic browser API's database into one freshly created local
PostgreSQL container per process. Retain its existing fresh e2e UUID schema, migrations,
seed, application code, fake providers, export fault controls and assertion/deadline
gates. Use the approved Compose PostgreSQL/pgvector image, resolved to its immutable
local ID with pull=never. No alternative database, cloud provider or application
architecture is introduced. The normal eight-service review stack remains running.

Extend ADR-065's existing OwnedServices guard with a closed browser purpose that permits
only source-db. Use a distinct generated browser name and ownership-label key, memory512m,
pids256, database tmpfs256m, random IPv4 loopback port and no persistent mounts. Unknown
purposes/components and nonstandard/remote/production profiles fail before creation.
Reject TCP/SSH Docker hosts/contexts before daemon commands. Context inspection reads
local metadata; pin the selected Unix socket in this harness process environment for
all creation/inspection/cleanup commands, removing the context override and restoring
the original environment afterward. Do not change the user's global Docker context.
Generate private database/encryption/lookup/signing credentials per invocation; pass
child credentials through environment/configuration, never command arguments/logs.

Only the returned full creation ID plus a matching invocation label permits cleanup.
Record that returned ID/invocation as infrastructure metadata for this run; no credential
or learner identifier is included.
Never adopt a pre-existing/name-conflicting resource or discover cleanup targets by
name/prefix. Ambiguous creation reports uncertainty without deleting by name. Use a bounded ten-second graceful API shutdown. Uvicorn re-raises SIGTERM after
restoring handlers; a test-only handler converts it to stack unwinding so owned finally
cleanup executes. This is a shutdown budget, not an increased API/test deadline. Always
attempt cleanup of exclusively owned services after startup failure and graceful API
shutdown; cleanup failure fails verification. No fallback to the configured review DB.
No developer schema, role, cache, image, SDK or volume is swept. Existing recovery
defaults and its standard55432 profile guard remain unchanged.

This removes accumulated shared catalogs as a dependency of the browser fixture; it
does not establish why any earlier request was cancelled or fix the separate pointer
failure by assertion. Do not increase SQL/client/test timeouts, add HTTP/test retries,
skip assertions or call providers. This is disposable synthetic test-resource cleanup,
not ADR-061 account erasure or authority over real/production data.

## Verification and rollback

Verify all existing recovery resource guards unchanged, plus browser-purpose isolation,
exact ID/label cleanup, uncertainty/collision refusal, profile/provider denial, private
environment handling, bounded startup and cleanup on failure. Exercise actual browser
startup and all existing engine journeys, confirm fresh catalogs and successful owned
cleanup while review services stay healthy. Run quality/unit/contracts/security/recovery/
image/service checks and complete exact-source hosted verification before acceptance.

Keep previous local failures visible and distinguish engineering acceptance from
production/device/academic/privacy gates. The dedicated configuration profile uses the standard API and inherits this isolation.
The separate short-text API retains its existing scope until separately assessed; do not claim this
first change covers every test runner. Rollback changes only the test entrypoint and
closed helper purpose; no application data or migrations need reversal.
