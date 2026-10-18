# Offline evaluation-report comparison verification

18 October 2026. Candidate ADR-052; FR-GRD-003/004, FR-OPS-002, NFR-MNT-001.
Scope: read-only comparison of existing synthetic short-text report-v1 artifacts.
No model/provider/evaluation call, application API, database or learner behavior changes.

## Implemented boundary

Strict versioned reports bind benchmark digest/version/case count, task/output schema,
metric policy, prompt/adapter/model/runtime/hardware/settings and complete outcome
counts. Local metadata requires the supported M4/16 GB class, digest, Q4/Q5 quantization,
license reference and Ollama version. Hosted free-evaluation metadata requires declared
terms and observed quotas/rate-limit counts. All are declarations, not proof of genuine
benchmark truth, sanitation, licensing, qualification or academic approval.

Scored cases require the dual-pass call lower bound; requests stay within declared
ceilings and the three-request-per-case ceiling. Unknown tokens/cost/latency remain null.
Every planned case stays in agreement denominators; fallback/failure/safety/unrun cases
cannot be hidden. Comparison requires matching frozen evidence/schema/policy, while
model/prompt/configuration differences are explicit closed flags. Output excludes
arbitrary labels and always states academic approval/scoring are not established/enabled.

Read at most 512 KiB from regular local files, rejecting final symlinks, special files,
duplicate JSON keys, invalid/coerced/non-finite values, unknown private fields and
incoherent counts. Nonblocking open plus fstat avoids FIFO hangs. CLI errors never echo
paths, file excerpts, validation errors or exception messages. No provider SDK is imported.

## Evidence

Initial format/test syntax and a local-profile fixture missing the newly required terms
reference failed during development; both are corrected without weakening validation.
Current `make format lint test-unit openapi-check security security-source` passes
881 unit/contract and 35 tooling cases. Bandit, source/secret scanning and both
Python/JavaScript dependency audits pass. Thirty-seven
new contract/reader/CLI cases include privacy canaries, unknown usage, all-fallback and
unrun outcomes, cross-provider declarations, mismatched benchmarks/schemas, symlink/FIFO,
malformed/duplicate/oversized input and deterministic safe CLI behavior.

The actual `make eval-compare` invocation on two original synthetic metadata files
passes, retaining the 10-case denominator (0.7/0.8 exact fractions) and explicit
changed-prompt flag. Both academic-approval/scoring fields remain false. No inference, corpus or learner data is involved. Full hosted
acceptance remains required before promotion. No migrations, browser regression or
service changes are applicable to this pure offline slice; prior API/worker/UI evidence
remains separately recorded. Local and Gemini evaluation still fail closed pending their
complete benchmark/provider implementation; Gemini evaluation has not been run.


## Hosted promotion

Complete run [39151730479](https://github.com/Jotham566/kasoma/actions/runs/39151730479)
passes at `17abb2d`; source is promoted to main and both report/navigation branches are
removed locally/remotely. This does not change the separate genuine release gates.
