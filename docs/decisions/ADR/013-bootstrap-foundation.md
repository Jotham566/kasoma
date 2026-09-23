# ADR-013: Bootstrap implementation choices

Date: 23 September 2026
Status: Accepted within explicitly delegated bootstrap discretion
Owners: Engineering (implementation agent)
Requirement IDs: NFR-MNT-001, NFR-OBS-001, NFR-SEC-001/002, FR-OPS-002

## Context and decision

Implement ADR-001–012 without changing the stack or learner behaviour. Use uv with
one Python 3.12 environment and committed lockfile. Pin Node 24 LTS, Corepack pnpm,
and exact resolved JS dependencies. pnpm workspaces/Turborepo coordinate web and
shared packages; Python entry points live in apps/api and apps/worker.

Add GET /api/v1/health (safe dependency readiness; 503 when degraded) and GET
/api/v1/live (process liveness). Both are public, expose no configuration or data,
and are included in generated OpenAPI. Other endpoints remain unavailable.
Server-render the shell using a generated typed client and propagate a validated
UUID request_id through API logs, trace attributes and worker headers.

Alembic's first migration enables vector and creates only curriculum foundation
tables; it does not implement learner/content/assessment schemas prematurely.
Synthetic seed scenarios for later domains are versioned fixtures, not persisted
production-like tables or published academic content. Later slices materialize
those fixtures under their approved domain constraints.

## Alternatives and consequences

Poetry/pip-tools would work; uv supplies Python installation and a single locked
workflow. Dockerized inference loses the intended Apple acceleration; retain
host-native Ollama. Never require inference to start the foundation. Local ports
bind to loopback, database/storage credentials are generated into ignored .env,
and automated tests prohibit internet sockets. No production startup is allowed
in this foundation. No provider fallback or paid adapter is introduced.

## Security/privacy/academic impact

No real users, no learner endpoints and no seeded auth credentials. Synthetic
curriculum labels are clearly marked and make no NCDC mapping claim. Health and
error logs use allowlisted metadata, never exception strings or request bodies.

## Migration or rollback

Initial schema is additive. No automated destructive downgrade/reset is provided.
The first release has no previous-release database snapshot; test repeat upgrade
and document that limitation until the next migration exists.

## Approval

User explicitly authorized best-practice decisions where specifications grant
implementation discretion, repository bootstrap and health/contracts. This record
does not approve any departure from existing ADRs or any production provider.

## Container hardening evidence

Initial Debian slim application images failed the strict HIGH/CRITICAL container
scan on base-system packages, including findings with no available Debian fix.
Use pinned Alpine 3.24 variants of the same approved Python/Node runtimes and
re-run builds, runtime smoke and scans. This changes only the container base,
not the approved application stack. No vulnerability suppression is introduced.

The web runtime uses Next's standalone output and excludes build-only package
managers and development dependencies. Initial scans identified vulnerabilities
in the base image's bundled npm tree; those tools are not needed to serve the app.
Container startup requires no registry access.
