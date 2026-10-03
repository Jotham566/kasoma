# ADR-032: Bounded asynchronous draft imports

Date: 3 October 2026
Status: Accepted within delegated MVP implementation discretion
Requirements: FR-CNT-001/002/004/005, FR-OPS-001/002/003, NFR-SEC-002, NFR-MNT-001

## Decision

Implement JSON-only import of 1–20 synthetic draft candidates, at most 64 KiB per request.
Each candidate uses the existing supported draft schema, a source locator and explicit
original-synthetic provenance. Import creates no approved content, successors or learners.
Authors correct incomplete candidates using the existing editor; existing submit/independent
review/rights gates remain authoritative. No PDF/archive/media/model extraction is enabled.

A recent-auth CONTENT_AUTHOR submits an actor/key-idempotent job. Validate every candidate
before queueing, including taxonomy, source/rights and duplicate candidates within the batch.
The job is a durable PostgreSQL command outbox; Redis is only a wake-up transport. Celery
polls the imports queue. One job transaction plus savepoint creates all new drafts and their
normal audits/events, or none. Author role/account state is rechecked by the worker without
storing a bearer token. Existing owned identical candidates are reported as duplicates,
never modified. Source locator is retained on the versioned document.

Rows are claimed with FOR UPDATE SKIP LOCKED. A crash rolls back the claim and partial
work. Retry transient failures at most three executions, with 60/120-second backoff;
a terminal failed job is visible to its owner. Raw validated job payload expires after
24 hours and is cleared on completion/failure; no original upload is stored. Minimal
job references/results remain material administrative evidence under the existing
six-year-after-account-closure obligation; retention processing remains required.

GET job/list responses are owner-only and contain safe statuses, row positions and draft
references, not candidate payloads or exception details. Queueing is five new jobs/author/hour,
reads sixty/author/minute. Retries recheck authorization and bind the exact canonical body.
Job status is QUEUED, COMPLETED or FAILED; a locked executing job remains QUEUED until its
atomic commit. No request path runs imports synchronously and no model/provider is called.

## Verification and boundary

Test role/ownership/revocation, schema/size/active-content rejection, all-or-none persistence,
duplicate handling, retry identity, competing workers, rollback, bounded retries/expiry,
audit/outbox and separate approval. Browser tests cover file validation, lost acknowledgement,
status recovery, editing imported drafts and accessibility. No migration removes existing data;
rollback disables submission/polling and preserves job evidence for a forward fix.

This completes the structured synthetic JSON import path, not arbitrary-file extraction or
academic release acceptance. External rights, NCDC mapping and benchmark approvals remain gates.
