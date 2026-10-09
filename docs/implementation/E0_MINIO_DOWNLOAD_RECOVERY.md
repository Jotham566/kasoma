# E0 MinIO dependency-download recovery

Requirement: NFR-MNT-001; bootstrap reproducibility and existing source-integrity gates.
Status: verified in hosted CI 37923437046 at `04de7ea`, promoted to main. Native image download
remains incomplete; hosted acceptance does not establish native storage availability.

## Evidence and change

After Docker Desktop became available, native PostgreSQL/Redis, migrations and database suites
passed. The approved MinIO source archive passed its pinned checksum, but four Go module downloads
ended with unexpected EOFs. The build failed; it did not produce a usable storage service.

`infra/containers/download-go-modules.sh` tries `go mod download` at most three times. Every attempt
retains Go checksum enforcement and the existing proxy/toolchain configuration. A successful download
must pass `go mod verify`; verification failure is terminal. Exhausting download attempts returns a
failure. Interrupt/termination handlers stop the helper instead of deliberately retrying cancellation.
There is no checksum suppression, provider replacement, alternate source or success-on-error path.

The Dockerfile mounts project-specific locked Go module/build caches. Download, verification and
compilation share one build step so pruning a cache cannot skip the helper on a later compilation.
Only the compiled binary and upstream license enter the runtime stage. Compiler/base/source pins,
readonly module build, private local service bindings and ADR-019 remain unchanged. This is build
implementation resilience under the existing architecture, so no new ADR is required.

## Verification

Four tests execute the real shell helper against an isolated deterministic fake `go` executable:
immediate success, two failed downloads followed by recovery, three failed attempts, and terminal
verification failure without another download. They perform no real dependency or provider requests.

Run `make format lint test-unit openapi-check`, then `make services migrate seed test` and the
existing hosted container/security pipeline. An actual final-Dockerfile build and storage health
check are required; helper tests alone do not prove service availability or artifact integrity.
The first native cached retry began before combining the build steps; repeat `make services` against
the final Dockerfile before accepting the resulting service image.

Retries are bounded by attempt count, not a new application/provider timeout or availability SLO.
A continuing network interruption can still fail setup safely. Do not delete volumes, weaken
checksums, disable verification or replace the approved source release to make the command pass.
Native browser download timeouts/resets are separate; Playwright's own retry remains in progress.

## Hosted acceptance

[CI 37923437046](https://github.com/Jotham566/kasoma/actions/runs/37923437046) passed the actual
service build, migrations/seed, 431 unit/contract plus 184 integration cases (615 Python), five
tooling checks, 63 real-API browser executions and one isolated editor case. Recovery restored
54 tables/272 rows in 361 ms with pgvector/immutable guards and no cleanup failures. Lint/types,
contracts/build, restricted-role verification, dependency/source/image scans and container smoke
all passed. Cold question transfers were 191513/194257/193614 bytes across the three engines.
Commit `04de7ea` is on main; the completed branch was removed locally and remotely.
