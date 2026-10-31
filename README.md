# Jev LLM Gateway

A reproducible study of three-tier language-model serving, answer quality, cost, and routing. The current application serves explicit `small`, `medium`, and configured `frontier` text-chat tiers. Its evaluation tools prepare a frozen 2,500-prompt benchmark across math, multiple choice, and coding tasks, record bounded attempts, score answers, and report coverage without hiding failures.

**Architecture:** [Implemented request and evaluation paths](docs/ARCHITECTURE.md) · **Reproduce:** [Evaluation workflow](docs/EVALUATION_WORKFLOW.md) · **Evidence:** [Experiment ledger](docs/EXPERIMENTS.md) · **Status:** [Verified and pending features](docs/FEATURE_STATUS.md)

## Research question

> How much answer quality can a cost-aware gateway retain while using smaller models when possible, and what latency and spending overhead do routing, verification, and caching introduce?

The gateway now supports automatic policy selection, typed Jev choice and success questions, a prompted small-model comparison, fixed and seeded-random baselines, and a local Strands typed-server adapter. The DistilBERT trainer and artifact-gated fallback are implemented but no trained artifact exists because real three-tier labels are absent. Optional verifier cascades and scoped semantic caching are implemented and offline-tested; their real model and cache performance remains unmeasured. Day 5 adds an ARM container, local Compose monitoring, a bounded load runner, and a tested kind deployment. Sustained real inference load remains pending because native Ollama is unreachable. The [project plan](docs/PLAN.md) describes the remaining scope.

## Observed evidence

- Pinned source preparation selected **2,500 prompts**: 1,100 GSM8K math, 1,000 MMLU choice, and 400 sanitized MBPP code tasks. Project splits are 1,500 train, 500 validation, and 500 held-out test. The committed [manifest index](docs/day2-manifest-index.jsonl) contains IDs and hashes, not private prompt text or answers.
- The Day 5 offline suite passed **119 tests**. The ARM gateway image served health checks; Prometheus scraped it; Grafana provisioned 14 panels. A bounded in-cluster pod replacement returned 39 HTTP 200 responses and one connection error across 40 API requests. This was application traffic without generation.
- A bounded real validation check attempted one prompt on each local tier. Both returned backend errors because Ollama was unreachable. Frontier was unconfigured. **No model answer quality, live serving latency, or paid API cost has been measured.** The project test split is unused.

See [the Day 5 handoff](docs/DAY5_HANDOFF.md) for deployment commands, actual checks, and limitations. [Day 4](docs/DAY4_HANDOFF.md) covers verification and cache behavior; [Day 2](docs/DAY2_HANDOFF.md) records source and evaluator preparation.

## Quick start on Mac

Install [uv](https://docs.astral.sh/uv/) and [native Ollama](https://docs.ollama.com/macos). Review disk space and available memory before pulling models.

```bash
uv sync --locked --extra test
uv run pytest -q
uv run jev doctor
```

The configured candidate tags are `qwen2.5:1.5b` and `qwen2.5:7b`. Once Ollama is running and the models are installed, start the gateway and make an explicit-tier request:

```bash
uv run jev serve
# In another terminal:
uv run jev smoke --tier small
```

`POST http://127.0.0.1:8080/v1/chat/completions` accepts text messages with `model` set to `small`, `medium`, `frontier`, or `auto`, plus optional `stream`, `max_tokens`, and `temperature`. `model=auto` uses the configured router and returns 503 when neither it nor a compatible trained fallback can decide. Tools, image, and audio inputs are not implemented. `/healthz` checks the process; `/readyz` does not prove a model is loaded. `jev doctor` checks backend availability. The frontier tier stays disabled without a model, key, current rates, and positive request, token, and USD caps. These application-side limits are not provider spending controls.

Optional `execution_mode` (`route_first`, `cascade`, `hybrid`) and `cache_mode` (`verified`, experimental `similarity_only`) fields enable Day 4 buffered paths. They require explicit configuration; the default remains `standard` with cache `off`. See [Day 4 configuration and failure semantics](docs/DAY4_HANDOFF.md).

For local deployment, `docker compose up -d --build` starts the gateway, Prometheus, and Grafana on loopback ports 8080, 9090, and 3000. `/metrics` exposes bounded aggregate series; detailed request stages stay in secret-free traces. The default Compose and kind profiles keep generation in native Ollama and paid calls disabled. Run `docker compose down` to stop without deleting monitoring data. The [Day 5 runbook](docs/DAY5_HANDOFF.md) explains backend connectivity, kind, load scenarios, and what readiness actually checks.

## Reproduce evaluation preparation

```bash
uv sync --locked --extra evaluation --extra test
uv run jev eval-prepare
uv run jev eval-run --split validation --tier small --tier medium --max-prompts 1 --max-requests 2 --max-tokens 10000 --output-tokens 32 --concurrency 1
```

The runner prints a private run-file path for `jev eval-report` and `jev eval-audit`. Normal offline checks do not download datasets or call paid APIs. [The evaluation workflow](docs/EVALUATION_WORKFLOW.md) covers resumption, audits, sourced rates, held-out test policy, and serving baselines.

## Repository layout

```text
src/jev_gateway/       Gateway API, transports, policy configuration, and evaluation package
tests/                 Offline gateway and evaluation checks
config/                Example environment profiles, without secrets
notebooks/             Separate Colab GPU serving experiment
scripts/               Explicit real checks and dataset preparation
docs/                  Architecture, methods, status, decisions, experiments, and notebook
evidence/              Committed sanitized engineering checks
prompts/               Original staged project instructions
runs/, data/           Ignored private outputs and source snapshots
```

The [Day 3 handoff](docs/DAY3_HANDOFF.md) gives routing, training, calibration, and comparison commands with current blockers. The [Colab notebook guide](notebooks/README.md) explains how to archive a committed source revision. A notebook runtime is not a permanent Mac service dependency. The [development guide](docs/DEVELOPMENT.md) explains module boundaries and testing. [Contributing](CONTRIBUTING.md) describes evidence and review expectations.

## Limitations

Generated code is scored only in a constrained Docker container; containers reduce risk but do not provide an absolute security boundary. The project split grouping catches exact case and whitespace variants, not semantic paraphrases. Current quality and cost reports are infrastructure, not completed three-tier benchmark results. Keep raw prompts, references, credentials, private audit exports, and model outputs out of public commits.

## Branch milestones

The `day-one` through `day-five` branches preserve the staged implementation. Changes are integrated through explicit local merge commits. See [the history guide](docs/HISTORY.md) for the graph and checkpoint lookup.
