# Start here

The repository contains a working explicit-tier text gateway and evaluation tooling. The [README](README.md) has the Mac quickstart. The [architecture guide](docs/ARCHITECTURE.md) explains the request and evaluation paths, and the [evaluation workflow](docs/EVALUATION_WORKFLOW.md) gives bounded commands and output locations.

## Current state

- The gateway accepts `small`, `medium`, and configured `frontier` text-chat requests. Streaming, diagnostics, traces, and process-local frontier admission controls are implemented.
- A pinned 2,500-prompt benchmark index, private prompt manifest, task scorers, Docker code evaluator, checkpointing, quality reports, and serving workload runner are implemented.
- The last observed Mac check found both Ollama tiers unreachable and frontier unconfigured. No model answer quality or serving latency has been measured. The project test split has not been used.
- The Colab notebook is prepared but has not run on a GPU. Jev routing, DistilBERT training, verifier cascades, semantic caching, deployment, load tests, and the final report remain planned work.

## First actions

1. From `llm_gateway_full_project`, run `uv sync --locked --extra test` and `uv run pytest -q`.
2. Install and start native Ollama, then run `uv run jev doctor`. Download candidate models only after checking available disk and memory.
3. Read [the evaluation workflow](docs/EVALUATION_WORKFLOW.md) before running a benchmark. Paid calls require explicit credentials, rates, and positive caps.

The [setup and build guide](SETUP_AND_BUILD_GUIDE.md) and [checkpoint plan](docs/COMMIT_PLAN.md) record the original project plan. They describe requested work, including components that have not been implemented. [Feature status](docs/FEATURE_STATUS.md) and [experiment evidence](docs/EXPERIMENTS.md) describe what has actually been checked.
