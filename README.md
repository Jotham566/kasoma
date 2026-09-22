# Kasoma

An adaptive revision and mastery platform for Uganda's competency-based secondary education.

Kasoma's planned learning loop is **Diagnose → Recommend → Practice → Explain → Reassess → Update mastery**. The MVP focuses on Senior 4 Mathematics and Physics, with a full web experience and linked-account short practice through WhatsApp.

## Repository status

This repository currently contains the product and engineering specification baseline. Application code, dependency manifests, local services and automated tests have not been implemented yet. There are no application setup or run commands at this stage.

## Documentation

| Document | Purpose |
| --- | --- |
| [Product whitepaper](Kasoma_Product_Whitepaper.md) | Long-term product vision |
| [Product roadmap](Kasoma_Product_Roadmap.md) | Scope and delivery plan for the 12-week MVP |
| [Engineering specification index](Kasoma_MVP_Engineering_Specification_Pack/00_README_Source_of_Truth.md) | Specification inventory, authority order and fixed MVP boundaries |
| [Implementation backlog](Kasoma_MVP_Engineering_Specification_Pack/11_Implementation_Backlog.md) | Ordered implementation slices |
| [Coding agent operating contract](Kasoma_MVP_Engineering_Specification_Pack/12_Coding_LLM_Operating_Contract.md) | Required engineering workflow |
| [Architecture decisions](Kasoma_MVP_Engineering_Specification_Pack/13_ADR_and_Decision_Log.md) | Architectural decisions and change control |
| [Repository bootstrap contract](Kasoma_MVP_Engineering_Specification_Pack/15_Repository_Bootstrap_and_Environment.md) | Requirements for the future development environment and CI |

## Starting implementation

Clone the specification baseline:

```sh
git clone https://github.com/Jotham566/kasoma.git
cd kasoma
```

Read the engineering specification index and follow the read order in the coding agent operating contract before implementing a backlog slice. Use the index's authority order to resolve document precedence.

The first implementation slice is the repository and runtime foundation described in the bootstrap contract. The setup instructions and validation commands should be added here as that foundation becomes runnable.

Keep credentials, real learner data, production exports, restricted source material and generated build artifacts out of Git. Future environment templates must use safe placeholders; local secret files are ignored.

## Planned architecture

The [system architecture](Kasoma_MVP_Engineering_Specification_Pack/02_System_Architecture.md) specifies a modular monolith with asynchronous workers:

- Next.js, React and TypeScript for the web application.
- FastAPI, Pydantic, SQLAlchemy and Alembic for the Python API and persistence.
- PostgreSQL for authoritative data; Redis and Celery for background work.
- Provider interfaces for AI, messaging and object storage, with local or deterministic fake adapters for development and tests.
- A pnpm/Turborepo monorepo with `apps/`, `packages/`, `services/`, `infra/`, `docs/` and `tests/` introduced during implementation.

These are specification decisions; the runtime foundation is still pending. See [CONTRIBUTING.md](CONTRIBUTING.md) for the change and review workflow.
