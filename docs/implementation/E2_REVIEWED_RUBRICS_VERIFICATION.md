# E2 reviewed rubric verification

Updated 9 October 2026. Requirements: FR-CNT-001/002/003/004, FR-GRD-003/004, NFR-SEC-002.
Status: synthetic authoring/review acceptance verified; learner short-text delivery remains disabled.

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

Hosted CI [37914864557](https://github.com/Jotham566/kasoma/actions/runs/37914864557)
passed at `ed7d7d5`: 427 unit/contract and 182 integration tests (609 Python total), five tooling
tests, 63 real-API browser journeys across Chromium/Firefox/WebKit and one isolated editor UI test.
Clean setup/migrations/seed, eight focused rubric cases, restricted-login verification,
lint/format/types/contracts/build, dependency/source/image security checks and container smoke all
passed. The isolated logical recovery restored 54 tables/272 synthetic rows in 455 ms and verified
pgvector/immutable guards; this is not production PITR/RPO/RTO evidence. Cold question transfers
were 191529/194251/193635 bytes, each below 250000. Commit `ed7d7d5` is on main; both completed
rubric/telemetry branches were deleted locally and remotely.

Native Docker now responds (29.8.2). Initial service retries failed because its installed CLI was
absent from PATH; the documented macOS PATH adjustment starts the approved service image builds.
Native database/browser acceptance remains pending those downloads/builds and subsequent checks.

## Limits and recovery

Synthetic review is infrastructure evidence, not approved curriculum inventory or grading accuracy.
Learner short-text eligibility, pending/neutral output, worker/fallback/mastery integration, frozen
benchmark and academic calibration remain open. Full hold/retention coverage and deletion remain
incomplete. Existing objective behavior must continue to pass regression.

After storing SHORT_TEXT documents, do not roll back to a pre-rubric binary. Use a compatible
forward fix to disable new authoring while preserving schema, reviewed evidence and assignment
guards. Migration downgrade intentionally refuses destructive removal.

## Failures corrected before acceptance

CI 37909280438 exposed JSONB operations against the legacy JSON document column. Migration 0023
now casts a local comparison value, preserving existing stored documents and hashes. CI 37910416518
then passed all database tests but failed the new browser lookup. Isolated UI run 37914386755
reproduced a label association problem after textarea remount. Explicit unique React IDs and
label associations fix the lookup without weakening multiline value or API round-trip assertions.
The complete successful run above supersedes those failures. Browser binaries use .local/browsers
to avoid the shared-cache lock failure seen during the first native install.
