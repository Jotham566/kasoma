# Grading operations readiness

18 October 2026. Requirements: FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-COMP-001.
Authority: SRD, security/AI/QA and production-pilot specifications; ADR-033/049/050/051.
The approved MVP remains S4 Mathematics/Physics, web and linked objective WhatsApp;
normal short-text scoring remains disabled and no provider call is authorized.

Existing ADMIN-only rate-limited operations API/UI monitors imports, flags, local
channel dispatch, exports and minimized request timing. It omits durable grading work
introduced by the verified candidate. Inspect `assessment_grading_work` and immutable
publication/review state; do not infer model cost, calibrated accuracy or academic
failure rate from neutral outcomes. The existing bounded count helper and closed
alerts provide the implementation pattern. No schema migration, provider, retention
or learner behavior change is needed; record additive API presentation under ADR-053.

Smallest complete slice: bounded queued/running/graded/neutral/processing-fallback counts,
oldest pending age and expired active leases; aggregate pending audit assignments and
previously activated disabled bands. Retain no per-learner, attempt, band or reviewer
identifiers in snapshots/logs. The stored GRADING_FAILED reason includes expected provider refusals plus budget,
validation and unexpected failures. Label that exact subset processing fallbacks,
separate from other neutral policy/expiry outcomes and academic correctness. Count pending audits
honestly, including sealed assignments that are not yet reviewer-accessible.

Use a typed local threshold for stale pending work. Do not automatically declare a
safe processing fallback to be an incident. Dashboard wording describes local queue health, not grading accuracy or the
release latency SLO. Missing database state is unavailable, not zero. Keep AI_USAGE and
GRADING_FAILURE_RATE unavailable: aggregate queue counts are not model spend or an
academic error-rate measurement. Do not alert permanently merely because a historical
band remains disabled; replacement approval is a separate controlled process.

Acceptance: actual synthetic encrypted queue/claim/neutral/grade transitions, expiry,
24-hour boundaries, threshold/recovery, bounded counts, revoked-role/IDOR and minimized
snapshot; generated API/client contracts; accessible desktop/320-pixel browser display;
full relevant backend/browser, lint/types/security/recovery/container checks before
promotion. No external calls, production data or destructive action.


The shared staff page applies zero-minimum grid sizing and anywhere wrapping, extending
existing review-page behavior to operations and other staff views. The operations
journey now checks actual 200% text reflow/axe at 320 pixels without clipping, followed
by unchanged standard-size state/alert assertions. Complete staff/browser acceptance
is rerun after rebuilding the native bundle; no concurrent native browser commands.
