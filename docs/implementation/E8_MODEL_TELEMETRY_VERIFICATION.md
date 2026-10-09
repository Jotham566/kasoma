# E8 synthetic model telemetry verification

Requirements: NFR-OBS-001, FR-OPS-002; supports FR-OPS-004 and AI specification §3.
Status: implemented; 427 unit/contract and five tooling checks pass; hosted regression is pending.

The existing short-text rehearsal now emits a closed model.call event per actual gateway dispatch
and a model.rehearsal outcome, sharing a caller-supplied UUID or fresh correlation UUID. The same
correlation covers independent passes and the single permitted repair. Invalid/flagged preflight
produces an outcome with zero calls. Candidate status means provider output, never accepted grading.

Call events contain registered prompt/provider/model labels, the offline deployment label,
monotonic rounded-up elapsed milliseconds, provider-reported input/output tokens and status.
Unregistered labels become UNREGISTERED, not arbitrary free text. Failed calls record unavailable
metadata and null usage rather than claiming zero consumption; provider exceptions are withheld.
No production cost or calibrated accuracy is inferred from reported fake usage.

Input/output fingerprints are HMAC-SHA256 under a fresh random 256-bit key per rehearsal. The key
is never logged or retained; identical data can be correlated only within that rehearsal. There is
no global/stable plain hash of low-entropy answers. Raw prompts, responses, criterion material,
context IDs, identities and provider diagnostics are excluded. Existing structured logging is used;
production log shipping, retention enforcement and aggregate usage alerts remain separate gates.

## Verification

Eleven additional contract cases cover repair correlation/usage totals, failures and timeouts,
unknown usage, preflight, rounded timing, unregistered metadata redaction, ephemeral keyed
fingerprints, provider fallback/flags, closed schema correspondence and wrong-task dispatch denial.
All inference uses FakeModelProvider with original synthetic fixtures. The existing independent
pass, global budget, repair, deadline and validation regressions remain applicable.

Run `make format lint openapi-check test-unit security`. No HTTP or database schema is changed;
no migration or inference/evaluation command is needed. Full hosted regression remains required
before promotion. This is instrumentation of the existing offline path, not live-provider or learner
acceptance. Automatic scoring stays disabled and the operator dashboard correctly retains AI_USAGE
as unavailable until durable aggregation and threshold handling exist.

No accepted architecture, provider, retention period or privacy policy changes. The implementation
uses the existing gateway, closed contracts and logging sink. No new ADR is required for this
instrumentation; its limited correlation/fingerprint policy is recorded here and in the runbook.

`make format lint openapi-check test-unit` passed. Bandit, local secret checks and Python audit
passed, but `make security` failed the JavaScript audit on newly reported high-severity Next.js,
sharp and source-map-js advisories. Dependency remediation and fresh regression are required.

The dependency refresh resolves the reported audit failures; full post-install lint/types/contracts,
427 unit/contract plus five tooling checks, build and security pass. Hosted regression remains pending.
