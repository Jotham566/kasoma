# ADR-060: Completed export accountability retirement

Date: 19 October 2026
Status: Proposed — awaiting explicit bounded synthetic implementation approval
Requirements: FR-ID-006, FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001

## Context and authorization

The [security retention schedule](../../specifications/09_Security_Privacy_and_Safeguarding.md)
requires minimized data-subject request evidence for six years after completion.
[ADR-027](027-data-request-intake.md) and
[ADR-048](048-asynchronous-owned-export-delivery.md) apply that policy to request
accountability and export-job summaries. Existing immutable DELETE guards retain
them even when their persisted deadline has passed. Copy expiry after 24 hours is
already separate and does not retire this evidence.

[ADR-045](045-accountability-record-holds.md) states: “Expiry/release never bypasses existing immutable
DELETE/UPDATE guards or authorizes deletion.” The
[source-of-truth change protocol](../../specifications/00_README_Source_of_Truth.md)
requires human approval before changing security, data or learner-visible behavior.
ADR-057's approved minimized channel snapshots grant no authority for this change.
This proposal supplies the concrete next decision; it is not an accepted exception
to any current guard or permission.

## Options and recommendation

1. Recommended: a default-disabled, policy-bound synthetic processor for completed
   EXPORT accountability only, with exact holds and restricted database execution.
   This delivers one testable retention slice while leaving account erasure separate.
2. Defer all accountability retirement until the complete account-erasure processor.
   This avoids an intermediate capability but leaves a known retention gap and couples
   export evidence to unrelated preservation work.
3. General DELETE privileges or a caller-set trigger bypass: rejected. Either would
   permit deletion outside the reviewed policy and weaken existing immutability.

## Proposed first vertical slice

Implement only against isolated synthetic databases, with explicit enablement and
default-disabled configuration. No real-data processing, running review-stack purge,
account closure, pending DELETE completion or production activation is authorized.
The later real-data decision remains subject to the privacy and release gates.

The deletion allowlist is exactly:

| Table | Proposed eligibility |
| --- | --- |
| `data_request_receipts` | Receipt for an eligible completed EXPORT, individually unheld |
| `data_request_reviews` | Review for that request, individually unheld |
| `personal_export_jobs` | That request's EXPIRED job, individually unheld, no grant or generation reference |
| `data_subject_requests` | That completed EXPORT, individually unheld, after all referencing evidence is removed |

An eligible parent has a valid completion timestamp and persisted deadline equal to
completion plus six calendar years, now due according to the database wall clock.
No caller-supplied clock, age or cutoff authorizes work. Pending requests, every DELETE
request and malformed deadlines fail closed. There must be no `data_exports` copy or
`personal_export_generations` row for the request. Existing 24-hour object/copy cleanup
must finish first; this processor never deletes a locator needed for retryable cleanup.
It does not delete objects, shorten a copy lifetime or reconstruct an expired copy.

Exclude users, sessions, consent, learning/assessment records, flags, channel records,
snapshot stores, legal-hold ledgers and general audit/history stores. No cascading
deletion or anonymization is introduced. Existing UPDATE immutability remains intact.

## Exact holds and ownership

Keep existing DATA_REQUEST and DATA_REQUEST_REVIEW holds. Add explicit original-record
hold targets for a request receipt and a cleared EXPIRED export-job summary; do not
freeze active jobs or temporary authentication grants. A receipt currently has an
actor/key composite primary key, so add an immutable generated unique receipt UUID
without changing its existing retry identity. The job's exact identity is its existing
request UUID. These are proposed new hold targets, not implied coverage from ADR-057.

Reuse independent recent-OTP ADMIN claim, pending DELETE case, reason/decision,
finite expiry and source-owner verification. For source identification, provide a
bounded, owner-checked lookup within that claimed case for an exact EXPORT request:
at most 50 stable receipt references per page and the cleared job reference. Return
no keys, hashes, grants, contact data or source payload. No global or per-user search
permission is added. Extend contracts and accessible existing hold controls only for
these explicit targets; retain feature-gate and authorization checks independently.

