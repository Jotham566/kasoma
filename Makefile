.DEFAULT_GOAL := help
PYTHON ?= python3
export PATH := $(CURDIR)/.local/runtime/node_modules/node/bin:$(CURDIR)/.local/tools/bin:$(PATH)
export NEXT_TELEMETRY_DISABLED := 1
export TURBO_TELEMETRY_DISABLED := 1
UV := $(CURDIR)/.local/tools/bin/uv run --frozen
PNPM := corepack pnpm

.PHONY: help setup services dev test test-unit lint format typecheck migrate seed openapi openapi-check e2e security check-docs build containers eval-local eval-gemini-free eval-compare
help:
	@echo "Kasoma E0: setup services migrate seed dev test lint openapi e2e security build containers"
setup:
	$(PYTHON) scripts/setup.py
services:
	docker compose up -d --wait postgres redis minio mailpit
dev: services migrate
	$(UV) python scripts/dev.py
test: test-unit
	$(UV) pytest -m integration --allow-hosts=localhost,127.0.0.1,::1
test-unit:
	$(UV) pytest -m 'not integration'
lint: check-docs
	$(UV) ruff check .
	$(UV) ruff format --check .
	$(UV) mypy
	$(PNPM) exec eslint apps/web packages tests/e2e scripts/*.mjs *.mjs *.ts --max-warnings=0
	$(PNPM) format:check
	$(PNPM) typecheck
format:
	$(UV) ruff format .
	$(UV) ruff check --fix .
	$(PNPM) format
typecheck:
	$(UV) mypy
	$(PNPM) typecheck
migrate:
	$(UV) alembic -c apps/api/alembic.ini upgrade head
seed:
	$(UV) python -m services.seed
	$(UV) python -m scripts.storage_init
openapi:
	$(UV) python -m scripts.openapi
	$(PNPM) exec openapi-typescript packages/api-client/openapi.json -o packages/api-client/src/schema.d.ts
openapi-check:
	$(UV) python scripts/check_contract.py
e2e:
	$(PNPM) exec playwright test
build:
	$(PNPM) build
containers:
	docker compose --profile application build
security:
	$(UV) bandit -r apps/api apps/worker services -q
	$(UV) python scripts/check_secrets.py
	$(UV) pip-audit --local
	$(PNPM) audit --audit-level=high
check-docs:
	$(PYTHON) scripts/check_docs.py
	git diff --check
	git diff --cached --check
eval-local eval-gemini-free eval-compare:
	@echo "$@: unavailable until frozen academic benchmark, task schemas and evaluation gates are implemented (E4). No inference performed." >&2
	@exit 1

.PHONY: security-source security-containers ollama-check
security-source:
	$(UV) python scripts/scan_source.py
security-containers:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kasoma-trivy-cache:/root/.cache/ aquasec/trivy:0.74.0 image --severity HIGH,CRITICAL --exit-code 1 kasoma-api
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kasoma-trivy-cache:/root/.cache/ aquasec/trivy:0.74.0 image --severity HIGH,CRITICAL --exit-code 1 kasoma-web
ollama-check:
	$(UV) python -m scripts.ollama_check

.PHONY: smoke-dev
smoke-dev:
	$(UV) python scripts/smoke_dev.py

.PHONY: setup-ollama ollama-serve
setup-ollama:
	$(UV) python scripts/setup_ollama.py
ollama-serve:
	OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_CONTEXT_LENGTH=8192 OLLAMA_MODELS=$(CURDIR)/.local/ollama-models $(CURDIR)/.local/ollama/ollama serve

.PHONY: container-smoke
container-smoke:
	$(UV) python scripts/container_smoke.py

.PHONY: staff-role
export KASOMA_STAFF_EMAIL
export KASOMA_STAFF_ROLE
export KASOMA_STAFF_REVOKE
staff-role:
	$(UV) python -m services.staff

.PHONY: seed-assessment
seed-assessment:
	$(UV) python -m scripts.assessment_fixtures

.PHONY: seed-numeric
seed-numeric:
	$(UV) python -m scripts.assessment_fixtures --numeric

.PHONY: seed-diagnostic
seed-diagnostic:
	$(UV) python -m scripts.assessment_fixtures --diagnostic

.PHONY: replay-mastery
replay-mastery:
	$(UV) python -m scripts.replay_mastery

.PHONY: replay-recommendations
replay-recommendations:
	$(UV) python -m scripts.replay_recommendations

.PHONY: seed-hints
seed-hints:
	$(UV) python -m scripts.assessment_fixtures --hints
