# Development and verification

## Install and test

```bash
uv sync --locked --extra test
uv run pytest -q
```

Add `--extra evaluation` only when preparing pinned Parquet datasets. Core gateway installation does not include Torch, CUDA, vLLM, or the Parquet reader. The last full offline suite passed 36 tests with one third-party Starlette deprecation warning. Offline tests use controlled transports and fixtures; they do not prove a real model is loaded or that a Colab GPU run succeeded. Live checks are explicit commands in [the evaluation workflow](EVALUATION_WORKFLOW.md).

## Code layout

| Path | Responsibility |
| --- | --- |
| `src/jev_gateway/api.py` | FastAPI chat contract, explicit dispatch, streaming, health endpoints |
| `config.py`, `budget.py` | Environment validation and frontier admission limits |
| `transport.py`, `ollama.py`, `tracing.py`, `diagnostics.py` | HTTP forwarding, local model checks, traces, doctor/smoke |
| `evaluation/datasets.py`, `manifest.py`, `records.py` | Pinned sources, frozen splits, immutable observations |
| `evaluation/scoring.py`, `sandbox.py`, `audit.py` | Task scoring, Docker-only code execution, private review export |
| `evaluation/runner.py`, `checkpoint.py`, `commands.py` | Bounded collection, compatible resumption, CLI |
| `evaluation/oracle.py`, `cost.py`, `report.py` | Hindsight training labels, cost states, quality denominators |
| `evaluation/serving.py`, `latency.py` | Client workload and latency/throughput summaries |
| `tests/`, `tests/evaluation/` | Offline contract, boundary, failure, and metric checks |
| `notebooks/` | Separate Colab GPU serving experiment; not a Mac service |

## Extending the evaluation

Keep each dataset row's source ID, revision, reference provenance, and exact prompt template. Change the template fingerprint when formatting changes. Keep source answers and coding tests out of generation prompts unless the protocol explicitly calls for them. Add scorer tests for ambiguous and malformed responses, not only correct examples. A backend exception, a scorer exception, and a wrong answer must remain distinct records.

When adding retries or another billable stage, record every attempt's usage and status. Reserve budget before concurrent calls and reconcile reported usage afterward. Keep actual provider charges separate from sourced estimates and from provisioned self-hosted capacity. Extend reports from saved records, with explicit missing evaluations and denominators; do not compute a p95 by adding stage p95 values.

A local Docker fixture is appropriate for checking code-scoring behavior. Generated model code must never run directly on the host as a fallback. A real model benchmark requires a reachable backend, its actual identity, a bounded workload, and a saved raw run. Do not insert mocked answers into a real run to fill missing coverage.

## Current evidence

[Engineering status](STATUS.md), [environment](ENVIRONMENT.md), [experiments](EXPERIMENTS.md), and [decisions](DECISIONS.md) are the evidence ledger. [Feature status](FEATURE_STATUS.md) separates implemented and pending components. The original [checkpoint plan](COMMIT_PLAN.md) is a plan, not proof of completion. The [history guide](HISTORY.md) explains descriptive commit subjects and checkpoint trailers.
