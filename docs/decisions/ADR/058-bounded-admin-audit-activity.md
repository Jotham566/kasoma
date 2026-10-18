# ADR-058: Bounded ADMIN audit activity summary

Date: 19 October 2026
Status: Accepted for bounded synthetic ADMIN activity; no individual support access
Requirements: FR-OPS-003, NFR-SEC-002, NFR-ACC-001, NFR-PERF-001, NFR-MNT-001

## Context and decision

The approved API includes GET /admin/audit and the UX includes Audit navigation.
Existing audit rows are append-only but no admin audit page is implemented. Operations
responses must expose aggregates; learner-level access needs separate explicit support
permission. Implement a fixed-category activity sample, not individual audit records.
This stays within delegated engineering discretion and grants no new support permission.

ADMIN authorization and live roles are rechecked on each request in the same database
transaction as the query; use twenty reads per administrator per minute. No query
parameters, actor/target search, free-text filtering, raw JSON or record drill-down.
The response includes the exact 24-hour window, at most 10,000 sampled actions, an
explicit cap flag, and seven fixed categories including OTHER. Query the newest rows
by created_at then UUID, with a 10,001st sentinel. Exclude future-dated rows. Counts
sum to the sample, and a capped sample is never described as the total audit history.
These are activity counts, not unique staff, learner, incident or correctness counts.

Classify actions inside SQL; only bounded category literals cross the database boundary.
Map known server action prefixes to CONTENT, FLAGS,
IMPORTS, PRIVACY, ROLES and GRADING_REVIEW; unknown actions become OTHER and their
text never leaves the server. Return every fixed category including zero values.
No actor/target/request UUID, reason, before/after hash, contact or body enters the
response, logs or telemetry. The read is not a critical administrative mutation and
creates no self-referential audit row on refresh. Existing action audits remain intact.

An additive created_at/id index supports the bounded time-window query. No row/data
transform, historical rewrite, retention extension, trigger change or cloud service.
The UI adds Audit to existing staff navigation, uses the existing green/paper design
and accessible controls, and clearly explains sampled/capped/empty/error states.
A failed refresh removes stale results; ADMIN remains enforced server-side.

## Acceptance and rollback

Require real API role/revocation/rate and sample/window/unknown-text minimization tests,
exact cap/tied timestamps, unchanged SQL audit immutability and clean/0036 upgrade.
Generate contracts, check static/unit suites, actual restricted login, populated
recovery, security, Docker smoke and full hosted acceptance. Verify actual authenticated
browser refresh and denied/empty/offline/capped states, keyboard/axe, 320-pixel and
200% text reflow with visual inspection. Do not infer application acceptance from docs.

Rollback can hide the new route/navigation while preserving audit evidence and its
existing immutable guards. Index removal is optional and does not delete records.
No real learner, legal, provider or production release approval follows from this slice.

## Complete hosted acceptance

Integrated source `5d95f9d7cc2fe37a9a2f8624ea6b6960f8e5f497` passes complete
[39171302022](https://github.com/Jotham566/kasoma/actions/runs/39171302022): 940 unit/contract, 378 integration,
35 tooling, 105 ordinary browser executions, three UI harness cases and three native
WebKit transport-control cases, migrations/restore/restricted login, source/dependency/
image security and container smoke. It is promoted to main with a documentation-only
closeout; merged branches are removed. The older standalone clock disk failure remains
failed evidence. No real-data, academic, provider or production approval is inferred.
