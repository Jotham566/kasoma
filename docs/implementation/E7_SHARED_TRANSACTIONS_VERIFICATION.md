# E7 shared assessment transaction verification

Status: transaction boundary verified; channel practice remains pending.
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
a normal restart, so database acceptance was obtained from
[hosted CI 37149982356](https://github.com/Jotham566/kasoma/actions/runs/37149982356) on exact
commit `50044d4`: 398 Python tests (257 unit/contract and 141 integration), 20 browser and five
tooling tests passed. Setup, clean migrations/seed, lint/types/contracts/build, security and
container smoke all passed. The commit is published on main. No migration or environment change is required
for this refactor. No academic/production or WhatsApp-practice acceptance is claimed.

## Independent formatting boundary

[ADR-036](../decisions/ADR/036-whatsapp-objective-message-format.md) and
`tests/contract/test_whatsapp_format.py` cover 33 pure formatting/normalization cases.
`make format lint test-unit` passes 290 unit/contract tests plus five tooling checks. Questions
must be explicitly WHATSAPP-suitable, plain text and fit without truncation; responses preserve
numeric representation and normalize to existing schemas. These helpers do not select approved
versions, authenticate message senders, bind reply context or create attempts. Integration remains
pending. The initial significant-figures fixture was corrected to exclude fractions, preserving
the existing academic rule rather than weakening it.

`make security` passed on 4 October after a transient dependency-audit connection reset on the
first attempt; both Python and JavaScript audits report no known vulnerabilities. Formatting
changes do not alter database schemas or public contracts. Full hosted regression remains pending
for this independent boundary.
