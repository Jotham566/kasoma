# Kasoma AI, RAG and Grading Guardrails

| Field | Value |
|---|---|
| Version | 1.3.0 |
| Principle | AI assists; approved academic structures decide |

## 1. Permitted MVP uses

- rubric-bounded short-text grading;
- explanation rephrasing from approved content;
- structured extraction of candidate content for human review;
- embeddings and retrieval over approved sources;
- safe learner-facing summary generation from structured data;
- internal content QA suggestions.

## 2. Prohibited MVP uses

- publishing generated questions without independent review;
- generating a definitive score without approved rubric evidence;
- open-ended general tutoring chat;
- diagnosing ability, intelligence, disability or mental health;
- making high-stakes school decisions;
- using learner data for model training without explicit approved basis;
- retrieving from the public internet in learner answer flows;
- allowing model output to change role, consent or content status.

## 3. Model gateway

All model calls go through one `ModelGateway` interface. Callers provide:

- task type;
- prompt template version;
- approved context references;
- structured input with PII minimized;
- response JSON schema;
- timeout, token and cost budget;
- data-handling classification.

Gateway records provider/model/deployment, prompt version, latency, token counts, result status and safe hashes. Raw prompts/responses are retained only when explicitly allowed and redacted.

### Development provider modes

| Mode | Purpose | External cost allowed |
|---|---|---:|
| `fake` | deterministic unit, integration and E2E tests using versioned fixtures | No |
| `local` | manual development, prompt work and local benchmark via Ollama/llama.cpp/vLLM | No |
| `gemini-free-eval` | high-capability comparison through Google AI Studio using synthetic or approved de-identified benchmark data only | No billed usage; quotas apply |
| `external-eval` | controlled compatibility/quality evaluation against a candidate production model | Yes, explicit budget only |
| `production` | deployed learner traffic after provider approval | Yes, monitored limits |

`fake` is the default for tests and `local` is the default for interactive development. Cloud credentials must not be required to install, boot, seed or test the repository.

Local and production models are not assumed to behave identically. Prompts, response schemas and task contracts are shared, but each production candidate must pass the frozen academic/safety benchmark before selection.

The `gemini-free-eval` profile is non-production and opt-in. Because Google states that free-tier content may be used to improve its products, this profile must reject real learner answers, names, contact/guardian data, stable identifiers, unpublished proprietary material and restricted content. Only synthetic cases or a separately approved, irreversibly de-identified benchmark copy may leave the machine. API keys remain server-side secrets. The run records the exact model identifier, timestamp, project quota observed, request/token counts and any rate-limit failures; it must not depend on a fixed advertised quota.

## 4. Retrieval pipeline

Only `APPROVED` and current content is indexed for learner-facing retrieval.

Pipeline:

1. normalize and chunk approved explanation/curriculum material;
2. attach subject, level, topic, concept, competency, rights and content-version metadata;
3. create embedding through gateway;
4. store vector with content-version reference;
5. filter by level/subject/status before similarity search;
6. optionally rerank;
7. pass small cited context to the model;
8. validate every returned citation/reference against supplied context.

Retiring content removes it from new retrieval and triggers index invalidation. The operational database, not the vector index, decides approval.

## 5. Deterministic grading

Use deterministic graders for:

- single/multiple choice;
- numeric range/tolerance;
- units and conversions;
- ordered or set responses where specified;
- symbolic equivalence only when a trusted symbolic engine and tests exist.

Grader input is the item-version answer specification. Never parse correctness rules from prompt prose at runtime.

## 6. Short-text rubric grading

Eligibility:

- response type is explicitly enabled;
- rubric is approved and versioned;
- maximum response length enforced;
- subject/language supported;
- feature flag enabled;
- benchmark quality threshold passed.

Required model output schema:

