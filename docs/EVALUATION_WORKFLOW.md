# Evaluation workflow

Run commands from the repository root. These steps separate offline preparation, real generation, private audit, and serving measurements.

## Prepare pinned sources and inspect splits

```bash
uv sync --locked --extra evaluation --extra test
uv run pytest -q
uv run jev eval-prepare
uv run jev doctor
```

`eval-prepare` downloads revision-specific GSM8K and MMLU Parquet files plus Google Research's sanitized MBPP JSON, then writes `runs/day2-manifest.jsonl`. Its tracked companion, `docs/day2-manifest-index.jsonl`, contains IDs, split labels, group hashes, and revisions only. The initial preparation observed 7,473 GSM8K, 14,042 MMLU, and 427 MBPP rows and selected 1,100/1,000/400 prompts. The project split is 1,500 train, 500 validation, and 500 held-out test. Re-running preparation refuses to replace an existing full manifest with different content. The source pools and protocol differences are described in [dataset notes](DAY2_DATASETS.md).

The benchmark's source split and the project's split are distinct. The project currently draws from GSM8K's official train and MMLU's official test pools. A project validation row from MMLU is not an official MMLU validation row. Exact case/whitespace-normalized prompt variants are grouped; semantic paraphrases are not detected. The evaluation CLI offers train and validation only. Keep the project test unused until the final policy freeze.

## Collect a bounded development subset

Start with one prompt per tier. Check `doctor` first. An unavailable backend produces a real error record and no scored answer.

```bash
uv run jev eval-run --split validation --tier small --tier medium --max-prompts 1 --max-requests 2 --max-tokens 10000 --output-tokens 32 --concurrency 1
```

The command prints a unique ignored `runs/day2-run-*.jsonl` path. Request and token caps apply across tier attempts, including retries. `--retries` is at most 3. `--concurrency` bounds simultaneous calls. Completed compatible results are checkpointed under `runs/day2-checkpoints/`; retries and failures remain visible in the run file. Reuse preserves the original run identity and timestamps. A changed prompt, template, model, backend, or generation setting prevents reuse. A failed evaluation can be retried on a later run.

For a frontier run, configure `JEV_FRONTIER_MODEL`, `JEV_FRONTIER_API_KEY`, positive `JEV_FRONTIER_MAX_REQUESTS`, `JEV_FRONTIER_MAX_TOKENS`, `JEV_FRONTIER_MAX_USD`, and current input/output rate environment values. Then pass `--tier frontier --paid-enabled --max-usd <positive-cap> --rate-file <private-json>`. The rate file is an array of objects with `model`, `input_usd_per_million`, `output_usd_per_million`, `effective_date` (ISO date), and `source_url`. Use the provider's current published rate page. Do not commit credentials, rate assumptions, raw answers, or private audit exports. Local application guards do not replace provider account spending controls.

## Report and audit an explicit run

```bash
uv run jev eval-report --run runs/<printed-day2-run-file>.jsonl --split validation
uv run jev eval-audit --run runs/<printed-day2-run-file>.jsonl --split validation
```

Reports compare observed prompt/tier pairs with the entire selected split. Scored accuracy uses correct/(correct+incorrect), while correct-completion rate uses correct/all expected prompts. Missing rows and failures remain visible. Overall rows weight tasks by selected prompt count. The audit CSV is private, includes reference answers or tests, and labels every exported row `pending_human_review`. Exporting it does not mean anyone reviewed or corrected it. The exporter takes up to 40 observed development rows per task, where available. [Record and metric definitions](DAY2_SCHEMA.md) describe outcomes, costs, and labels.

## Measure serving separately

```bash
uv run jev eval-serving --tier small --prompt 'Say hello.' --requests 3 --arrival-interval 1 --concurrency 1 --output-tokens 32 --warmup 1 --cache-state off --placement mac --model-condition unverified
```

This sends streaming traffic and writes an ignored `runs/day2-serving-*.json`. It records scheduled and achieved starts, first visible text, end-to-end latency, errors, and provider output tokens when available. It does not score answer quality. Do not label a run cold or warm without checking model state. No serving baseline has been measured against a live model yet; [serving definitions](DAY2_SERVING.md) give the formulas.

## Known blockers and next step

The last real `doctor` check found both configured Ollama tags unreachable and frontier unconfigured. One validation prompt attempted on small and medium returned two backend errors. Docker code-scoring fixtures did run successfully. Start Ollama, verify actual model identities and memory, then run a small real train/validation subset before increasing caps. Human audit and complete three-tier training observations are needed before hindsight labels can support Day 3 routing work. See [the handoff](DAY2_HANDOFF.md) for exact observed evidence.
