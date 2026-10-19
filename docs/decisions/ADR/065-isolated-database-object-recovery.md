# ADR-065: Isolated synthetic database and private-object recovery

Date: 19 October 2026
Status: Accepted within delegated local engineering discretion; local synthetic verification passes; full hosted acceptance pending
Requirements: NFR-REL-002, NFR-SEC-002, NFR-MNT-001

## Decision and boundary

Retain ADR-042's existing logical drill unchanged. Add a separate local rehearsal for
its explicitly unproved object-storage boundary. The rehearsal uses the approved
PostgreSQL/pgvector and MinIO images declared by the approved local Compose configuration and already built locally,
resolved to immutable image IDs, with pull=never. It creates two fresh PostgreSQL
containers and two fresh MinIO containers. No configured database or bucket is copied,
queried for records, restored over or cleaned. No volume, cache, image or SDK cleanup.

Generate one unpredictable invocation suffix, fixed component names and ownership
labels. Only a successfully created container's returned full ID grants cleanup
authority; recheck its exact label before removal. Never discover cleanup targets by
name/prefix. Refuse production, remote or nonstandard local profiles before resource
creation. Keep database and object data on explicitly bounded tmpfs mounts, with no
host paths or named/anonymous data volumes. Bind random service ports to IPv4 loopback
only. Generate private credentials and encryption/lookup/signing keys per invocation;
pass child secrets via environment, not command arguments or diagnostic output.

Use the same generated database name on the two independent PostgreSQL instances.
The existing export storage HMAC includes database name and search path, so a renamed
database is not an equivalent restore. Preserve that scope and encryption keys while
changing only local service endpoints. Do not change storage_scope or add a scope
bypass. Create the normal minimal source owner before migrations; restoration strips
ownership/ACLs and must continue to deny retirement execution. Whole-container cleanup
removes only the newly owned cluster; no shared developer role cleanup is needed.

Migrate and populate the source using original synthetic fixtures and fake providers.
Publish their existing frozen export ciphertext into the fresh source MinIO, verify
it through the actual private adapter, then back up the database with matching local
pg_dump and save only exact manifest-bound ciphertext objects as private temporary
files. Stop and verify both owned source services stopped before restoring from
those files; do not read through to the source. Restore into the
fresh destination and verify exact inventories, selected immutable guards, pgvector,
encrypted answer/preservation evidence and unchanged frozen export bytes through the
normal adapter/codec. Remove and corrupt only owned destination fixture objects to
prove failures, then restore the original bytes and reverify. These fault probes are
not application deletion authority and do not touch shared storage.

Keep the temporary database dump mode0600 under ignored .local and remove it on exit.
Object bytes are already authenticated ciphertext; no plaintext export backup or public URL
is introduced. Bound object count/size to the existing artifact format. Reports expose
only fixed stages, counts, elapsed fixture restore time, booleans and owned cleanup
failures; no records, hashes, credentials, tokens, object keys or raw diagnostics.

## Acceptance and limits

Add tests for unsafe profiles, generated identities, immutable image validation,
loopback ports, private environment handling, partial creation cleanup, label/ID
mismatch refusal, bounded ciphertext copying and missing/corrupt object rejection.
Execute the real command locally and in hosted CI alongside all existing gates before
acceptance. Mocks alone cannot establish object recovery. Preserve the running preview.

This is local synthetic recovery preparation, not managed backups, 35-day PITR,
secondary-region encryption, credential escrow, production recovery authorization,
RPO/RTO, full disaster rehearsal or release approval. Object consistency covers this
quiescent frozen fixture, not concurrent production snapshots. No production provider,
new learner data, retention policy, erasure or account permission is approved. Rollback
removes the standalone tooling/CI target; existing application behavior is unchanged.

The existing preservation read verifier keeps its default dst-name restriction.
A separate explicit expected-source-name option accepts only the exact generated
src database name and checks current_database before reading. ADR-065 passes this
name only after its exclusive destination-container identity/loopback checks. It
changes no capture or data mutation guard. Fixture event logging is suppressed
only inside this standalone synthetic process and restored on exit; running
application observability is untouched.
