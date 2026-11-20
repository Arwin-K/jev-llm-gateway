# Day 8 handoff — 2026-11-20 America/Toronto

## Completed this session

- Medium `qwen2.5:7b` train math/choice: all 1,260 prompts, with 420 prior checkpoints reused and 840 new responses. Audit: `evidence/day8/medium-train-math-choice-audit-20261120.json`.
- Medium train code: all 240 prompts completed through Docker's isolated scorer. Audit: `evidence/day8/medium-train-code-audit-20261120.json`.
- Medium train aggregate: all 1,500 prompts across math, choice, and code, with 1,487 binary labels. Audit: `evidence/day8/medium-train-full-audit-20261120.json`.
- Medium validation math/choice: all 420 prompts, 420 new responses. Paired IDs and fingerprints match the small-tier validation rows. Audit: `evidence/day8/medium-validation-math-choice-audit-20261120.json`.
- The held-out test was not touched. No paid API calls or external compute were used. No threshold was selected because medium code validation is still missing.

## Next: score medium validation code

Docker was initially unavailable because a stale UI process remained while its daemon was down. After terminating those stale UI/helper processes, `docker desktop start --detach` restored engine 29.6.2. The pinned ARM sandbox image is cached, and the medium train code evaluation completed with no containers left running. Recovery evidence: `evidence/day8/docker-recovery-20261120.json` and `.txt`; the initial failure remains in `evidence/day8/mac-docker-blocker-20261120.json` and `.txt`.

Before the validation code task, verify Docker is still healthy:

```sh
docker info --format '{{.ServerVersion}} {{.Architecture}} {{.MemTotal}}'
```

Ensure Ollama is listening on loopback in another shell (the server's model keep-alive may have unloaded the 7B weights):

```sh
OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

Then run medium validation code (80 prompts, 103,736-token cap) with the same single-request/zero-retry settings:

```sh
PYTHONUNBUFFERED=1 ./.venv/bin/jev eval-run \
  --split validation --task code --tier medium \
  --max-prompts 80 --max-requests 80 --max-tokens 103736 \
  --output-tokens 512 --concurrency 1 --retries 0 \
  2>&1 | tee evidence/day8/medium-validation-code-20261120.txt
```

Keep the held-out test locked. Once this stage completes, validation will cover math, choice, and code for both local tiers, allowing a full local-tier comparison. Jev decision API access is still separate and unconfigured.

Colab GPU/DistilBERT training, NVIDIA/vLLM, configured Jev/frontier comparisons, verification cascade, cache comparison, and sustained real serving/load runs remain outside today's executed work. Paid runs remain disabled.
