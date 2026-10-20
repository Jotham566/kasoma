# LINK/GUARDIAN credential dispatch verification

Requirements: FR-ID-001/002/003/005/006, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-075](../decisions/ADR/075-linked-credential-dispatch-gates.md).
Status: local engineering checks pass; own complete hosted acceptance pending.

## Protocol and scope

Recent actor authentication precedes recipient pre-read/shared coordination and
rate/identifier work. A different recipient takes no second account HMAC lock.
Re-read the original binding under identifier serialization; changed ownership
requires fresh issuance. Known closed email/phone recipients receive the existing
generic acceptance without a code, challenge or provider call.

The dispatch helper accepts only a tuple of one or two UUID subjects, deduplicates
and sorts them, and uses one pooled connection for nonblocking session-shared gates.
Partial/uncertain acquisition or release invalidates that connection. A short fresh
transaction on the same connection rechecks current recent actor authentication,
the original binding and closure; commit before send. No row/HMAC lock or open
transaction spans provider I/O. The existing model None-valued port is unchanged.

Failure cleanup coordinates the expected actor and deletes at most its exact new
pending challenge. Committed actor closure leaves the source and original expiry
for the restricted lifecycle/expiry; consumed evidence is not discarded. No hash
sweep, third-party attribution, new retention clock or preservation authority exists.
Only actual provider calls affect the existing returned/failed observations.

Originally unbound recipients have no attributable recipient gate. This does not
claim future relationships or replace the required original-clock unbound drain,
third-party payload clearance or permanent write guards before actual erasure.
There is no migration, new environment key/DTO, normal review activation, closure
executor, removal or completed DELETE. Production provider cancellation/concurrency,
external checkpoint recovery and academic/privacy/device/release gates remain open.

## Evidence and retained failures

The unchanged parent fails all eight initial native email/phone and late-closure
regressions; 11 existing gate contract cases pass. The first correction passes 19
combined cases and the existing 18 LOGIN/refresh cases. Expanded two-subject, cleanup,
binding and pool controls pass 40 combined cases plus 18 existing credentials.

The latest focused matrix passes 44 cases: 17 gate contracts and 27 new native cases.
These cover both purposes, closed recipients, actor/recipient late closure, revoked
and no-longer-recent sessions, two idle gates on one connection, partial acquisition,
single-connection pools, closed/consumed cleanup, both binding-change stages, duplicate
self-link and forced opposing actor/recipient lock order. Original rate limits and
assertions remain; no timeout, retry or acceptance threshold is relaxed.

Each native case uses the registered fresh fake-only source factory and standard
migrations. Future closed-row fixtures restore the exact named trigger before
consumer checks and verify zero erasure jobs; they do not prove real closure or SQL
authorization. Successful native contexts independently assert exact source-container
absence. Full broader, browser, captured-ID cleanup and own hosted evidence remain
pending and must be recorded separately, without reclassifying the initial failures.

## Requirements mapping

| Requirement | Changed component/evidence | Boundary |
| --- | --- | --- |
| FR-ID-001/002 | Identifier binding pre-read/recheck and generic code suppression | No new registration/link policy or owner DTO |
| FR-ID-003 | GUARDIAN dispatch current actor/recipient barriers | Consent wording/eligibility and guardian evidence policy unchanged |
| FR-ID-005 | Current token and recent OTP rechecked before send | Ordinary logout and refresh reuse protections retained |
| FR-ID-006, BR-010 | Closed actor/recipient and exact pending cleanup | Consumer prerequisites; no erasure fulfillment |
| NFR-SEC-002 | Bounded UUID set, partial cleanup and opposing lock tests | No arbitrary subject endpoint or SQL capability |
| NFR-MNT-001 | Named Make target, typed helpers, ADR, API/runbook and traceability | Full exact-source engineering verification required |


## Final local engineering checks

make format/lint, test-erasure-linked-dispatch (44), test-erasure-credentials (18),
test-erasure-identity-isolated (29 identity/lifecycle, 19 model, 16 source, six staff),
test-otp-observations-api (one integration/two deselected), test-unit (1,501 unit/
contract and 35 tooling), openapi-check, build, security and security-source pass.
Strict typing covers 228 Python sources. Existing populated additive migrations
pass unchanged; each new native source runs standard clean migrations. No public
migration/dependency change or generated contract difference is introduced.

make e2e separately passes 123 executions: 108 standard, 12 short-text and three
configuration. Its 12 exact recorded source IDs have empty cleanup reports and
independent full-ID absence. Twelve captured native IDs across initial failed and
final cohort logs are independently absent. The final27 new and18 existing native
contexts also assert exact owned absence; no inference is made about older unrelated
resources. Initial eight failures remain failures and are not application acceptance.

Preissued GUARDIAN consumption and closed-identity staff role revocation still need
closure-aware checks before activation; dispatch barriers do not prove those consumer
paths. Full installed SQL/ACL/ownership/payload/preservation/export guards, durable
fulfillment and checkpoint recovery remain. Normal review stays healthy/dormant on0045
and its actual source is the separately verified v3 preview. This candidate still
requires its own full639-integration/image/service/recovery hosted acceptance.