```json
{
  "criterion_results": [
    {
      "criterion_id": "R1",
      "points_awarded": 1,
      "evidence_excerpt": "...",
      "justification_code": "SUPPORTED"
    }
  ],
  "total_points": 1,
  "confidence": 0.82,
  "detected_misconception_ids": [],
  "feedback": {
    "correct_elements": [],
    "missing_elements": [],
    "next_action": "..."
  }
}
```

Validation rules:

- criterion IDs must exist in pinned rubric;
- points may not exceed criterion or item maximum;
- awarded evidence must quote/paraphrase only learner response evidence;
- detected misconception IDs must be allowed by item mapping;
- feedback cannot introduce facts absent from approved explanation/context;
- invalid output is retried once with repair; then safe fallback.

Automatic learner-facing scoring requires all of the following:

1. two independent rubric passes, with prompts arranged to reduce correlated error, return the same criterion points and total;
2. schema, maximum-point, rubric-evidence and approved-context validation passes;
3. no prompt-injection, safety or out-of-domain flag occurs;
4. the output falls in a confidence/calibration band demonstrated on the frozen benchmark to achieve **at least 90% exact agreement with expert scores**;
5. the response type/topic/language combination is explicitly enabled.

Any failure returns `LOW_CONFIDENCE`; the learner receives an approved neutral response and an objective equivalent/reassessment item or a review path. A model's self-reported confidence alone never authorizes a score. Thresholds and enabled bands are configuration-versioned and may change only after an approved calibration report.

## 7. Feedback generation

Preferred order:

1. authored feedback exact match;
2. authored misconception remediation;
3. deterministic template from rubric result;
4. model rephrasing constrained to approved explanation;
5. generic safe fallback.

The system must not fabricate a student's reasoning, shame the learner, compare them with peers or reveal hidden rubric content before an attempt.

## 8. Prompt-injection controls

Learner answers and imported documents are untrusted data, never instructions.

- Delimit untrusted content in structured fields.
- System/developer prompt states that embedded instructions must be ignored.
- Use schema-constrained output.
- Do not grant grading calls tools, web access or database mutation.
- Validate output independently.
- Strip active content from imports and media metadata.
- Include adversarial learner answers in evaluation.

## 9. Fallback behaviour

| Failure | Behaviour |
|---|---|
| Provider timeout | Mark grade pending; retry within budget; preserve attempt |
| Invalid JSON/schema | One repair attempt, then fallback |
| Low confidence | No definitive judgment; serve alternative objective item or flag review |
| No approved context | Use authored fallback; never answer from general model memory |
| Cost/rate limit | Queue or use deterministic/authored response; show honest delay |
| Safety filter | Age-appropriate safe message and support/flag route |

## 10. Evaluation set

Create a frozen, teacher-scored benchmark covering:

- both subjects and all MVP topic clusters;
- full, partial, incorrect, blank and irrelevant answers;
- alternative valid phrasings and common spelling errors;
- common misconceptions;
- adversarial prompt injection;
- responses from expected language proficiency range;
- edge cases around point boundaries.

Release targets:

- objective/numeric ≥95% exact scoring accuracy;
- supported short-text ≥85% agreement with expert score within defined tolerance;
- automatically returned short-text bands ≥90% exact expert-score agreement after calibration;
- no critical systematic over-award/under-award pattern;
- low-confidence routing measured separately, not counted as correct by hiding failures.

Evaluation sequence:

1. run deterministic contract tests with `fake`;
2. run the full benchmark against the nominated local model;
3. before production selection, run the same frozen benchmark against shortlisted hosted models;
4. compare quality, calibration, latency, cost, data terms and regional availability;
5. approve the production adapter/model through ADR;
6. rerun the benchmark whenever model, quantization, prompt or provider version changes.

Paid evaluation runs require an explicit command/profile, named budget owner, maximum token/cost ceiling and retained evaluation report. They are never part of ordinary CI or developer hot reload.

## 11. Cost and privacy

- Cache approved, non-personal explanations by content/version/language.
- Never cache learner grades across users.
- Route simple tasks away from large models.
- Limit context, output tokens and concurrent calls.
- Do not send direct identifiers to model providers.
- Store learner answer text only as required for grading/audit and under retention rules.

