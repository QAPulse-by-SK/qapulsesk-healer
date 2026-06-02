# qapulsesk-healer Makefile — convenience targets for local dev.
#
# Usage:
#   make install     # install all extras + dev tooling in editable mode
#   make test        # run unit tests (skips integration tests)
#   make test-all    # include integration tests (requires ANTHROPIC_API_KEY)
#   make lint        # ruff check + format check
#   make format      # auto-format with ruff
#   make typecheck   # mypy --strict
#   make check       # lint + typecheck + test (what CI runs)
#   make clean       # remove build artifacts and caches

.PHONY: install test test-all lint format typecheck check clean

PYTHON ?= python3
PIP    ?= pip

install:
	$(PIP) install -e ".[selenium,playwright,appium,dev]"

test:
	pytest -m "not integration" --cov=qapulsesk_healer --cov-report=term-missing

test-all:
	pytest --cov=qapulsesk_healer --cov-report=term-missing

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check . --fix

typecheck:
	mypy

check: lint typecheck test

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
