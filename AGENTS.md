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
Genuine academic/report/safety/provider authority,
complete preservation coverage and production release approval remain pending. See
`docs/implementation/CURRENT_SPRINT.md` and maintain the evidence register at
`docs/implementation/REQUIREMENTS_TRACEABILITY.md`. Accepted decisions remain
in `docs/specifications/13_ADR_and_Decision_Log.md`; new ADRs belong in
`docs/decisions/ADR/`. Do not claim application acceptance from documentation checks.

For documentation-only tasks, verify links and whitespace; application tests,
migrations and generated contracts apply when those components change.

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
