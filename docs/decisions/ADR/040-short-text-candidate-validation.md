# ADR-040: Fail-closed synthetic short-text candidate validation

Date: 4 October 2026
Status: Accepted within delegated implementation discretion; offline foundation only
Requirements: FR-GRD-003/004/005

## Decision

Implement the independent output-validation boundary before enabling any short-text assessment
route. The fixture context pins item and rubric versions, unique criteria whose maxima sum to the
item maximum, allowed misconception IDs and authored feedback. It is explicitly synthetic and
does not grant academic approval. No existing content type, database constraint, learner contract,
model gateway or enabled response type changes in this slice.

Reject duplicate JSON fields at every nesting level, non-finite numbers, extra/missing fields,
coerced score types, unknown/duplicate/omitted criteria, over-awards and inconsistent totals.
Awarded evidence must be a nonempty exact substring of the supplied response. Contradiction
evidence must also quote the response. Require the correct/missing feedback and next action to
match context strings exactly. This deliberately conservative first validator supports exact
quotes and authored feedback; semantic paraphrase validation awaits benchmark evidence. A valid
quote proves provenance, not the academic correctness or sufficiency of that evidence.

Initial internal resource ceilings are 2,000 response characters, 16,384 output characters,
20 criteria, 100 total points and 50 mapped misconceptions. These are synthetic implementation
bounds, not an approved academic response-format policy. Document any future eligibility limits
with the approved rubric and frozen benchmark. No output or validation exception is logged.
Failures return LOW_CONFIDENCE with a bounded reason code and no candidate payload. Valid output
returns VALIDATED_CANDIDATE only, even when the model claims confidence 1. Safety/injection/domain
flags are required caller input; this structural validator does not itself detect those hazards.

## Remaining gates

This is not a grader and has no persistence, HTTP endpoint, model execution or learner display.
Gateway budgeting, independent dual-pass orchestration, one schema-repair attempt, detectors,
approved-context/rubric loading, neutral learner fallback, calibrated ≥90% exact-agreement bands,
the overall ≥85% short-text benchmark and audit/disable controls remain required. No synthetic
test or confidence number enables automatic grading. FakeModelProvider remains the only model
provider for automated orchestration tests; these pure tests validate fixture JSON without calls.

## Verification

Exercise boundary/coercion failures, duplicate/nested malformed JSON, rubric point/set invariants,
quote provenance, context allowlists, flags, adversarial embedded instructions and redacted repr.
Run repository formatting, lint/type, contracts and unit commands. No migration is introduced.
