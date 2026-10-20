# Installed erasure principal separation verification

Requirements: FR-ID-006/FR-OPS-003, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-078](../decisions/ADR/078-installed-erasure-principal-fence.md).

## Implementation boundary

The fresh-only v6 compiler freezes explicit grant tuples for the three new principals
and private objects, PUBLIC source-table/column controls, and original database
CONNECT/TEMP. It compares both directions, grantors/options, role flags/global
settings/memberships/defaults and persistent ownership. Only exact control-table,
primary-index and linked TOAST dependencies are allowed. No name-prefix adoption.
All decisions use raw catalog fields and fixed built-in signatures. No deparser,
source row/key export, live-derived ACL expectation or new permission is introduced.

scope_identity_ok adds the predicate compiled from the immutable checked template;
it never rewrites/normalizes a live body. Readiness, plan/version and expiry therefore
fail before source writes. Existing v1-v5 recipes stay historical and are not adopted.
The public0045 schema and both false execution flags remain. Temporary objects retain
the existing documented shadow-test scope; no ordinary source access is granted.

This does not cover every unrelated existing-role/public-function grant or the full
installed code/catalog/payload/hold/preservation/export fence. Those remain required
before durable atomic authorization/closure, permanent write guards, bounded removal
and external checkpoint/quarantined restore. No actual job or erasure is enabled.

## Retained failures and diagnosis

Eight pre-change native cases all fail because readiness still returns after extra
source/table/column/schema/function/grant-option rights, lost SELECT or changed role
settings. A first format check fails default-call style/long literals; a subsequent
one fails one overlong test literal. Strict typing catches one inferred Composed/
Composable assignment; each is corrected without weakening checks.

The first new native run fails all8 at fresh installation. A test-only closed phase
message establishes HANDOFF, without SQL/key/URL details. Stable C ordering is added
for role settings, but the unchanged8 still fail: it is not claimed as the cause.
A separate exclusively owned diagnostic source temporarily omits only the new scope
call to inspect metadata. This is NOT recipe acceptance or execution authority. ACL
differences are empty; exact control ownership also includes PostgreSQL's TOAST table
and index. Following their actual catalog links corrects the expectation. The probe
cleans its exact container; no normal review, old schema, role, image or cache is swept.
The corrected8 drift cases,11 fresh bootstrap and24 plan cases pass. The positive
actual-login test preserves TEMP shadow behavior and denies calling the private ACL
helper directly. Expanded21 drift cases and final engineering checks are running.

## Verification and next gates

Prescribed make test-erasure-principals is the focused target. Run format/lint, fresh
bootstrap, plans/legacy, consumer gates, unit/tooling, generated contracts/build,
security/source, browser and complete own hosted acceptance before main promotion.
The security and strict typing lists include the new trusted compiler. No migration,
dependency, environment key or public schema/DTO is added. Retain all failed runs.

Parent portable-catalog9fece6a and consumer1597a68 remain frozen for independent live
hosted39378996412 and39380895685. Neither accepts this v6 compiler. Main37be6e3 remains
unchanged and eight normal Docker services are healthy, execution disabled. Production,
real-data, academic/provider and physical/branded acceptance remains unproved.


## Final backend local verification

Expanded make format lint test-erasure-principals test-erasure-fresh-scope test-unit
openapi-check build security security-source passes:21 drift,11 bootstrap,1,502
unit/contract,35 tooling,231 strictly typed files, generated contract equality,
web build, static/dependency/secret checks. The collection now includes676 integration
cases; this count is not a full local integration pass. make test-erasure-plans
test-erasure-consent-consumers test-erasure-catalog additionally passes24/12/28.

The21 drift cases prove refusals for PUBLIC table/column/schema creation, lost owner
SELECT/UPDATE column, private LOGIN source access, crypto/type/helper rights, database
CREATE, global defaults, memberships, unsafe owner flags/expiry, grant options,
persistent ownership and third-party private execution grants. Both LOGIN readiness,
maintenance expiry and actual case issuance refuse with42501 and unchanged plan/audit/
job counts. Healthy actual logins, private-helper refusal, TEMP shadowing and real
legacy v2-v5 API refusal pass. All native resources use exact fresh creation receipts;
no existing resources are adopted or swept. Full browser and own hosted engineering,
restricted/recovery/image/service acceptance remain pending. Review is unchanged.


## Final local source and files

The final compiler also compares grant multiplicity with EXCEPT ALL and includes
implicit owner privileges plus unexpected grants on the control relation's exact
TOAST dependency. These are metadata checks, not new grants. After that change,
make format lint test-erasure-principals test-erasure-fresh-scope passes21/11;
make test-erasure-plans test-unit openapi-check build security security-source
check-docs passes24,1,502 unit/contract,35 tooling and the quality/security gates.
Generated public contracts remain equal. The application/browser test tree is
unchanged by that final private compiler adjustment; make e2e passes123 executions
(108 standard,12 short-text,3 configuration). Complete frozen-source hosted
acceptance is still required; no full676-case local integration pass is inferred.

All12 standard/configuration browser cleanup reports are empty. Together with
retained failed native/probe logs,45 captured created container IDs are independently
absent. Passing fresh native contexts separately assert their own exact-ID absence.
The existing short-text schema scope is retained; no older developer resource sweep
is performed. Normal review is8/8healthy on0045; state creation/execution/eligibility
are allfalse, with zero private erasure principals and zero closed users. No normal
review model call, erasure or private capability installation occurs.

Created: scripts/erasure_acl_sql.py, tests/integration/test_erasure_principal_fence.py,
ADR-078 and this verification document. Changed: scripts/erasure_capability.py,
services/erasure_capability_contract.py, services/erasure_plans.py (version comment),
Makefile, pyproject.toml (typing scope only), test_erasure_capability.py,
test_erasure_plans.py (actual v5 refusal and closed phase-only test diagnostics),
CHANGELOG, current sprint, traceability, API contract and both decision indexes.
No dependency, migration, public schema/DTO, environment key or production permission
changes. Additional expanded test-literal and stable-order SQL formatting failures
are corrected; earlier installation failures remain recorded above.

Next: full installed raw/code/catalog fence with checked expected templates and
independent fresh-source reproduction, followed by complete payload/ownership/
preservation/export checks before the durable atomic barrier and recovery checkpoint.


## Frozen v6 source4bf5a77

Exact4bf5a77347af725cdb05853392f73e14c6e68fef is pushed on
codex/erasure-principal-fence for own hosted39383925992, confirmed in progress.
Keep that remote head unchanged; workflow concurrency cancels on later pushes.
Only Markdown closeout follows the verified runtime/test/Make/pyproject tree. Parent
catalog9fece6a and consumer1597a68 remote SHAs are independently unchanged while
39378996412 and39380895685 remain live. Neither parent accepts the v6 recipe.
Main37be6e3 and its healthy normal preview remain unchanged; no branch is promoted
from a partial or another source's result. The previous two long-lived local identity
TRUNCATE57014 failures remain failures; native owned controls pass without a claimed
cause or timeout correction. Full own hosted/recovery/restricted/image/service and
remaining acceptance still apply. No account erasure, MVP completion or release claim.

Next exact slice: the full installed raw/code/catalog fence with independently
reproduced versioned expectations, including complete live-body comparisons rather
than normalizing live code. The principal fence alone cannot clear altered code,
constraints/policies, unrelated-role grants or source payload/hold/export graphs.
Those checks precede durable atomic authorization/closure and checkpoint recovery.
