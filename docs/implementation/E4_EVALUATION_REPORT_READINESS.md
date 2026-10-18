# Offline evaluation comparison readiness

Requirements: FR-GRD-003/004, FR-OPS-002 and NFR-MNT-001; evaluation profile 18 sections
5–7. The required `make eval-compare` command currently always exits unavailable.
Existing fake rehearsal/calibration metadata does not provide a versioned portable
report reader or comparison. Frozen academic benchmark/report authority, actual Ollama
inference and opt-in Gemini evaluation remain independent gates.

Smallest complete slice: a strict versioned payload-free synthetic report contract,
bounded local-file reader, pure summary comparison and the prescribed offline command.
No application route, persistence, learner selection, gateway dispatch or model provider
changes. No inference/evaluation is run. Tests use original synthetic metadata and fake
provider outputs where orchestration is exercised. Do not fabricate benchmark truth or
claim a report is genuine approval.

Require identical frozen benchmark digest/version/case count, task/output schema and
metric policy before comparing. A model, prompt or inference configuration change may
be the purpose of the comparison; identify those differences explicitly rather than
silently pretending the runs are identical. Record exact model/runtime/quantization,
context, deterministic sampling, adapter/prompt versions and hardware in each input.
Report counts must include every case, with low-confidence/invalid/provider/safety
fallbacks separate from scored cases and excluded from correct numerators. Preserve
unknown usage as null; zero is not evidence that usage was measured. Compare exact and
within-tolerance fractions, critical errors, bounded latency and token/request usage.
Never convert synthetic fractions into calibrated band activation or academic approval.

Privacy/resource boundary: no prompts, answers, identities, credentials, raw output,
free-text diagnostics or cloud URLs are allowed in reports. Reject unknown fields,
coercion, non-finite values, duplicate JSON keys, inconsistent counters and oversized
files. Errors are closed codes with no paths, exception messages or file excerpts.
The comparison output includes safe report IDs and aggregate metrics, not arbitrary
model/configuration strings from untrusted files. Use existing Pydantic/standard-library
and Make conventions, without new dependencies. New artifact contract belongs in an ADR.

Acceptance: valid matching/different-provider reports, changed-prompt flags, mismatched
benchmark/schema rejection, no hiding fallback cases, zero-score/all-fallback reports,
unknown usage, privacy canaries, malformed/duplicate/oversized input and deterministic
CLI output/failure. Run prescribed lint/types/unit/source-security/docs checks and the
actual `make eval-compare` against controlled synthetic files. Actual local and Gemini
commands remain fail closed pending their own complete benchmark/provider slice.


Implementation checkpoint: the declared sanitizer marker and license/terms/runtime/
quota values are input artifact metadata, not a performed sanitizer or verified provenance.
Strict field validation cannot establish that an academic benchmark/report is genuine.
The comparison does not resolve trusted approval authority or enable a grading band.
