UV ?= uv
PYTHON ?= .venv/bin/python

.PHONY: setup-test verify test compile build setup-figures figures \
	laya-config setup-laya doctor-local chat

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

# Optional: regenerate docs/figures/progress from committed evidence (separate venv).
FIGURES_PYTHON ?= .venv-figures/bin/python

setup-figures:
	python3 -m venv .venv-figures
	$(FIGURES_PYTHON) -m pip install -r requirements/figures.txt

figures:
	$(FIGURES_PYTHON) scripts/make_progress_figures.py

# Create a private, shell-compatible native Laya profile without overwriting user config.
laya-config:
	@if [ -e .env.laya ]; then \
		echo ".env.laya already exists; leaving it unchanged"; \
	else \
		cp config/laya.env.example .env.laya && echo "Created .env.laya from config/laya.env.example"; \
	fi

# Install the CLI and native Laya runtime from the committed lockfile.
setup-laya:
	UV_PROJECT_ENVIRONMENT=.venv-laya $(UV) sync --locked --extra test --extra laya

doctor-local:
	@test -f .env.laya || { echo "Run 'make laya-config' and review .env.laya first"; exit 2; }
	@set -a; . ./.env.laya; set +a; .venv-laya/bin/laya-gateway doctor

chat:
	@test -f .env.laya || { echo "Run 'make laya-config' and review .env.laya first"; exit 2; }
	@test -n "$(PROMPT)" || { echo "Usage: make chat PROMPT='your question' [MODEL=auto|small|medium]"; exit 2; }
	@set -a; . ./.env.laya; set +a; .venv-laya/bin/laya-gateway chat --model '$(if $(MODEL),$(MODEL),auto)' '$(PROMPT)'
