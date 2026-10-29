# Experiment evidence

No project experiments have been executed while preparing this pack. Link each actual experiment's hypothesis, source revision/dirty snapshot, environment, model identity, controls, commands, raw outputs, repetitions, observations, and limitations. Keep raw data immutable and distinguish Mac, Colab, mock, replayed, and estimated results.

## Day 1 engineering checks — 2026-10-27 America/Toronto

Run `mac-day1-offline-20261027-1309`: Python 3.14.5, macOS 26.5.2, local project venv; `.venv/bin/pytest -q` returned 15 passed, one Starlette deprecation warning in 0.23 seconds. Mock HTTP transports supplied backend responses; these are not model experiments.

Run `mac-day1-offline-20261027-1314`: after `uv sync --locked`, `uv run --extra test pytest -q` returned 15 passed, one warning in 0.16 seconds. Raw output: `evidence/day1/mac-offline-20261027-1314.txt`. Doctor's raw JSON is `evidence/day1/mac-doctor-20261027-1314.json` (exit status 1 because models are unavailable).

Run `mac-day1-health-20261027-1310`: a brief real localhost gateway process returned HTTP 200 and `{"status":"ok"}` from `/healthz`. Initial default-sandbox bind failed with EPERM; an authorized elevated loopback run succeeded. No backend was called.

Run `mac-day1-doctor-20261027-1308`: both Ollama tiers returned `ConnectError`; frontier was disabled. Colab and paid-provider runs: none.

Official sources consulted 2026-10-27: https://docs.ollama.com/macos, https://docs.ollama.com/api/openai-compatibility, https://ollama.com/library/qwen2.5, https://docs.vllm.ai/en/stable/getting_started/installation/gpu/, https://docs.astral.sh/uv/. The Ollama listing supplied download-size candidates, not runtime memory measurements.


## Day 2 engineering evidence — 2026-10-28 America/Toronto

Source preparation: `scripts/prepare_day2.py` retrieved pinned source snapshots: GSM8K 7,473 rows, MMLU 14,042 rows, sanitized MBPP 427 rows. It selected 2,500 source prompts with per-task 60/20/20 project splits. The first viewer-API attempt failed with HTTP 429; the direct pinned-file path succeeded. This is dataset preparation, not inference.

Sandbox check: Docker Engine 29.6.2, `python:3.12.7-slim-bookworm` digest in `DAY2_HANDOFF.md`. Controlled fixtures produced `passed` (exit 0), `failed_tests` (exit 1), `crashed` (exit 1), and `timeout` (no exit code); a post-check `docker ps` showed no evaluation containers. These fixture programs were run inside Docker only.

Run `day2-validation-8debb816`: `.venv/bin/jev eval-run --split validation --tier small --tier medium --max-prompts 1 --max-requests 2 --max-tokens 10000 --output-tokens 32 --concurrency 1`. Two real network attempts returned backend errors because Ollama was unreachable. The ignored raw result is `runs/day2-run-8debb816c7474f559ab5197df9c1fea6.jsonl`. `eval-report` showed 1 observed and 499 missing per local tier; frontier had 0 observed and 500 missing. `eval-audit` exported two pending rows, with no human review. No paid or test-split calls occurred. The full offline suite: 36 passed, one Starlette deprecation warning, 0.24 seconds. Model quality and serving performance remain unmeasured.

## Day 3 block 1 — 2026-10-29 America/Toronto

The existing `runs/day2-run-8debb816c7474f559ab5197df9c1fea6.jsonl` was inspected locally: two validation records, both `backend_error`, and no train records. No training labels, model training, or live router selections were produced. Focused routing contract, baseline, and training-data tests used fixtures only.

## Day 3 validation replay — 2026-10-29 America/Toronto

`python -m jev_gateway.routing.comparison --run runs/day2-run-8debb816c7474f559ab5197df9c1fea6.jsonl --output runs/day3-validation-comparison-20261029.json` produced a private JSON report and SVG (`runs/day3-validation-comparison-20261029.svg`). It enumerated ten planned policies but plotted zero cost-quality points. Small and medium fixed baselines each matched one backend-error result and lacked 499 results; frontier lacked all 500. The seeded random baseline matched one backend error and lacked 499 results. No router had saved real selections or scored answers. This is offline replay, not a live request or end-to-end timing result. The empty plot is the correct evidence state, not a quality comparison.

## Day 3 local decision-only benchmark — 2026-10-29 America/Toronto

Run `e6f85069cc9d4bd3a5545766cb7dc0a6` is preserved in ignored `runs/day3-routing-benchmark-e6f85069cc9d4bd3a5545766cb7dc0a6.json`. On the execution Mac, 10 warm-ups and 100 sequential measured calls per available local baseline used one short prompt and distinct request IDs. Always-small p50/p95 were 0.001583/0.001667 ms; always-medium 0.001583/0.001667 ms; seeded-random 0.002188/0.002750 ms. All 300 measured decisions succeeded. These microsecond-scale Python policy timings are subject to timer and scheduling noise; no model loaded, network call, generation, or full request was measured. Classifier, Jev, prompted, and Strands timings remain pending access.
