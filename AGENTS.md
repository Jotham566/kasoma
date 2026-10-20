# Kasoma Engineering Instructions

## Product identity

- Product name: Kasoma.
- The MVP must be completed within 12 weeks.
- Build only the approved MVP scope unless the user explicitly changes it.
- The product whitepaper describes the mature north-star product.
- The SRD and specification pack define the approved MVP implementation.

## Authoritative documents

Before planning or implementing work, read:

1. `docs/specifications/00_README_Source_of_Truth.md`
2. `docs/product/PRODUCT_WHITEPAPER.md`
3. `docs/product/PRODUCT_ROADMAP.md`
4. `docs/specifications/01_SRD.md`
5. The specification documents relevant to the task.

Use this authority order when documents disagree:

1. Approved ADRs
2. Security, privacy and safeguarding requirements
3. API contract and database constraints
4. SRD
5. QA acceptance and release specification
6. System architecture
7. Adaptive engine and AI specifications
8. UX and content-operation specifications
9. Product roadmap
10. Product whitepaper

The whitepaper is the product north star, but it does not automatically expand
the MVP scope.

## Mandatory workflow

Before changing code:

1. Identify the applicable requirement IDs.
2. Read the relevant specifications and accepted ADRs.
3. Inspect the current implementation and tests.
4. State assumptions where the documents do not decide something.
5. Do not silently invent requirements.
6. Implement the smallest complete change satisfying the requirement.
7. Add or update tests.
8. Update `CHANGELOG.md`, the current sprint, requirements traceability and relevant
   API/runbook/verification documentation alongside each implementation change.
9. Run the required quality checks.
10. Report the requirement IDs satisfied and any remaining gaps.

If documents conflict, stop and report the conflict. Do not choose silently.

## Scope and drift control

- Do not add features merely because they appear in the mature whitepaper.
- Do not alter accepted architecture without creating or updating an ADR.
- Do not replace approved technology without documenting the reason.
- Do not weaken privacy, safeguarding, academic or AI controls.
- Do not mark work complete unless its acceptance criteria pass.
- Do not use production or real learner data during development.

## AI development

- Automated tests use `FakeModelProvider`.
- Interactive local inference uses host-native Ollama.
- The supported machine is an M4 Mac Mini with 16 GB unified memory.
- The normal local model class is quantized 4B–8B.
- Gemini free-tier testing is manual and opt-in.
- Never send real learner, guardian, confidential or restricted data to
  Google AI Studio.
- Follow:
  - `docs/specifications/06_AI_RAG_and_Grading_Guardrails.md`
  - `docs/specifications/18_Ollama_and_Gemini_Evaluation_Profile.md`

## Definition of done

A task is complete only when:

- applicable acceptance criteria pass;
- tests have been added or updated;
- linting, formatting and type checks pass;
- migrations work from a clean database when applicable;
- API/schema changes are reflected in generated contracts;
- documentation and traceability are updated;
- no secrets or personal data are committed;
- the implementation remains within the approved MVP scope.

## Repository stage

