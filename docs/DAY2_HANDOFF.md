# Day 2 handoff — 2026-10-28, America/Toronto

The committed index `day2-manifest-index.jsonl` contains 2,500 source IDs, group hashes, project splits, dataset revisions, and template fingerprints. It has no prompt text, answers, or MBPP tests. The corresponding full private prompt manifest is `runs/day2-manifest.jsonl`; regenerate it with `jev eval-prepare` after installing the optional `evaluation` extra. Source snapshots are ignored under `data/day2_sources/`. Revisions are GSM8K `740312add88f781978c0658806c59bc2815b9866`, MMLU `c30699e8356da336a370243923dbaf21066bb9fe`, and Google Research MBPP `1ae1fded5c616deb6b4652818588577e8fca0f06`. GSM8K and MMLU are downloaded by revision-specific Parquet URLs; MBPP uses the commit-specific sanitized JSON. The Hugging Face row API returned HTTP 429 during the first acquisition attempt, so direct pinned files replaced it.

The target has 1,100 math, 1,000 choice, and 400 code prompts. By project split it has 1,500 training, 500 validation, and 500 held-out test prompts. All 2,500 selected group hashes are distinct. The project test gate rejects ordinary loads and all evaluation CLI commands accept only train/validation. This manifest uses GSM8K's official train and MMLU's official test as source pools, then creates project splits; the split names should not be confused with official benchmark evaluations. The exact normalized-prompt grouping does not detect semantic paraphrases or source contamination.

The Docker Engine was reachable at version 29.6.2. `python:3.12.7-slim-bookworm` resolved to digest `sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d`. Controlled code fixtures returned `passed`, `failed_tests`, `crashed`, and `timeout` as expected, and no `jev-eval-` container remained running. These fixtures prove the local execution path, not absolute isolation against adversarial code.

`jev doctor` outside the restricted sandbox found `qwen2.5:1.5b` and `qwen2.5:7b` configured but unreachable (`ConnectError`); these are configured tags, not verified loaded model identities. Frontier was unconfigured. One real, bounded validation prompt was attempted on each local tier with a two-request cap, 10,000 reserved-token cap, and 32 output-token cap. Both attempts returned `backend_error`; there were zero scored completions, zero paid calls, and no training or validation quality measurement. The report correctly shows 1 observed backend failure and 499 missing validation results per local tier, and 500 missing frontier results. A private audit export contains two pending-review rows for the same math prompt across tiers; no human review occurred. No held-out test prompt was sent.

The full offline suite returned 36 passed and one third-party Starlette deprecation warning. Cost, latency, throughput, and oracle accuracy remain unmeasured for real model answers. The next Day 3 prerequisites are to install/start Ollama, pull and verify both models, acquire bounded three-tier training/validation answers with a configured sourced rate file and paid approval if frontier is used, and conduct the pending human scoring audit. Labels must be derived only from complete training observations. Configured limits are application-side guards and do not enforce provider account caps.

## Commands

```bash
uv sync --locked --extra evaluation --extra test
uv run jev eval-prepare
uv run jev doctor
uv run jev eval-run --split validation --tier small --tier medium --max-prompts 1 --max-requests 2 --max-tokens 10000 --output-tokens 32 --concurrency 1
uv run jev eval-report --run runs/<printed-day2-run-file>.jsonl --split validation
uv run jev eval-audit --run runs/<printed-day2-run-file>.jsonl --split validation
uv run jev eval-serving --tier small --prompt 'Say hello.' --requests 3 --arrival-interval 1 --concurrency 1 --output-tokens 32 --warmup 1 --cache-state off --placement mac --model-condition unverified
```

`eval-run` also accepts `--tier frontier --paid-enabled --max-usd ... --rate-file ...` only with a configured key, model, positive environment caps, and a dated sourced JSON rate file. The rate file is an array of objects with `model`, `input_usd_per_million`, `output_usd_per_million`, `effective_date` (ISO date), and `source_url`. Real prices must come from the chosen provider's current published rate page. Private run outputs under `runs/` are ignored by Git. Do not use the serving command on frontier without explicit paid controls.
