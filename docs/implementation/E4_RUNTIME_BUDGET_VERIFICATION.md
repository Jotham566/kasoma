# Runtime grading budget verification

18 October 2026. FR-OPS-004, FR-GRD-004, NFR-SEC-002, NFR-MNT-001.
The existing shared request/token/time budget is now operator-configurable only within
its unchanged hard envelope. Defaults remain three requests, 16,384 tokens and five
seconds. One validated snapshot governs both independent passes, optional repair and
pre-dispatch remaining deadline. Normal scoring remains disabled.

No new architecture/ADR, API/schema, provider, inference profile, personal record or
retention change. Existing ADR-041/050 controls remain. This is not a learner/day/fleet
quota or proof of token billing, academic calibration or approval.

Verification is running: invalid above/below-envelope settings; unchanged defaults;
actual FakeModelProvider request-repair exhaustion, zero-dispatch token starvation and
controlled monotonic deadline expiry; preserved encrypted attempt, no grade/mastery,
neutral retrieval and exact replay without new work. Run lint/types/contracts/unit,
flow/review/role/security/recovery and hosted acceptance before promotion.


## Local evidence

`make format lint test-unit test-short-text-flow openapi-check` passes 891 unit/contract
and 35 tooling cases plus 21 actual encrypted API/worker flow cases. Seven new settings
cases protect the envelope/defaults; three new fake-worker cases cover request repair
exhaustion, zero-dispatch token starvation and controlled remaining-deadline expiry.
Each preserves the saved attempt, neutral no-score/no-mastery outcome and exact replay.
No provider call is made by the token/deadline exhaustion paths.

`make test-grading-reviews test-runtime-role` passes 33 review cases and actual
restricted-login encrypted grading/review. `make security security-source recovery-drill`
passes Bandit, secret/source and dependency audits plus populated logical restore
(65 tables/616 rows, 310 ms, no cleanup failure). Genuine PITR/object recovery remains
unproved. Final rebuilt API/web images pass current HIGH/CRITICAL scans; all eight
services, scheduled synthetic private export/frozen retry and scoped metrics smoke pass.
Exact-source hosted acceptance remains required before promotion.
No browser/API/schema/migration change is made; default browser behavior is unchanged.


## Hosted acceptance

Complete hosted run [39157127637](https://github.com/Jotham566/kasoma/actions/runs/39157127637)
passes for exact source `f5f408e`. The source is on main and its merged branch is removed locally/remotely. All external academic/provider/privacy and actual scoring gates
remain; this verified engineering setting does not establish approval or billing truth.
