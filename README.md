# Local Model Routing Gateway

A reproducible study of three-tier language-model serving, answer quality, cost, and routing. The current application uses a self-hosted Laya decision service by default and serves explicit `small`, `medium`, and configured `frontier` text-chat tiers. Its evaluation tools prepare a frozen 2,500-prompt benchmark across math, multiple choice, and coding tasks, record bounded attempts, score answers, and report coverage without hiding failures.

**Architecture:** [Implemented request and evaluation paths](docs/ARCHITECTURE.md) · **Reproduce:** [Evaluation workflow](docs/EVALUATION_WORKFLOW.md) · **Evidence:** [Experiment ledger](docs/EXPERIMENTS.md) · **Status:** [Verified and pending features](docs/FEATURE_STATUS.md)

## Research question

> How much answer quality can a cost-aware gateway retain while using smaller models when possible, and what latency and spending overhead do routing, verification, and caching introduce?

The gateway now supports automatic Laya policy selection, optional hosted Jev comparison, a prompted small-model comparison, fixed and seeded-random baselines, and a local Strands typed-server adapter. The DistilBERT trainer and artifact-gated fallback are implemented but no trained artifact exists because complete compatible three-tier labels are absent. Optional verifier cascades and scoped semantic caching are implemented and offline-tested; their real model and cache performance remains unmeasured. Day 5 adds an ARM container, local Compose monitoring, a bounded load runner, and a tested kind deployment. Sustained real inference load remains pending. The [project plan](docs/PLAN.md) describes the remaining scope.

## Observed evidence

- Pinned source preparation selected **2,500 prompts**: 1,100 GSM8K math, 1,000 MMLU choice, and 400 sanitized MBPP code tasks. Project splits are 1,500 train, 500 validation, and 500 held-out test. The committed [manifest index](docs/day2-manifest-index.jsonl) contains IDs and hashes, not private prompt text or answers.
- The latest local offline suite passed **181 tests** on 2026-11-22; the base and Laya-overlay Compose configs also parsed. Both the native MPS path and CPU-only Compose path completed one capped real smoke through Laya to `qwen2.5:7b`, returning `Hello!`. These are connectivity checks, not routing-quality results. See `evidence/testing/local-laya-gateway-smoke-20261122.txt`, `evidence/testing/laya-compose-smoke-20261122.txt`, and `evidence/testing/laya-compose-suite-20261122.txt`. Earlier, the ARM gateway image served health checks; Prometheus scraped it; Grafana provisioned 14 panels. A bounded in-cluster pod replacement returned 39 HTTP 200 responses and one connection error across 40 API requests. This was application traffic without generation.
- The real v2 small-tier validation set covers 500 prompts (324 correct, 157 incorrect, 19 parse errors); small-tier train covers all 1,500 IDs (991 correct, 453 incorrect, 54 parse errors, one persistent backend error, one sandbox timeout). Medium-tier train covers all 1,500 IDs (1,224 correct, 263 incorrect, 13 parse errors, no backend/evaluator errors). Medium validation has records for all 500 IDs: 402 correct, 92 incorrect, and 6 parse errors (494 binary scores). A saved code response previously classified as an environment block was re-scored in the Docker sandbox and found to contain invalid Python syntax. Small/medium validation IDs and fingerprints match across all three tasks. These remain descriptive comparisons, not a frozen routing result. Frontier is unconfigured, Jev has not made live decisions, no paid API cost has been measured, and the held-out test remains unused. See the [small-tier audits](evidence/day7/local-v2-coverage-audit-20261114.json), [medium train audit](evidence/day8/medium-train-full-audit-20261120.json), and [reclassified medium validation audit](evidence/day8/medium-validation-full-audit-reclassified-20261120.json).

See [the Day 6 protocol](docs/DAY6_PROTOCOL.md) for the frozen-evaluation gate and Colab performance procedure. [Day 5](docs/DAY5_HANDOFF.md) covers deployment checks; [Day 4](docs/DAY4_HANDOFF.md) covers verification and caching.

## Quick start on Mac

