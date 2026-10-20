# Closed credential intake and dispatch verification

Requirements: FR-ID-001/002/005/006, BR-010, NFR-SEC-002, NFR-MNT-001.
Decision: [ADR-074](../decisions/ADR/074-closed-identity-credential-dispatch.md).
Status: local engineering checks pass; complete own hosted acceptance remains pending.

## Implemented boundary

LOGIN pre-reads the current identifier owner, takes its existing account/shared
processing gate before rate/identifier locks, then rechecks the same binding and
fresh user. A retained closed identifier receives the same generic acceptance but
no code, challenge or provider call. A new binding requires fresh issuance rather
than a late lock/adoption. Existing finite security rates remain unchanged.

Known-user dispatch holds an idle session-shared subject gate and uses that exact
connection for the short fresh recheck. It commits before provider.send: no row lock,
HMAC lock or open transaction spans the call. The existing model guard retains its
None-valued port and delegates to the shared connection helper. No extra checkout
or larger pool is required. Uncertain acquisition/release invalidates that connection.
Suppression/gate failure is not a provider failure. An actual provider return remains
a return observation even if later gate cleanup fails. Only this invocation's exact
new challenge is discarded on failure/suppression; older unbound challenges remain.

Closed LOGIN refuses before consuming/incrementing a retained challenge. Closed
refresh refuses before family-wide reuse mutation. Nonclosed ACTIVE/DISABLED reuse
still revokes the family. Authentication retains its ACTIVE/status/session checks,
backed by SQL's immutable closed-implies-DISABLED constraint. ACTIVE historical
migration fixtures need not read a column that their old schema does not yet have.
There is no missing-column fallback or optional current-schema closure guard.

## Evidence and retained failures

The first four native regressions give three failures/one pass on the unchanged
parent: closed email/phone still dispatch, and reused closed refresh rewrites its
family. After the first implementation, four and then 17 cases pass. The first
broader identity cohort fails its existing additive0044-to0045 fixture with a new
deferred-column read (28 pass/one failure). The fixture/assertion is unchanged; the
consumer now relies on the existing ACTIVE invariant before reading a marker.

A separate one-connection regression fails before the reuse correction (17 pass/one
failure). The first shared-helper signature change is rejected by strict typing at
the existing model gateway. Preserving that None-valued port through a wrapper and
using the same owned connection for OTP rechecks fixes both without pool expansion.
An earlier long SQL literal is a formatting failure, not application acceptance.

The final 18 native cases pass, including email/SMS, retained session/challenge
integrity, active/nonclosed-disabled reuse, idle gate/exclusive conflict, provider
failure, closure between commit/dispatch, busy dispatch, uncertain release, both
binding-change stages and a single-connection pool. Full broader local/own hosted
results remain separately pending. No earlier failure is reclassified as a pass.

## Fixture and remaining gates

Every new case creates an exclusively owned fake-only source through the registered
factory and standard migrations. Its future-state fixture toggles only the named
closure trigger in that source/transaction, sets a synthetic closed row and restores
the trigger before consumers run. The fixture verifies restored trigger state and
zero erasure jobs. It is not an application closure command, authorization proof or
SQL erasure-guard acceptance. Successful native contexts independently assert exact
container absence; all final captured IDs must also be checked at closeout.

No public migration, new API schema/environment key, real data, normal review closure,
erasure activation or DELETE completion is introduced. Original unbound challenge
expiry/drain, installed-catalog/ACL/SQL ownership and payload checks, richer exact
preservation, export drain, permanent write guards, atomic authorization/closure,
bounded durable removal and external-checkpoint quarantine recovery remain required.
Physical/branded devices, academic/privacy/provider and production release gates remain.


This slice protects LOGIN dispatch. LINK/GUARDIAN dispatch after its authentication
transaction, including a separately bound recipient identity, still needs closure
coordination before activation. Current authentication rejects requests begun after
closure but is not proof against that later dispatch race. Known LOGIN dispatch
occupies one pooled connection through the local provider call; production provider
concurrency and process-loss cancellation remain separate acceptance work.


## Final local engineering results

make format/lint, test-erasure-credentials (18), test-erasure-identity-isolated
(29 identity/lifecycle, 19 fake model dispatch, 16 source and six staff),
test-otp-observations-api (one integration/two deselected), test-unit (1,495
unit/contract and 35 tooling), openapi-check, build, security and security-source
all pass. Strict typing covers 228 Python sources. The existing populated0044
upgrade test passes unchanged. New native fixtures repeatedly run standard clean
migrations; there is no new public migration or API DTO.

make e2e separately passes 123 executions: 108 standard, 12 short-text and three
configuration. Its 12 recorded exact source IDs have empty cleanup reports and
independent full-ID absence. Nine captured native IDs across the retained failure
and final cohort logs are independently absent; the 18 final successful new
contexts also assert their own exact absence. This is not an inventory-based
cleanup claim about older unrelated resources.

The normal eight-service Docker preview remains the independently hosted-verified
v3 source on0045, with erasure/retirement/ordinary short text disabled. Candidate
image/service/recovery and full612 integration acceptance require its own complete
hosted source; no parent pipeline or Markdown-only check substitutes for that run.
