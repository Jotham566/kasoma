# ADR-054: Bounded local worker model-usage observations

Date: 18 October 2026
Status: Accepted for local synthetic engineering; hosted 39160113771 passes at 0c73c45
Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001

Extend the approved OTel/local Redis architecture with six static, attribute-free delta
counters for actual worker provider-port attempts: candidate/fallback/unavailable
outcomes, unavailable token usage and known reported input/output tokens. Candidate
responses precede validation and are not grades. Unknown usage is not zero; only
explicitly supplied token fields count as reported. No billed cost or calibrated
accuracy claim. Generic observed-provider wrapping occurs after current dispatch
authorization/deadline checks and cannot change provider behavior on metric failure.

Use one owned SDK provider with static resource/scope, disabled exemplars and no host,
identity, route, prompt, answer, model/provider label or content fingerprint dimensions.
Record and collect the fixed counter set atomically; retain only earliest observation
time/current-batch count, not per-call samples. This dates retention by actual observed
outcomes rather than a potentially old SDK counter start after an idle period.

Collect every five seconds off-call. Share only the existing bounded byte transport,
keeping request/model codecs, purpose hashes and keys separate. Preserve request wire
compatibility. At most 256 canonical <=1024-byte intervals; immutable retry, missing-data
unavailability, finite capping marker, 15-second freshness and absolute 300-second
expiry from earliest observation. Reuse existing bounded skew/server-expiry checks.
No Redis I/O or metadata serialization occurs on model dispatch. Export/shutdown have
bounded time/resources; outages are best-effort loss, not a complete usage ledger.

Only the ordinary worker explicitly imports the collector lifecycle; the export-only
worker must not publish freshness. Support solo and child-process shutdown. A fixed
development-only FakeModelProvider probe verifies collection without inference, grading
or learner data. Expose aggregate observations through the existing ADMIN snapshot and
accessible UI; a typed local volume threshold can warn, never approve/disable grading
or act as billing/quota enforcement. Unknown/expired/corrupt sources stay unavailable.

No database, provider, model/inference profile or production privacy approval changes.
Real data/production usage still requires the existing DPIA/provider/release gates.
See [readiness](../../implementation/E8_MODEL_USAGE_READINESS.md) for acceptance.
