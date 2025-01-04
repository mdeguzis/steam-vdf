# Variables
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
PYTHON        := python3

# Set default goal
.DEFAULT_GOAL := build

# Declare PHONY targets
.PHONY: check build docs clean

# Fix formatting
format:
	isort .
	black .

# Check formatting
check:
	isort --check-only .
	flake8 .

# Generate other items for dev
# Output to requirements.txt to reduce maintenance load
# pyproject.toml - modern main project file
# requirements.txt - used by most automation, GitHub actions
# Pipfile - pipenv only
requirements:
	pip-compile pyproject.toml --output-file=requirements.txt

# Main build target
build: clean check
	$(PYTHON) -m build

upload:
	twine check dist/*
	twine upload dist/*

# Documentation target
docs:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Clean build artifacts
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf dist/*
	rm -rf *.egg-info
