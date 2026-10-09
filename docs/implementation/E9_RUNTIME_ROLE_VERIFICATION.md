# E9 restricted assessment login verification

Requirements: NFR-SEC-002; supports FR-GRD-001 and FR-MST-001.
Status: implemented; hosted database acceptance pending.

`tests/integration/test_runtime_role.py` provisions a UUID-named temporary PostgreSQL LOGIN
against only the existing isolated synthetic assessment schema. The login has no superuser,
database creation, role creation or RLS bypass capability and owns no schema or evidence tables.
It connects using its own generated credential; it does not use SET ROLE through an owner connection.

The profile grants schema usage/table reads and enumerated writes required for rate limits,
sessions, items, attempts, grades, receipts/events and mastery evidence/estimates/history.
PostgreSQL row locking requires UPDATE on a column of item_versions: UPDATE(id) enables the
existing lock while the existing identity/revision trigger rejects an actual ID write. The role
cannot update revision, content or approval status. This nuance is asserted rather than assumed.

The test starts, serves and grades an original synthetic objective item, checks idempotent replay
and exactly one attempt/grade/mastery evidence row, and denies another learner's session access.
It verifies permission denial for schema creation, trigger disabling, table deletion, evidence
rewrites, role/content changes, replication bypass, owner-role escalation and password-catalog reads.
The narrow item-version column grant is separately checked against the immutable trigger.

The ephemeral password is bound through a transaction-local setting, excluded from engine parameter
logs, and provisioning diagnostics are withheld because dynamic SQL errors can contain expanded
statements. Cleanup revokes only this generated role's fixture grants and drops that exact role;
it never uses DROP OWNED, prefix cleanup, production data or a developer schema reset.

Run `make test-runtime-role` after `make setup services`. The command is also covered by the
integration suite in `make test`. Local `make format lint openapi-check test-unit` passes 394 unit/
contract and five tooling checks. Native focused execution fails during fixture connection because
PostgreSQL on localhost:55432 is unavailable; no role was created and no assertion acceptance is
claimed. Full hosted execution is required before promotion.

No migration, API contract, dependency or architectural decision changes. Default application
credentials remain unchanged. This tests the assessment permission profile only; complete module
and worker grants, separate migration/runtime credentials, deployment provisioning, production MFA
and role governance remain release gates. It does not establish database row-level tenant isolation.

The first hosted run 37227070209 passed all 162 existing integration cases but the new restricted
login correctly failed the attempt-hint guard's users-row lock. PostgreSQL requires an UPDATE
privilege for SELECT FOR UPDATE. The test profile now grants only UPDATE(display_name), the
mutable encrypted field used by existing profile editing, and explicitly verifies that users.id,
status and birth_date remain unwritable. This does not assert that display names are immutable or
that application ownership checks are implemented by database RLS. The grant is revoked during
exact-role cleanup. Full hosted verification must be rerun before promotion.

CI now runs the focused `make test-runtime-role` immediately after recovery, before the complete
regression suite, so grant-profile failures surface early. The full integration suite still includes it.

## Hosted acceptance recorded 9 October 2026

Commit `64394ac` passed [CI 37228984415](https://github.com/Jotham566/kasoma/actions/runs/37228984415):
413 unit/contract, 174 integration, 60 browser and five tooling checks, plus focused restricted-login,
clean migrations/seed, isolated recovery (52 tables, 272 rows), lint/types/contracts/build, security
and container smoke. It is promoted to main. This supersedes earlier hosted-pending statements.
Native PostgreSQL remains unavailable; production, academic and other stated scope limits remain.
The restricted-login users-row lock grant correction is included and verified.