E0–E4 foundation, identity/consent, content review and deterministic assessment
and the E5 synthetic diagnostic/mastery slice are merged. Synthetic recommended
practice, reviewed hints, unseen reassessment and E6 progress/history are merged.
Learner flags, independent staff triage and exact-set multiple-choice assessment are
merged. Data-request intake and administrator review are merged. Owned JSON exports,
completion evidence and 24-hour copy expiry are merged. A non-destructive administrator
deletion-impact preview is merged. Specific-record legal holds for consent, attempts,
content flags and data requests are merged. Bounded synthetic JSON draft imports, source
locators and atomic worker processing are verified. Local ADMIN operational health and
threshold alerts are merged. Bounded local channel queue/status and fake-dispatch timing
are verified; minimized API response-start timing is verified, and minimized synthetic model-call telemetry is verified; bounded local aggregate request telemetry is verified. Local consent-gated WhatsApp
linking, signed durable intake, STOP/unlink barriers, fake delivery and expiry are verified.
Internal channel selection and objective grading/mastery parity are verified under ADR-037.
End-to-end five-question WhatsApp conversations, reply binding, shared grading, STOP/expiry and
safe fake delivery are verified under ADR-038. Deletion/anonymization, remaining
hold coverage, large-history fulfillment and accountability-retention processors remain pending.
Offline synthetic short-text candidate validation and budgeted fake dual-pass rehearsal are
verified. Isolated synthetic logical recovery and Chromium/Firefox/WebKit journeys with a
cold question transfer budget are verified. Restricted assessment database login, grade/mastery
record holds and bounded OTP/rate expiry are verified. Exact flag-history and request-review holds
are verified under ADR-045; full preservation coverage and deletion execution remain pending.
Reviewed rubric authoring under ADR-044 is
verified with learner delivery disabled. Learner short-text integration, academic calibration,
production PITR/RPO/RTO and branded/mobile browser acceptance remain pending.
Narrow 320-pixel touch journeys are verified across the three test engines; physical-device and
branded-browser acceptance remain separate. The ADR-046 objective load baseline passes locally
with shared content locks and batched plan validation; full hosted regression is verified.
Incremental export encoding and ADR-047 private artifact format are verified; asynchronous
publication and delivery are locally verified and merged under ADR-048. Production release
gates remain. Calibration eligibility, immutable bands and bounded grading work are
merged; per-grade publication/audit assignment and privacy coverage are merged after
hosted verification. The encrypted synthetic learner flow and independent blinded review/rolling disablement
are merged after local and hosted verification; normal learner short-text delivery remains
disabled. Responsive staff navigation and payload-free offline report comparison are
merged after hosted verification. The local grading queue snapshot and database-clock
completion cap are merged after hosted verification. Configurable existing runtime
budgets and bounded local model observations are merged after complete hosted
verification. Exact terminal channel receipt holds are merged after complete hosted verification, with new
creation default-disabled; full channel preservation coverage remains incomplete. The four
legacy hold DELETE clocks and bounded ADMIN audit activity are merged after complete
hosted verification at 5d95f9d. Guarded disposable CI storage preparation is verified;
it never authorizes developer SDK or application-volume cleanup.
ADR-057 has explicit user approval for bounded synthetic implementation only.
Exact encrypted owned link/conversation-version capture, finite disposal, independent
API/SQL guards and accessible controls are merged at `0a8f674` after complete hosted
39183714273. Clean/additive 0038, actual restricted logins, populated logical recovery,
1055 unit/contract, 412 integration and full browser/security/image/service checks pass.
The advancing-clock conversation expiry correction is verified; creation stays false.
Full raw/live-body coverage, erasure and accountability expiry remain pending.
See `docs/implementation/E8_CHANNEL_PRESERVATION_VERIFICATION.md` for the exact boundary.
Request-local progress replay reuse under unchanged ADR-024 is merged after complete
hosted 39184552472 at `7148a1c`; shared native select touch targets are merged after
complete hosted 39185423895 at `6d53541`. Load tooling/test source `6b06c53` passes
complete hosted 39217860618: 1092 unit/contract, 412 integration, 35 tooling and 108
browser executions, plus recovery, actual restricted logins, security/images and
service smoke. Both native objective profiles pass, including 25,000 prior grades
and timed choice/numeric feedback; full provider/deployment/soak acceptance remains.
Only Markdown/aggregate JSON closeout follows that verified code/test/Makefile tree.
Publication through main `6ebdf71` is verified and its merged load branch is removed.
Separately, provider-isolation tests at `8a938dd` pass complete hosted 39220793602
with 415 integration and 108 browser executions. Profile UI correction at
`44ae9ad` passes complete hosted 39222489376 with 415 integration and
108 browser executions plus full engineering gates. The latter passes nine local identity
journeys and is running in the healthy Docker web preview; no acceptance is inferred
for those branches from the load CI. Docker has recovered healthy on 0041 and host-native
Ollama connectivity is restored without inference. ADR-060 has explicit bounded synthetic approval; additive exact export evidence
holds/receipt identity pass complete hosted 39232307831 at `be2735e`. The additive
0041 SQL kernel passes complete hosted 39234377840 at `e5d3d98`: 1,096 unit/contract,
456 integration, 35 tooling and 108 browser executions plus all engineering gates.
Hosted recovery verifies 69 tables/686 rows in 713 ms. The interrupted local full
run is not a pass; existing volumes/images recover without data/cache cleanup. State remains
false and scope excludes review public. Separate executor operations with additive0042,
private configuration/AppLoader, finite count-only health and accessible UI are in
verification: 25 focused cases, 1,112 unit/contract, 465 integration, 108 browser
executions and 69-table/686-row recovery pass locally. Hosted 39243195783 at `94b40a6`
passes backend gates but fails one Chromium intercepted transport reset; a bounded
synthetic-only harness correction passes12 controls and108 local browser executions at
`b6aea35`. Hosted 39249423592 passes backend/transport gates but fails a WebKit resumed
pointer transition. A deterministic delayed-hints layout regression reproduces a
47.421875-pixel shift; moving review hints below actions passes nine focused cases.
Latest source `e33ec69` passes111 local browser executions, quality/build and
updated image/source/service checks; Docker is healthy on 0042 with retirement false.
Hosted 39255125288 starts no steps because GitHub reports failed account payments or
insufficient spending capacity. Owner action is requested once; main remains `e9f688e`,
the active branch is preserved and complete hosted acceptance remains pending; ADR-057 does not authorize account erasure.
The owner-authorized public visibility change clears CI startup. Complete hosted
39256037485 attempt2 at `d8fc031` now passes: 1,112 unit/contract, 465 integration,
35 tooling, 111 browser executions, nine focused assessment, 12 transport controls,
three staff UI and three native WebKit controls plus all engineering gates. Recovery
verifies 69 tables/686 rows in 465 ms. This supersedes the preceding pending operations
acceptance only; earlier failures remain failures. Only Markdown closeout follows the
verified application/test/Makefile/workflow tree `e33ec69`. Review Docker is healthy on
0042 with retirement false. Disposable load-role source `a23e9bc` passes complete hosted 39267916272:1,130 unit/contract,
479 integration,35 tooling and 111 browser executions plus all focused/engineering gates.
Recovery verifies 69 tables/686 rows in561ms. Exclusive committed creation and exact OID
checks protect concurrent creators/replacements;69 focused native cases pass. Only
Markdown/aggregate JSON closeout follows that verified code/test/Make/workflow tree.
Corrected native objective/history recheck pass, but the initial history START p95
559.306ms miss remains failed; variability is unexplained. Main follow-up39264562568
fails at the export journey's initial OTP POST socket reset; unchanged focused Firefox
and the new full suite pass, without a claimed transport fix. Review retirement stays
false; existing resources are never swept. The exact account-erasure proposal is now
prepared as ADR-061 and E8_ERASURE_DISPOSITION_PROPOSAL.md, published on main 4377da5
with status Proposed after documentation checks. Its full 69-table/488-column inventory
and actual primary-key matrix are assessment evidence, not clearance or execution
approval. The explicit request for bounded synthetic approval is pending; do not infer
it from generic continuation, ADR-057/060 approvals or a green pipeline.
No account-erasure authority or new anonymity policy is inferred.
Independent fresh-revision response source 58d598e passes 40 focused integration,
1,130 unit/contract, 35 tooling and nine assessment browser executions plus quality,
contracts/build, source/dependency/images and container smoke. It removes only two
known-empty response reads for this transaction's new revision; existing resumes and
reassessment provenance remain current. Complete hosted 39286019222 at 58d598e passes 1,130 unit/contract, 483 integration,
35 tooling and 111 browser executions plus all focused/engineering gates. Recovery
verifies 69 tables/686 rows in 477ms. Only Markdown/aggregate JSON closeout follows
the verified runtime/test/Make tree. The new objective profile passes with START p95 408.061ms, 7,000 requests,
zero errors and owned cleanup. Mixed-history also passes with 25,000 prior grades,
START p95 422.913ms, 7,000 successful requests and owned cleanup. Full hosted engineering acceptance now passes;
explanation of earlier variance and full release gates remain pending. All eight Docker services are
healthy on 0042; export retirement remains disabled.
Recovery role ownership correction is a separate local candidate: two actual source/
destination pre-existing-role regressions fail before the change. Shared exact-OID
creation/cleanup checks now give recovery authority only over its exclusively created
source owner; a destination grants no role ownership. 98 focused cases and a 69-table/
686-row logical restore pass (295ms, no cleanup failure). Quality/contracts/build, 1,138 unit/contract,
35 tooling and dependency/source security pass; complete combined-source hosted
acceptance remains pending. No role sweep or ADR-061 approval.
After integrating activity source78ca959 through02c9abc and main e7a4fc0, 98 role,
55 progress and40 assessment executions pass (shared channel cases overlap), plus
1,154 unit/contract,35 tooling, quality/build/security and69-table/686-row restore
in329ms. Complete combined-source hosted acceptance remains pending; the original
practice branch head stays unchanged while its full CI runs.


