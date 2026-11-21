UV ?= uv
PYTHON ?= .venv/bin/python

.PHONY: setup-test verify test compile build compose-config setup-figures figures

# Install the locked, offline test environment without optional model stacks.
setup-test:
	$(UV) sync --locked --extra test

# Full local regression path: syntax checks followed by the offline suite.
verify: compile test

test:
	$(PYTHON) -m pytest -q

compile:
	$(PYTHON) -m compileall -q src load scripts tests

build:
	$(UV) build

# Validate deployment configuration without starting services or opening ports.
compose-config:
	docker compose config --quiet

# Optional: regenerate docs/figures/progress from committed evidence (separate venv).
FIGURES_PYTHON ?= .venv-figures/bin/python

setup-figures:
	python3 -m venv .venv-figures
	$(FIGURES_PYTHON) -m pip install -r requirements/figures.txt

figures:
	$(FIGURES_PYTHON) scripts/make_progress_figures.py
