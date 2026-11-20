# Day 8 handoff — 2026-11-20 America/Toronto

## Completed this session

- Medium `qwen2.5:7b` train math/choice: all 1,260 prompts, with 420 prior checkpoints reused and 840 new responses. Audit: `evidence/day8/medium-train-math-choice-audit-20261120.json`.
- Medium train code: all 240 prompts completed through Docker's isolated scorer. Audit: `evidence/day8/medium-train-code-audit-20261120.json`.
- Medium train aggregate: all 1,500 prompts across math, choice, and code, with 1,487 binary labels. Audit: `evidence/day8/medium-train-full-audit-20261120.json`.
- Medium validation math/choice: all 420 prompts, 420 new responses. Paired IDs and fingerprints match the small-tier validation rows. Audit: `evidence/day8/medium-validation-math-choice-audit-20261120.json`.
- Medium validation code: all 80 prompt IDs have records; 75 are binary-scored and 5 are parse errors. The saved `mbpp:401` response was re-scored as incorrect after the sandbox captured a Python `SyntaxError`; no model request was made. Across all medium validation tasks there are 494 binary scores. See `evidence/day8/medium-validation-code-audit-reclassified-20261120.json`.
- Corrected a false positive in the pre-test freeze audit: task-specific math/choice/code templates are now compared within their task. Six focused tests passed. The current audit reports no identity issues but keeps `ready_for_test=false` because required freeze fields and full coverage are still missing. See `evidence/day8/freeze-audit-current-20261120.json`.
- The held-out test was not touched. No paid API calls or external compute were used. No threshold was selected.

## Current validation exception and next research gate

Docker was initially unavailable because a stale UI process remained while its daemon was down. After terminating those stale UI/helper processes, `docker desktop start --detach` restored engine 29.6.2. The pinned ARM sandbox image is cached, and the medium train and validation code stages completed with no containers left running. Recovery evidence: `evidence/day8/docker-recovery-20261120.json` and `.txt`; the initial failure remains in `evidence/day8/mac-docker-blocker-20261120.json` and `.txt`.

The validation set has all 500 medium prompt IDs, paired with small on identical prompts/fingerprints. Initially, `mbpp:401` was blocked in three generations. A diagnostic run of the already saved code then produced `SyntaxError: invalid syntax`, which exposed a sandbox classification bug: Python reports this without the `Traceback` marker previously required for a code-crash status. The sandbox now recognizes `SyntaxError`; the saved response scores incorrect/0. The pre-correction record remains in the original immutable run files, and the supplemental correction is in `evidence/day8/medium-validation-code-mbpp401-rescore-20261120.json` and `.jsonl`. No further generation is needed for this row.

Before further local work, verify Docker and Ollama are still available:

```sh
docker info --format '{{.ServerVersion}} {{.Architecture}} {{.MemTotal}}'
ollama list
```

The math, choice, and code validation prompt IDs have been compared; 494 of 500 medium rows have binary scores, with six parse errors. Router thresholds, Jev probabilities, and cost-aware operating points have not been selected. The freeze audit is not ready for held-out evaluation: freeze fields are absent, tier coverage is incomplete, and frontier has no observations. The held-out test remains locked. Jev decision API access is separate and unconfigured.

Colab GPU/DistilBERT training, NVIDIA/vLLM, configured Jev/frontier comparisons, verification cascade, cache comparison, and sustained real serving/load runs remain outside today's executed work. Paid runs remain disabled.
