# ADR-029: Minimized deletion-impact preview

Date: 29 September 2026
Status: Accepted within delegated implementation discretion (non-destructive preview only)
Requirements: FR-ID-006, BR-010, FR-OPS-003, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001

## Context and decision

ADR-027 requires a narrow reviewed erasure processor that reconciles immutable learning
and accountability evidence. Security section 6 and production-pilot section 5 require
record-specific, time-bounded legal holds and a re-identification risk review before
retaining de-identified metrics. Neither a legal-hold check nor an approved anonymization
transform exists yet. Changing user IDs alone is pseudonymization, not proof of anonymity.

Implement the next prerequisite as a complete read-only staff review journey. The
independent ADMIN who claimed a pending DELETE request can inspect counts of linked
records and their controlling retention/review categories. Require recent OTP again,
audited access and a per-admin limit of ten previews/minute. Other staff, another claimant,
the requester and revoked/stale sessions cannot access it. EXPORT requests are rejected.
No contact, profile, answer, score, guardian, comment, content or credential value is
selected or returned. Only request ID, observation time, fixed labels, bounded counts,
policy codes, limitations and known blockers leave the domain service.

The response always has execution_enabled=false. It cannot authorize execution, satisfy
a legal-hold check, establish an anonymization method, revoke sessions or mark a request
completed. UI makes that boundary explicit. Counts are current observations, not a frozen
execution plan; future execution must revalidate ownership, legal holds, inventory and
policy inside its own transaction. No destructive migration or broad trigger bypass.

## Inventory boundary

Use explicit relational queries for identity/profile, authentication, learning evidence,
consent, owned data requests, short-lived exports, learner flags and staff provenance.
Count unbound OTP challenges by the account's verified identifier lookup hash as well as
user ID, without reading/decrypting identifiers. Counts stop at 10,001 matching rows per
source: return 10,000 with at_least=true when truncated. SQL statement timeout remains
active; never return a partially failed preview as complete.

Related staff records are not necessarily owned by the learner: author/reviewer/audit
and support relationships require separate treatment. Shared curriculum is excluded.
Rate-bucket keys are opaque; they are not claimed to be fully attributed to an account.
Arbitrary embedded references, backups and operational logs are outside this relational
inventory. WhatsApp/channel links do not exist yet. These limitations are explicit;
zero rows never means erasure is safe or complete. Adding data-bearing tables requires
updating this inventory before enabling a future processor.

## Retention and next slice

Display the approved six-year consent/material-audit and request-evidence policies,
24-month resolved-flag policy and 24-hour export-copy expiry without inventing closure,
resolution or legal-hold dates. This slice creates no new retained copy of learner data;
only existing minimized audit metadata records access. No analytics identity event is
emitted for a preview. No architectural stack change, provider or external call.

Next implement record-specific legal-hold lifecycle and deletion execution state, then
review the exact erasure/anonymization migration and recovery plan. Destructive execution
must not precede that work. Production privacy/legal approval remains a separate gate.
