# E2 reviewed rubric verification

Updated 9 October 2026. Requirements: FR-CNT-001/002/003/004, FR-GRD-003/004, NFR-SEC-002.
Status: implemented; local checks pass; hosted database/browser acceptance pending.

[ADR-044](../decisions/ADR/044-reviewed-rubric-persistence.md) adds synthetic SHORT_TEXT authoring
and independent review to existing content workflows. Migration 0023 creates version-pinned rubrics
and ordered criteria. SQL requires normalized material to match the canonical reviewed document,
freezes it outside DRAFT and rejects learner assignment. Existing objective hashes/retries remain
compatible because absent/null rubric fields are omitted from canonical serialization.

Staff can author criterion text, points, acceptable evidence, common errors and prohibited inference;
reviewers see the full material and immutable version reference. Complete review requires summed
points equal the item maximum, CRITERION_SUM, no objective answer key, and all existing rights,
curriculum and review controls. Rubric rows are included in staff-provenance deletion inventory;
learner exports continue to exclude hidden rubric material. Learner submissions, grading and mastery
are not broadened. No model, messaging, email or cloud runtime call is made.

## Acceptance coverage

- Three contract cases preserve legacy serialization and reject duplicate criteria and learner/
  WhatsApp short-text submission.
- Eight real-database cases cover storage/replay, independent review, returned corrections, approved
  immutability/new versions, access restrictions, incomplete review, SQL projection/list guards,
  staff inventory, objective selection and assignment exclusion, and an unchanged legacy document/
  receipt across upgrade from 0022 (including repeated upgrade).
- The new browser journey authors multiline evidence, saves/reloads it, rejects self-approval,
  checks the full independent review material and accessibility, and approves without enabling
  learner delivery. The inventory is 21 cases per engine, 63 executions across Chromium/Firefox/WebKit.

## Commands and current results

`make openapi format lint openapi-check test-unit build e2e-list security` passed: 416 unit/contract
and five tooling tests, Python/TypeScript lint/types, generated contracts, production build, all
three browser inventories, Bandit, secret-boundary checks and Python/JavaScript dependency audits.
No new dependency was introduced.

Native `make migrate`, focused `PYTEST_ADDOPTS='-k reviewed_rubrics' make test` and `make e2e`
failed during PostgreSQL connection/setup on localhost:55432. The eight database fixtures and
browser application assertions were not executed successfully. Docker.app remains unavailable.
Hosted CI must pass clean setup/migrations/seed, the full database suite, recovery, browser matrix,
security scans and container smoke before this slice is promoted to main.

## Limits and recovery

Synthetic review is infrastructure evidence, not approved curriculum inventory or grading accuracy.
Learner short-text eligibility, pending/neutral output, worker/fallback/mastery integration, frozen
benchmark and academic calibration remain open. Full hold/retention coverage and deletion remain
incomplete. Existing objective behavior must continue to pass regression.

After storing SHORT_TEXT documents, do not roll back to a pre-rubric binary. Use a compatible
forward fix to disable new authoring while preserving schema, reviewed evidence and assignment
guards. Migration downgrade intentionally refuses destructive removal.

Rubric acceptance follow-up (9 October): CI 37909280438 passed clean migration/seed but failed
synthetic recovery population. `make test-reviewed-rubrics` now runs before recovery to expose
focused database diagnostics; the complete recovery and regression gates remain required. No
rubric acceptance or main promotion is claimed from this failed run.

The rubric SQL guard incorrectly treated the existing item_versions.document JSON column as JSONB.
Normalize a local comparison value to JSONB before equality/existence checks; retain the original
column, stored documents and hashes. Existing fresh/upgrade and projection tests cover this path;
complete hosted rerun remains required.

CI 37910416518 verifies the rubric SQL correction: eight focused rubric cases, all 182 integration
and 427 unit/contract tests pass, as do the restricted login and 54-table/272-row recovery drill.
The new Chromium rubric journey fails after save/reload. Add exact API round-trip assertions and
`make test-web-content`, an isolated deterministic HTTP-fixture browser regression, before full CI
services. It supplements, not replaces, the 63 real-API journeys. Main promotion remains blocked.
Browser binaries now use the repository-local .local/browsers cache to avoid shared-cache mutation.

The isolated UI run 37914386755 reproduced the rubric lookup failure immediately after save.
Nested labels included the remounted textarea's initial text in exact label matching. Use unique
React IDs with explicit label associations for criterion/evidence textareas; retain exact label,
multiline value and API round-trip assertions. Local lint/types/build pass; browser rerun required.
