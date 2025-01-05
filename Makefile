.PHONY: setup clean test format check build lock

POETRY := poetry

.DEFAULT_GOAL := all

all: clean setup test

# Update lock file
lock:
	$(POETRY) lock --no-update

# Install dependencies and set up development environment
setup: lock
	$(POETRY) install
	$(POETRY) run pip install -e .

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