The new ADR-062 practice-day candidate implements roadmap 3.5's read-only consistency
indicator without a stored streak/reward system, added SQL, evidence replay or retention
permission. It preserves current consent, ownership and unfinished-diagnostic sealing.
55 focused cases (41 contract/rollup/replay and 14 integration), 1,146 unit/contract,
35 tooling and three final progress browser executions pass, plus quality/contracts/build,
security/source/images and service smoke. Narrow screenshot review places the next
learning action above the activity card. Generated contracts are updated; no migration
or dependency change. Its own full combined-source load/hosted acceptance remains pending;
normal Docker stays healthy on 0042 with retirement false. Native branded review was
unavailable because the Mac was locked; automated engines do not satisfy physical gates.
After integrating verified main 83f30cc, the 55-case progress and 40-case assessment
targets, 1,146 unit/contract, 35 tooling and three progress browser executions pass,
plus quality/contracts/build and security/source/images/service smoke. Seven channel
cases overlap the two targeted commands. Combined source 78ca959 passes both native
profiles (START p95 455.214/409.196ms; PROGRESS p95 14.087/16.522ms), each with 7,000
requests, zero errors and owned cleanup. Full hosted 39294126038 is in progress; do not
replace its branch head or infer acceptance from the earlier performance CI. Only
Markdown/aggregate JSON closeout follows that runtime/test/Make tree. ADR-061 approval
and physical/branded review remain pending; unlock was requested once from the owner.
Hosted 39294126038 at activity source 78ca959 is terminal FAILED: backend 1,146
unit/contract,484 integration,35 tooling and69-table/686-row recovery (548ms) pass,
but WebKit data-requests.spec.ts:167 reaches the unchanged30-second total timeout.
No failing-action stack establishes the cause. Later browser/security/image stages
are unexecuted. Unchanged six-case native privacy diagnosis passes; no fix is inferred.
Combined recovery/activity source adf4328 is pushed for full hosted39299684285, now
in progress. Main remains e7a4fc0; neither branch is promoted. Preserve the active
remote head; only Markdown closeout follows that runtime/test/Make tree.
ADR-063 is a separate local OTP observation candidate: four payload-free static
API email/SMS return/failure counters, an app-local observer, default-disabled and
development/test only. It reuses finite OTel/Redis bounds with a separate namespace.
ADMIN DTO/UI and local warnings add no delivery/billing/quota or production authority.
Initial SDK/Redis/API checks pass; final local and its own full hosted verification
remain pending. Parent adf4328 CI39299684285 stays live and unchanged; it cannot accept
the OTP feature. Final native quality/build/contracts, 1,171 unit/contract,35 tooling,
35 OTP/identity,24 operations and43 model cases, six browser executions and
security/images/service smoke pass. A finite namespace uncertainty marker prevents
known export loss from becoming a false zero after recovery; production/disabled
readers never connect. Normal Docker stays healthy with collection/retirement false.
See E8_OTP_OBSERVATIONS_VERIFICATION.md for retained schema, security
and presentation-test failures/corrections. No ADR-061 approval is inferred.
OTP source ceee4012c7f74dcc0c387a45ab112ed35d657f1b is pushed on its own branch;
complete hosted39304052749 is confirmed in progress. Parent adf4328 hosted39299684285
is separately in the browser stage. Neither feature is accepted from another source;
main remains e7a4fc0. Preserve both live heads; only Markdown OTP closeout follows ceee401.

