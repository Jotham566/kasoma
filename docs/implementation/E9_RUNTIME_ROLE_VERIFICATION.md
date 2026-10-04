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
