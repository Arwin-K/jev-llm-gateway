# Native Laya CLI setup

Laya runs in the `laya-gateway` Python process. There is no separate Laya model server and no decision HTTP endpoint. The CLI uses Laya for `auto` tier selection, then uses local Ollama for text generation.

## Install and configure

```bash
make laya-config
# Review .env.laya; this command never overwrites an existing file.
make setup-laya
```

`make setup-laya` installs the CLI, tests, and pinned `laya==0.5.2` extra into `.venv-laya` from `uv.lock`. Laya loads `typed-decisions` from its reviewed pinned revision on first use. This extra is intentionally incompatible with the separate `training` extra because Laya currently requires Transformers 5.x while the Colab training path uses 4.x. Use separate virtual environments for those workflows.

The example profile requests MPS. If PyTorch cannot use that accelerator, Laya falls back to CPU. `doctor` reports the requested and observed device. Device capability depends on the installed PyTorch build and host; it is not inferred from the configured value.

## Run local chat

Start Ollama locally and ensure the configured `qwen2.5:1.5b` and `qwen2.5:7b` models are installed. Then:

```bash
make doctor-local
make chat PROMPT='Explain how model routing works' MODEL=auto
```

`auto` makes a local in-process Laya decision between `small` and `medium`. `MODEL=small` or `MODEL=medium` bypasses Laya and selects that Ollama model explicitly. The generation call uses Ollama's loopback OpenAI-compatible endpoint; the application does not start or expose an HTTP server. No Laya API key, hosted decision call, or paid usage is required.

Configuration lives in `.env.laya` and uses `LAYA_MODEL`, `LAYA_DEVICE`, `LAYA_REVISION`, `LAYA_MAX_REQUESTS`, `LAYA_MAX_INPUT_UNITS`, plus `LAYA_GATEWAY_*` variables for local generation models and the CLI policy. `config/laya.env.example` contains the defaults. Do not place credentials or private prompts in committed config.

## Verification limits

The local checkpoint has loaded and answered one synthetic choice prompt on this machine. The doctor run found MPS unavailable and used CPU; Ollama was unreachable at that time. No project-specific routing accuracy, confidence calibration, throughput, or complete generated chat result has been established. Laya emits an upstream calibration warning for one `choice:11+` value; the application's route has two choices, but the model still requires domain-specific evaluation before its probabilities can be treated as calibrated.

The pinned package provenance and prior safety review are recorded in `evidence/day10/laya-source-review-20261122.txt`. The decision runtime does not send user text to an external service. The Ollama endpoint is configured to loopback by default; changing that URL can send prompts to the configured host.
