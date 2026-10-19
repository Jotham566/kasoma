# Local API OTP adapter observations - candidate verification

Requirements: FR-OPS-002, FR-ID-001, NFR-OBS-001, NFR-SEC-002,
NFR-ACC-001 and NFR-MNT-001. Decision: [ADR-063](../decisions/ADR/063-local-otp-dispatch-observations.md).
Status: local engineering checks pass; own complete hosted acceptance pending.

## Requirement and implementation boundary

The approved MVP operations scope includes messaging usage/failures. Existing channel
counters and model observations do not cover email/SMS OTP adapter invocations. This
slice supplies four static return/failure counters through a request-local observer;
normal domain calls are unchanged and unobserved. It records no codes, recipients,
purposes, identifiers, tokens, requests, exceptions or content fingerprints. Adapter
return is not delivery, human receipt or billed usage. General messaging costs and
production provider/availability evidence remain missing release work.

Collection defaults false and only development/test API lifespans may enable it.
Production refuses construction and reads even when the flag is true. No database,
provider, external call, credential, learning-data or academic change. The additive
ADMIN DTO/UI preserves authentication, recent consent/rate/ownership rules and generic
OTP responses. Failed sends retain the existing challenge cleanup; observer failure
cannot change provider/verification behavior. No Redis I/O occurs on the send path.

An owned OTel provider records four synchronous attribute-free counters with static
resource/scope, disabled exemplars, bounded integer sums and no per-call samples.
The existing bounded byte transport adds a separate OTP namespace/purpose hash and
four-count canonical codec. Request/model wire semantics and Lua limits are unchanged.
Five-second collection exports at most 256 <=1024-byte frames, with absolute expiry
300 seconds from earliest observation and 15-second freshness. Unknown/corrupt/lost/
stale data is unavailable, never zero. A successful fresh empty collection may show
zero observations. The existing periodic warning uses an inclusive typed local failure
threshold; it changes neither quotas nor learner decisions. No external notification.

## Executed checks and retained failures

- The first command scaffolding attempt names an integration file before creation;
  it fails collection and is not product-defect or acceptance evidence.
- Against the original API, `make test-otp-observations-api` fails one actual PostgreSQL
  case on missing otp_dispatch; the access/unavailable behavior is then implemented.
- Initial `make test-otp-observations` passes 13 cases, then expanded SDK/Redis/API/
  lifecycle/threshold controls pass 26 cases. The final cleanup-invariance case is
  added afterwards and still needs its final command result recorded.
- `make test-operations` passes 24 cases; `make test-model-metrics` passes 43. Existing
  request/model namespaces, ADMIN controls and local warnings remain covered.
- Initial `make test-unit` finds the new alert code missing from the closed analytics
  schema (one failed, 1,169 passed). Updating that allowlist without relaxing its fields
  passes 1,170 unit/contract and 35 tooling cases before the final cleanup test addition.
- Initial security rejects two bare except/pass cleanup handlers. A dedicated bounded
  best-effort close helper and explicit startup/cleanup invariance checks replace them;
  no scanner threshold or suppression is changed. Final security is pending.
- Initial new Chromium UI case fails because its presentation route still fulfills
  requests while the browser is offline. Remove that handler for the real offline
  check and restore it for subsequent presentation states; no product code, timeout,
  assertion or retry is relaxed. Final three-engine execution is pending.

`make format openapi` regenerates additive API/client contracts. Initial
`make lint openapi-check build` passes with 200 typed source files. Full final local
checks, images/service smoke and this source's own complete hosted verification remain
required. The parent combined source adf4328 run39299684285 is live; do not replace
its remote head for this separate increment. Its result cannot accept the OTP feature.
The earlier activity run39294126038's WebKit privacy timeout remains unexplained and
failed; unchanged six-case native diagnosis is not a fix or full acceptance.

## Files and next gate

New OTP observer, SDK, store and collector modules; API lifecycle/identity route and
service injection; typed settings/contracts/operations; existing bounded transport
namespace and scope literal extension; ADMIN card, API/analytics contracts and isolated
synthetic browser actor. Tests/Make targets, ADR/index/API/runbook and mandatory tracking
travel together. No migration/dependency or normal Docker flag activation is made.
Finish local verification, record exact results, publish the candidate for its own
complete hosted engineering run and preserve every external release/ADR-061 gate.