Complete hosted39299684285 is SUCCESS at exact combined source
adf432879a8b55eeb1f9e8d59f5d6b053f76bf56:1,154 unit/contract,487 integration,35 tooling
and111 full browser executions plus every focused/setup/migration/seed/role/quality/
contract/build/security/image/service gate. Recovery verifies69 tables/686 rows in493ms,
no cleanup failure and stripped retirement execution denied. Bounded practice-day and
recovery-ownership engineering are accepted. Earlier39294126038 WebKit privacy timeout
remains FAILED/unexplained; no fix or new adf load measurement is inferred. Only
Markdown closeout follows the verified tree. Separate OTP sourceceee401 CI39304052749
is live, not accepted by this run. Normal review Docker stays healthy on0042; local
preview includes that separate OTP candidate with collection/retirement disabled.
Publication through main87a93d7 is verified; merged practice/recovery branches are
removed locally/remotely. The only remaining feature branch is OTP observations.
Its local integration of main changes Markdown only relative to sourceceee401;
keep that remote head unchanged while hosted39304052749 runs. Do not infer OTP
acceptance from the parent result. Earlier pending-main notes retain their historic
state; current main is87a93d7. No ADR-061 approval or production acceptance is inferred.
ADR-064 is a separate local known-metric-loss correction candidate. Two actual
SDK/Redis request/model cases fail at parentceee401 because lost nonempty exports
appear as fresh zero. Finite namespace uncertainty guards now cover all three kinds;
13 focused cases pass. Payload/codecs, original expiry, API schemas and provider
outcomes stay unchanged. Broad/own hosted acceptance and all current-reader rollout
remain pending; parent OTP CI39304052749 stays live and unchanged. See
E8_METRIC_LOSS_VERIFICATION.md; no complete ledger, production or ADR-061 authority.
Genuine academic/report/safety/provider authority,
complete preservation coverage and production release approval remain pending. See
`docs/implementation/CURRENT_SPRINT.md` and maintain the evidence register at
`docs/implementation/REQUIREMENTS_TRACEABILITY.md`. Accepted decisions remain
in `docs/specifications/13_ADR_and_Decision_Log.md`; new ADRs belong in
`docs/decisions/ADR/`. Do not claim application acceptance from documentation checks.

