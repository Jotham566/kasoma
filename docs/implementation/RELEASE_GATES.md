# MVP release gates — outstanding evidence

Reviewed 4 October 2026. This register records missing release evidence, not exceptions.
The [requirements register](REQUIREMENTS_TRACEABILITY.md) remains authoritative for code
coverage. Synthetic fixtures, automated tests and developer-authored ADRs do not constitute
academic, legal, safeguarding or production-provider approval.

| Gate | Required evidence | Responsible function / status | Safe work meanwhile |
| --- | --- | --- | --- |
| Delivery calendar and capacity | Named kickoff date; accountable product/technical/academic/safeguarding owners; reviewer capacity for the 12-week plan | Owner assignments and kickoff not recorded | Implement independent synthetic slices; preserve relative week deadlines |
| Academic release inventory | Exact NCDC learning-outcome mappings; rights evidence; independent reviews; minimum 250 approved items with required subject/topic/competency/difficulty coverage | Academic and content leads; not supplied | Synthetic schema, import, review and publication-control tests |
| Grading benchmark | Frozen expert-scored choice/numeric/short-text cases, unseen equivalent pairs, versioned rubric/answer truth and prompt-injection cases | Academic lead; not supplied | Deterministic regressions and fail-closed model contracts; no academic-accuracy claim |
| Short-text enablement | Week 5 ≥85% expert-agreement evidence; dual-pass validation and calibration bands demonstrating ≥90% exact agreement for automatic scoring; approved enabled combinations | Academic/technical leads; not supplied | Disabled synthetic path and fallback tests; no automatic learner scoring or Gemini calls |
| Privacy and safeguarding | Approved Uganda notices/guardian/assent procedure; DPIA; applicable PDPO obligations; processor register/agreements; cross-border safeguards | Privacy/legal/safeguarding owners; not supplied | Synthetic data only; authorization, data-request and retention-control tests |
| Production provider (Week 8) | Recorded approved hosting/database/Redis/storage/model/messaging decision, credentials handling, budgets and vendor/privacy review | Product/technical/privacy owners; not supplied | Local PostgreSQL/Redis/MinIO/Mailpit, fake providers and adapter boundaries |
| Destructive migration | Exact affected tables/columns/rows, transform and preservation rules, hold coverage, explicit human approval and tested recovery plan | Engineering prepares; owner approves before destructive migration | Additive schema, advisory preview, synthetic tests and concrete transform proposal |
| Operational release | Alert/kill-switch tests, restore evidence meeting RPO/RTO, load/latency evidence, supported-browser checks, support/content/safeguarding rehearsals | Technical and operational owners; incomplete | Local reproducible tests, failure visibility and runbooks |
| Pilot launch | All requirement evidence or approved exceptions, zero S1/S2 defects, configuration/template verification, release/rollback evidence and named owner sign-offs | Product/technical/academic/safeguarding owners; pending | Keep deployment and feature enablement disabled |

## Open questions and recommendation

OPEN-QUESTION RELEASE-01: identify existing approved mappings, benchmark, rights and privacy
artifacts and record their version/location and approving owner. Recommendation: link the
approved evidence and keep synthetic fixtures separate. If evidence does not exist, assign
owners and dates; missing evidence remains a gate rather than an inferred approval.

OPEN-QUESTION RELEASE-02: record the Week 8 provider decision when approved. Recommendation:
continue the local adapter profile until then. Selecting a vendor prematurely creates
privacy, cost and portability obligations without satisfying the decision gate.

The coding agent has requested the evidence locations from the owner and continues
unaffected work. No answer or elapsed time grants approval. No new architectural decision,
legal interpretation, schedule extension or reduced acceptance threshold is made here.

Sources: [ADR-017](../decisions/ADR/017-readiness-resolutions.md),
[release acceptance](../specifications/10_Testing_Acceptance_and_Release.md),
[security/privacy](../specifications/09_Security_Privacy_and_Safeguarding.md),
[production decisions](../specifications/16_Production_Pilot_Decisions.md),
[coding contract](../specifications/12_Coding_LLM_Operating_Contract.md).

## Verified engineering evidence added 4 October

Local synthetic logical restore now passes, including 52 tables, 270 rows, pgvector and selected
immutable guards; see [recovery verification](E9_RECOVERY_VERIFICATION.md). Three browser engines
pass 60 journey executions and cold question transfer stays below 250,000 bytes; see
[browser verification](E9_BROWSER_COVERAGE_VERIFICATION.md). These reduce engineering gaps but
do not replace production PITR/RPO/RTO, branded/mobile tests, academic approval or owner sign-off.

## Preservation design approval recorded 19 October

OPEN-QUESTION PRESERVATION-01 is resolved only for the bounded synthetic implementation
of [ADR-057](../decisions/ADR/057-minimized-channel-preservation-proposal.md): the human
user explicitly approved its source identities, field allowlists and finite lifecycle.
Raw messages, usable credentials and real-data processing remain excluded. Source
`0a8f674` passes complete hosted 39183714273 for bounded capture/lifecycle/API/UI/
recovery and security/service engineering. Creation remains default-disabled. This decision cannot close all hold coverage or authorize erasure;
destructive execution still needs the separate reviewed transform and approval.

## Further engineering verification recorded 19 October

Progress source `7148a1c` passes complete hosted [39184552472](https://github.com/Jotham566/kasoma/actions/runs/39184552472); shared-control/latest
application source `6d53541` passes complete hosted [39185423895](https://github.com/Jotham566/kasoma/actions/runs/39185423895). All 1,074 unit/contract,
412 integration, 35 tooling and 108 browser executions, recovery, restricted login,
security/images and service smoke pass. This supplies bounded synthetic engineering
evidence only. It does not waive remaining preservation/erasure/accountability,
academic, privacy/provider, production recovery, physical/branded-device or pilot gates.
