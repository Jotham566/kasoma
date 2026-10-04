# ADR-041: Budgeted synthetic dual-pass rehearsal

Date: 4 October 2026
Status: Accepted within delegated MVP implementation discretion; offline preparation
Requirements: FR-GRD-003/004/005, NFR-SEC-002

## Decision

Extend the existing ModelGateway task/result contracts additively with pinned context references,
structured untrusted input, response schema, time/token/zero-cost ceilings, usage and bounded raw
candidate output. Keep existing foundation tasks compatible. FakeModelProvider accepts deterministic
response/exception fixtures and keeps synthetic calls in memory for tests; the default still returns
LOW_CONFIDENCE. No live inference adapter, external provider, endpoint or worker task is enabled.

Add a synthetic rehearsal that calls the same gateway twice with distinct versioned criteria-first
and evidence-first instructions. Both receive only the same fixture rubric and response; the second
does not receive the first candidate. Require independently validated results to agree on every
criterion and the total. Even agreement returns AGREEING_CANDIDATES with automatic scoring false,
never a learner grade. Context is the explicitly synthetic fixture type from ADR-040. Its simple
criterion metadata is not a complete academically approved rubric or an inference-ready prompt.

Allow at most one additional schema-repair generation across the entire two-pass operation. It
receives the original structured input/schema and a repair marker, not untrusted output promoted to
instructions. Rubric/evidence/context failures are not repaired; they fall back immediately. Timeout,
provider exceptions/fallback, safety flags, disagreement and exhausted budgets also fall back without
returning a candidate. Never surface provider exception text or raw output in logs/errors.

Defaults are three requests, 16,384 total reported tokens and five seconds for the entire rehearsal;
typed bounds cap configuration at three requests, 32,768 tokens and 30 seconds. Each call reserves
at most 4,096 input and 1,024 output tokens within the remaining budget and receives the remaining
deadline. Account actual reported usage across repairs and passes; reject per-call or total excess.
Check deadlines before and after dispatch. Adapters must enforce the supplied timeout/token ceilings:
these synchronous checks cannot forcibly interrupt a misbehaving adapter or prevent an adapter from
misreporting usage. Only an instantaneous deterministic fake is shipped in this path. Future live
adapters need conformance/timeout tests and accurate token/cost accounting before enablement.

## Boundaries and verification

Pure fake tests verify independent inputs, both repair positions, global repair/request/token/time
ceilings, malformed/unsupported output, caller/provider flags, low-confidence default, disagreement
and exception minimization. No schema migration or HTTP change is made. No inference is performed.

Academic rubric/context approval, prompt validation, frozen benchmark/calibration, injection/domain
detectors, eligible combinations, neutral learner fallback/persistence, gateway telemetry, production
adapter decisions and audited band disablement remain required. This adds testable orchestration;
it does not satisfy those gates or authorize a confidence threshold for automatic scoring.
