# Kasoma Ollama and Gemini Evaluation Profile

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Status | Approved development profile |
| Hardware baseline | Apple M4 Mac Mini, 16 GB unified memory |

## 1. Purpose

This profile gives coding agents one reproducible, low-cost way to develop AI features locally and a separate way to compare them with a capable hosted model. Ollama is the normal inference path. Google AI Studio's Gemini free tier is a supplementary quality test, not a production runtime and not a substitute for deterministic tests.

## 2. Runtime layout

- Install and run Ollama natively on macOS to use Apple acceleration.
- Run the web app, API, worker, PostgreSQL, Redis, MinIO and Mailpit natively or with Docker Compose.
- Host processes call `http://localhost:11434/v1`.
- Containers call `http://host.docker.internal:11434/v1`.
- All calls still pass through `ModelGateway`; no domain module imports an Ollama or Google SDK.

## 3. Local model profiles

| Alias | Model class | Use | Required status |
|---|---|---|---|
| `local-fast` | Quantized 4B instruct | prompt/schema iteration | supported |
| `local-quality` | Quantized 7B/8B instruct | local benchmark and normal manual testing | supported default |
| `local-stretch` | Quantized 12B instruct | occasional quality comparison | optional |

Select the exact model and quantization using the frozen Kasoma benchmark, licensing review and measured latency/memory. Start with Q4/Q5 quantization and an 8k context. Do not require a 27B-class model on 16 GB hardware. Record model digest, quantization, Ollama version, context, sampling settings and machine profile in every report.

## 4. Gemini free-tier boundary

`gemini-free-eval` is allowed only when all conditions are true:

1. `ALLOW_GOOGLE_FREE_TIER_EVAL=true` was deliberately set for the run;
2. `GEMINI_API_KEY` is present only in the server-side/local secret environment;
3. the input is synthetic or has a recorded approval as irreversibly de-identified;
4. the preflight sanitizer finds no names, emails, phone numbers, account/learner/guardian IDs, free-form real learner answers, production extracts, secrets, unpublished proprietary content or rights-restricted material;
5. explicit request and input-token ceilings are configured;
6. the run writes an auditable manifest without storing disallowed raw prompts or responses.

This restriction is mandatory because Google's published pricing information says free-tier content may be used to improve its products. Paid-tier or production use requires a separate privacy/legal/vendor review; switching tiers alone does not approve a production provider.

Google quotas are per project and can vary by model, tier and capacity. Read the current limit in AI Studio before a run, treat it as an upper bound rather than a guarantee, use bounded exponential backoff for rate limiting, and stop instead of bypassing limits with extra projects or keys.

## 5. Required commands

```text
make test               # fake provider only; offline and deterministic
make eval-local         # frozen benchmark through Ollama
make eval-gemini-free   # sanitizer, explicit opt-in, then Gemini comparison
make eval-compare       # compare existing reports; performs no inference
```

`make eval-gemini-free` must fail closed before the first request if the opt-in, secret, sanitizer, model alias or ceilings are missing. It must never be called by ordinary CI.

## 6. Comparable report

Every local or Gemini report contains:

- benchmark and prompt/schema versions;
- provider, exact model identifier and adapter version;
- runtime/hardware or hosted tier and run timestamp;
- task-level accuracy/agreement, low-confidence routing and safety failures;
- latency distribution, tokens and rate-limit errors;
- sanitizer result and dataset classification;
- reproducibility settings and failure reasons.

Promoting a model requires the thresholds in document 06. A good Gemini result identifies a candidate; it does not authorize automatic grading, production data access or deployment.

## 7. Acceptance criteria

- A clean local test run works without internet access or model API keys.
- Ollama executes each `ModelGateway` task contract on the M4/16 GB baseline.
- Containers can reach host-native Ollama without exposing it publicly.
- A fixture containing a canary email, phone number or learner ID is blocked before a Gemini request.
- Gemini evaluation stops at its configured ceilings and reports `429` responses without retry storms.
- Local and Gemini runs produce the same report schema and can be compared without changing domain code.