Install [uv](https://docs.astral.sh/uv/) and [native Ollama](https://docs.ollama.com/macos). Review disk space and available memory before pulling models.

```bash
make setup-test
make verify
make mac-config
# Review .env; it contains local defaults and no credentials.
make setup-laya
```

`make verify` compiles the gateway, load tools, scripts, and tests, then runs the complete offline pytest suite. It does not contact model providers or download datasets. To check the Docker Compose deployment file without starting containers, run `make compose-config`; use `make build` to build the Python package. If you do not use `uv`, create a fresh virtual environment and install the same extra with `python3 -m venv .venv` followed by `.venv/bin/python -m pip install -e '.[test]'`, then run `.venv/bin/python -m compileall -q src load scripts tests` and `.venv/bin/pytest -q`.

The configured candidate tags are `qwen2.5:1.5b` and `qwen2.5:7b`. Start Ollama and ensure both tags are installed. In separate terminals, run the decision service and gateway:

```bash
# Terminal 1: start Laya; first startup downloads its pinned model.
make laya-serve
# Terminal 2: start the gateway using settings from .env.
make serve-local
# Terminal 3: inspect backend readiness, then test automatic routing.
make doctor-local
uv run jev smoke --tier auto
```

`make mac-config` never overwrites an existing `.env`; review that file before running local commands. `make setup-laya` installs the pinned Laya service into the ignored `.venv-laya`, separate from the gateway environment. `make doctor-local` checks both Ollama tiers and, when the selected router requires Laya, its loopback `/health` endpoint. The ordinary `jev` CLI reads environment variables from the current shell; to run other CLI commands with `.env`, use `set -a; source .env; set +a` first.

`POST http://127.0.0.1:8080/v1/chat/completions` accepts text messages with `model` set to `small`, `medium`, `frontier`, or `auto`, plus optional `stream`, `max_tokens`, and `temperature`. `model=auto` uses the local Laya decision service by default and returns 503 when neither it nor a compatible trained fallback can decide. Tools, image, and audio inputs are not implemented. `/healthz` checks the process; `/readyz` does not prove a model is loaded. `jev doctor` checks backend availability. The frontier tier stays disabled without a model, key, current rates, and positive request, token, and USD caps. Local Laya decision calls are bounded by positive request/token caps and do not require credentials. Hosted Jev remains an optional paid comparison, disabled by default.

Optional `execution_mode` (`route_first`, `cascade`, `hybrid`) and `cache_mode` (`verified`, experimental `similarity_only`) fields enable Day 4 buffered paths. They require explicit configuration; the default remains `standard` with cache `off`. See [Day 4 configuration and failure semantics](docs/DAY4_HANDOFF.md).

For the base local deployment, `docker compose up -d --build` starts the gateway, Prometheus, and Grafana on loopback ports 8080, 9090, and 3000. `/metrics` exposes bounded aggregate series; detailed request stages stay in secret-free traces. This base profile keeps generation in native Ollama. To enable `model=auto` routing inside Compose, start the private CPU Laya service with the overlay:

```bash
docker compose -f compose.yaml -f compose.laya.yaml up -d --build
```

The overlay does not publish Laya's port; its checkpoint persists in a named local volume. The initial image build and checkpoint download need internet access and local disk/memory. The gateway and monitoring ports remain bound to loopback. Run `docker compose down` to stop services without deleting monitoring data or the Laya model volume. The [Day 5 runbook](docs/DAY5_HANDOFF.md) explains backend connectivity, kind, load scenarios, and what readiness actually checks.

## Reproduce evaluation preparation

```bash
uv sync --locked --extra evaluation --extra test
uv run jev eval-prepare
uv run jev eval-run --split validation --tier small --tier medium --max-prompts 1 --max-requests 2 --max-tokens 10000 --output-tokens 32 --concurrency 1
```

The runner prints a private run-file path for `jev eval-report` and `jev eval-audit`. Normal offline checks do not download datasets or call paid APIs. [The evaluation workflow](docs/EVALUATION_WORKFLOW.md) covers resumption, audits, sourced rates, held-out test policy, and serving baselines.

[Progress figures](docs/FIGURES.md) show the system map, evaluation pipeline, small-vs-medium results, policy replay, freeze gate, and engineering progress, all regenerated from committed evidence with `make figures`.

For clean-checkout validation, real-backend smoke checks, Compose/kind paths, figures, and Colab artifacts, follow [the Day 6 reproduction guide](docs/DAY6_REPRO.md).

## Repository layout

```text
src/jev_gateway/       Gateway API, transports, policy configuration, and evaluation package
tests/                 Offline gateway and evaluation checks
config/                Example environment profiles, without secrets
notebooks/             Separate Colab GPU serving experiment
scripts/               Explicit real checks and dataset preparation
docs/                  Architecture, methods, status, decisions, experiments, and notebook
evidence/              Committed sanitized engineering checks
runs/                  Ignored private evaluation outputs
data/                  Benchmark index and local source snapshots
```

The [Day 3 handoff](docs/DAY3_HANDOFF.md) gives routing, training, calibration, and comparison commands with current blockers. The [Colab notebook guide](notebooks/README.md) explains how to archive a committed source revision. A notebook runtime is not a permanent Mac service dependency. The [development guide](docs/DEVELOPMENT.md) explains module boundaries and testing. [Contributing](CONTRIBUTING.md) describes evidence and review expectations.

## Limitations

Generated code is scored only in a constrained Docker container; containers reduce risk but do not provide an absolute security boundary. The project split grouping catches exact case and whitespace variants, not semantic paraphrases. Current quality and cost reports are infrastructure, not completed three-tier benchmark results. Keep raw prompts, references, credentials, private audit exports, and model outputs out of public commits.

## Branch milestones

The `day-one` through `day-five` branches preserve the staged implementation. Changes are integrated through explicit local merge commits. See [the history guide](docs/HISTORY.md) for the graph and checkpoint lookup.
