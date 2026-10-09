# CI cold-start runtime and official image mirror

Date: 10 October 2026. Requirement: NFR-MNT-001; acceptance remains required.

Export head `ac4e10f` hosted run 37987018714 was cancelled by the 40-minute job
limit during `make e2e security containers`. The runner annotation explicitly says
the maximum execution time was exceeded. It is not a successful full run.
Timing head `b014070` run 37991389904 failed during service startup: Docker Hub
returned an unauthenticated pull-rate limit for Mailpit. Application tests were
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
