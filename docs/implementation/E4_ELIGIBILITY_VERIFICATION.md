# Short-text calibration and audit eligibility

Date: 10 October 2026. Requirements: FR-GRD-003/004/005, FR-MST-001, NFR-SEC-002.
Decision: [ADR-050 proposal](../decisions/ADR/050-short-text-pending-and-eligibility.md).

## Implementation and boundaries

`services/short_text_eligibility.py` evaluates an immutable trusted report projection
and current band-bound audit state. Integer counts preserve exact >=85% overall
within-tolerance and >=90% held-out exact agreement; self-reported model confidence
is not an input. Subject/topic/language, model/prompt/configuration and response length
must match. Approval references, timestamps and subgroup approval are required;
critical errors, disablement, insufficient assignment coverage or rolling agreement
below 90% prevent an eligible candidate result. Nested model copies are revalidated.

The proposed window is the latest 100 completed audits (all available when fewer).
Completed counts must match window length; duplicate, unordered, future or cross-band
records fail closed. Pending reviews are never counted as correct. Sampling the first
and each tenth subsequent return assigns ceil(N/10) in every prefix, including partial
batches. The policy is versioned and requires academic approval before production.

This module writes no data and performs no model/provider calls. It does not establish
that an approval reference exists, authenticate reviewers, generate an audit assignment,
persist a kill switch, create a grade or update mastery. A caller must load authorized
current evidence under a band lock and recheck it before dispatch/publication. These
integration gates remain open, as do complete answer/worker/learner UI integration,
independent blinded expert review, privacy holds/retention and real academic calibration.
No production band, benchmark result or academic approval is fabricated.

## Checks

`make test-short-text-eligibility` runs synthetic policy checks. Full component acceptance
uses `make format lint test-unit openapi-check security-source`. Tests cover threshold
boundaries, every scope/version mismatch, length limits, missing/future approval,
malformed copied models, subgroup/critical errors, audit coverage, pending/omitted
reviews, sticky disablement, cross-band replay and prefix sampling through 10,000 returns.
Verification passes: 780 unit/contract tests (33 new eligibility cases), 35 tooling
tests, formatting/lint/Python and TypeScript types, generated-contract comparison,
source-secret scanning and dependency/security checks. The dedicated 33-case command
also passes. Logs: `.local/short-text-eligibility-checks.log` and
`.local/short-text-eligibility-security.log`. No database or HTTP schema changes are
introduced here; runtime, persistence and academic acceptance remain unproven.
