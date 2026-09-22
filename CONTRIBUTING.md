# Contributing to Kasoma

Start with the [specification index](Kasoma_MVP_Engineering_Specification_Pack/00_README_Source_of_Truth.md) and [coding operating contract](Kasoma_MVP_Engineering_Specification_Pack/12_Coding_LLM_Operating_Contract.md). The index defines document precedence; the contract defines the implementation workflow for coding agents.

## Changes and review

1. Select a bounded slice from the [implementation backlog](Kasoma_MVP_Engineering_Specification_Pack/11_Implementation_Backlog.md) and identify its requirement or story IDs.
2. Create a focused branch from `main`. Keep one coherent change per pull request and preserve unrelated work.
3. Explain the intended behavior, affected contracts, acceptance checks and any unresolved questions before implementing.
4. Follow the approved architecture. Record proposed scope, schema, public API or architectural changes through the specification's ADR process before implementing them.
5. Run checks appropriate to the change and document their results in the pull request. Reference requirement or story IDs in the pull request title and description.
6. Obtain review before merging. Branch protection and required status checks must be configured in GitHub when implementation CI is available; these files alone do not enforce them.

## Current validation

This is a documentation baseline with no runnable application or test suite. For documentation changes, verify relative links and run `git diff --check` (or `git diff --cached --check` for staged changes). Check that descriptions distinguish planned behavior from implemented behavior.

During foundation implementation, add the setup, lint, test, migration, OpenAPI, security and end-to-end commands required by the [bootstrap contract](Kasoma_MVP_Engineering_Specification_Pack/15_Repository_Bootstrap_and_Environment.md), and document the exact commands in the root README. Pin tooling and commit dependency lockfiles.

## Data and provider boundaries

- Never commit credentials, real learner data, production exports or restricted academic source material.
- Use safe placeholders in environment examples and original synthetic data in fixtures.
- Keep local startup, tests and ordinary CI independent of paid or external model APIs.
- Preserve deterministic grading, approved content boundaries, consent and safeguarding requirements.
- Report suspected credential exposure or sensitive-data issues privately to the repository owner; do not include sensitive material in public issues or pull requests.
