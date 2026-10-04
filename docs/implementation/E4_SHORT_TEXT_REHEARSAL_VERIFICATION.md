# E4 synthetic dual-pass rehearsal verification

Requirements: FR-GRD-003/004/005, NFR-SEC-002 (partial foundation).
Decision: [ADR-041](../decisions/ADR/041-synthetic-short-text-rehearsal.md).

Files: `services/short_text_orchestration.py`, additive contracts/fixtures in `services/providers.py`,
and `tests/contract/test_short_text_orchestration.py`. Fifteen fake-only cases cover independent
passes, criterion/total disagreement, repair on either pass and global repair exhaustion,
provider exceptions/fallback, flags and input bounds, token/request ceilings and deadline boundaries.

`make format lint openapi-check test-unit` passes 372 unit/contract and five tooling tests.
An initial line-length failure was fixed before this passing run. HTTP contracts are unchanged;
no migration was added. The 162 integration tests are deselected by the local unit command.
Hosted full regression remains required before promoting this commit. Native Docker/PostgreSQL
is unavailable; no inference or evaluation command was executed.

The fake returns known fixtures; this proves control flow, not model intelligence, prompt safety,
academic calibration, hard preemption of a real adapter or learner fallback. Both agreement and
failure retain automatic scoring disabled. See the [release gates](RELEASE_GATES.md).

Bandit initially interpreted `pass_name` as a password variable. Renamed it to `evaluation_order`;
no security rule was disabled and no credential was present. Repeat security checks are required.

After the rename, the full local formatting/lint/types/contracts, 372 unit/contract and five tooling
checks pass. `make security` passes Bandit, local secret checks and both dependency audits.
