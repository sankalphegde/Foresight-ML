.PHONY: help setup local-up local-down lint format typecheck test

help:
	@echo "Foresight-ML Data Pipeline"
	@echo ""
	@echo "Setup:"
	@echo "  make setup           - Install uv and initialize project"
	@echo ""
	@echo "Local Development:"
	@echo "  make local-up        - Start local Airflow"
	@echo "  make local-down      - Stop local Airflow"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run ruff linter"
	@echo "  make format          - Format code with ruff"
	@echo "  make typecheck       - Run mypy type checker"
	@echo "  make check           - Run all checks (lint + typecheck)"
	@echo "  make test			  - Runs pytests"

setup:
	@echo "Installing uv..."
	command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "Initializing project..."
	uv sync
	@echo "Setup complete!"

local-up:
	docker-compose up -d
	@echo "Airflow UI: http://localhost:8080 (admin/admin)"

local-down:
	docker-compose down

lint:
	uv run ruff check src/ airflow/

format:
	uv run ruff format src/ airflow/
	uv run ruff check --fix src/ airflow/

typecheck:
	uv run mypy src/

check: format typecheck
	@echo "All checks passed"
	
test:
	uv run pytest tests/