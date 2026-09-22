.DEFAULT_GOAL := help
PYTHON ?= python3

.PHONY: help check-docs setup dev test lint migrate seed openapi e2e security eval-local eval-gemini-free

help:
	@echo "Kasoma specification and repository baseline"
	@echo "  make check-docs  Validate documentation links, traceability and whitespace"
	@echo "  Runtime targets are reserved for E0 bootstrap and currently fail explicitly."

check-docs:
	$(PYTHON) scripts/check_docs.py
	git diff --check
	git diff --cached --check

setup dev test lint migrate seed openapi e2e security eval-local eval-gemini-free:
	@echo "'$@' is not implemented: complete E0 using docs/specifications/15_Repository_Bootstrap_and_Environment.md." >&2
	@exit 1
