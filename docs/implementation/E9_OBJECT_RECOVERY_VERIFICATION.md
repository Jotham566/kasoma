# E9 isolated database and private-object recovery - candidate

Requirements: NFR-REL-002, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-065](../decisions/ADR/065-isolated-database-object-recovery.md).
Status: final local engineering/real recovery checks pass; own complete hosted verification pending.

## Scope and evidence

The older [logical drill](E9_RECOVERY_VERIFICATION.md) explicitly does not prove object
storage recovery. The separate make recovery-objects command creates fresh source and
destination PostgreSQL/pgvector and MinIO services using approved local image IDs and
bounded tmpfs, random loopback ports and generated private credentials/keys. It migrates
and populates the original synthetic fixture only. No configured developer data is read,
copied, restored over or deleted. Existing services remain running.

The fixture's already frozen ciphertext is uploaded to actual source MinIO and verified
using PrivateExportStorage and the ordinary authenticated artifact codec. Its in-memory
object map is then cleared. Private temporary database/object backups are taken. Both
owned source services are stopped and verified stopped before restoring from those files.
The same generated database name, search path and cryptographic keys preserve storage
scope on the independent destination; no storage-scope override is added.

The passing real local rehearsal restores 69 tables/686 rows and one encrypted object
(42,084 ciphertext bytes), in 151ms for database/object restore. Source services are
unavailable throughout verification. Inventory equality, pgvector, immutable guards,
stripped retirement execution denial, encrypted answer/result/preservation and exact
frozen export bytes pass. Missing and corrupt destination object probes fail closed;
original ciphertext is replaced and successfully reverified after each probe. Cleanup
reports no failures. This timing covers this fixture only; production_rpo_rto remains false.

The fixture originally publishes through its existing in-memory synthetic transport;
source MinIO is populated and independently verified before backup. This drill is not
an end-to-end worker publication or HTTP delivery proof; those remain covered separately.
It does not establish concurrent snapshot consistency, managed 35-day PITR, regional
copies, escrow, production recovery permissions, RPO/RTO or release approval.

## Retained failures and corrections

- Initial focused run: 42 pass, one failure. A partial-creation test accidentally inherits
  the test-schema database URL and is correctly refused before Docker. Fix its declared
  local profile; do not loosen profile validation.
- Initial real attempt: image resolution fails before creation, cleanup empty. The running
  MinIO service references an unavailable historical image ID after local recovery.
  Resolve the approved configured tag to its present immutable local ID, never pull or
  silently substitute a provider/image. Tests refuse an unapproved configured tag.
- Next real attempt: database/object restore reaches evidence verification but fails,
  cleanup empty. Inspection finds the old read-only preservation verifier requires a
  dst-name database, whereas namespace-preserving restoration needs the exact src-name
  on an independent server. Add an explicit generated exact-name read-only option and
  verify current_database; default verification/capture guards remain unchanged.
- The subsequent real rehearsal passes as recorded above. No failed attempt is a pass.

## Contract controls and final gates

make test-recovery-objects passes 50 controls in0.49s. They cover unsafe profile/name/image
rejection, private environment arguments, bounded tmpfs and loopback ports, exact returned
creation ID and ownership label, refusal of persistent mounts, partial-start cleanup,
ambiguous-create reporting without adoption, private bounded backup files and offline
restoration, changed lengths/acknowledged bytes, missing/corrupt read failures, exact
read-only preservation names and restored fixture logging state. Mocks are safety
controls, not the real recovery result.

Initial mypy passes202 source files. Final quality/contracts/build, full unit and existing
recovery/guard controls, security/source checks, final real rehearsal and own full hosted
pipeline remain pending. CI will run the standalone command after the unchanged logical
drill; neither pending parent run accepts this new tooling/workflow/test tree. Normal
application image behavior and HTTP/generated contracts are unchanged.

## Final local source verification

The final focused suite passes59 controls in0.50s, including readiness backoff,
verified source shutdown, generated keys/default-disabled flags and closed Docker
failure categories with diagnostic/credential canaries. Final make lint openapi-check
build test-unit passes: 1,239 unit/contract, 35 tooling,202 typed source files;502
integration cases deselected and three existing TestClient/network-block warnings.
make test-recovery-role-cleanup passes98 cases; make test-channel-preservation passes
105 contract and34 actual PostgreSQL/role cases (132.71s integration). The existing
default opposite-stage preservation refusal remains covered and unchanged.

make security security-source passes dependency/source checks with no known vulnerable
dependencies or leaked secrets. Final source real make recovery-objects passes69 tables/
686 rows/one42,084-byte encrypted object in147ms, sources stopped, exact scope,
all integrity/failure probes and cleanup empty. An intermediate real repeat passes196ms;
the unchanged logical make recovery-drill also passes69/686 in325ms. These are separate
fixture measurements, not production recovery targets.

A later attempt during concurrent normal image rebuilding fails CREATE_OWNED_SERVICES
and reports one uncertain generated destination-object name. Inspection of that exact
reported name confirms it does not exist; no adoption, prefix scan or cleanup sweep is
performed. Its underlying create failure is not established. Add closed Docker failure
categories (image unavailable, name conflict, storage full, daemon unavailable, timeout
or generic failure) without echoing diagnostics. The subsequent serialized final source
rehearsal passes147ms as above; this does not establish the earlier failure's cause.

Normal image/security/container smoke passes with eight healthy services; after final
tooling diagnostics are added, repeat the image/source smoke before publication so no
image acceptance is inferred for files captured at an uncertain build time. Own complete
hosted execution of this exact tooling/test/Make/workflow tree remains required. Parent
OTP complete hosted39304052749 accepts only ceee401, and metric-loss39308594889 accepts
only its own b5557a3 source if it completes successfully.

Final repeat make containers security-containers container-smoke exits zero after
the final tooling source changes. Owned export/request/model probes pass and all
eight preview services remain healthy. Only documentation changes follow this
checked tooling/test/Make/workflow tree before the candidate commit.

## Verified parent integration

OTP sourceceee401 passes complete hosted39304052749 and is published with Markdown
closeout to main557f90fb02b2557cdd4ff8d6929e068cb4145153. Remote SHA/ancestry are
verified before its owned branch is removed locally/remotely. Integrating main into
this recovery candidate changes Markdown only relative to locally checked a4152b8.
Four documentation conflicts retain both acceptance and candidate histories. No
new runtime/test/workflow change follows those passing local checks. The pending
metric-loss remote b5557a3 remains unchanged for hosted39308594889.
