# ADR-052: Bounded offline evaluation-report comparison

Date: 18 October 2026
Status: Proposed for synthetic engineering; acceptance pending
Requirements: FR-GRD-003/004, FR-OPS-002, NFR-MNT-001

## Decision and boundary

Implement the prescribed `make eval-compare` command as a read-only local comparison
of two strict versioned synthetic short-text reports. Record frozen benchmark digest,
version and case count; task/output-schema/metric policy; exact model/adapter/prompt/
inference settings; runtime/hardware and declared weights/license/terms digests; observed hosted quotas
and rate-limit counts; complete outcome counts; latency and nullable
usage. No prompt, answer, identity, raw output, secret or free-text diagnostic field.
The initial contract supports short-text grading reports only; it does not pretend to
implement evaluation/reporting for the other gateway tasks.

Require matching benchmark digest/version/case count and task/output schema/metric
policy. Prompt/model/configuration changes are legitimate comparison subjects and are
reported explicitly as closed changed-field names. All planned cases remain in quality
denominators; unrun, low-confidence, invalid, provider and safety outcomes never become
correct by exclusion. Persist the two-pass lower bound for scored cases and maximum
three-request-per-case ceiling, with observed usage not exceeding the declared ceilings.
Preserve unavailable usage as null. Input metadata is declared
report evidence, not proof of academic truth, rights, calibration or approval.

Read at most 512 KiB per regular local file. Reject final-path symlinks, special files, duplicate
JSON keys, non-finite/coerced values, inconsistent counters and unknown fields. Return
closed errors without paths, file excerpts or exception messages. Output only safe
report IDs, aggregate metrics and closed flags; do not echo arbitrary input labels.
Use existing Pydantic/stdlib and Make tooling, with no new dependency or service.

No network, model, messaging, cloud or evaluation call; no persistent application data,
public HTTP contract or grading-policy change. `eval-local` and `eval-gemini-free` remain
fail-closed pending complete frozen-benchmark/provider integration. No real data is
introduced. Neither a comparison nor meeting a numerical threshold activates a band.

## Acceptance

Strict contract/coherence tests; identical and changed-model/prompt comparisons;
mismatched frozen benchmark/schema rejection; all-fallback/incomplete reports; unknown
usage; malformed/duplicate/oversized/special-file/privacy-canary rejection; safe CLI
errors and deterministic actual Make invocation on controlled synthetic files. Run
lint/types/unit/source-security/docs and retain full hosted acceptance before promotion.
See [readiness](../../implementation/E4_EVALUATION_REPORT_READINESS.md).
