# E4 synthetic short-text validation evidence

Requirements: FR-GRD-003/004/005 (partial, offline foundation).
Decision: [ADR-040](../decisions/ADR/040-short-text-candidate-validation.md).

`services/short_text_validation.py` validates strict candidate JSON against a version-pinned
synthetic rubric and supplied response. `tests/contract/test_short_text_validation.py` covers
40 cases, including malformed/duplicate JSON, strict finite scores, complete rubric criteria,
maximum/sum bounds, exact excerpts, authored feedback, misconception allowlists and caller flags.
There are no database writes, HTTP routes, model calls or learner scores in this slice.

`make format lint openapi-check test-unit` passes 357 unit/contract tests and five tooling checks.
The 162 existing integration cases are deselected by this unit command, not claimed as run.
HTTP contracts are unchanged. Native PostgreSQL/Docker remains unavailable as documented in
[channel operations evidence](E8_CHANNEL_OPERATIONS_VERIFICATION.md). No inference evaluation
was requested or executed. Full short-text acceptance remains blocked on the academic and
integration gates in ADR-040 and the [release register](RELEASE_GATES.md).

A quote check establishes source provenance only. The adversarial fixture verifies that embedded
instructions cannot alter the validator's schema/point bounds; it does not establish detection
or model resistance to prompt injection. Semantic grading validity remains an expert benchmark gate.

`make security` also passes Bandit, local secret checks and both dependency audits.

## Hosted acceptance

Commit `3b74f5b` passed [CI 37221835579](https://github.com/Jotham566/kasoma/actions/runs/37221835579):
357 unit/contract and 162 integration tests (519 Python), 20 browser and five tooling checks.
Setup, clean migrations/seed, lint/types/contracts/build, security audits/scans and container smoke
all passed. Promoted to main; the completed validation branch was removed. This validates the
offline foundation, not academic agreement or learner short-text enablement.

## Explicit criterion material follow-up

The synthetic context now also requires criterion_text, acceptable_evidence, common_errors and
prohibited_inferences, as specified by the domain rubric model. Text is trimmed, nonblank and
bounded to 2,000 characters; each list is bounded to ten entries. Acceptable evidence must have at
least one entry. Errors/inferences require explicit lists but permit an authored empty list rather
than inventing content. These are internal synthetic resource bounds, not an approved academic
eligibility policy. Repr and validation-error strings omit input material.

Thirteen new cases verify required fields, whitespace/size/list limits and redaction. Existing
candidate score/provenance/context/flag checks still apply. Both independent fake passes receive
the same complete criterion material under distinct synthetic v2 prompt versions. The current
local `make format lint openapi-check test-unit` run passes 413 unit/contract and five tooling
checks. Hosted full regression is pending; approved persisted rubrics, calibration and learner
integration remain required. No HTTP schema, database migration or architecture changes.
