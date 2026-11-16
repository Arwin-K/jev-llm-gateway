UV ?= uv
PYTHON ?= .venv/bin/python

.PHONY: setup-test verify test compile build compose-config

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
