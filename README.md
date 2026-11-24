# Local Model Routing with Native Laya

This repository studies model routing, answer quality, cost, verification, and semantic caching. The interactive application is a local command-line program: it embeds the pinned Laya Python runtime to choose a local generation tier, then sends the prompt to Ollama on loopback. It does not run a gateway HTTP server or a separate Laya service.

The research code also contains benchmark preparation and scoring, fixed and random baselines, prompted-router comparisons, DistilBERT training/fallback support, verification and cache experiments, and Colab serving experiments. Prior Jev-based service and gateway runs are retained as historical evidence; they do not describe the current interactive runtime.

## Quick start on Mac

Install Python 3.11–3.14, `uv`, and [Ollama](https://docs.ollama.com/). Download the configured local generation models if needed. Laya downloads its pinned decision checkpoint on first use.

```bash
make setup-test
make verify
make laya-config
make setup-laya
```

Review `.env.laya` before use. Defaults point to Ollama at `127.0.0.1:11434`, select the `typed-decisions` Laya checkpoint, and make no paid-provider calls.

```bash
make doctor-local
make chat PROMPT='Explain how model routing works' MODEL=auto
```

`MODEL` can be `auto`, `small`, or `medium`. In `auto` mode, Laya runs in-process and picks between the two local Ollama models. The text-generation request goes only to the local Ollama endpoint. No CLI command starts a gateway server or exposes a port.

Equivalent direct commands after setup:

```bash
set -a; source .env.laya; set +a
.venv-laya/bin/laya-gateway doctor
.venv-laya/bin/laya-gateway chat --model auto 'Explain how model routing works'
```

## Evaluation

The benchmark tooling is separate from interactive chat. It prepares the frozen dataset manifest, runs explicitly bounded evaluations, and reports saved observations:

```bash
uv sync --locked --extra evaluation --extra test
uv run laya-gateway eval-prepare
uv run laya-gateway eval-run --split validation --tier small --tier medium \
  --max-prompts 1 --max-requests 2 --max-tokens 10000 --output-tokens 32 --concurrency 1
```

Paid tiers remain disabled unless a provider credential, model, sourced rates, and positive run/request/token/USD limits are configured and explicitly enabled. Do not use held-out test data for tuning. See [evaluation workflow](docs/EVALUATION_WORKFLOW.md), [architecture](docs/ARCHITECTURE.md), [status](docs/STATUS.md), and [experiment ledger](docs/EXPERIMENTS.md).

## Current evidence and limitations

The repository contains a frozen 2,500-prompt benchmark index and historical real small/medium generation observations. Those records are not results from the current in-process Laya router. A direct local Laya checkpoint inference was observed during this migration, but the complete CLI chat path still needs a fresh local check against an available Ollama installation. Laya routing quality, calibration, and performance on this project’s prompts have not yet been established. No paid model calls or external publishing are part of the default workflow.

Code evaluation uses a Docker sandbox; containers reduce risk but are not an absolute security boundary. Colab notebooks are experiments, not permanent service dependencies. Historical deployment and API artifacts are not the current application interface.

## Repository layout

```text
src/laya_gateway/       Native Laya runtime, CLI chat, routing, evaluation, cache, and verifier code
tests/                  Offline checks
config/                 Example environment profiles without secrets
notebooks/              Colab GPU and model experiments
scripts/                Data preparation, audits, and local research utilities
docs/                   Architecture, methods, decisions, status, and experiment records
evidence/               Sanitized historical engineering outputs
runs/                   Ignored local evaluation outputs
data/                   Benchmark index and source snapshots
```
