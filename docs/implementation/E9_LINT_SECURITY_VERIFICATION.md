# E9 lint dependency security verification

Date: 3 October 2026. Requirements: NFR-MNT-001, NFR-SEC-001 security gate.

The refreshed audit found GHSA-vfj7-8cjw-p6xm in braces 3.0.3, with no patched release.
[ADR-031](../decisions/ADR/031-lint-glob-security.md) records a narrow Next lint-only
replacement and compatibility patch. No runtime/data/API changes or audit exemptions.

## Checks

- `make deps-lock setup`: frozen installation passed with pinned Node/pnpm and existing
  environment preserved. An initial direct pnpm install correctly rejected the global
  Node version; dependency updates now have a repository-pinned command.
- `make format test-tooling lint security build`: formatting, plugin regressions,
  Python/TypeScript lint/types, dependency audits, Bandit, secret-boundary checks and
  native production web build passed. All five final tooling regressions and 223 Python
  unit/contract tests pass.
- Prior legal-hold evidence: 337 Python and 17 browser tests plus 22 final focused tests
  passed on 30 September. On 3 October, 223 Python unit/contract tests passed again.
- Docker-dependent services/source-scan retries failed because Docker is waiting for a
  macOS privileged-port configuration prompt. No Docker reset or data removal attempted.
  Hosted [CI run 37126531374](https://github.com/Jotham566/kasoma/actions/runs/37126531374)
  subsequently passed all setup/migration/seed, full tests/browser, source/container scans
  and container smoke steps. Commits ec53ac4 and b766266 are published to main.

Initial replacement testing caught path/automatic-directory-expansion differences.
The pinned patch explicitly configures compatible directory matching; tests exercise
actual Next helpers and lint rules, not a separate mock implementation. A hand-written
patch hunk failed validation and was regenerated from exact installed source before the
successful frozen setup. No compatibility failure was suppressed.

## Files

Makefile, pnpm-workspace.yaml, pnpm-lock.yaml, patches/next-eslint-glob.patch,
scripts/tooling.test.mjs, infra/containers/web.Dockerfile (copies the install patch), ADR-031 and its indexes, CHANGELOG.md, current sprint,
requirements traceability, local runbook and this report.

## Remaining gates

This repairs the dependency gate only. Full MVP implementation, approved academic content,
calibration, privacy/processor approvals, production provider selection, restore evidence
and pilot sign-offs remain required. No real learner data or external providers were used.
