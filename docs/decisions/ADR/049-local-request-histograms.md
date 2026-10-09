# ADR-049 proposal: Bounded local request histograms

Date: 9 October 2026
Status: Proposed; candidate runtime integration under verification
Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-MNT-001

## Context and proposed decision

ADR-033 exposes unavailable latency honestly. Existing response-start logs are not
an aggregate. Extend the approved OpenTelemetry metrics architecture with a single
attribute-free histogram of API middleware entry to response headers ready, in integer
milliseconds. This is not complete-body latency, an operation-specific load gate or an
availability SLO. Keep existing request logs and correlation traces separate.

Use fixed inclusive upper bounds 0, 10, 25, 50, 100, 250, 500, 1000, 1500, 3000,
8000 and 30000 ms plus overflow. Disable exemplars and minimum/maximum recording;
use an explicit static resource rather than environment/host resource discovery.
The storage projection will retain only interval times and bucket counts, not SDK
JSON, sums, raw durations, request timestamps, status/route dimensions or identifiers.
Nearest-rank p95 must be presented as a bucket interval, never an exact number.
Empty observations, measured zero and overflow are distinct states.

The complete slice uses an owned SDK delta reader with periodic off-request export
to existing local Redis. Five-second collection, at most 256 interval records,
and absolute expiry five minutes after each interval starts are implemented. Expiring
from the start bounds the age of every retained observation, including delayed export.
Retry must not extend
retention or double count. Scope keys by the existing keyed database/search-path
identity; no global key scans. Each interval is at most 1024 bytes; a fixed registry
indexes separately expiring keys. Identical retries use the same key and conflicting
payloads fail closed. Capacity eviction sets a finite capping marker. A random owned
collector identity separates process streams and is never presented to operators.
Redis writes validate time against its own clock, allowing at most one second of
host-native/Docker clock skew; stale or more-distant future intervals cannot refresh
freshness. Actual Redis expiry is additionally capped at five minutes from its own
clock, including when an accepted SDK interval starts slightly ahead. A real local
collector test exposed millisecond host/VM clock differences and exercises this bound.
A successful empty SDK collection refreshes a separate 15-second heartbeat.
Missing unexpired entries or malformed data are unavailable rather than measured zero.
Bounded exporter failure must not fail learner requests.
One owned thread collects every five seconds; SDK recording performs no Redis I/O.
The Redis client has 500ms connection/read bounds, no automatic retry and one connection.
Shutdown signals the thread and joins for at most three seconds before disposing owned
resources. Best-effort observed intervals are not a complete request ledger: outages,
process exits and capacity limits can lose measurements. Dashboard wording must preserve
this distinction, and this aggregate cannot establish an agreed-load SLO.

These are local engineering choices within delegated discretion, not new production
provider or privacy approval. Final lifecycle and storage details require tests before
acceptance of this proposal.

Expose the aggregate through the existing ADMIN-only, rate-limited snapshot and its
monitoring task. Mark malformed, expired or unavailable sources unavailable. A fresh
empty collection is different from an absent collector; add a bounded freshness signal.
Keep the aggregate window and any coverage/capping limitations visible. Alert only
when the histogram proves the configured threshold breach with sufficient samples;
do not infer a breach from an upper bound that merely overlaps the threshold.

## Privacy review and limits

No actor, session, correlation, path, query, model input or free text enters this
metric. One fixed series prevents dimension-based singling out and uncontrolled
cardinality. Disabling exemplars prevents automatic trace/span identity attachments.
Short-lived counts still reveal aggregate activity; restrict access to ADMIN, retain
only the bounded window and require the existing privacy/DPIA review before real
learner use. This local minimization assessment is not that external approval.

## Acceptance and rollback

Verify real SDK delta semantics, boundary/property tests, empty/zero/overflow,
metadata canaries, finite retention, retry idempotency, corruption, Redis outage,
multi-process aggregation, bounded memory/I/O, lifecycle shutdown, revoked-role
denial, API contracts, simulated alert/recovery and browser presentation. Run the
repository quality and full application gates before enabling and promoting.

Candidate API lifecycle, ADMIN snapshot, monitoring and presentation are running on
the local review stack after full native API/backend/browser and container checks.
Hosted acceptance remains pending; this proposal is not accepted on main.
Rollback removes the reader/exporter and lets its
finite Redis TTL expire; the dashboard must return to unavailable, not zero.
