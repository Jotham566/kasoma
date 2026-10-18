# Local worker model-usage observation readiness

18 October 2026. FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001.
The existing bounded ADMIN dashboard still marks AI_USAGE unavailable. Closed per-call
logs exist, but they are not an aggregate. Inspect the existing request OTel collector,
Redis interval store, model gateway/telemetry and worker lifecycle before implementation.

Use the already approved OTel/Redis architecture. One owned worker SDK records six
attribute-free delta counters: returned candidates, returned fallbacks, unavailable
results, unavailable token usage and known reported input/output tokens. These observe
provider-port calls before grading validation, not grades, accuracy, billing or all fleet
traffic. Missing ModelResult token fields must remain unknown, distinct from explicit
reported zero. Wrap actual provider dispatch after current authorization/deadline checks;
metrics failure must never fail model work. No network I/O on recording.

Only a fixed number of counters and earliest current-batch observation time/count are
held in memory. Collect atomically every five seconds, then export off-call. Reuse the
existing finite byte-store rules with separate purpose/key namespace and strict codecs:
at most 256 <=1024-byte intervals, 300-second retention from earliest observation,
15-second successful-collection freshness, bounded host/VM skew, immutable retry and
finite capping marker. No actor/attempt/request/correlation IDs, content fingerprints,
model/provider labels, raw SDK metadata, prompts or answers enter aggregate storage.

Register the collector only in the ordinary worker through its explicit import module;
export-only workers and API processes must not create false model freshness. Preserve
native solo/prefork/spawn lifecycle and bounded shutdown. Add a developer-only fake
provider probe to verify worker-to-Redis collection without inference or learner data.
No cloud dependency, real model call, database migration, grade policy or retention change.

Expose optional ADMIN aggregate plus a local observed-volume threshold/alert. Missing
or malformed collection is unavailable, not zero. Display known subtotals and unknown
usage honestly, with capped/best-effort/retained-window limits and costs unavailable.
The card must remain accessible at desktop/320px/200% text. No automatic grade or
provider approval is inferred. New decision belongs in ADR-054 before code.

Acceptance: real SDK delta/zero/unknown/coherence and privacy-canary tests; existing
request-store regression; real Redis retry/TTL/cap/corruption/isolation/freshness; actual
FakeModelProvider success/failure/omitted-versus-zero token fields; worker lifecycle and
fake probe; ADMIN denial, alert/recovery, generated contracts, browser presentation,
source/dependency/image security, recovery and complete hosted gates before promotion.
