# Day 8 handoff — 2026-11-20 America/Toronto

## Completed this session

- Medium `qwen2.5:7b` train math/choice: all 1,260 prompts, with 420 prior checkpoints reused and 840 new responses. Audit: `evidence/day8/medium-train-math-choice-audit-20261120.json`.
- Medium train code: all 240 prompts completed through Docker's isolated scorer. Audit: `evidence/day8/medium-train-code-audit-20261120.json`.
- Medium train aggregate: all 1,500 prompts across math, choice, and code, with 1,487 binary labels. Audit: `evidence/day8/medium-train-full-audit-20261120.json`.
- Medium validation math/choice: all 420 prompts, 420 new responses. Paired IDs and fingerprints match the small-tier validation rows. Audit: `evidence/day8/medium-validation-math-choice-audit-20261120.json`.
- The held-out test was not touched. No paid API calls or external compute were used. No threshold was selected because medium code validation is still missing.

## Current validation exception and next research gate

Docker was initially unavailable because a stale UI process remained while its daemon was down. After terminating those stale UI/helper processes, `docker desktop start --detach` restored engine 29.6.2. The pinned ARM sandbox image is cached, and the medium train and validation code stages completed with no containers left running. Recovery evidence: `evidence/day8/docker-recovery-20261120.json` and `.txt`; the initial failure remains in `evidence/day8/mac-docker-blocker-20261120.json` and `.txt`.

The validation set now has all 500 prompt IDs for medium, paired with small on identical prompts/fingerprints. One row remains unscored: `mbpp:401` produced `blocked/environment_error` in the initial run and two exact prompt-ID recovery invocations. A separate trivial call to the project sandbox passed, so the Docker daemon was generally available, but that does not diagnose the failing benchmark execution. Raw outputs and the preserved blocked record are documented in `evidence/day8/medium-validation-code-audit-20261120.json` and `evidence/day8/medium-validation-code-sandbox-sanity-20261120.txt`. Do not relabel it as correct/incorrect or repeat generation without new diagnostic evidence.

Before further local work, verify Docker and Ollama are still available:

```sh
docker info --format '{{.ServerVersion}} {{.Architecture}} {{.MemTotal}}'
ollama list
```

The math, choice, and code validation prompt IDs have been compared, but a fully scored local comparison still has the one blocked code row. Router thresholds, Jev probabilities, and cost-aware operating points have not been selected. The held-out test remains locked. Jev decision API access is separate and unconfigured.

Colab GPU/DistilBERT training, NVIDIA/vLLM, configured Jev/frontier comparisons, verification cascade, cache comparison, and sustained real serving/load runs remain outside today's executed work. Paid runs remain disabled.
