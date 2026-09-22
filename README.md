# Kasoma

An adaptive revision and mastery platform for Uganda's competency-based secondary education.

Kasoma's planned learning loop is **Diagnose → Recommend → Practice → Explain → Reassess → Update mastery**. The MVP focuses on Senior 4 Mathematics and Physics, with a full web experience and linked-account short practice through WhatsApp.

## Repository status

This repository contains the product and engineering specification baseline, governance documents and workspace scaffolding. Application code, dependency manifests, local services and application tests have not been implemented yet. Runtime Make targets fail explicitly until E0 bootstrap is implemented; `docker-compose.yml` reserves the service configuration and contains no services yet.

## Documentation

| Document | Purpose |
| --- | --- |
| [Product whitepaper](docs/product/PRODUCT_WHITEPAPER.md) | Long-term product vision |
| [Product roadmap](docs/product/PRODUCT_ROADMAP.md) | Scope and delivery plan for the 12-week MVP |
| [Engineering specification index](docs/specifications/00_README_Source_of_Truth.md) | Specification inventory, authority order and fixed MVP boundaries |
| [Implementation backlog](docs/specifications/11_Implementation_Backlog.md) | Ordered implementation slices |
| [Coding agent operating contract](docs/specifications/12_Coding_LLM_Operating_Contract.md) | Required engineering workflow |
| [Architecture decisions](docs/specifications/13_ADR_and_Decision_Log.md) | Architectural decisions and change control |
| [Repository bootstrap contract](docs/specifications/15_Repository_Bootstrap_and_Environment.md) | Requirements for the future development environment and CI |
| [Current sprint](docs/implementation/CURRENT_SPRINT.md) | Completed preparation, next slice and open differences |
| [Implementation traceability](docs/implementation/REQUIREMENTS_TRACEABILITY.md) | Implementation and test evidence for every SRD requirement |
| [ADR index](docs/decisions/ADR/README.md) | Existing decisions and location for new proposals |
| [Changelog](CHANGELOG.md) | Repository and product change history |

## Repository layout

```text
AGENTS.md                 Engineering instructions and specification navigation
docs/product/             Product roadmap and whitepaper
docs/specifications/      Authoritative engineering specification pack
docs/decisions/ADR/        ADR index and future decision records
docs/implementation/      Current sprint and live requirements evidence
apps/                     Reserved for web, API and worker entry points
services/                 Reserved for shared domain services
packages/                 Reserved for shared packages and generated client
infra/                    Reserved for containers and deployment configuration
tests/                    Reserved for application and contract tests
scripts/                  Repository maintenance and validation tools
```

Empty implementation directories are tracked with `.gitkeep` files. Their presence does not indicate implemented components.

## Repository checks

With Git, Make and Python 3.9+ available for the documentation checker, run:

```sh
make check-docs
```

This checks local Markdown file links, SRD coverage in the implementation register, and Git whitespace errors. It does not run application acceptance tests. `make help` describes the current command boundary.

The future application runtime still requires Python 3.12 and pinned tooling as specified in the bootstrap contract.

## Starting implementation

Clone the specification baseline:

```sh
git clone https://github.com/Jotham566/kasoma.git
cd kasoma
```

Read the engineering specification index and follow the read order in the coding agent operating contract before implementing a backlog slice. Use the index's authority order to resolve document precedence.

The first implementation slice is the repository and runtime foundation described in the bootstrap contract. The setup instructions and validation commands should be added here as that foundation becomes runnable.

Keep credentials, real learner data, production exports, restricted source material and generated build artifacts out of Git. [.env.example](.env.example) documents the planned configuration vocabulary, leaves secrets empty and disables external model calls. It is not a runnable environment yet; local secret files are ignored.

## Planned architecture

The [system architecture](docs/specifications/02_System_Architecture.md) specifies a modular monolith with asynchronous workers:

- Next.js, React and TypeScript for the web application.
- FastAPI, Pydantic, SQLAlchemy and Alembic for the Python API and persistence.
- PostgreSQL for authoritative data; Redis and Celery for background work.
- Provider interfaces for AI, messaging and object storage, with local or deterministic fake adapters for development and tests.
- A pnpm/Turborepo monorepo using the reserved directories above.

These are specification decisions; the runtime foundation is still pending. See [CONTRIBUTING.md](CONTRIBUTING.md) for the change and review workflow.
