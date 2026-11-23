UV ?= uv
PYTHON ?= .venv/bin/python

.PHONY: setup-test verify test compile build compose-config setup-figures figures \
	mac-config setup-laya laya-serve serve-local doctor-local

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
	docker compose -f compose.yaml -f compose.laya.yaml config --quiet

# Optional: regenerate docs/figures/progress from committed evidence (separate venv).
FIGURES_PYTHON ?= .venv-figures/bin/python

setup-figures:
	python3 -m venv .venv-figures
	$(FIGURES_PYTHON) -m pip install -r requirements/figures.txt

figures:
	$(FIGURES_PYTHON) scripts/make_progress_figures.py

# Create a private, shell-compatible Mac profile without overwriting user config.
mac-config:
	@if [ -e .env ]; then \
		echo ".env already exists; leaving it unchanged"; \
	else \
		cp config/mac.env.example .env && echo "Created .env from config/mac.env.example"; \
	fi

# Keep the optional decision-model stack isolated from the portable gateway venv.
setup-laya:
	python3 -m venv .venv-laya
	.venv-laya/bin/python -m pip install -r requirements/laya.txt

# Run Laya on loopback. It downloads its pinned model the first time it starts.
laya-serve:
	@test -x .venv-laya/bin/laya-serve || { echo "Run 'make setup-laya' first"; exit 2; }
	@set -a; if [ -f .env ]; then . ./.env; fi; set +a; \
	LAYA_HOST="$${LAYA_HOST:-127.0.0.1}" \
	LAYA_PORT="$${LAYA_PORT:-8000}" \
	LAYA_DEVICE="$${LAYA_DEVICE:-mps}" \
	LAYA_MODELS="$${LAYA_MODELS:-typed-decisions}" \
	LAYA_PRELOAD="$${LAYA_PRELOAD:-1}" \
	LAYA_REVISION="$${LAYA_REVISION:-reviewed}" \
	.venv-laya/bin/laya-serve

# The gateway reads its configuration from the private .env in this shell.
serve-local:
	@test -f .env || { echo "Run 'make mac-config' and review .env first"; exit 2; }
	@set -a; . ./.env; set +a; $(PYTHON) -m jev_gateway.cli serve

doctor-local:
	@test -f .env || { echo "Run 'make mac-config' and review .env first"; exit 2; }
	@set -a; . ./.env; set +a; $(PYTHON) -m jev_gateway.cli doctor
