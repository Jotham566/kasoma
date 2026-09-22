# Kasoma Local Development and Provider Portability

| Field | Value |
|---|---|
| Version | 1.1.0 |
| Status | Approved MVP development policy |
| Default cost | Zero paid API usage |

## 1. Decision

Kasoma shall run, develop and test locally without paid LLM, messaging, email, SMS, storage or cloud infrastructure calls. Local open models support prompt and AI workflow development; deterministic fakes support automated tests. The production cloud and hosted model are selected later using measured evidence.

This is good engineering practice because it lowers cost, improves reproducibility, lets developers work offline and reduces vendor lock-in. The main risk is behaviour difference between local and production models. Kasoma addresses that risk with provider contracts and a frozen cross-model evaluation suite.

## 2. Local stack

| Capability | Local implementation | Production interface |
|---|---|---|
| Web/API/worker | Native processes or Docker Compose | OCI containers |
| Database/vector | PostgreSQL + pgvector | Managed PostgreSQL-compatible service |
| Cache/queue | Redis | Managed Redis-compatible service |
| Object storage | MinIO | S3-compatible adapter or cloud object-store adapter |
| Email | Mailpit | Email provider adapter |
| SMS OTP | deterministic fake/outbox viewer | Uganda-capable SMS adapter |
| WhatsApp | fake webhook/message simulator | Meta WhatsApp Cloud API adapter |
| LLM automated tests | `FakeModelProvider` fixtures | same task/result contracts |
| LLM developer inference | Host-native Ollama on M4 Mac Mini 16 GB | model-provider adapter |
| Shared GPU inference | vLLM OpenAI-compatible server | optional self-hosted/managed provider |
| Observability | local OpenTelemetry collector + open-source backend or console exporter | managed/self-hosted compatible backend |

## 3. Model gateway contract

All inference backends implement the same application contract:

```text
grade_short_answer(task) -> GradeResult
rephrase_explanation(task) -> ExplanationResult
extract_content_candidate(task) -> CandidateResult
embed_approved_content(task) -> VectorResult
```

Application modules do not send vendor-specific payloads. Adapters translate the task contract into the provider API. Every result records provider, model, quantization, adapter, prompt and schema versions.

An OpenAI-compatible HTTP interface is preferred for local Ollama/vLLM and hosted adapters, but application code still calls `ModelGateway`, not an SDK directly.

## 4. Three AI test levels

### Level 1 — Deterministic contract tests

- Default for unit, integration and E2E tests.
- Versioned fake responses for success, low confidence, invalid schema, timeout and safety failure.
- Fast, reproducible and free.
- Tests orchestration and product behaviour, not model intelligence.

### Level 2 — Local-model benchmark

- Runs manually or nightly on available GPU hardware.
- Uses the frozen teacher-scored evaluation set.
- Tests prompt/schema robustness, injection resistance and approximate task quality.
- Records model name, weights/license, quantization, runtime and hardware.
- No result from this level alone authorizes production grading.

### Level 3 — Hosted production-candidate evaluation

- Manually triggered only.
- Uses the identical frozen benchmark and metrics.
- Has an approved maximum request/token/cost budget.
- Compares quality, calibration, latency, cost, regional availability, privacy terms and operational complexity.
- Required before choosing or changing the production model.

### Level 2b — Gemini free-tier comparison

- Manual and opt-in; never a PR/main CI dependency.
- Uses Google AI Studio only with synthetic or approved irreversibly de-identified benchmark fixtures.
- Rejects real learner responses, identifiers, guardian/contact data, confidential or restricted material before network access.
- Records the exact Gemini model, timestamp, observed project quotas and rate-limit results because limits vary by model, tier and capacity.
- Uses bounded retry/backoff for `429` responses and stops at configured request/token ceilings.

## 5. Avoiding local/production drift

- Keep task and result JSON schemas provider-neutral and versioned.
- Do not write prompts that depend on undocumented quirks of one model.
- Maintain provider-specific conformance tests.
- Validate schema outside the model for every backend.
- Re-run benchmark when model, weights, quantization, prompt, inference settings or adapter changes.
- Store model aliases in configuration; never hard-code a marketing model name in domain logic.
- Use deterministic sampling for grading (`temperature=0` or closest supported setting), while recognizing that providers may still vary.
- Keep a small approved set of production shadow comparisons before enabling a new adapter.

## 6. External-service testing

SMS, email and WhatsApp cannot be proven solely through local simulation. Use this progression:

1. fake adapter in all automated tests;
2. recorded provider-contract fixtures;
3. official sandbox/test credentials where available;
4. a small pre-production integration test with strict spend/rate limits;
5. production credentials stored only in the deployment secret manager.

Local code must never silently fall back from a fake/local adapter to a paid provider.

## 7. Production provider selection gate

Complete by end of Week 8, before beta with real learner data.

Score AWS, Azure and GCP against:

| Criterion | Weight |
|---|---:|
| Uganda latency and African/nearby region coverage | 15% |
| Managed PostgreSQL/Redis/container reliability | 15% |
| Data protection, processor terms and cross-border safeguards | 20% |
| AI model quality and data-use terms | 15% |
| Pilot and projected scale cost | 15% |
| Backup, recovery, observability and security controls | 10% |
| Team familiarity and operational burden | 10% |

Minimum conditions override weighted score: legal/privacy approval, required generally available services, successful restore test, acceptable benchmark quality and sustainable projected cost.

The resulting ADR records provider, primary/recovery regions, services/SKUs, model deployment, monthly budget, data-flow changes, RPO/RTO evidence and exit/migration considerations.

## 8. Cost controls

- `ALLOW_EXTERNAL_API_CALLS=false` by default.
- No cloud credentials in ordinary local or CI environments.
- Paid runs use a separately named `external-eval` profile.
- Require request count, token and currency-denominated ceiling.
- Stop on budget exhaustion; never auto-expand limits.
- Cache only approved non-personal outputs where safe.
- Track cost by task type, model and environment.
- Use local embeddings during development; rebuild the production index through the selected approved embedding adapter.

## 9. Hardware profiles

The supported developer machine is an Apple M4 Mac Mini with 16 GB unified memory. Ollama runs natively on macOS for Apple acceleration; PostgreSQL, Redis, MinIO, Mailpit and application containers may remain in Docker. Start with an 8k context window and increase it only after measuring memory pressure.

Model profiles:

- `local-fast`: a quantized 4B-class instruct model for rapid iteration;
- `local-quality`: a benchmark-selected quantized 7B/8B-class instruct model and the normal quality baseline;
- `local-stretch`: a quantized 12B-class model for manual experiments when memory headroom is demonstrated;
- 27B-class models are outside the supported 16 GB local baseline.

Also support:

- CPU/laptop: fake provider and small quantized model through llama.cpp/Ollama;
- other developer GPU: Ollama or vLLM depending on hardware;
- shared high-memory GPU such as an RTX 8000: vLLM server for team benchmark/inference;
- CI: fake provider only unless an explicitly provisioned local-model runner exists.

The repository README must state memory expectations for the selected development model, but the architecture must not require every developer to run the largest model.

## 10. Acceptance criteria

- A clean clone can start and run all required tests without cloud credentials.
- Disconnecting the internet does not break the seeded core learner journey.
- Automated tests fail if an unexpected external network model call is attempted.
- The local model can execute every AI task contract, even if quality differs.
- The frozen benchmark produces comparable reports across local and hosted adapters.
- Changing providers requires configuration/adapter work, not domain rewrites.
