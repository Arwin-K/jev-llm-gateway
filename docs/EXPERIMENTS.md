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

Day 3 final offline check: `.venv/bin/pytest -q` returned 69 passed, one Starlette deprecation warning, 0.40 seconds. Sanitized raw output is `evidence/day3/mac-offline-20261029.txt`. `jev doctor` returned both local tiers unavailable with `ConnectError` and frontier unconfigured. No inference or training job is running.

Day 3 post-merge command check (decision only): `.venv/bin/python -m jev_gateway.routing.evaluate --policy always-small --max-prompts 1 --max-decisions 1 --output runs/day3-decisions-fixed-small-20261029.jsonl` recorded one deterministic local selection and zero errors. It did not call Ollama or generate an answer. Calibration reporting against the existing two-error Day 2 run returned `insufficient_data`, count 0, with no SVG; the private report is `runs/day3-calibration-fixed-small-20261029.json`. A comparison replay accepted the saved decision file. No live router was contacted.

The first replay with the saved fixed-policy selection exposed a duplicate-key error: replay had already generated that same baseline prompt. The comparison loader now replaces the generated baseline row with the saved decision for that policy/prompt and rejects duplicate supplied rows. The rerun wrote `runs/day3-validation-comparison-3bea4651658849c281cc93880b2c82e9.json` and still plotted zero points. This was a real workflow bug, not a model-quality finding.

## Day 4 cache benchmark preparation — 2026-10-30 America/Toronto

`data/cache_benchmark_v1.jsonl` contains 12 hand-authored validation cases in four seed groups: four true paraphrases, four near misses that change a number, entity, or base constraint, and four unrelated queries. Related cases share a group ID and seed entry. These are small controlled examples, not model-generated observations or a held-out quality estimate; no project test prompt or answer was used.

Day 4 cache comparison preflight: the CLI read the 12 hand-authored cases and an intentionally empty private observation file (`runs/day4-cache-observations-empty-20261030.jsonl`). It wrote `runs/day4-cache-report-empty-20261030.json` with six mode/origin coverage rows and zero real observations. It measured no embedding retrieval, Jev check, generator answer, latency, usage, or cost. A fixture unit test demonstrates how harmful reuse denominators are computed; its numbers are not empirical cache performance.

## Day 4 final offline integration — 2026-10-30 America/Toronto

Run `mac-day4-offline-20261030-1838`: `.venv/bin/pytest -q` passed 99 tests, one Starlette deprecation warning, 0.46 seconds. Raw output is `evidence/day4/mac-offline-20261030-1838.txt`. The five HTTP integration tests use mock HTTP responses and controlled decision fixtures to check dispatch, rejection/escalation, cache-hit avoidance, cache-miss insertion, and disabled paid/experimental gates; their counts are included in the 99. They are engineering checks, not answer-quality or cache-performance measurements. `.venv/bin/jev doctor` reported the two Ollama tiers unavailable with `ConnectError` and frontier unconfigured; raw JSON is `evidence/day4/mac-doctor-20261030-1838.json`. No paid call or live model run was made. Real cache thresholds, model answer quality, latency, usage, and cost remain unknown.

## Day 5 deployment and load evidence — 2026-10-31 America/Toronto

Run `mac-day5-offline-20261031`: `.venv/bin/pytest -q` returned 119 passed, one third-party Starlette deprecation warning, 0.92 seconds. Raw output: `evidence/day5/mac-offline-20261031.txt`. Focused Ruff E4/E9/F lint and Python compileall passed. The remote GitHub Actions workflow has not run. The 50 fixed CI cases are synthetic HTTP contract fixtures, not benchmark prompts, model answers, or held-out data.

Compose check: the ARM image built, a temporary nonroot container passed `/healthz` and Docker health, `docker compose config` passed, `promtool check config` accepted one scrape file and four rules, and Prometheus reported `up{job="jev-gateway"}=1`. One bounded explicit-small request returned HTTP 502 and emitted `jev_client_requests_total{mode="standard",status="502"}=1` plus one generation-error attempt. Grafana 12.2.0 provisioned the 14-panel dashboard and all 17 PromQL expressions parsed against actual Prometheus. These observations check the gateway/monitoring path, not model serving. Container-to-host Ollama failed with `Network is unreachable`.

Run `day5-pod-20261031T194116Z`: kind v0.33.0 used the official pinned Kubernetes v1.37.0 node image in project cluster `jev-gateway-day5`. Two gateway pods were ready. The controlled in-cluster client sent 40 `GET /v1/models` requests while one pod was deleted. It observed 39 HTTP 200 responses, one `URLError` at request index 5, and 4.812771874945611 seconds of actual traffic. Ready-pod count dropped to one in sampled snapshots and returned to two; the replacement rollout succeeded. Raw per-request and pod timeline: `evidence/day5/kind-pod-replacement-20261031.json`. This endpoint returns the configured model catalog and does not call any generation backend, so no inference failover or backend capacity conclusion follows. Final in-pod diagnostic and pod state: `evidence/day5/kind-doctor-20261031.json` and `evidence/day5/kind-final-20261031.txt`.

Run `day5-20261031T194858Z`: Locust 2.47.0 launched a planned 600-second steady scenario with one closed-loop user, two-request cap, 32 output-token reservation cap, and a fixed small-tier prompt. It stopped after 1.884353 seconds. Both actual requests returned HTTP 502 because native Ollama was unreachable; zero successful model answers were observed. The achieved request count over that short interval was two, and the report classifies it as `shorter_than_planned`. The periodic Locust CSV still showed zero requests and `N/A` percentiles when the capped run ended; a per-request event file captured both failures and the reporter flags that mismatch. Raw manifest and request events plus derived report are in `evidence/day5/locust-smoke-*20261031T194858Z.*`; the original Locust CSV/log remain in ignored `runs/day5-locust-smoke-events-20261031/`.

Controlled Jev outage fixture: `tests/routing/test_outage_integration.py` injected two HTTP 503 dependency responses. The breaker opened after its fixture threshold of two, the labeled classifier fixture handled three routing fallbacks, a later probe closed the breaker, and a separate verifier outage returned HTTP 503 without an answer. The two focused tests passed; raw test output is `evidence/day5/jev-outage-fixture-20261031.txt`. No real Jev API, trained DistilBERT model, semantic cache model, or sustained real inference load was used. The ten-minute steady, fivefold two-minute spike, one-hour soak, live Jev outage, and final held-out evaluation remain pending.

Official deployment references consulted 2026-10-31: https://docs.docker.com/desktop/features/networking/networking-how-tos/, https://kind.sigs.k8s.io/docs/user/quick-start/, https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0, https://kubernetes.io/docs/concepts/workloads/pods/probes/, https://prometheus.io/docs/practices/histograms/, and https://docs.locust.io/en/latest/configuration.html. These inform the implementation but do not substitute for the observed checks above.
