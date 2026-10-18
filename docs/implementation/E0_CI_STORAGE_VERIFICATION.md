# Disposable CI storage verification — candidate

19 October 2026. NFR-MNT-001; supporting the existing security and release checks.
[ADR-059](../decisions/ADR/059-disposable-ci-runner-storage.md) records the bounded profile.

## Failure and scope

Hosted 39167600610 at 978ab30 passes 918 unit/contract, 373 integration and five
15-case browser batches, then ends with the runner diagnostic `No space left on device`.
It is failed evidence; the remaining browser/security/image/smoke gates are unverified.
No disk snapshots establish which component exhausted space. Do not infer a specific
cause or accept the run by combining its partial results with another incomplete run.

The proposed correction reclaims only preinstalled .NET/Android SDK roots in the exact
owned disposable Ubuntu 24.04 X64 hosted job. Default invocation only reports root usage.
Preparation requires explicit hosted context, Linux/release/root/workspace/temp and
symlink-safe removal checks. No target/capacity CLI overrides, user path, Docker prune,
volume reset, local SDK cleanup, production service or application data mutation.
The workflow keeps all existing checks and adds preflight/phase capacity snapshots and
always-run read-only diagnostics. Initial free-space gate is 24 GiB; later read-only
phase checks require 8 GiB. These engineering budgets are not production SLOs.

## Executed local checks

`make format test-ci-storage test-unit lint openapi-check security security-source
ci-storage-check` passes: 22 isolated safety tests, 940 unit/contract and 35 tooling cases,
strict Python/TypeScript lint/types/format, generated contract consistency, read-only
local capacity check and dependency/source scans. Safety tests cover environment and
host mismatches, direct/parent/looping symlinks, non-directory targets, no partial removal
on failed validation, only synthetic SDK roots removed, capacity failure, read-only
modes, actual subprocess refusal and rejection of path/threshold override arguments.
No real SDK directory is removed locally.

Production application code is unchanged by this correction. Earlier complete local
application verification is 378 integration cases, actual restricted logins, 65-table/
648-row logical recovery, source/dependency/image security and eight-service smoke.
The full browser matrix also passes 93 standard plus 12 short-text executions after
replacing the formerly unimplemented Audit-link absence guard with an exact route
assertion. Role denials, learner/staff navigation separation, axe/reflow/touch checks and
real authenticated audit tests remain. The full Chromium target separately passes
all 31 cases; no assertion is relaxed to permit denied access.

Hosted acceptance on the complete corrected source remains required. The failed run
is retained at `.local/hold-delete-clock-hosted-full.log`; SDK guard/suite evidence is
in `.local/ci-runner-storage-*.log`. Physical/branded browser, production recovery,
academic/privacy/provider approval and complete preservation gates remain separate.