## Local end-to-end verification and known-loss correction

The final real integration path enables the actual API lifespan with an owned OTP
collector, makes normal fake email/SMS calls, collects actual SDK deltas into Redis
and reads the ADMIN snapshot/threshold alert. SMS provider failure and simultaneous
provider/observer failure retain generic responses and challenge cleanup; an observer
failure leaves valid OTP verification usable. Cooldown and unauthenticated guardian
requests do not count as adapter calls. Production/disabled lifespans do not construct
a collector, and their operations reader never connects to OTP metric storage.

A final review finds that a failed export followed by an empty pulse could otherwise
make known loss appear as zero. The OTP collector now marks a finite uncertainty window
and republishes its remaining duration on recovery before any freshness pulse. One
namespace-only marker (no source/identity data) cannot shorten another producer's
window; Redis READ checks it atomically for OTP. Existing three-key request/model
reads and wire codecs remain compatible. A real Redis regression proves unacknowledged
write, empty recovery still unavailable, finite TTL, refusal to shorten another
producer's marker and forced expiry only within the isolated test namespace. This
is not a real five-minute soak or a complete usage ledger.

Expanded `make test-otp-observations` adds existing identity regressions: 35 cases pass
in 29.43s, comprising 17 contract and 18 PostgreSQL/Redis integration cases. The
existing model target passes 43 cases in 0.28s. Earlier `make test-operations` passes
24 in 22.10s. These are per-command results, not a sum of distinct full-suite tests.

The corrected new browser case passes three engines (11.3/12.0/11.3s). Expanding
`make test-web-otp-observations` to include the existing operations journey passes
six executions (two per engine; commands 13.7/14.7/13.6s), covering real offline
recovery, old-field absence, zero/capped counts, keyboard, axe and 320-pixel layout.
The Chromium counter-region screenshot is visually inspected and readable without
clipping; automated engine acceptance does not replace physical/branded review.

Before the loss-marker addition, final quality/contracts/build, 1,171 unit/contract,
35 tooling, dependency/source and image/service checks pass. All eight Docker services
remain healthy with collection disabled and retirement false. Final broader checks
on the loss-guard tree still need recording; own complete hosted acceptance remains
pending. No migration, new dependency, external delivery/model call or source PDF.

## Final native checks before publication

After the uncertainty guard and production-reader tests, `make lint openapi-check build`
passes with 200 typed source files and matching contracts. `make test-unit` passes
1,171 unit/contract and 35 tooling cases, with 498 integration cases deselected and
three existing TestClient/deliberate network-denial warnings. The final
`make test-otp-observations test-operations test-model-metrics` passes 35 cases in
41.73s, 24 in 24.28s and 43 in 0.27s respectively. The first target includes existing
identity regressions and the real SDK/API/Redis uncertainty tests. Per-command counts
overlap the unit suite; they are not a combined distinct-test total.

`make security security-source` passes without known dependency vulnerabilities or
source leaks. `make containers security-containers container-smoke` passes on the
final runtime tree: dependency/image/source checks and service/owned export/request/
model smoke. All eight Docker services stay healthy on schema0042; no volumes, images,
caches or unrelated roles are swept. Normal review OTP collection and export retirement
stay disabled. No migration or dependency changes require a new database setup.

The six operations/OTP browser executions described above remain the final UI result;
the loss guard changes only back-end availability for the already-tested null state.
Physical/branded-browser and actual delivery/billing gates remain separate. This
increment is ready for its own exact-source full hosted run, not for main promotion
or any production enablement. Parent source adf4328's live run cannot accept this
new API/SDK/UI/test/Make tree. Only Markdown closeout should follow its published head.

## Published verification candidate

Exact runtime/API/UI/test/Make source ceee4012c7f74dcc0c387a45ab112ed35d657f1b is
pushed on codex/otp-dispatch-observations. Its own complete hosted run is
[39304052749](https://github.com/Jotham566/kasoma/actions/runs/39304052749), confirmed
in progress. Do not replace that remote head for Markdown closeout. Parent combined
source adf4328 run39299684285 is separately in the browser stage; neither result is
inferred from another source. Main remains e7a4fc0 and no merged-branch cleanup is
yet authorized by ancestry. This following closeout is Markdown only.
