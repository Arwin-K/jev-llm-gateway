# Reproduce this checkpoint

## Clean Mac checkout

Use Python 3.11–3.14. A fresh checkout needs network access to install Python dependencies and, for the full evaluation, to download pinned source datasets. The application itself has no CUDA dependency.

```bash
git clone <repository-location> jev-gateway
cd jev-gateway
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/jev doctor
.venv/bin/pytest -q
```

`doctor` reports whether native Ollama is reachable and whether frontier credentials/rates are configured. It does not load a model. For a bounded real answer, install native Ollama, pull the configured `qwen2.5:1.5b` tag, verify `doctor` reports it available, run `.venv/bin/jev serve`, and in another terminal run `.venv/bin/jev smoke --tier small`. Initial downloads and model residency are environment-specific. Do not infer a quality result from this smoke check.

To prepare the private 2,500-prompt manifest, install the evaluation extra and follow [the evaluation workflow](EVALUATION_WORKFLOW.md):

```bash
.venv/bin/python -m pip install -e '.[evaluation]'
.venv/bin/jev eval-prepare
```

`runs/` and `data/day2_sources/` are ignored and are **not** in a clean clone. The public manifest index is only IDs and hashes. Recreate private data using the pinned preparation command; do not expect the evidence audit in this branch to contain original prompts or answers. The test split remains locked while scored train/validation coverage and policy freeze are incomplete.

## Local deployment and experimental modes

`docker compose up -d --build` starts the loopback gateway and monitoring stack. `docker compose down` stops it without erasing monitoring volumes. The [Day 5 handoff](DAY5_HANDOFF.md) has kind creation/deletion and load commands; the default local profiles do not provision external compute. The [Day 4 handoff](DAY4_HANDOFF.md) gives exact `route_first`, `cascade`, `hybrid`, verified-cache, and experimental similarity-only configuration. These modes need their respective local models, artifacts, and optional positive paid gates. Do not enable paid execution without credentials, sourced rates, and explicit positive request/token/USD caps.

## Colab and figures

`notebooks/README.md` explains how to archive a committed revision and verify its SHA-256 in Colab. `notebooks/day6_nvidia.ipynb` records actual GPU/software identity, runs a bounded synthetic workload on loopback vLLM, and optionally profiles a separate run. Save its JSON, server log, and `.nsys-rep` outside the ephemeral notebook before disconnecting. The current checkpoint has **no executed NVIDIA run**.

The available coverage figure is regenerated from its raw audit:

```bash
.venv/bin/python -m jev_gateway.day6.figures \
  --freeze-audit evidence/day6/freeze-audit-20261101.json \
  --output runs/day6-coverage-local.svg
```

Day 3 calibration and comparison commands are in [the Day 3 handoff](DAY3_HANDOFF.md); the Day 4 cache report command is in [the Day 4 handoff](DAY4_HANDOFF.md). They currently produce insufficient-data and zero-coverage reports, respectively, because real model observations are missing. The final quality/cost/latency plots become meaningful only after complete compatible raw records exist.
