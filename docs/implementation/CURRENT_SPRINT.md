# Current Sprint

## E0 preparation — repository organization

Status: documentation and repository scaffolding complete; runtime foundation not started.

The MVP delivery horizon is 12 weeks from kickoff. No calendar kickoff date has been assigned here.

## Completed preparation

- Product documents and engineering specifications organized under `docs/`.
- Root agent instructions, contributor guidance and PR template.
- ADR navigation, changelog and live register of all 61 SRD requirements.
- Tracked workspace directories, environment example and bootstrap command boundaries.
- Documentation link, traceability and whitespace checks.

These changes support E0 planning. They do not complete NFR-MNT-001 or NFR-OBS-001.

## Next slice — E0 runtime foundation

Follow the [bootstrap contract](../specifications/15_Repository_Bootstrap_and_Environment.md) and [operating contract](../specifications/12_Coding_LLM_Operating_Contract.md).

- Pin Node.js, pnpm and Python tooling; select and lock the Python dependency tool.
- Implement the workspace, local services and deterministic fake provider profile.
- Add API health/dependency reporting and generated OpenAPI client consumed by the web shell.
- Add the migration framework, worker and correlation-ID propagation.
- Implement the prescribed commands, test harnesses and CI quality gates.
- Verify all bootstrap acceptance criteria before starting learner features.

## Decisions and open differences

The organization guide's sample authority order differs from the approved specification index. This reorganization preserves the existing index order, including the priority of security, privacy and safeguarding. Any hierarchy change requires an explicit decision; no such change is needed for runtime bootstrap.

The guide's optional `services/api/` and `services/worker/` examples differ from the approved architecture's `apps/api/` and `apps/worker/`. Use the approved architecture when implementing those entry points; `services/` remains available for shared domain modules.

The documentation layout now uses `docs/decisions/ADR/` for new ADRs. Existing accepted decisions remain canonical in the specification decision log and are linked from the ADR index.
