# E4 unseen reassessment verification

Date: 28 September 2026. Synthetic local development only.

Reviewed hints were committed and pushed to main as `3c0c3ba`; the completed branch
was deleted. Reassessment was subsequently committed and pushed to main as `73c1fba`;
`codex/e4-unseen-reassessment` was deleted. Local evidence is recorded below; the
[next progress slice](E6_PROGRESS_VERIFICATION.md) records the resulting main CI status.

## Requirements and decisions

FR-GRD-008: reviewed equivalent claims, same-primary-skill/difficulty fallback,
all-time unseen identities, active-reservation/clone exclusion, one-item assessment,
durable source linkage, safe shortage, retry/resume and separate immutable grading.
Supporting FR-REV-003/005, FR-GRD-007, FR-MST-001/003, FR-CNT-001/004, FR-ID-003,
FR-OPS-001, NFR-SEC-002, NFR-ACC-001 and NFR-MNT-001.

[ADR-023](../decisions/ADR/023-unseen-reassessment.md) records the optional reviewed
claim format, primary-skill tie break, deterministic duplicate thresholds, one-link
policy and independent one-item session. No architecture/provider replacement or
calibration change. Migration 0010 preserves prior sessions and evidence; forward
fixes retain reassessment linkage. Safe lifecycle events contain no raw answer text.

## Verification

All applicable local checks passed on the final implementation.

| Command | Result |
| --- | --- |
| `make setup` | Pinned runtimes/locked dependencies verified; existing environment preserved. |
| `make migrate seed seed-reassessment` | Additive migration 0010 and independently reviewed synthetic fixture inventory succeeded. |
| `make format lint` | Formatting, Python/TypeScript lint/types, documentation links and whitespace passed. |
| `make test` | 181 unit/contract/property and 68 integration tests passed (249 total). |
| `make openapi openapi-check build` | Generated contracts match and production web build passed. |
| `make e2e` | All 13 browser tests passed on the final services, including retry after lost acknowledgement, reload before/after answering, return to original feedback, keyboard and axe. |
| `make replay-mastery replay-recommendations replay-reassessments` | Passed read-only with zero stored projections/snapshots in default local DB; integration verifies nonempty reassessment and mastery history. |
| `make security security-source` | Bandit, secret-boundary/Gitleaks and Python/JavaScript dependency audits passed. |
| `make containers security-containers container-smoke` | Final images built; HIGH/CRITICAL vulnerability gates and API/database/Redis/worker/web smoke passed. |

Coverage includes deterministic duplicate/value masking and primary-skill tie breaks;
reviewed-pair preference and fallback; clone/shortage/reservation rejection;
publication and either-author review denial; choice/numeric independent grades;
current consent and cross-learner denial; retirement and expiry; concurrent/different-key
start, answer replay and atomic outbox rollback; immutable source/linkage; nonempty
selection/mastery replay. Integration uses isolated clean schemas upgraded through head
and repeated migration application. The default development DB upgrade preserves
existing synthetic history. No destructive reset or downgrade was used.

Failures corrected: Python typing/formatting; an assertion confusing two history rows
plus one current projection with four projections; a shared synthetic staff identity
hitting the existing OTP cooldown; and a Bandit false positive on the numeric text-token
similarity threshold. The fixture now has separate identities and the setting is named
word-overlap threshold. No controls were disabled or release criteria weakened.
No unresolved check failures remain. Existing non-failing tool/dependency warnings remain; production and academic acceptance
are not inferred from local checks.

Ignored logs: `.local/reassessment-final-verification.log`,
`.local/reassessment-final-browser.log`, `.local/reassessment-migrations.log`,
`.local/reassessment-foundation.log` (initial security finding),
`.local/reassessment-security.log` (successful recheck),
`.local/reassessment-final-containers.log` and `.local/reassessment-docs.log`.

## Files

- Domain/services: `services/reassessment_engine.py`, `services/reassessments.py`,
  `services/assessment.py`, assessment/content contracts, `services/content.py`,
  `services/domain/assessment.py`.
- API/data: `apps/api/assessment.py`, migration `0010_unseen_reassessment.py`,
  analytics schema, generated OpenAPI and TypeScript client.
- Web: staff content editor/reviewer, shared revision player and API proxy.
- Tests: `tests/contract/test_reassessment_engine.py`,
  `tests/integration/test_reassessments.py`, `tests/e2e/reassessment.spec.ts`.
- Tooling: `Makefile`, `scripts/assessment_fixtures.py`, `scripts/e2e_api.py`,
  `scripts/replay_reassessments.py`.
- Documentation: root instructions/README/changelog, current sprint, traceability,
  ADR-023/indexes, API/data/content specs, local runbook, hint verification and this report.

## Limits and next task

Synthetic varied wording tests software selection and recovery, not academic transfer.
Text normalization/similarity cannot certify semantic novelty; independently reviewed
content and benchmark validation remain release prerequisites. No misconception-resolution
claim is emitted without reviewed tags and a calibrated criterion threshold. No real
learner data, external models/messaging, Gemini or production cloud calls were used.
Next: FR-MST-004/005 learner progress and recent history with confidence and sparse-evidence
language. All privacy, academic, Week 5 and Week 8 gates remain intact.

Hosted CI for main `3c0c3ba`: [passed](https://github.com/Jotham566/kasoma/actions/runs/36401623871).
