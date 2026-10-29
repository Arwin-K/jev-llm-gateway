# Jev LLM Gateway

A reproducible study of three-tier language-model serving, answer quality, cost, and routing. The current application serves explicit `small`, `medium`, and configured `frontier` text-chat tiers. Its evaluation tools prepare a frozen 2,500-prompt benchmark across math, multiple choice, and coding tasks, record bounded attempts, score answers, and report coverage without hiding failures.

**Architecture:** [Implemented request and evaluation paths](docs/ARCHITECTURE.md) · **Reproduce:** [Evaluation workflow](docs/EVALUATION_WORKFLOW.md) · **Evidence:** [Experiment ledger](docs/EXPERIMENTS.md) · **Status:** [Verified and pending features](docs/FEATURE_STATUS.md)

## Research question

> How much answer quality can a cost-aware gateway retain while using smaller models when possible, and what latency and spending overhead do routing, verification, and caching introduce?

The gateway and evaluation foundation are implemented. Jev routing, a trained DistilBERT fallback, verifier cascades, semantic caching, deployment, and controlled load studies remain future stages. The [project plan](docs/PLAN.md) describes their scope; it is not a claim that they have run.

## Observed evidence

- Pinned source preparation selected **2,500 prompts**: 1,100 GSM8K math, 1,000 MMLU choice, and 400 sanitized MBPP code tasks. Project splits are 1,500 train, 500 validation, and 500 held-out test. The committed [manifest index](docs/day2-manifest-index.jsonl) contains IDs and hashes, not private prompt text or answers.
- The offline suite passed **36 tests** at the last recorded check. Controlled code fixtures passed, failed, crashed, and timed out inside the Docker evaluator as expected.
- A bounded real validation check attempted one prompt on each local tier. Both returned backend errors because Ollama was unreachable. Frontier was unconfigured. **No model answer quality, live serving latency, or paid API cost has been measured.** The project test split is unused.

See [the Day 2 handoff](docs/DAY2_HANDOFF.md) for the exact environment, commands, counts, and limitations.

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

`POST http://127.0.0.1:8080/v1/chat/completions` accepts text messages with `model` set to `small`, `medium`, or `frontier`, plus optional `stream`, `max_tokens`, and `temperature`. `model=auto`, tools, image, and audio inputs are not implemented. `/healthz` checks the process; `/readyz` does not prove a model is loaded. `jev doctor` checks backend availability. The frontier tier stays disabled without a model, key, current rates, and positive request, token, and USD caps. These application-side limits are not provider spending controls.

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

The [Colab notebook guide](notebooks/README.md) explains how to archive a committed source revision. A notebook runtime is not a permanent Mac service dependency. The [development guide](docs/DEVELOPMENT.md) explains module boundaries and testing. [Contributing](CONTRIBUTING.md) describes evidence and review expectations.

## Limitations

Generated code is scored only in a constrained Docker container; containers reduce risk but do not provide an absolute security boundary. The project split grouping catches exact case and whitespace variants, not semantic paraphrases. Current quality and cost reports are infrastructure, not completed three-tier benchmark results. Keep raw prompts, references, credentials, private audit exports, and model outputs out of public commits.