For documentation-only tasks, verify links and whitespace; application tests,
migrations and generated contracts apply when those components change.

The follow-up practice viewport candidate reproduces48 pixels of scroll movement under
delayed hints. A root-only opt-out while practice is present passes15 focused and108
standard three-engine executions, including320/1280 pointer targets; nine exact owned
containers are independently absent. Three fresh shards per engine retain the unchanged
OTP peer limit. Earlier numeric/OTP failures stay recorded; no full combined/hosted
acceptance or new erasure execution is inferred. Main publication remains pending.

ADR-069 extends exact-ID test resources with a separate erasure-test purpose for the
closed identity target, not an execution capability. The OTP race candidate fails two
regressions before the change and passes all11 after, plus1,444 unit/contract and105
resource/controller cases. It now combines the local practice root-scroll correction;
full exact-source combined hosted acceptance remains pending. No account closure or
DELETE completion is enabled. Preserve the normal review stack and all prior failures.


## Frozen identity/UI source12c6b60 — complete local browser and recovery results

The default-cache complete matrix passes123 browser executions:108 standard,12
short-text and three configuration. Twelve owned standard/configuration PostgreSQL
containers have empty cleanup reports and independently confirmed exact-ID absence.
The separate short-text runner retains its existing schema scope; no cleanup of
older developer schemas/roles/caches occurs. Recovery passes71 tables/691 rows318ms
logically and71/691/one42,084-byte ciphertext163ms with actual MinIO, stopped source
services, fault/immutable guards, denied stripped retirement and empty cleanup.
Actual restricted-login verification passes. Production RPO/RTO remains false.

Full own hosted39337786063 remains in progress at exact12c6b60d3a76a82c5e10ee15fc51122f4a130fcb.
Only Markdown closeout follows that runtime/test/Make/workflow tree. Earlier missing
browser/native-cache failures remain failed and are not application acceptance.

Separately, verified foundation source2966bab is published through main64e1f72ee10a3ed39a344525f49b9252341224b6
after complete hosted39334774152. Its configuration, erasure-foundation and browser
branches are proven merged and removed locally/remotely. A remote deletion response
reported ref errors, but independent ls-remote and fetch/prune confirm all three
remote refs absent; no unmerged source is discarded. The main follow-up39339512181
remains live. Docker is8/8 healthy on0044, with the locally verified viewport preview
36cb6e9 and retirement/normal short-text disabled. Host-native Ollama connectivity
is restored without inference. Account closure, erasure and DELETE fulfillment remain
unimplemented; approved ADR-061's SQL barrier/resumable job is the next vertical slice.


## Verified configuration, erasure prerequisites and browser foundation

