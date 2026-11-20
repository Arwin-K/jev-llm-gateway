# Day 7 handoff — 2026-11-19 America/Toronto

## Resume the medium-tier train run

The medium `qwen2.5:7b` train run is paused at 420 saved math checkpoints (409 correct, 10 incorrect, 1 parse error); no choice prompt was reached. The evaluation runner and Ollama server are stopped. The checkpoint JSON files and raw answers remain in ignored `runs/day2-checkpoints/`. Do not treat this partial run as the completed medium comparison. See `evidence/day7/medium-train-stop-audit-20261119.json` for the run ID, model digest, caps, and shutdown evidence.

From the repository root, start Ollama in one shell, bound to loopback:

```sh
OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

In another shell, resume with the same split, tasks, model, settings, and caps. Checkpointed prompt IDs will be reused. Unbuffered output makes the command summary and any interruption visible in the saved log.

```sh
PYTHONUNBUFFERED=1 ./.venv/bin/jev eval-run \
  --split train \
  --task math --task choice \
  --tier medium \
  --max-prompts 1260 \
  --max-requests 1260 \
  --max-tokens 2887016 \
  --output-tokens 512 \
  --concurrency 1 \
  --retries 0 \
  2>&1 | tee evidence/day7/medium-train-math-choice-resume-20261120.txt
```

The 1,260-request/2,887,016-token ceilings are the original positive local run caps; no paid calls are involved. Keep the held-out test untouched.

## Remaining local comparison steps

After train math/choice completes, collect medium train code (240 prompts, token cap 307,828) and medium validation math/choice (420 prompts, token cap 961,536). Medium validation code has 80 prompts and token cap 103,736. Code tasks need Docker Desktop for the network-disabled sandbox; start it only for those tasks and watch memory while the 7B model is resident. Use concurrency one and zero retries as in the recorded train run. The small-tier full-train evidence and current medium partial results are documented in `docs/STATUS.md` and `docs/EXPERIMENTS.md`.

Colab DistilBERT training, NVIDIA/vLLM experiments, Jev/frontier API comparisons, cascades, calibration, semantic-cache comparisons, and sustained real serving/load tests still require the separately documented GPU/provider/service setup. Paid runs remain disabled.
