# E7 shared assessment transaction verification

Status: implementation in progress; database acceptance pending.
Requirements: FR-WA-002/003/004, FR-ID-003, FR-REV-001/002, FR-GRD-001/002, FR-MST-001.
Decision: [ADR-035](../decisions/ADR/035-shared-assessment-transactions.md).

`AssessmentService.start_in_transaction`, `next_item_in_transaction` and
`submit_in_transaction` reuse existing grading/mastery and receipt logic in a caller transaction.
`authorize_actor` obtains the identity actor lock and reloads current account state before
checking consent, S4 level and subject enrollment. Public web wrappers authenticate the existing
bearer and call these operations. No HTTP actor override or WHATSAPP provenance is enabled.

New integration regressions cover rollback of session/assignment/attempt/grade/receipt/mastery/
events together, committed retry through the unchanged web fingerprint, foreign ownership,
unknown and disabled actors (including an ORM-cached stale user), consent withdrawal and enrollment.
Use `make test-assessment-transactions` for focused checks; all ordinary `make test` suites also
collect them. Existing full assessment/diagnostic/numeric/multiple-choice/hint/reassessment tests
remain necessary because the web wrappers now use the extracted operations.

Executed locally: `make format lint openapi-check test-unit` passes (257 Python unit/contract
and five tooling tests), with unchanged generated API contracts. Docker remains unavailable after
a normal restart, so the three new PostgreSQL integration cases have not run locally. Hosted CI
must validate the exact snapshot before promotion. No migration or environment change is required
for this refactor. No academic/production or WhatsApp-practice acceptance is claimed.
