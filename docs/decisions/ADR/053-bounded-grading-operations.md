# ADR-053: Bounded local grading operations

Date: 18 October 2026
Status: Accepted; local and hosted verification pass at a357222 (39155326659)
Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-COMP-001

Extend the existing ADMIN snapshot with additive optional grading counts from durable
work and review/publication state. Reuse capped 10,000 counts with lower-bound markers.
Expose queue/running counts, oldest pending age, expired running leases, definitive/
neutral/processing-fallback terminal counts in the inclusive previous 24 hours, pending
review assignments and bands disabled after activation. No record identities, model
inputs/results, band scope or reviewer details enter the projection or alert logs.

The stored GRADING_FAILED reason covers provider refusals, budget and validation
fallback as well as unexpected failures. Expose its exact LOW_CONFIDENCE subset as
processing_fallback_finished_24h, with explicit wording; never interpret it as an
academic error rate or automatically declare an incident. Other neutral policy/expiry
outcomes remain outside that subset. Only stale pending age receives a new typed local
threshold and GRADING_STALLED alert. Do not create a permanent alert on historical
sticky disablement; exclude never-activated rejected candidates from that count.
Pending audits include sealed internal assignments and never count as successful reviews.

Existing authorization/rate limits and unavailable-on-DB-failure behavior remain.
The UI retains AI_USAGE and GRADING_FAILURE_RATE as unavailable. This is local queue
observation within ADR-033, not a provider/retention/grading-policy change. No migration,
inference, new service or cloud dependency. Thresholds are local engineering defaults,
not a performance SLO or academic/pilot approval. Verify actual synthetic transitions,
boundaries/alerts/recovery, minimization, contracts and affected browser/worker regression.
See [readiness](../../implementation/E8_GRADING_OPERATIONS_READINESS.md).


The shared staff page applies zero-minimum grid sizing and anywhere wrapping, extending
existing review-page behavior to operations and other staff views. The operations
journey now checks actual 200% text reflow/axe at 320 pixels without clipping, followed
by unchanged standard-size state/alert assertions. Complete staff/browser acceptance
is rerun after rebuilding the native bundle; no concurrent native browser commands.