Retire eligible unheld leaves first. A held leaf keeps its necessary parent reference;
it does not hold sibling rows. A held parent does not silently hold every child.
Foreign keys remain enforced, and a still-referenced parent remains as a structural
dependency until safe retirement. Recheck source ownership, terminal state, deadline
and exact active holds under locks at deletion time. Hold creation and retirement
must use a compatible lock order so a race either preserves the committed hold or
refuses preservation of an already-absent source; never acknowledge a lost hold.

## Execution and accountability

Use a dedicated restricted maintenance database login, not general application DELETE
rights. A narrowly owned, fixed-search-path SECURITY DEFINER routine may process only
the allowlist and independently validate every predicate. Revoke PUBLIC execution;
ordinary API/worker roles cannot invoke it, assume its owner, change guards or supply
arbitrary SQL/targets/cutoffs. Do not use a caller-set session variable as authority.
The owner must be non-login with only the privileges required for this routine.
Any migration/role integration must be proven using actual restricted logins before
acceptance; inability to enforce this boundary blocks implementation acceptance.

Bound each batch to 100 removed and 200 examined rows, a five-second cooperative
budget and database statement/lock timeouts. Use resumable stable scanning with wrap
so a held prefix or large receipt history cannot starve later eligible evidence.
Replays after commit are harmless; a failed transaction rolls back removals and its
audit together. Configuration requires exact-hold support before retirement enablement.
Existing holds remain readable/releasable independently of new-creation switches.

Record a minimized system batch audit atomically: generated batch/correlation UUID,
fixed operation code, time, per-table counts and closed skip/failure categories.
No learner/source/receipt identifiers, keys, hashes, payloads or per-record tombstones
are copied into a replacement log. Use the existing audit mechanism with no actor
reference, subject to a proposed security-audit classification (12 months under the
retention schedule). Active-investigation preservation and finite audit disposal must
be resolved before real processing; this slice does not claim full audit retention.
Aggregate operational health reports bounded progress/backlog and failures without
individual evidence. Preserve confidential diagnostic handling.

After lawful receipt retirement, a previously used UUID key cannot be recognized
indefinitely. Propose ordinary current authentication, rate limits and pending-request
deduplication for a later POST using that key; it may create a new request, never
resurrect the retired one. Reads of retired requests return the existing absent-record
response. During retention, exact retry binding is unchanged. This finite retry boundary
needs explicit approval and API documentation; do not add an indefinite key tombstone.

## Acceptance and implementation sequence after approval

1. Add receipt identity and the two exact hold targets with migration, contract,
   ownership, claim, feature-gate and accessible operator tests. No deletion yet.
2. Add the policy-bound SQL capability and deterministic synthetic processor with
   current/restricted login denial tests, exact hold races and atomic audit checks.
3. Integrate bounded scheduling, health and runbook controls. Keep review-stack
   retirement disabled; exercise only owned isolated synthetic fixtures.
4. Run prescribed lint/type/contract, clean and populated migration, integration,
   security, recovery and three-engine operator/browser checks. Verify hosted CI,
   docs and traceability before claiming this bounded slice accepted.

Tests must cover just-before/at deadline and calendar-year boundaries; database versus
caller clock; pending/DELETE/future/malformed cases; stale grants and uncleared objects;
per-record holds, release, expiration and parent dependencies; concurrent hold/delete;
large-history progress; crash/retry/rollback; original composite-key behavior; and direct
DELETE/DDL/role/session-variable bypass attempts through actual restricted logins.
Use fake providers and synthetic data. No inference or external delivery is needed.

## Consequences and remaining gates

This is additional retention machinery and two narrowly defined hold permissions,
not an accepted architectural change until reviewed. Approval would authorize only
the bounded synthetic implementation above. Full preservation coverage, account
deletion/anonymization, other retention classes, legal sufficiency and real-data
release remain incomplete. The six-year policy and 24-hour export access rule do not
change. An implementation failure cannot justify weakening holds, ownership or SQL
guards; return for a revised decision if the proposed boundary cannot be enforced.

Approval record: pending. No processor, migration, API change or runtime enablement
is included in this documentation increment.
