.DEFAULT_GOAL := help
PYTHON ?= python3
TRIVY_TIMEOUT ?= 30m
TRIVY_DB_REPOSITORY ?= mirror.gcr.io/aquasec/trivy-db:2,ghcr.io/aquasecurity/trivy-db:2
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
.PHONY: lock-python
lock-python:
	$(CURDIR)/.local/tools/bin/uv lock --offline
services:
	docker compose up -d --wait postgres redis minio mailpit
.PHONY: check-ci-profile
check-ci-profile:
	docker compose -f docker-compose.yml -f docker-compose.ci.yaml config --quiet
.PHONY: ci-docker-config
ci-docker-config:
	node scripts/ci-docker-mirror.mjs
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
.PHONY: test-erasure-contracts
test-erasure-contracts:
	$(UV) pytest tests/contract/test_erasure_contracts.py tests/contract/test_erasure_config.py tests/contract/test_erasure_manifest.py
.PHONY: test-erasure-identity-isolated
test-erasure-identity-isolated:
	$(UV) python -m scripts.erasure_identity_check
.PHONY: test-erasure-identity
test-erasure-identity:
	$(UV) pytest tests/integration/test_identity.py tests/integration/test_erasure_staff_barrier.py --allow-hosts=localhost,127.0.0.1,::1
.PHONY: test-erasure-source
test-erasure-source:
	$(UV) pytest tests/integration/test_erasure_source_shape.py tests/integration/test_erasure_staff_barrier.py --allow-hosts=localhost,127.0.0.1,::1
.PHONY: test-operations-configuration
test-operations-configuration:
	$(UV) pytest tests/contract/test_operations_configuration_contract.py tests/integration/test_operations_configuration.py --allow-hosts=localhost,127.0.0.1,::1
.PHONY: test-web-operations-configuration
test-web-operations-configuration:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test --config=playwright.operations-configuration.config.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test --config=playwright.operations-configuration.config.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test --config=playwright.operations-configuration.config.ts
.PHONY: test-request-metrics
test-request-metrics:
	$(UV) pytest tests/contract/test_request_metrics.py tests/contract/test_request_metrics_collector.py tests/integration/test_request_metrics_store.py --allow-hosts=localhost,127.0.0.1,::1
.PHONY: smoke-request-metrics
smoke-request-metrics:
	$(UV) python -m scripts.request_metrics_smoke
