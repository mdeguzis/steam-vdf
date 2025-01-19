.PHONY: setup clean test format check build lock

POETRY := poetry

.DEFAULT_GOAL := all

# Match with maximum set in pyproject.toml
# Use mise to make this easy in the parent env
# Example: mise use python@3.10 python@3.11 python@3.12
PYTHON_VERSION := python3.10
VENV_PATH := $(shell $(POETRY) env info -p 2>/dev/null)

all: clean setup build test

# Update lock file
lock:
	$(POETRY) lock

# Install dependencies and set up development environment
setup: lock
	$(POETRY) install
	$(POETRY) env use $(PYTHON_VERSION)
	$(POETRY) run pip install -e .

build:
	$(POETRY) build

# Upload the package to PyPI
upload: build
	twine upload dist/*

# Format code
format:
	$(POETRY) run black .
	$(POETRY) run isort .

# Run linting and type checks
check:
	$(POETRY) run flake8 .
	$(POETRY) run black --check .
	$(POETRY) run isort --check .

# Run tests
test:
	$(POETRY) run pytest

test-verbose:
	$(POETRY) run pytest -v --capture=no

test-coverage:
	$(POETRY) run pytest --cov=steam_vdf

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	$(POETRY) env remove python || true
