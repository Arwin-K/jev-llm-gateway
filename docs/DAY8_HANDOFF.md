# Day 8 handoff — 2026-11-20 America/Toronto

## Completed this session

- Medium `qwen2.5:7b` train math/choice: all 1,260 prompts, with 420 prior checkpoints reused and 840 new responses. Audit: `evidence/day8/medium-train-math-choice-audit-20261120.json`.
- Medium validation math/choice: all 420 prompts, 420 new responses. Paired IDs and fingerprints match the small-tier validation rows. Audit: `evidence/day8/medium-validation-math-choice-audit-20261120.json`.
- The held-out test was not touched. No paid API calls or external compute were used. No threshold was selected because medium code validation is still missing.

## Next: restore Docker, then score medium code

At session close, the Docker Desktop UI process remained open but the daemon socket was unavailable. `docker desktop start` reported that Docker was already running; `docker desktop status` could not retrieve status; and `docker desktop restart --timeout 120` failed to stop stale helper processes. No containers were running or started. Full observations are in `evidence/day8/mac-docker-blocker-20261120.json` and `.txt`.

On resume, check Docker Desktop's UI and restart the application if needed, then verify the daemon before running code tasks:

```sh
docker info --format '{{.ServerVersion}} {{.Architecture}} {{.MemTotal}}'
```

Start Ollama bound to loopback in another shell:

```sh
OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

Then run medium train code, with the pinned network-disabled evaluator image already cached:

```sh
PYTHONUNBUFFERED=1 ./.venv/bin/jev eval-run \
  --split train --task code --tier medium \
  --max-prompts 240 --max-requests 240 --max-tokens 307828 \
  --output-tokens 512 --concurrency 1 --retries 0 \
  2>&1 | tee evidence/day8/medium-train-code-20261120.txt
```

Afterward run medium validation code (80 prompts, token cap 103,736) under the same settings. Keep the held-out test locked. The math/choice validation audit is not enough to select a threshold or freeze a full-task comparison until code coverage is complete.

Colab GPU/DistilBERT training, NVIDIA/vLLM, configured Jev/frontier comparisons, verification cascade, cache comparison, and sustained real serving/load runs remain outside today's executed work. Paid runs remain disabled.
