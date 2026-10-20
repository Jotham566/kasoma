# ADR-075: Actor and bound-recipient credential dispatch gates

Date: 20 October 2026 (Africa/Kampala)
Status: Accepted technical implementation under approved ADR-061; verification pending
Requirements: FR-ID-001/002/003/005/006, BR-010, NFR-SEC-002, NFR-MNT-001

## Decision

Extend ADR-074 to LINK/GUARDIAN. After current recent actor authentication, pre-read
the recipient's exact current verified identifier binding. Coordinate that recipient
with a shared subject gate before rate/identifier work. Do not acquire a second
account HMAC lock: opposing actor/recipient requests could otherwise invert locks.
Recheck the original binding under the identifier lock. New or changed bindings
require fresh issuance, never late account adoption. A retained closed recipient
receives generic acceptance without a new challenge/code/provider call.

Dispatch protects the authenticated actor and known recipient on one owned pooled
connection. Accept only a finite tuple of one or two UUID subjects, deduplicate and
sort before nonblocking shared acquisition. Any partial/uncertain acquisition or
release invalidates that connection. Reuse it for a fresh short transaction that
reauthenticates the current recent actor token and rechecks binding/closure; commit
before send. No row/HMAC lock or open transaction spans the provider call. A duplicate
actor/recipient takes one gate; the model gateway's existing None-valued port remains.

An originally unbound recipient has no attributable subject gate. Changed binding
before the recheck suppresses dispatch; it does not authorize hash attribution or
claim later relationships. ADR-061's original-clock unbound drain and full third-party
payload clearance remain required before actual erasure/identifier removal.

Failure/suppression cleanup takes only this invocation's exact new challenge identity
and expected actor binding. Coordinate the actor before deleting. If closure has
committed, leave its original source and clock for the restricted lifecycle/expiry;
ordinary application code cannot remove it. If a code was consumed, leave that
evidence intact. Otherwise discard at most the exact pending new row. No hash sweep,
other-request deletion, retention extension or new ownership policy is permitted.
Suppression/authentication/gate failures are not provider observations. Actual
returned/failed calls retain their existing finite observation semantics.

## Scope and acceptance

No new public schema/migration/environment key, normal review activation, real data,
closure executor, preservation authority or DELETE completion. The approved generic
OTP response and existing rate/consent/verification policy remain. Native tests use
only the registered fresh-source factory and fake providers; future closed-row
fixtures are not SQL authorization, closure or erasure acceptance.

Prove actor/recipient late closure and current-session rejection, closed email/phone
recipients, actual two-subject idle gates, partial-acquisition cleanup, duplicate
subjects, one-connection operation, changed binding, closed/consumed failure cleanup,
unchanged LOGIN/model/consent paths and exact owned cleanup. Full source/payload/SQL
guards, exact preservation, bounded removal and quarantined recovery remain required.
