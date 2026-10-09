# ADR-045: Individual flag-history and request-review holds

Date: 9 October 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002

Extend ADR-030/043's explicitly partial target registry with FLAG_HISTORY and DATA_REQUEST_REVIEW.
These are existing immutable accountability records. FLAG_HISTORY uses content_flag_history.id
and follows the flag's immutable reporter. DATA_REQUEST_REVIEW uses its request_id primary key and
follows the reviewed request's owner; it has no independent review UUID. The reviewer/triage actor
is not used as the requester ownership link. API and SQL lock/check both the named row and parent.

Retain the independent recent-OTP ADMIN claimant, existing mutation/read bounds, exact body/key
receipts, finite authorized decision, one-time release and six-year-after-request-completion hold
evidence policy. No record body, staff identity, internal resolution or guardian data is exposed.
Operators must already have an authorized preservation decision; this is not a legal determination.

A hold names only that immutable row. It does not hold its mutable parent flag, parent request,
sibling history, all reviewer activity or an account. Normal flag triage may continue by appending
new history; existing history remains immutable. Expiry/release never bypasses existing immutable
DELETE/UPDATE guards or authorizes deletion. Existing parent/reference protections remain intact.

Migration 0024 widens the registry and ownership guard while preserving previous validation, and
adds exact DELETE guards for the two records. No stored evidence or retention deadline is rewritten.
The administrator form explains the request key and exposes the expanded strict generated enum.
Existing deletion inventory already includes both sources; active holds appear through its existing
count and blocker. LEGAL_HOLD_COVERAGE_INCOMPLETE and execution_enabled=false remain mandatory.
Channel records, embedded references, other logs/backups and erasure/retention processors remain open.

Verify API/direct-SQL owned and foreign/missing targets, idempotency, scope, release/expiry, denied
held DELETE, unchanged immutable UPDATE/DELETE after release, continued parent triage, safe export,
fresh/upgrade migration and unchanged disabled deletion. Preserve all earlier hold regressions.
Rollback disables the new options/routes and uses a compatible forward fix; downgrade must not
remove registered holds or their guards. No provider, model, retention policy or disclosure change.
