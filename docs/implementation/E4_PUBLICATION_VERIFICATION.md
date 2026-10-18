# Publication and audit assignment verification

Date: 10 October 2026. Requirements: FR-GRD-003/004, FR-MST-001, FR-ID-006,
NFR-SEC-002 and NFR-REL-002. Decision:
[ADR-050 proposal](../decisions/ADR/050-short-text-pending-and-eligibility.md).

## Implemented boundary

Migrations 0030/0031 add an immutable per-grade publication binding and audit assignment,
with monotonic per-band aggregate counters. SQL serializes publication on the band,
checks enabled state and definitive-grade scope, assigns the ordinal and creates a
required audit atomically. Sampling selects the first and every subsequent tenth grade,
so every prefix has at least 10% assignments. This does not prove completed expert audit.
Replay preserves the original record; rollback restores counters and assignments.
A different-band replay is rejected. Invalid or disabled publication cannot consume
an ordinal. Counters cannot be reset or advanced without their publication/audit.

Personal records receive owned minimized exports, diagnostic sealing, deletion-impact
inventory and exact-record holds. Calibration IDs, ordinals and sampling flags are
excluded from learner exports. Audit holds use the assignment UUID; publication holds
use the attempt UUID. Hold release preserves record immutability. Existing retention
requirements still need an approved processor; these guards do not authorize indefinite
raw-answer retention or deletion.

The restricted login can insert publication/assignment records and update guarded
counters. It cannot rewrite/delete those records or activate bands/change approval
metadata. The recovery fixture's owner-only synthetic activation is restricted to
generated recovery-source database names. No production role deployment or approval
authority is supplied by these verification fixtures.

## Executed checks

| Command | Result and scope |
| --- | --- |
| `make migrate` | Additive head migration passes; no developer database reset |
| `make test-grading-publications` | 12 PostgreSQL cases pass: concurrent duplicate, sampling, rollback, invalid timestamp/missing grade, scope/replay mismatch, forged audit, disablement, immutable counters/records, ownership/export/inventory, exact holds and diagnostic sealing |
| `make test-grading-bands` | 13 cases pass, including populated 0028-to-head upgrade/replay, preserved band/history and empty counter backfill |
| `make test-legal-holds` | 19 existing preservation cases pass |
| `make test-runtime-role` | Real restricted-login case passes, including new publication and denial assertions |
| `make recovery-drill` | 63 tables / 302 rows, 282 ms restore, exact inventory and immutable guards verified, cleanup failures empty |
| `make build test-web-privacy` | Six executions pass across Chromium, Firefox and WebKit |
| `make format lint openapi-check` | Formatting, lint/types, links/whitespace and generated contracts pass |
| `make containers security-containers container-smoke security-source` | Rebuilt image scans, eight-service health, owned export/metrics smoke and source-secret checks pass |
| `make test` | 780 unit/contract, 35 tooling and 291 integration cases pass; final focused additions verified separately |
| `make security` | Retry passes: no known dependency vulnerabilities; initial attempt timed out contacting PyPI |

Logs: `.local/grading-publication-final-focused.log`,
`.local/grading-publication-upgrade.log`, `.local/grading-publication-privacy-checks.log`,
`.local/grading-publication-role.log`, `.local/grading-publication-recovery.log`,
`.local/grading-publication-browsers-rebuilt.log`, `.local/grading-publication-containers.log`
and `.local/grading-publication-full-regression.log`.

The first test run failed collection due to an incorrect test-only projection import;
corrected before passing focused checks. The first browser run used a stale production
build and failed the new hold option-list assertion. Rebuilding resolved it without
weakening the assertion. The full backend run was collected before the final diagnostic,
scope and upgrade assertions; read it together with the final focused checks. Exact-head
hosted acceptance remains required before promotion.

## Remaining integration and release work

Tests use valid synthetic objective grades. No SHORT_TEXT assignment guard is bypassed,
and no synthetic fixture is academic approval. The future worker must call publication
inside the same transaction as grade/mastery creation after current authorization,
consent, content and eligibility checks. Independent blinded review, rolling audit
results, automatic band disablement, full worker/learner fallback and genuine academic
calibration remain required. No learner short-text delivery or external inference is enabled.

## Resumed verification — 18 October 2026

The prior regression is terminal: all tests passed; its security step failed on a PyPI
read timeout. `.local/grading-publication-security-retry.log` confirms the complete
security retry passed. No dependency, threshold or scanner was changed. The baseline
`46a0f8a` passed hosted run 38034913518 and is now on main; merged historical branches
were removed. The publication changes require a new hosted run before promotion.

## Verified main promotion — 18 October 2026

Publication commit `bd00c49f8e212235b51ba456ec8c6da571b18917` passes the full hosted
pipeline [39137945443](https://github.com/Jotham566/kasoma/actions/runs/39137945443).
It has been fast-forwarded to main and pushed. Merged calibration, publication,
request-timing and export branches were removed locally and remotely. This closes the
publication storage slice only; the learner-flow and independent expert-review gates
above remain separate.
