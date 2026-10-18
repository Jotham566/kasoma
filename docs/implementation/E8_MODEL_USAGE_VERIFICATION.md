# Local model observation verification — candidate

18 October 2026. FR-OPS-002, NFR-OBS-001, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.
Source: [ADR-054](../decisions/ADR/054-bounded-worker-model-usage.md) and
[readiness](E8_MODEL_USAGE_READINESS.md). Hosted acceptance and promotion remain pending.

## Implementation boundary

Six owned attribute-free SDK delta counters observe actual ordinary-worker provider
calls after dispatch authorization/deadline barriers. Missing usage is unknown; both
explicit token fields are required to claim reported usage. Candidates precede grade
validation. Only static resource/scope, integer counters and bounded interval times
enter aggregate storage. No prompts, answers, identities, fingerprints or arbitrary
model/provider labels. Recording performs no network I/O. Collector failure cannot
change provider outcomes, and shutdown has finite waits.

The request histogram codec and namespace remain unchanged. Shared byte transport
preserves absolute five-minute expiry from earliest observation, immutable retries,
256-interval cap, <=1024-byte canonical bodies, bounded host/Redis skew, 15-second
freshness, finite cap marker and missing/corrupt data unavailability. Model purpose
hashes and namespaces are separate. Fresh successful empty collection is distinct
from an absent collector. Export workers/API roles do not publish model freshness.

The existing ADMIN snapshot adds local attempts/outcomes/known token subtotals,
nullable totals, interval/cap limits and a local volume warning. Unknown totals remain
unknown; zero requires fresh observation. Billing, full fleet accounting and academic
error rate remain unavailable. Desktop and narrow/200% text use the existing staff
visual language; compact card padding and stacked values preserve readable mobile
width. No database migration, cloud provider, model inference or learner enablement.

## Executed evidence

- `make format lint openapi-check build`: passes after the final narrow-screen
  refinement. Generated API/client and analytics-alert
  schema agree. `make test-unit`: 916 Python unit/contract and35 tooling cases pass.
- `make test-model-metrics`:43 cases pass using real owned SDK, FakeModelProvider and
  real isolated Redis namespaces. Covers reported zero/unknown/error, delta/idle time,
  private attributes, canonical/coherent bounds, role/lifecycle, collector failure,
  exact volume threshold/recovery, immutable retry, TTL, cap and corruption.
- `make test-request-metrics`:51 unchanged histogram/collector/Redis regressions pass.
  `make test-operations`:24 cases pass including ADMIN denial, actual model aggregates,
  unknown totals, alert and corruption recovery. No IDs enter the response.
- `make test-short-text-flow`:22 cases pass, including actual two-pass worker counter
  publication. Both safety-allowed and safety-refusal/no-dispatch parameters pass in a
  final two-case focused rerun. Attempts, replay, grades and mastery retain existing controls.
- `make container-smoke`: all eight rebuilt services, owned asynchronous export,
  request aggregation and fixed fake model probe pass. This is actual worker-to-Redis
  evidence. Final source/UI rebuild, service/fake-probe smoke and image scans also pass.
- `make security security-source security-containers test-runtime-role recovery-drill`:
  pass. No HIGH/CRITICAL image findings. Restricted database login passes; isolated
  synthetic logical restore verifies65 tables/616 rows in351ms with pgvector,
  immutable and encrypted learner-flow guards. Production PITR/RPO/RTO is unverified.
- Initial broad browser run passes Chromium/Firefox and14 of15 WebKit first-shard
  journeys; the flag-report click overlaps the authoritative session refresh and its
  form does not open. Trace retained locally. The test now awaits the existing ready
  button and exact saved count before the same report assertions. Cause beyond the
  observed overlap is not claimed. Final serial operations/flags pass all six three-engine executions, including
  320-pixel reflow, 200% text and axe; the mobile card was visually inspected.
  Final WebKit full-suite rerun passes30 journeys. Short-text profiles remain in progress. No assertion, timeout or privacy control is reduced.
- `make test`:914 unit/contract cases pass before two additional contract cases;
  broad PostgreSQL regression remains in progress. Do not infer it has passed.

Local logs: `.local/model-usage-*.log`; screenshots `.local/ui-review/model-usage-*`.
No real learner/corpus or external model, Gemini, email or messaging calls were used.
Normal learner short-text delivery and production release remain disabled. Genuine
academic, safeguarding, privacy and provider authority gates remain required.