Complete hosted [39334774152](https://github.com/Jotham566/kasoma/actions/runs/39334774152)
is SUCCESS at exact2966bab656cc6520c57264e45acce2366ca40786:1,425 unit/contract,
514 integration (1022.25s),35 tooling and117 full browser executions, plus every
required setup/migration/seed, focused, role, quality/contracts/build, security, image
and service gate. Logical recovery verifies71 tables/691 rows in464ms; actual
database/MinIO recovery verifies71/691/one42,084-byte ciphertext in189ms, stopped
source services, fault/guard checks and empty cleanup. Production RPO/RTO is false.

FR-OPS-002/003 and NFR-SEC-002/OBS-001/ACC-001/LOC-001/MNT-001: accept the bounded
15-key warning configuration, immutable versions/audited retry and accessible editor.
NFR-MNT-001/PERF-001/002/SEC-002/OBS-001: accept the owned browser fixture and bounded
diagnostics. FR-ID-006/BR-010 receive strict internal contracts, private fake-only
profile,71-source structural drift fence and disabled-role prerequisites only.
No account closure, erasure, permanent SQL barrier or DELETE completion exists.

The native full run remains FAILED:513 integration pass and one Alembic upgrade-head
setup error for test_exact_history_hold_preserves_snapshot_without_freezing_new_transitions
(2294.28s). Its captured diagnostic does not establish a cause. The unchanged serial
make test-grading-work recheck passes26 cases in56.16s; no timeout, retry or assertion
changes and no schema/role/cache cleanup. This does not turn the failed native run
into a pass. All514 cases pass in the exact-source clean hosted run above.

Only Markdown closeout follows this verified runtime/test/Make/workflow tree. The
newer identity-coordination and practice-viewport candidates need their own complete
verification. Normal Docker stays healthy on0044 with retirement/short-text disabled.
Full privacy/erasure, academic, provider, physical/branded-device and pilot gates remain.

## Standard commands

Prefer repository commands over improvised alternatives:

- `make setup`
- `make dev`
- `make test`
- `make lint`
- `make migrate`
- `make seed`
- `make openapi`
- `make e2e`
- `make security`
- `make eval-local`
- `make eval-gemini-free`

If a required command does not exist, implement it according to the repository
bootstrap specification rather than silently substituting an undocumented
workflow.

## Task completion report

At the end of every coding task, report:

- requirements addressed;
- files changed;
- tests and checks executed;
- results;
- architectural decisions made;
- unresolved risks or specification gaps;
- recommended next task.

ADR-064 local engineering verification passes: 1,180 unit/contract, 35 tooling,
13 loss-window, 51 request, 43 model, 35 OTP/identity, 24 operations and six browser
executions; quality/contracts/build/security/images/service checks pass. Its own
complete hosted acceptance remains pending. Native Edge access times out after
the Mac becomes visible; no physical/branded acceptance is inferred.

ADR-065 is a separate local database/private-object recovery candidate. One real
69-table/686-row/one-object rehearsal passes after stopping both owned source
services; missing/corrupt object rejection and empty cleanup are verified. Final local checks pass1,239 unit/contract,35 tooling,59 focused controls and
quality/build/contracts/security; final real restore147ms cleans successfully. Own
complete hosted verification remains pending.
No production PITR/RPO/RTO, developer data cleanup or ADR-061 authority is inferred.



ADR-063 OTP observations pass complete hosted39304052749 at exactceee401:1,171
unit/contract,498 integration,35 tooling and114 browser executions plus all focused
and engineering gates. Logical recovery69 tables/686 rows892ms cleans successfully;
object-storage and production recovery remain unproved by that run. Only Markdown
closeout follows; separate metric-loss/object-recovery candidates need own acceptance.
Collection stays defaultfalse and no ADR-061 or production enablement is inferred.

OTP engineering is published on main557f90f after complete own39304052749; its
merged local/remote branch is removed after remote SHA/ancestry proof. Object
recovery exactsource29f1ddc is pushed for own live39311093503; metric-loss source
b5557a3 stays unchanged for live39308594889. Only Markdown closeout follows these
heads; neither pending feature is accepted yet. Docker8/8healthy; read-only
ownership-label audit finds no leftover recovery containers.

ADR-066 older/diagnostic load tooling is a separate candidate: independent clocks
and normal OTP/domain paths, no source-row rewrite or changed deadline/latency gate.
Initial69 focused controls and203 typed files pass; a full native profile is live,
not accepted. Own final local/hosted evidence and original/recent rechecks remain.

ADR-066 final local tooling gates pass1,253 unit/contract,35 tooling,69 focused
controls,203 typed files and quality/contracts/build/security. Native temporal
measurement remains live; no performance acceptance. Learner-level ADMIN mastery
replay cannot be inferred from aggregate audit access: explicit support permission/
audit is required by API section9 and remains unresolved.


ADR-064 known metric-loss windows pass complete hosted39308594889 at b5557a3:
1,180 unit/contract,502 integration,35 tooling,114 full browser executions plus
all focused/engineering gates. Logical69-table/686-row restore425ms cleans without
failure and retirement stays denied. Only Markdown follows that verified tree;
object-recovery and temporal-load candidates need separate own acceptance.

Current verification snapshot: main3cde8c2 contains fully verified ADR-064 and
its merged branch is removed after remote/ancestry proof. ADR-066 first temporal
native profile passes35000 grades/7000 HTTP/zero errors,START p95410.622ms and
cleanup_failed=false; original/recent profile rechecks and own full hosted remain.
ADR-065 source29f1ddc stays unchanged for live39311093503. The load candidate
integrates main through Markdown only; do not infer full MVP/release acceptance.

Temporal candidate exactsource687d86c is pushed for live own39313955470. Original
baseline recheck passes on its unchanged runtime:2500 grades/7000 HTTP/zero errors,
START p95428.329ms,cleanup_failed=false. Sequential recent-history recheck remains
live. Main3cde8c2 is remotely verified and its merged metric branch is removed.
Provider recovery documentation research changes no selection, cloud dependency,
permission, architecture approval, retention or release gate.

ADR-066 all three native profiles now pass on unchanged candidate runtime:
temporal35000 grades/START p95410.622ms; original2500/428.329ms; recent27500/
424.046ms. Each has7000 successful HTTP/zero errors and cleanup_failed=false.
Recent START p991074.231ms remains visible; no subsecond-tail/production claim.
Own hosted39313955470 and object39311093503 remain live, remote heads unchanged.
Only Markdown/aggregate evidence follows; local final image/service checks run.

Temporal candidate final local image/source/service gates pass and all8 normal
Compose services are running/healthy after rebuild. Three native profiles and
all local engineering gates pass; own687d86c hosted39313955470 remains pending,
as does29f1ddc object39311093503. No full MVP or production approval is inferred.

ADR-065 exact29f1ddc passes complete hosted39311093503:1,239 unit/contract,502
integration,35 tooling,114 browser executions and all engineering gates. Actual
quiescent database/MinIO restore69 tables/686 rows/one42,084-byte object241ms verifies
sources stopped, integrity/failure probes and empty cleanup. Logical restore504ms.
Only Markdown follows. Production recovery and ADR-061 remain unapproved.

ADR-066 exact687d86c passes complete hosted39313955470:1,253 unit/contract,502
integration,35 tooling,114 browser executions and all engineering gates. All three
native profiles pass7000 HTTP/zero errors each: temporal35000 grades/START p95
410.622ms, original2500/428.329ms, recent27500/424.046ms. Cleanup=false for all;
recent START p991074.231ms retained. Only Markdown/aggregate evidence follows.
Production/provider/daily soak, academic/privacy release and ADR-061 remain gated.

ADR-067 bounded warning configuration is an unmerged implementation candidate under
FR-OPS-002/003. Additive0043 plus forward0044, ADMIN/recent OTP, immutable global numeric
versions and existing staff audit support exact retry/version authority.34 focused SQL/
contract and three dedicated narrow/a11y browser executions pass. Partial schema fallback
is refused; worker/API saved values agree. Normal Docker preview runs0044 with8 healthy
services and retirement/normal learner short-text disabled. Full own frozen backend/
browser and hosted verification remain required. ADR-061 remains proposed/unapproved;
source inventory/disposition explicitly track the two shared configuration tables.

Explicit human approval of updated ADR-061 is recorded20 October2026 for bounded
synthetic implementation and isolated tests, including0044 source addendum, exact richer
profile/contact/reply preservation, eligible owned-row removal, affected-band disablement
and finite custody/retirement. No normal Docker review database, real-data or production
execution is authorized. This supersedes earlier unapproved-status snapshots only for
that exact lane. Implementation starts with closed contracts, additive lifecycle and
closure barriers/resumable jobs; no partial phase may complete a DELETE request.


NFR-MNT-001/OBS-001: frozen configuration backend passes1277 unit/contract,35 tooling
and512 integration, but serial local Chromium fails two cases with HTTP500. Promotion
remains pending. A bounded fake-only/owned-schema driver-error diagnostic is a separate
local test-harness candidate; it logs fixed categories only, changes no timeout/retry
and does not claim a fix. See E8_OPERATIONS_CONFIGURATION_READINESS.md.


Complete hosted39322035839 is SUCCESS at exact configuration source3e6175b:1277
unit/contract,512 integration,35 tooling and117 full browser executions plus every
mandatory engineering gate. Recovery verifies71 tables/691 rows (logical531ms; actual
PG/MinIO one42,060-byte object308ms), guards/scope/fault probes and empty cleanup.
Local serial/browser diagnosis still reproduces an assessment500 with QUERY_CANCELLED;
no cause/fix is claimed, and main promotion remains deferred. The separate bounded
local diagnostic harness has24 focused/1301 unit cases but no own hosted acceptance.
ADR-061 foundation1851740 is separately pushed for complete hosted39328044945; its
head stays fixed and its acceptance remains pending. See configuration/erasure readiness.


ADR-068 (NFR-MNT-001/PERF-001/002/SEC-002/OBS-001) is a separate browser-isolation
candidate after observing11.3GB of shared system catalogs. Only a new owned bounded
PostgreSQL service hosts the standard synthetic browser fixture; normal services and
all existing schemas remain. Scope/cleanup/private-key tests and actual browser/hosted
acceptance are pending. No prior HTTP500 or pointer failure is declared fixed.

ADR-061 lifecycle work is isolated on codex/erasure-lifecycle. Closed plan/authorization/
status types, a disabled private fake-only profile and a71-source/501-column0044 structural
manifest pass97 focused and1374 unit/contract tests plus35 tooling, lint/types and
security/source checks. Actual isolated catalog drift and disabled-role provisioning
cases pass2/2. These are foundation checks only: no closure migration, provisioner, executor, routes or DELETE
completion exists. Trigger/grant/payload/ownership validation,
permanent closure and full first-slice/hosted acceptance remain pending. Keep review
execution disabled; see docs/implementation/E8_ERASURE_LIFECYCLE_READINESS.md.


ADR-061 prerequisite source1851740 passes complete hosted39328044945:1374 unit/contract,
514 integration,35 tooling and117 browsers plus all engineering gates. Recovery71 tables/
691 rows passes logical607ms and actual PG/MinIO one42,060-byte object193ms with empty
cleanup and stripped retirement denied. Only closed contracts/private configuration,
structural drift checks and disabled-role grant refusal are accepted; no closure or
account-erasure execution/fulfillment exists. Only Markdown closeout follows this source.
Combined integration and full approved lifecycle/preservation/removal acceptance remain.


The combined codex/browser-isolation candidate now integrates independently hosted-
verified configuration3e6175b and ADR-061 foundation1851740 (only Markdown follows),
plus locally verified ADR-068 browser isolation and pinned-local Docker transport.
All117 pre-integration browser executions pass with nine exact owned containers removed;
the transport follow-up passes nine actual assessment executions with empty cleanup.
The merge changes no application schema beyond0044. Combined-source backend/browser/
recovery/security/image/service and complete hosted acceptance are still required.
Main remains eb05457; review execution stays off and no account closure/removal exists.

## Verified identity coordination and practice viewport

Complete hosted [39337786063](https://github.com/Jotham566/kasoma/actions/runs/39337786063)
is SUCCESS at exact12c6b60d3a76a82c5e10ee15fc51122f4a130fcb:1,444 unit/contract,
517 integration (1600.91s),35 tooling,11 owned identity cases and123 full browser
executions. All required setup/migration/seed, focused, restricted-role, quality,
contracts/build, security, image and service gates pass. Logical recovery verifies
71 tables/691 rows in530ms; actual PostgreSQL/MinIO recovery verifies71/691/one
42,084-byte ciphertext in311ms, stopped source services, fault/immutable guards,
denied stripped retirement and empty cleanup. Production RPO/RTO remains false.

FR-ID-003/005/006 and NFR-SEC-002/MNT-001: accept existing-user LOGIN coordination
and ADR-069's exclusively owned fake identity verification source. NFR-ACC-001/
COMP-001 and FR-REV-005: accept the viewport correction and delayed-hints pointer
regressions. Local source12c also passes123 browser executions with12 independently
absent owned containers. Earlier native integration/cache/attachment failures remain
failed; no unsupported root-cause claim. Main64e1f72 follow-up39339512181 also passes.
Only Markdown closeout follows this verified runtime/test/Make/workflow tree.
No permanent SQL closure, erasure executor or DELETE completion is accepted; those
remain the next bounded ADR-061 slice. Normal review activation stays disabled.

Parent0045 hosted39346406621 atcb0cd22 is FAILED:1,445 unit/contract and521 integration
pass; the sole failure is the0042 configuration upgrade's whole-user JSON comparison
not expecting closed_at:null. The correction must require exactly that addition while
preserving all old fields/rows. It remains unaccepted pending focused and full hosted
verification; do not enable closure or erasure. Main72c9c17 follow-up39345752803 is SUCCESS.


## Accepted dormant lifecycle source — hosted39350745638

Complete hosted [39350745638](https://github.com/Jotham566/kasoma/actions/runs/39350745638)
is SUCCESS atb4b20f1b0e44d1ae08ae58091f35bb9c060e957f:1,445 unit/contract,
522 integration,35 tooling,22 owned identity/lifecycle checks and123 full browser
executions. All required setup, clean/additive migrations, seed, focused/restricted
login, quality/contracts/build, recovery, dependency/source/image security and service
smoke gates pass. Logical recovery verifies74 tables/692 rows in559ms. Actual stopped-
source PostgreSQL/MinIO restore verifies74/692/one42,084-byte ciphertext in316ms,
with fault/immutable/dormant guards, stripped retirement denied and empty cleanup.
Production RPO/RTO remains false. Prior39346406621 stays failed; this source corrects
only the additive-upgrade test's expected closed_at:null, preserving all old fields.

Accept0045 dormant lifecycle persistence, the structural manifest and denial tests.
No plan/job creation, SQL erasure owner/executor, authorization, permanent closure,
removal or DELETE completion is accepted. Normal review activation stays false.
Coordination94feeab and source ownership752cda1 need their own complete hosted runs;
this acceptance covers neither. Only Markdown closeout follows the verified runtime/
test/Make/workflow tree. Native review images rebuild successfully; make migrate and
container-smoke pass with all eight services healthy on0045. Direct count-only inspection
confirms scope/creation/execution=false, owner/executor absent and zero closed users.
Existing review data/volumes remain; no account-erasure operation is performed.

Native rebuilt API/web image HIGH/CRITICAL scanning also passes before publication.
