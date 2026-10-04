# ADR-035: Shared transaction-scoped assessment operations

Date: 3 October 2026
Status: Accepted within delegated implementation discretion; implementation verified (hosted CI 37149982356)
Requirements: FR-WA-002/003/004, FR-ID-003, FR-REV-001/002, FR-GRD-001/002, FR-MST-001

## Decision

Extract transaction-scoped start, next-item and answer submission operations from the existing
assessment application service. Web entry points continue authenticating bearer sessions and
calling the same operations. Internal operations accept a trusted actor UUID and caller-owned
SQLAlchemy transaction, acquire the existing actor lock, and independently enforce current account,
consent, S4 level and subject enrollment. An actor UUID is never accepted as HTTP authentication.
No bearer token is manufactured for the channel worker and no scoring/mastery logic is copied.

Preserve web API schemas, canonical idempotency fingerprints, content/version eligibility,
assignment ordering, hints, sealed diagnostic behavior, immutable attempts, deterministic grading,
mastery reconciliation and versioned outbox events. Internal methods never commit. A caller's
rollback must remove the assignment/attempt/grade/receipt/mastery/events together, allowing the
future channel worker to include its incoming receipt and outgoing reply in that transaction.

This refactor does not enable WHATSAPP attempts or change database channel constraints. A later
additive migration and channel capability/conversation implementation are required. Before enabling
practice, document explicit subject/topic selection, reply-to-question binding, expiry, concise
feedback, STOP behavior and supported-content filtering, then prove cross-channel parity. The
existing web contract remains WEB-only so clients cannot impersonate channel provenance.

## Verification and boundary

Run existing assessment, diagnostic, numeric, multiple-choice, hint, reassessment and mastery
regressions. Add direct internal-operation tests for transaction rollback, committed retry identity,
unknown/inactive actors, missing consent and foreign subjects/sessions. Execute clean-schema
integration in hosted CI if local Docker is unavailable. Synthetic fixtures and FakeModelProvider
remain mandatory. No academic threshold, model, provider or production enablement decision is made.
