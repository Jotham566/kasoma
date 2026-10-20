# Closed guardian and local role consumer verification

Requirements: FR-ID-003/005/006, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-077](../decisions/ADR/077-closed-consent-consumer-guards.md).

Only invocation-owned synthetic sources and fake providers are used. The exact
future-state fixture restores the closure trigger before consumers run. No actual
closure authorization, staff erasure or executor is proved; normal review is untouched.

## Retained failures and focused evidence

The initial five-test harness fails on incorrect SQL table names; these errors are
not application regressions. After correcting names, the unchanged implementation
fails three cases and passes two. A valid preissued guardian code accepts new closed
recipient evidence, an invalid code increments its challenge, and a closed nonstaff
role revoke appends audit. The changed implementation passes all five.

An initial extended formatting run fails two long SQL lines; splitting their literals
fixes formatting without changing SQL. Final make format lint test-erasure-consent-consumers
passes ten cases. Additional controls prove open/unbound/temporarily-disabled consent,
exact accepted replay, withdrawal after recipient closure, and new-binding refusal
without challenge changes. A real PostgreSQL exclusive gate blocks consumption while
another transaction can NOWAIT-lock the code; committed future closure is then rejected
with zero new consent/job and an unchanged challenge. Closure trigger is restored.
Role tests preserve closed audit sources and permit active/temporary-disable revocation.

## Commands and remaining gates

make test-erasure-consent-consumers is the prescribed focused command. Broader prior
credential/dispatch/identity, unit/tooling, quality/contracts/build/security, browser
and own hosted verification are pending. Parent catalog source9fece6a remains frozen
for separate run39378996412; it cannot accept this new consumer behavior. Main37be6e3
follow-up39374776606 is successful. Full installed SQL/catalog/payload/preservation,
export drain, durable closure/removal/checkpoint recovery and external release gates
remain required. No migration, new environment key or generated contract change.


The first broader make test-erasure-identity is FAILED:28 pass and one dormant
lifecycle test fails. TRUNCATE account_erasure_state returns SQLSTATE57014 (statement
timeout), rather than expected42501. It establishes no successful forbidden mutation
or cause; its historical identity fixture preserves the created debugging schema.
No schema/role/cache sweep is authorized or performed. No timeout, retry,
assertion or guard is changed. An unchanged prescribed-target recheck is running.
Earlier make test-erasure-credentials18 and test-erasure-linked-dispatch44 pass.
The initial combined command stops here; later unit/contracts/build/security stages
are unexecuted in that invocation and run separately. No failed run is called a pass.


Separate make test-unit openapi-check build security security-source passes:1,502
unit/contract,35 tooling, generated contract equality, web build, static security,
Python/JavaScript dependency checks and source secret scanning. The preceding make
format lint includes strict typing of230 source files and web/package type checks.
The unchanged long-lived-database identity recheck also FAILS:28 pass/one same57014
TRUNCATE timeout (140.01s). Neither run establishes a cause. Existing debugging schemas
are preserved by their fixture; no cleanup is attempted. The prescribed fresh-owned
make test-erasure-identity-isolated and full make e2e remain running. Isolated sources
are separate from the normal eight healthy review services; flags remain disabled.


Final focused make format lint test-erasure-consent-consumers passes12 cases,
including two additional wrong-code controls: open bound/unbound contacts still
increment attempts once, keep original expiry and record no consent. No further
runtime change follows the first five-case correction. The prescribed owned runner
passes all70 executions (29 identity,19 dispatch,16 ownership,6 staff) with four empty
cleanup reports. This does not explain or turn either long-lived-database failure
into a pass. Full browser/own hosted acceptance is still pending at this checkpoint.


## Final local ADR-077 verification

Final source passes12 consumer cases,18 prior credential and44 gate/linked cases;
the fresh-owned runner passes70 executions (29/19/16/6). Final1,502 unit/contract
and35 tooling, strict typing230 files, formatting/lint, generated contracts, build,
dependency/static/source security and documentation checks pass. make e2e passes123
executions:108 standard,12 short-text and3 configuration across the three engines.
Twelve standard/configuration browser and four owned prerequisite containers have
empty cleanup reports; all16 captured exact IDs are independently absent. Native
consumer fixtures additionally assert their own created-container absence. The
short-text runner retains its existing schema scope; no older resource sweep occurs.

Two long-lived-database identity invocations remain FAILED (28 pass/one57014 timeout
each); the unchanged fresh-owned target passes29, without establishing a cause or
changing timeouts/assertions. No application failure is hidden or converted to a pass.
Complete own hosted full integration, recovery/restricted-login/image/service and
remaining engineering acceptance is required before promotion. The final tree now
contains654 integration cases; this is a collection count, not a local full pass.
Normal Docker remains eight healthy services on0045 with all excluded execution
flags disabled. Main stays37be6e3. Next: installed SQL/catalog/ACL/payload guard and
preservation/export checks before atomic durable authorization/closure; full erasure,
quarantined checkpoint recovery and external release gates remain incomplete.


## Frozen consumer source1597a68

Exact1597a68192e9351f0bfbb14fcb44566536e3c851 is pushed on
codex/erasure-consent-consumers for own hosted39380895685, confirmed in progress.
Preserve that remote head: its concurrency group cancels on a later push. Only
Markdown closeout follows the verified runtime/test/Make tree. Parent portable
catalog9fece6a hosted39378996412 is independently in progress. Neither may be
promoted from another source's result. Main37be6e3 follow-up39374776606 is SUCCESS;
main remains37be6e3 and normal Docker is8/8healthy, execution disabled. The exact
owner-approved orphan91c93448d8156695319097ff17e29cc9094e7265cb530d84bcbc809619559eff
is independently confirmed absent; no broader removal is authorized or performed.

Next implement the full installed capability/catalog/ACL and payload/source checks
under ADR-061/072/073 before atomic durable authorization/closure. Existing v5
pre-install verification and disabled plans do not prove those installed checks,
permanent SQL guards, preservation, export drain, erasure or checkpoint recovery.
Both long-lived local identity failures stay failed; fresh-owned70, consumer12 and
all123 browsers plus engineering checks pass as recorded above. No MVP/release or
physical/branded acceptance is inferred.


## Complete own consumer verification at1597a68

Hosted39380895685 is SUCCESS at exact1597a68192e9351f0bfbb14fcb44566536e3c851:
1,502 unit/contract,654 integration,35 tooling,123 full browser executions and all
required setup/migration/seed, focused, restricted-login, quality/contracts/build/
security/image/service gates. Logical recovery74 tables/692 rows569ms; stopped-source
PostgreSQL/MinIO74/692/one42,084-byte ciphertext317ms with integrity/fault/immutable/
dormant checks and empty cleanup. Production RPO/RTO and erasure recovery remain false.
Optional registry authentication alone is legitimately skipped when credentials are
absent. This accepts ADR-077's guardian consumption and closed local-role guard only
at that combined source. Two prior local long-lived TRUNCATE57014 failures remain
failed/unexplained; clean hosted acceptance does not turn them into passes.

The candidate is not yet published to main. Main825d57e follow-up39387033557 remains
live and unchanged; the principal4bf5a77/39383925992 result is independently pending.
No v6/v7, actual erasure or production acceptance is inferred from this consumer run.