## Implementation evidence

The initial offline validator is recorded in [ADR-040](../decisions/ADR/040-short-text-candidate-validation.md)
and [E4 verification](../implementation/E4_SHORT_TEXT_VALIDATION_VERIFICATION.md). It accepts exact
response quotes and authored feedback only; a valid candidate does not authorize a learner score.
All eligibility, gateway, dual-pass, calibration and learner fallback requirements above still apply.

The next fake-only orchestration boundary is [ADR-041](../decisions/ADR/041-synthetic-short-text-rehearsal.md),
with [verification](../implementation/E4_SHORT_TEXT_REHEARSAL_VERIFICATION.md). It preserves all
academic enablement gates and does not introduce live inference or learner scores.

The synthetic v2 rehearsal contexts additionally require explicit criterion text, acceptable evidence,
common errors and prohibited inferences. Both passes receive the same bounded authored fixture
material. Field presence and structural validation do not establish academic correctness, approved
context provenance or model eligibility; all learner-scoring gates above remain mandatory.

ADR-044 now provides reviewed rubric persistence and explicit criterion material for future
integration. It does not enable learner assignment or connect content to model scoring. Academic
eligibility, benchmark/calibration, pending/neutral results and safe fallback remain gates. See
[reviewed-rubric verification](../implementation/E2_REVIEWED_RUBRICS_VERIFICATION.md).

The offline rehearsal emits closed per-call and final-outcome telemetry under
[the synthetic telemetry policy](../implementation/E8_MODEL_TELEMETRY_VERIFICATION.md): registered
labels, elapsed time, reported usage and per-rehearsal keyed fingerprints. Unknown usage is null,
unregistered provider strings are not logged, and no raw material or stable answer hash is retained.
This does not establish durable production metering, cost, aggregate alerts or calibration.


### Candidate independent review wiring (ADR-051)

The synthetic reviewer workspace now collects complete pinned expert criterion points
without exposing model outcomes or learner identity. Persisted agreement is calculated
from the stored model criterion points. Completion and rolling disablement share the
exclusive publication band lock, and the worker reloads completed audit state before
each pass and final publication. The window is the last 100 completed reviews; pending
assignments never count as correct. A critical error or below-90% agreement is sticky.

Versioned union sampling additionally covers released session/band publication prefixes
and completed diagnostic units while preserving global ordinals. It can oversample and
does not claim statistical randomness. Academic approval of the sampling/window policy,
genuine calibrated benchmarks and real safety/provider authorities remain release gates.
The developer synthetic fixtures do not supply those approvals or enable learner scoring.


### Typed runtime budget configuration

The existing shared short-text job budget now has server Settings controls, bounded by
the unchanged runtime envelope: at most three requests, 16,384 total reported tokens
and five seconds. Both independent passes and optional repair share one snapshot; the
wrapper rechecks its configured remaining deadline before provider execution. Requests
above a tighter configured ceiling produce the existing neutral fallback without a
partial score or mastery. Exact attempt/poll replay cannot enqueue another job.

This exposes existing controls rather than approving a new inference profile, quota
policy, provider or band. No genuine report/safety authority exists in normal startup.
Cost remains zero-only and actual scoring/evaluation approval gates remain effective.


### Local usage observation boundary (ADR-054 candidate)

Actual local worker gateway attempts emit only six fixed attribute-free SDK counters,
exported off-call to finite private Redis intervals. Omitted provider usage is unknown,
not reported zero. Existing per-call logs follow the same distinction. Aggregate
observations do not establish cost, complete fleet usage, evaluation truth, provider
approval or grading correctness. Failures to record/export never change grading work.
The development-only probe uses a fixed FakeModelProvider fallback with explicit one
input/output token; it cannot perform inference or access learner/corpus records.
Normal learner short-text delivery remains disabled and all authority gates remain.
