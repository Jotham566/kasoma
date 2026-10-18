# Configurable runtime grading budgets

18 October 2026. Requirements: FR-OPS-004, FR-GRD-004, NFR-SEC-002, NFR-MNT-001.
Authority: SRD, AI/security/QA specifications and ADR-041/050. Inspect the existing
RehearsalBudget, VersionedGateway and finite-lease processor before changing code.

The worker currently instantiates the existing shared per-job budget with fixed defaults:
three requests, 16,384 total reported tokens and five seconds. The same budget covers
both independent passes and one optional repair. A separate wrapper enforces the
remaining deadline, and Celery hard limits remain outside it. Per-job limits already
exist; the missing slice is typed operator configuration rather than a new quota policy.

Expose only settings that tighten those existing hard ceilings. Defaults remain exactly
unchanged; two independent passes remain mandatory and max requests stays 2–3. Preserve
the generic offline rehearsal type's existing range but do not let runtime configuration
increase the current 16,384-token/five-second envelope. Snapshot one validated budget
for the job and use its timeout in both rehearsal and pre-dispatch wrapper. A stricter
ceiling can yield neutral fallback, never a partial/unsupported score or mastery update.
Poll/replay must not repeat work. No public API, migration, provider or personal record.

No new architectural decision: these are the already approved budget controls exposed
through existing Settings/.env conventions. No learner/day/fleet quota, new inference
profile or production approval is invented. Normal startup has no genuine approval/safety
authority and remains disabled. A future authority must bind the approved actual model,
prompt/configuration and relevant resource settings; UUID metadata alone is insufficient.

Acceptance: invalid/above-ceiling settings fail before startup; default behavior remains;
actual fake worker dispatch respects configured two-request repair exhaustion, token
starvation before any provider call, and remaining-deadline expiry. All exhausted paths
preserve the saved attempt, neutral no-score/no-mastery outcome and exact replay. Run
lint/types/contracts, unit, flow/review/role and applicable recovery/security/hosted checks.
No model, Gemini, messaging or cloud call, real learner data or destructive action.