lint: check-docs
	$(UV) ruff check .
	$(UV) ruff format --check .
	$(UV) mypy
	$(PNPM) exec eslint apps/web packages tests/e2e tests/browser-control scripts/*.mjs *.mjs *.ts --max-warnings=0
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
	$(MAKE) test-web-short-text
	$(MAKE) test-web-operations-configuration
build:
	$(PNPM) build
containers:
	docker compose --profile application build
security:
	$(UV) bandit -r apps/api apps/worker services scripts/ci_runner_storage.py scripts/e2e_failures.py scripts/browser_database.py scripts/erasure_identity_check.py -q
	$(UV) python scripts/check_secrets.py
	$(UV) pip-audit --local
	$(PNPM) audit --audit-level=high
check-docs:
	$(PYTHON) scripts/check_docs.py
	git diff --check
	git diff --cached --check
eval-local eval-gemini-free:
	@echo "$@: unavailable until frozen academic benchmark, task schemas and evaluation gates are implemented (E4). No inference performed." >&2
	@exit 1

export KASOMA_EVAL_BASELINE KASOMA_EVAL_CANDIDATE
eval-compare:
	$(UV) python -m scripts.compare_evaluations

.PHONY: security-source security-containers ollama-check
security-source:
	$(UV) python scripts/scan_source.py
security-containers:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kasoma-trivy-cache:/root/.cache/ aquasec/trivy:0.74.0 image --no-progress --db-repository $(TRIVY_DB_REPOSITORY) --timeout $(TRIVY_TIMEOUT) --severity HIGH,CRITICAL --exit-code 1 kasoma-api
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kasoma-trivy-cache:/root/.cache/ aquasec/trivy:0.74.0 image --no-progress --db-repository $(TRIVY_DB_REPOSITORY) --timeout $(TRIVY_TIMEOUT) --severity HIGH,CRITICAL --exit-code 1 kasoma-web
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
	node --test scripts/tooling.test.mjs scripts/export-stream.test.mjs scripts/ci-docker-mirror.test.mjs

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
.PHONY: test-e2e-failure-diagnosis
test-e2e-failure-diagnosis:
	$(UV) pytest tests/contract/test_e2e_failure_diagnosis.py
.PHONY: test-browser-database
test-browser-database:
	$(UV) pytest tests/contract/test_browser_database.py tests/contract/test_object_recovery.py tests/contract/test_erasure_identity_check.py
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

.PHONY: load-objective load-history-mixed test-load-profile test-load-role-cleanup
load-objective:
	$(UV) python -m scripts.objective_load
load-history-mixed:
	$(UV) python -m scripts.objective_load --history-mixed
test-load-profile:
	$(UV) pytest tests/contract/test_objective_load.py
test-load-role-cleanup:
	$(UV) pytest tests/contract/test_objective_load.py tests/integration/test_load_role_lifecycle.py --allow-hosts=localhost,127.0.0.1,::1

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

.PHONY: test-export-download
EXPORT_FAULT ?= stall|corrupt
test-export-download:
	$(PNPM) exec playwright test tests/e2e/export-download.spec.ts --workers=1 --grep '$(EXPORT_FAULT) mid-transfer' --trace retain-on-failure

.PHONY: test-export-download-control
test-export-download-control:
	$(PNPM) exec playwright test tests/browser-control/download.spec.ts --config=playwright.export-control.config.ts

.PHONY: test-export-download-control-linux
test-export-download-control-linux:
	docker run --rm --network none --memory 2g --cpus 2 --shm-size=256m --read-only --tmpfs /tmp \
		-e KASOMA_E2E_BROWSER=webkit -e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
		-v "$(CURDIR)/node_modules:/work/node_modules:ro" \
		-v "$(CURDIR)/tests/browser-control:/work/tests/browser-control:ro" \
		-v "$(CURDIR)/playwright.export-control.config.ts:/work/playwright.export-control.config.ts:ro" \
		-w /work mcr.microsoft.com/playwright@sha256:6446946a1d9fd62d9ae501312a2d76a43ee688542b21622056a372959b65d63d \
		node node_modules/@playwright/test/cli.js test tests/browser-control/download.spec.ts --config=playwright.export-control.config.ts --output=/tmp/control-results

.PHONY: test-firefox-native-download
test-firefox-native-download:
	$(UV) python -m scripts.firefox_native_control

.PHONY: worker-exports
worker-exports:
	$(UV) celery -A apps.worker.entrypoint:app worker --include=apps.worker.export_tasks --loglevel=INFO --pool=prefork --concurrency=1 --prefetch-multiplier=1 --queues=exports --hostname=exports@%h

.PHONY: smoke-export
smoke-export:
	$(UV) python -m scripts.export_smoke

.PHONY: test-grading-work
test-grading-work:
	$(UV) pytest tests/contract/test_short_text_workflow.py tests/integration/test_grading_work_store.py tests/integration/test_grading_history_holds.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-short-text-eligibility
test-short-text-eligibility:
	$(UV) pytest tests/contract/test_short_text_eligibility.py

.PHONY: test-grading-bands
test-grading-bands:
	$(UV) pytest tests/integration/test_grading_bands.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-grading-publications
test-grading-publications:
	$(UV) pytest tests/integration/test_grading_publications.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-short-text-flow
test-short-text-flow:
	$(UV) pytest tests/integration/test_short_text_flow.py tests/integration/test_short_text_processing.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-provider-fault-isolation
test-provider-fault-isolation:
	$(UV) pytest tests/integration/test_provider_fault_isolation.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-identity
test-web-identity:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/identity.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/identity.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/identity.spec.ts

.PHONY: test-grading-reviews
test-grading-reviews:
	$(UV) pytest tests/contract/test_grading_review_contracts.py tests/integration/test_grading_reviews.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-short-text
test-web-short-text:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test --config playwright.short-text.config.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test --config playwright.short-text.config.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test --config playwright.short-text.config.ts

.PHONY: test-web-privacy
test-web-privacy:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/data-requests.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/data-requests.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/data-requests.spec.ts

.PHONY: test-grading-operations
test-grading-operations:
	$(UV) pytest tests/contract/test_operations_contract.py tests/integration/test_operations.py tests/integration/test_grading_operations.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-model-metrics smoke-model-metrics
test-model-metrics:
	$(UV) pytest tests/contract/test_model_metrics.py tests/contract/test_model_telemetry.py tests/integration/test_model_metric_store.py --allow-hosts=localhost,127.0.0.1,::1
smoke-model-metrics:
	$(UV) python -m scripts.model_metrics_smoke

.PHONY: test-web-operations
test-web-operations:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/operations.spec.ts tests/e2e/flags.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/operations.spec.ts tests/e2e/flags.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/operations.spec.ts tests/e2e/flags.spec.ts

.PHONY: test-channel-receipt-holds
test-channel-receipt-holds:
	$(UV) pytest tests/integration/test_channel_receipt_holds.py tests/integration/test_channel_receipt_runtime_role.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-channel-preservation-format
test-channel-preservation-format:
	$(UV) pytest tests/contract/test_channel_preservation_format.py

.PHONY: test-channel-preservation
test-channel-preservation:
	$(UV) pytest tests/contract/test_channel_preservation_contracts.py tests/contract/test_channel_preservation_format.py
	$(UV) pytest tests/integration/test_channel_preservation.py tests/integration/test_channel_preservation_runtime_role.py tests/integration/test_channel_preservation_sql.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-channel-preservation
test-web-channel-preservation:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/channel-preservation.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/channel-preservation.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/channel-preservation.spec.ts

.PHONY: test-channel-clock
test-channel-clock:
	$(UV) pytest tests/contract/test_channel_clock.py

.PHONY: test-hold-delete-clock
test-hold-delete-clock:
	$(UV) pytest tests/integration/test_hold_delete_clock.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-audit-activity
test-audit-activity:
	$(UV) pytest tests/integration/test_audit_activity.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-audit
test-web-audit:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/audit.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/audit.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/audit.spec.ts

.PHONY: ci-runner-storage ci-storage-report ci-storage-check test-ci-storage
ci-runner-storage:
	$(PYTHON) scripts/ci_runner_storage.py --prepare
ci-storage-report:
	$(PYTHON) scripts/ci_runner_storage.py
ci-storage-check:
	$(PYTHON) scripts/ci_runner_storage.py --check
test-ci-storage:
	$(UV) pytest tests/contract/test_ci_runner_storage.py

.PHONY: test-progress
test-progress:
	$(UV) pytest tests/contract/test_practice_activity.py tests/contract/test_progress_engine.py tests/contract/test_progress_reuse.py tests/integration/test_progress.py tests/integration/test_channel_assessment.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-web-select-targets
test-web-select-targets:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/mobile-reflow.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/mobile-reflow.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/mobile-reflow.spec.ts

.PHONY: test-export-evidence-holds
test-export-evidence-holds:
	$(UV) pytest tests/integration/test_export_evidence_holds.py tests/integration/test_export_evidence_runtime_role.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-recovery
test-export-recovery:
	$(UV) pytest tests/integration/test_export_recovery.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-export-retirement
test-export-retirement:
	$(UV) pytest tests/integration/test_export_retirement.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: retirement-provision retirement-enable retirement-disable worker-retirement
retirement-provision:
	KASOMA_RETIREMENT_ACTION=provision $(UV) python -m services.export_retirement_cli
retirement-enable:
	KASOMA_RETIREMENT_ACTION=enable $(UV) python -m services.export_retirement_cli
retirement-disable:
	KASOMA_RETIREMENT_ACTION=disable $(UV) python -m services.export_retirement_cli
worker-retirement:
	$(UV) celery -A apps.worker.retirement_entrypoint:app worker --pool=prefork --concurrency=1 --prefetch-multiplier=1 --queues=privacy-maintenance --hostname=privacy@%h --loglevel=warning

export KASOMA_RETIREMENT_CONFIG KASOMA_RETIREMENT_SCHEMA
.PHONY: test-retirement-runtime
test-retirement-runtime:
	$(UV) pytest tests/contract/test_retirement_executor_contract.py tests/integration/test_export_retirement_runtime.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-commit-interception test-web-whatsapp
test-commit-interception:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/browser-control/committed-intercept.spec.ts --config=playwright.export-control.config.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/browser-control/committed-intercept.spec.ts --config=playwright.export-control.config.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/browser-control/committed-intercept.spec.ts --config=playwright.export-control.config.ts
test-web-whatsapp:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/whatsapp.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/whatsapp.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/whatsapp.spec.ts

.PHONY: test-web-assessment
test-web-assessment:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/assessment.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/assessment.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/assessment.spec.ts

.PHONY: test-web-progress
test-web-progress:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/progress.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/progress.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/progress.spec.ts

.PHONY: test-fresh-session-response
test-fresh-session-response:
	$(UV) pytest tests/integration/test_fresh_session_response.py tests/integration/test_assessment.py tests/integration/test_recommendations.py tests/integration/test_reassessments.py tests/integration/test_assessment_transactions.py tests/integration/test_assessment_content_locks.py tests/integration/test_channel_assessment.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-recovery-role-cleanup
test-recovery-role-cleanup:
	$(UV) pytest tests/contract/test_recovery_drill.py tests/contract/test_objective_load.py tests/contract/test_disposable_owner.py tests/integration/test_recovery_role_lifecycle.py tests/integration/test_load_role_lifecycle.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: test-otp-observations
test-otp-observations:
	$(UV) pytest tests/contract/test_otp_metrics.py tests/integration/test_otp_observations.py tests/integration/test_otp_metric_store.py tests/integration/test_identity.py --allow-hosts=localhost,127.0.0.1,::1
.PHONY: test-otp-observations-api
test-otp-observations-api:
	$(UV) pytest tests/integration/test_otp_observations.py -k disabled --allow-hosts=localhost,127.0.0.1,::1
.PHONY: test-web-otp-observations
test-web-otp-observations:
	KASOMA_E2E_BROWSER=chromium $(PNPM) exec playwright test tests/e2e/otp-observations.spec.ts tests/e2e/operations.spec.ts
	KASOMA_E2E_BROWSER=firefox $(PNPM) exec playwright test tests/e2e/otp-observations.spec.ts tests/e2e/operations.spec.ts
	KASOMA_E2E_BROWSER=webkit $(PNPM) exec playwright test tests/e2e/otp-observations.spec.ts tests/e2e/operations.spec.ts

.PHONY: test-metric-loss
test-metric-loss:
	$(UV) pytest tests/contract/test_metric_loss_contract.py tests/integration/test_metric_loss_recovery.py --allow-hosts=localhost,127.0.0.1,::1

.PHONY: recovery-objects test-recovery-objects
recovery-objects:
	$(UV) python -m scripts.object_recovery_drill
test-recovery-objects:
	$(UV) pytest tests/contract/test_object_recovery.py

.PHONY: load-history-temporal test-temporal-load
load-history-temporal:
	$(UV) python -m scripts.objective_load --history-temporal
test-temporal-load:
	$(UV) pytest tests/contract/test_temporal_history_load.py tests/contract/test_objective_load.py
