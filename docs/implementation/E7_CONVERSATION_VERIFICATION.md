# E7 local conversation verification

Status: synthetic/local application verified; production and measured performance gates remain.
Requirements: FR-WA-002/003/004/005/006, FR-ID-003/006, FR-CNT-004, NFR-PERF-002.
Decision: [ADR-038](../decisions/ADR/038-local-whatsapp-practice.md).

The internal foundation `c0b5b55` passed hosted CI 37217857047, including three-format score/mastery
parity. This report covers the subsequent signed conversation integration, not that earlier proof.

## Required checks

- `make format lint openapi-check test-unit`: local checks pass 310 unit/contract and five tooling
  tests so far; generated HTTP contracts are unchanged. Initial line-length/type issues were fixed.
- `make test-whatsapp-practice`: eleven real-database cases cover five-question single-choice,
  multiple-choice and numeric delivery, duplicate IDs, missing/stale contexts, STOP-before-worker,
  consent withdrawal and retirement before delivery, savepoint rollback/retry, expiry and owned projections.
- Run clean setup/migrations/seed, full test/browser suites, security audits/scans and containers
  in hosted CI because local Docker has no running socket. No native database acceptance is claimed.
- Deterministic fake providers only. No learner data, external messaging/model calls or Gemini.

## Local operation and rollback

Keep outbound disabled except for synthetic fake-delivery testing. `make process-messages` drains
bounded batches; the API now requests an immediate local Celery wake-up after commit, with the
existing ten-second periodic drain as recovery. Dependency outages must not reject durable intake.
`channel.wakeup_failed` carries no broker credentials or payload. Rate limits still apply.

START/CONTINUE presents or resumes a topic; reply directly to its menu/question. After each answer,
CONTINUE requests the next question. PROGRESS links to authenticated web progress. STOP cancels
pending delivery and clears the pointer; submitted learning evidence stays available on the web.
Pointers and queued encrypted replies expire after 24 hours. Export/inventory includes only owned
conversation metadata, not recipient hashes, ciphertext, menu internals or provider reply IDs.

For rollback, disable the channel entry points and workers and preserve evidence for a forward
fix. Do not downgrade, reset volumes or delete learning records. Production, academic, privacy,
remaining channel legal holds/erasure and measured latency/load acceptance remain pending.

## Native check results before hosted submission

`make format lint openapi-check test-unit` passed 310 Python unit/contract and five tooling tests.
`make security` passed Bandit, local secret boundaries and both dependency audits. `make migrate`
failed because PostgreSQL is unavailable, and all nine focused integration cases failed at fixture
setup before application assertions. These are not passing database results. No Docker reset or
data deletion was performed; hosted clean-schema verification is required for this snapshot.

Permanent stale/unauthorized/retired dynamic replies are cancelled without provider retries.
Unexpected provider failures retain the existing bounded retry policy. Outgoing references are
flushed before binding a conversation pointer, preserving foreign-key insertion order.

Follow-up: add concurrent distinct-message answers to the same question (one attempt/evidence),
align local web/runbook instructions and reconcile superseded foundation status notes. Local lint,
types, contracts and 310 unit/contract tests pass; hosted acceptance for the final snapshot remains required.

Review found a cross-channel continuation edge: WEB entry points must also recheck the version
channel label. Added this check and a WA-only content regression; no published content or existing
attempts are changed. The ADR-037 clarification preserves reviewed channel suitability.

Add an API regression for a broker wake-up exception returning durable acceptance and
leaves the message available to the recovery drain. No broker diagnostic or credentials are logged.

## Final hosted acceptance and publication

Commit `5063528` passed [CI 37220225176](https://github.com/Jotham566/kasoma/actions/runs/37220225176):
310 unit/contract plus 159 integration tests (469 Python total), 20 browser tests and five tooling
checks. Setup, clean migrations/seed, lint/types/contracts/build, security audits/source/image scans
and container smoke all passed. This includes the final concurrent-answer, broker-outage and
WEB/WHATSAPP suitability regressions. Promoted to main; the conversation branch was removed.
Earlier pending/native-failure notes above describe the pre-hosted attempts, not final acceptance.
No external transport, model evaluation, academic calibration or latency/load gate was exercised.
