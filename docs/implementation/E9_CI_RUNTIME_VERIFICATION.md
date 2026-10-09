# CI cold-start runtime and official image mirror

Date: 10 October 2026. Requirement: NFR-MNT-001; acceptance remains required.

Export head `ac4e10f` hosted run 37987018714 was cancelled by the 40-minute job
limit during `make e2e security containers`. The runner annotation explicitly says
the maximum execution time was exceeded. It is not a successful full run.
Timing head `b014070` run 37991389904 failed during service startup: Docker Hub
returned an unauthenticated pull-rate limit for Mailpit. The standalone content UI check passed, but the full backend regression was
not reached by that run. Neither run permits main promotion.

## Changes

- Bound the complete hosted job at 90 minutes for clean browser/service installation,
  expanded integration tests, all browser engines, image builds and scans. No test,
  application timeout, latency threshold or verification step is removed or relaxed.
- Cache only `.local/browsers`, keyed by OS, architecture and the exact pnpm lockfile.
  The pinned installer still runs; cache misses cannot skip tests. No environment file,
  database, inbox, trace or application build is cached. GitHub's official cache action
  v6.1.0 is pinned to `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` and uses Node 24.
- Use the publisher's official GHCR Mailpit mirror only through the CI Compose override.
  `docker buildx imagetools inspect` confirms both registries' v1.29.2 OCI index:
  `sha256:030f06031ce5c60913ac9363da1ab0d4be6fd2a78147dd0e1ca0fcac665d6b34`.
  The override pins that digest. AMD64 manifest is
  `sha256:e09b9e78336e0e8c2174790ea5ce7587de986884c5640a6ae1deb1ef23c70f5f`;
  ARM64 is `sha256:f6e751f85b3ecf75c4550b6432ce49de0ac87413fe26937308d35ade3d3fdcfb`.

This changes CI artifact transport, not application technology, Mailpit version,
production provider selection or an accepted architectural decision. Other existing
Docker Hub images still depend on registry availability. No registry credential or
production cloud service is introduced. Native Compose and its running inbox remain unchanged.

## Verification

Run `make check-ci-profile` for quiet validation without replacing services. Pull
the exact mirrored digest and run its version command, then repository formatting,
lint/docs and source checks. A new exact-head hosted run must execute the complete
pipeline; local validation does not prove hosted acceptance.

Local validation passes: `make check-ci-profile format lint security-source`, including
types and 120-document link/whitespace coverage. The exact mirrored digest pulls
successfully; an isolated `--network none` container running
`/mailpit version --no-release-check` reports v1.29.2 on linux/arm64 and exits successfully.
The existing eight services remain healthy. Evidence:
`.local/ci-runtime-remediation-checks.log` and `.local/ci-mailpit-mirror-pull.log`.
Hosted verification of this remediation remains pending.

Sources: [official Mailpit mirror documentation](https://mailpit.axllent.org/docs/install/docker/),
[cache action release](https://github.com/actions/cache/releases/tag/v6.1.0),
[pinned action definition](https://github.com/actions/cache/blob/55cc8345863c7cc4c66a329aec7e433d2d1c52a9/action.yml).

## Broader registry throttling follow-up

Run 37992401078 at `f9516f7` also failed during service startup, this time on
PostgreSQL's Docker Hub pull limit. The Mailpit mirror alone was insufficient.
The CI workflow now merges `https://mirror.gcr.io` into the disposable Linux runner's
Docker daemon configuration, validates it with `dockerd --validate`, and restarts
that runner's daemon with a 60-second bound before any application containers start.
Existing daemon settings and mirrors are preserved. Docker Hub remains the fallback
for cache misses; cache availability is not guaranteed. Native Docker is never changed.

Both upstream and public-cache manifest inspections for `pgvector/pgvector:0.8.2-pg16`
returned `sha256:00ba258a66dac104fd5171074a0084462a64a1369d8513f3d0a634e2f24d15bc`.
This is CI artifact transport, not a production cloud dependency or provider decision.
No application image version, test or security scan is relaxed. The new
`make ci-docker-config` command requires Linux GitHub Actions and an explicit temporary
configuration path; it never installs/restarts Docker itself. Tooling tests cover
preservation, idempotence, malformed inputs and refusal outside that CI environment.
Hosted startup and the complete pipeline still require verification.

Source: [public Docker Hub cache configuration](https://docs.cloud.google.com/artifact-registry/docs/pull-cached-dockerhub-images).

Local follow-up validation passes: `make format lint test-tooling check-ci-profile
security-source`, including all 35 tooling tests, types, document checks and no
source-secret findings. All eight native Compose services remain healthy. Log:
`.local/ci-public-cache-checks.log`. This does not prove hosted mirror startup.

## Authenticated pulls remain available when cache misses are throttled

Run 37993094065 at `bbe3b43` validated the daemon configuration, restarted successfully
and reported the configured public mirror. Build/browser/content checks then passed,
but PostgreSQL service startup still hit Docker Hub's anonymous pull limit. Thus the
cache is not sufficient evidence of reliable hosted service startup. Logs are retained
under `.local/ci-public-cache-hosted-full.log` and its failure counterpart.

The workflow now supports optional repository Actions secrets `DOCKERHUB_USERNAME`
and `DOCKERHUB_TOKEN` (read-only Docker Hub token). A step projects only availability;
credentials are scoped to that check and the official pinned Docker login action,
never to application containers or client variables. Login automatically logs out at
job completion. No credential values are printed, cached or committed. Fork runs without
secrets retain anonymous public pulls and every verification gate. Missing credentials
are not an application test pass; pull throttling remains a possible infrastructure failure.
The owner has been asked to configure these secrets securely; no token is requested in chat.

The [official login action v4.6.0](https://github.com/docker/login-action/releases/tag/v4.6.0)
is pinned to `dbcb813823bdd20940b903addbd779551569679f`; its action metadata uses Node 24.
This remains CI artifact access, not application provider selection or cloud provisioning.

Optional-auth workflow local checks pass: `make format lint test-tooling
check-ci-profile security-source`, including 35 tooling tests, types and no source
secret findings. Log: `.local/ci-registry-auth-checks.log`. Authenticated pulls cannot
be claimed until the repository secrets exist and a hosted run verifies them.
