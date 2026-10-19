# ADR-063: Bounded local API OTP adapter observations

Date: 19 October 2026
Status: Accepted within delegated MVP engineering discretion; verification pending
Requirements: FR-OPS-002, FR-ID-001, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001

## Decision and boundary

The approved operations scope includes messaging failures and usage. Existing local
channel observations do not cover email/SMS OTP adapter calls. Add four fixed,
attribute-free OpenTelemetry delta counters: email returned/failed and SMS returned/
failed. Count only an actual API OTP provider-port invocation after existing challenge
and rate/ownership checks. A normal return is not handset delivery, human receipt,
billing evidence or proof of a valid recipient. No transport receipt or error body is
collected. Rate-limited or otherwise suppressed sends are not adapter attempts.

Use a request-local injected observer, not a mutable global or a replacement messaging
provider. Ordinary domain/CLI calls remain compatible and unobserved. Observation
failure must not change the generic OTP response, delivery exception handling,
challenge cleanup, authentication, rate limits or any provider behavior. No Redis or
serialization runs on the send path; record four bounded integers under the existing
owned SDK pattern, with disabled exemplars and only static resource/scope names.

Collection defaults off. Enable only in development/test profiles using existing
fake/Mailpit adapters. Production stays unavailable even if the flag is set; no new
cloud provider, outbound call, credential or real-data approval is introduced.

Reuse ADR-054's bounded byte transport with a separate OTP purpose hash, Redis
namespace and canonical four-count codec. Preserve existing request/model keys and
codecs. Collect every five seconds off-request. Keep at most 256 <=1024-byte frames,
absolute 300-second expiry from the earliest observation, 15-second freshness and
existing bounded clock-skew/immutable-retry rules. Store no per-call records, identity,
contact, code, token, purpose, IP, route, error string, provider label or content hash.
Unknown, disabled, stale, corrupt or unacknowledged-export data is unavailable, never measured zero.
A fresh successful empty collection can report zero observed attempts in its scope.
A known SDK/export failure sets one finite namespace-wide uncertainty marker for up
to 300 seconds. On recovery, republish only its remaining window before freshness;
an empty pulse must not hide known loss. Producers cannot shorten another producer's
window. Reads check this marker atomically; existing request/model wire behavior is
unchanged. Intentional interval capping remains explicit lower-bound observations.

Expose only the bounded aggregate in the existing ADMIN snapshot and accessible web
card. Clearly label best-effort local adapter outcomes and capping/loss; retain general
messaging delivery/cost instrumentation as pending. One typed local failure threshold
(default one) may produce the existing periodic allowlisted warning; it enforces no
quota or learner decision and is not a production SLO. Existing ADMIN authorization,
read limits and no-store behavior remain unchanged. No database migration is needed.

## Acceptance and rollback

Test actual SDK delta/count/coherence, static scope/resource and no labels/exemplars;
strict canonical wire data and finite observation expiry; independent Redis namespaces,
immutable retries, cap/loss/staleness/corruption; normal API fake email/SMS attempts,
suppressed sends, provider failure and failing-observer invariance. Verify app-local
lifecycle and production refusal, current/revoked ADMIN access, count-only API/alerts,
older-response absence and zero/positive/unavailable keyboard/axe/narrow UI states.
Generate additive API/client contracts and run engineering/security/hosted gates.
No genuine delivery, billing, availability or academic acceptance follows these tests.

Rollback disables the collector/card and lets all transient keys expire. It does not
change or remove OTP challenges, credentials, learner history or audit evidence.

Complete hosted39304052749 succeeds at exact sourceceee401:1,171 unit/contract,
498 integration,35 tooling,114 full browser executions plus all engineering gates.
This verifies the bounded synthetic implementation; collection remains defaultfalse
and production/provider/delivery/billing/release gates remain unchanged.
