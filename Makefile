.DEFAULT_GOAL := help
PYTHON ?= python3
TRIVY_TIMEOUT ?= 30m
export PATH := $(CURDIR)/.local/runtime/node_modules/node/bin:$(CURDIR)/.local/tools/bin:$(PATH)
export NEXT_TELEMETRY_DISABLED := 1
export TURBO_TELEMETRY_DISABLED := 1
export PLAYWRIGHT_BROWSERS_PATH := $(CURDIR)/.local/browsers
UV := $(CURDIR)/.local/tools/bin/uv run --frozen
PNPM := corepack pnpm

.PHONY: help setup services dev test test-unit lint format typecheck migrate seed openapi openapi-check e2e security check-docs build containers eval-local eval-gemini-free eval-compare
help:
	@echo "Kasoma E0: setup services migrate seed dev test lint openapi e2e security build containers"
setup:
	$(PYTHON) scripts/setup.py
services:
	docker compose up -d --wait postgres redis minio mailpit
.PHONY: services-db test-data-exports
services-db:
	docker compose up -d --wait postgres redis
test-data-exports:
	$(UV) pytest tests/integration/test_data_exports.py --allow-hosts=localhost,127.0.0.1,::1
dev: services migrate
	$(UV) python scripts/dev.py
test: test-unit
	$(UV) pytest -m integration --allow-hosts=localhost,127.0.0.1,::1
test-unit: test-tooling
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
	$(MAKE) e2e-chromium
	$(MAKE) e2e-firefox
	$(MAKE) e2e-webkit
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
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kasoma-trivy-cache:/root/.cache/ aquasec/trivy:0.74.0 image --timeout $(TRIVY_TIMEOUT) --severity HIGH,CRITICAL --exit-code 1 kasoma-api
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kasoma-trivy-cache:/root/.cache/ aquasec/trivy:0.74.0 image --timeout $(TRIVY_TIMEOUT) --severity HIGH,CRITICAL --exit-code 1 kasoma-web
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

.PHONY: replay-reassessments
replay-reassessments:
	$(UV) python -m scripts.replay_reassessments

.PHONY: seed-reassessment
seed-reassessment:
	$(UV) python -m scripts.assessment_fixtures --reassessment --hints

.PHONY: seed-multiple-choice
seed-multiple-choice:
	$(UV) python -m scripts.assessment_fixtures --multiple-choice --hints

.PHONY: expire-exports
expire-exports:
	$(UV) python -m scripts.expire_exports

.PHONY: deps-lock test-tooling
deps-lock:
	$(PNPM) install --lockfile-only
test-tooling:
	node --test scripts/tooling.test.mjs scripts/export-stream.test.mjs

.PHONY: process-imports
process-imports:
	$(UV) python -m scripts.process_imports

.PHONY: monitor-operations
monitor-operations:
	$(UV) python -m scripts.monitor_operations

.PHONY: test-operations
test-operations:
	$(UV) pytest tests/contract/test_operations_contract.py tests/integration/test_operations.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-whatsapp
test-whatsapp:
	$(UV) pytest tests/contract/test_whatsapp_ingress.py tests/integration/test_whatsapp_linking.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: process-messages
process-messages:
	$(UV) python -m scripts.process_messages

.PHONY: simulate-whatsapp
export KASOMA_WHATSAPP_TEXT
simulate-whatsapp:
	$(UV) python -m scripts.simulate_whatsapp

.PHONY: test-assessment-transactions
test-assessment-transactions:
	$(UV) pytest tests/integration/test_assessment_transactions.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-channel-assessment
test-channel-assessment:
	$(UV) pytest tests/integration/test_channel_assessment.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-whatsapp-practice
test-whatsapp-practice:
	$(UV) pytest tests/integration/test_whatsapp_practice.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-channel-operations
test-channel-operations:
	$(UV) pytest tests/integration/test_channel_operations.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: recovery-drill
recovery-drill:
	$(UV) python -m scripts.recovery_drill

.PHONY: e2e-install e2e-list e2e-chromium e2e-firefox e2e-webkit
e2e-install:
	$(PNPM) exec playwright install --with-deps chromium firefox webkit
e2e-list:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test --list
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test --list
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test --list
e2e-chromium:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test --shard=1/2
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test --shard=2/2
.PHONY: e2e-chromium-full
e2e-chromium-full:
	KASOMA_E2E_CHROMIUM_CHANNEL=chromium $(MAKE) e2e-chromium
e2e-firefox:
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test --shard=1/2
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test --shard=2/2
e2e-webkit:
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test --shard=1/2
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test --shard=2/2

.PHONY: test-runtime-role
test-runtime-role:
	$(UV) pytest tests/integration/test_runtime_role.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-reviewed-rubrics
test-reviewed-rubrics:
	$(UV) pytest tests/integration/test_reviewed_rubrics.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-content
test-web-content:
	$(PNPM) exec playwright test --config=playwright.ui.config.ts

.PHONY: test-legal-holds
test-legal-holds:
	$(UV) pytest tests/integration/test_legal_holds.py tests/integration/test_learning_record_holds.py tests/integration/test_accountability_holds.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-mobile
test-web-mobile:
	$(PNPM) exec playwright test tests/e2e/mobile-reflow.spec.ts

.PHONY: load-objective test-load-profile
load-objective:
	$(UV) python -m scripts.objective_load
test-load-profile:
	$(UV) pytest tests/contract/test_objective_load.py

.PHONY: test-assessment-locks
test-assessment-locks:
	$(UV) pytest tests/integration/test_assessment_content_locks.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-storage
test-export-storage:
	$(UV) pytest tests/contract/test_export_storage.py tests/contract/test_export_reader.py tests/integration/test_export_reader_transport.py tests/integration/test_private_minio_exports.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-reader
test-export-reader:
	$(UV) pytest tests/contract/test_export_reader.py tests/integration/test_export_reader_transport.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-jobs
test-export-jobs:
	$(UV) pytest tests/integration/test_export_jobs.py tests/integration/test_export_download_lifecycle.py tests/integration/test_export_cursor_redis.py tests/integration/test_export_upgrade.py tests/integration/test_export_api.py tests/integration/test_export_recovery.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-worker
test-export-worker:
	$(UV) pytest tests/contract/test_export_worker.py tests/integration/test_export_worker_limits.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-gateway
test-export-gateway:
	$(PNPM) exec playwright test tests/e2e/export-gateway.spec.ts

.PHONY: worker-exports
worker-exports:
	$(UV) celery -A apps.worker.entrypoint:app worker --include=apps.worker.export_tasks --loglevel=INFO --pool=prefork --concurrency=1 --prefetch-multiplier=1 --queues=exports --hostname=exports@%h

.PHONY: smoke-export
smoke-export:
	$(UV) python -m scripts.export_smoke
