# Experiment evidence

## Maintenance verification — 2026-11-17 America/Toronto

Run `maintenance-offline-20261117`: `make verify` on the existing project `.venv` (Python 3.14.5) compiled `src`, `load`, `scripts`, and `tests`, then passed **149 offline tests** in 0.82 seconds with one third-party Starlette deprecation warning. Raw output: `evidence/testing/maintenance-offline-20261117.txt`. Focused checks also passed before the final suite: sandbox 3 tests, checkpoint persistence 5 tests, Locust runner 4 tests, and Locust report 6 tests. Ruff/remote CI were not run because the local `uv`/`ruff` tools are unavailable; no live service or experiment was started.

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

## Day 6 local investigation and release check — 2026-11-01 America/Toronto

The actual pre-freeze audit `evidence/day6/freeze-audit-identity-20261101.json` read the ignored 2,500-prompt manifest and the one two-row validation result file. It found 1,500 train, 500 validation, and 500 test IDs, with **zero unique scored real train or validation observations for every tier**. All required freeze fields remain null; the audit returned `ready_for_test=false`. The only observed generation outcomes were the two earlier backend errors. `evidence/day6/system-audit-20261101.json` read the existing Day 3 validation replay and Day 4 empty cache report, finding no real scored routing or cache comparison. The held-out test was not read as prompt content or executed.

No `nvidia-smi`, `nsys`, native Ollama, configured Jev/frontier API, or Colab GPU was available on this Mac session. The Day 6 notebook and synthetic serving scripts were syntax/offline checked only. **No** vLLM baseline, profile, optimization candidate, alternating comparison, real composed-system result, empirical calibration, or provider charge was observed. The derived SVG `evidence/day6/pre-freeze-coverage-20261101.svg` visualizes missing scored coverage from the audit rather than a quality curve.

Package run: pinned `hatchling==1.27.0` was installed in temporary build storage after the default sandbox could not resolve PyPI. The wheel built and installed with standard runtime dependencies in a separate Python 3.14 venv; `jev --help`, package imports, and `jev doctor` ran. The final source wheel was rebuilt and reinstalled after the source-revision and freeze-integrity changes; its SHA-256 and size are in `evidence/day6/package-check-final-20261101.json`. No CUDA dependency is in the core package.

Clean local clone: `git clone --no-hardlinks . /tmp/jev-day6-clean`, fresh test-extra install, and `.venv` equivalent tests yielded **127 passed, one third-party warning, 1.03 seconds** at that revision. A temporary loopback `/healthz` returned HTTP 200. The first bind in the default sandbox failed with `operation not permitted`, then the bounded local bind succeeded with permitted execution. No real model request succeeded because Ollama was absent. See `evidence/day6/clean-clone-20261101.json`. Private `runs/` inputs were absent in the clone by design; documentation now explains regeneration.

Final Mac source check after the later freeze/environment changes: `.venv/bin/pytest -q` returned **129 passed, one third-party Starlette warning, 0.69 seconds** in `evidence/day6/mac-offline-final-20261101.txt`; Python `compileall` passed. This verifies offline behavior, not Linux/Colab or provider compatibility. The remote CI workflow was not run. Official runtime/profiler references and the controlled procedure are in `DAY6_PROTOCOL.md`.

## First live local inference — 2026-11-13 America/Toronto

Run `mac-live-smoke-20261113T184458-0500`: native Ollama 0.40.16 with `qwen2.5:1.5b` (ID `65ec06548149`) and `qwen2.5:7b` (ID `845dbda0ea48`). `jev doctor` reported both tiers installed. Through a loopback `jev serve`, `jev smoke --tier small` returned a real answer in 1.72 s wall time and `--tier medium` in 3.85 s, each including a cold model load; these are single observations, not latency distributions. `ollama ps` showed 1.2 GB and 4.8 GB resident at 100% GPU; after the medium request only the 7B model remained loaded. Raw record: `evidence/day7/mac-live-smoke-20261113.json`.

Bounded pilot `day2-run-7eafd76f97304422910d6dfb9cdf23d9` (10 validation math prompts, small tier, 256 output tokens) returned **10 parse errors, 0 scored**. A scratch probe using the unchanged scorer found the models usually reach the reference value but end with units, currency, inline `Answer:` markers or `\boxed{}`, which the strict math scorer rejects; moving the instruction after the question changed math from 10/10 to 9/10 parse errors and choice from 5/10 to 2/10. Raw details: `evidence/day7/answer-format-probe-20261113.txt`. No train/validation coverage was added; full evaluation is paused on the answer-format decision. Docker was not running, so code scoring remained blocked.


## Offline test environment verification — 2026-11-16 America/Toronto

Run `make verify` (run ID: `offline-suite-20261116`) with the existing Python 3.14.5 `.venv` and pytest 9.1.1: syntax compilation passed; **141 offline tests passed** in 0.90 seconds, with one third-party Starlette deprecation warning. `make compose-config` passed as a syntax/configuration check only; it did not start the gateway, monitoring services, or open ports. Raw pytest output: `evidence/testing/offline-suite-20261116.txt`. No provider or model calls were made. The `uv` CLI was absent, so clean environment installation and package build were not checked in this run; see `ENVIRONMENT.md`.

## Local v2 model results and checkpoint audit — 2026-11-13/14

The v2 template decision was already implemented when these observations were collected. The private file `runs/day2-run-ddd52bb7b6c74b15b68a1df581e8ba1b.jsonl` contains 500 unique small-tier validation prompts using `qwen2.5:1.5b`: 220 math (175 correct, 33 incorrect, 12 parse errors), 200 choice (116 correct, 84 incorrect), and 80 code (33 passed, 40 failed tests, 7 parse errors). Overall: 324 correct, 157 incorrect, 19 parse errors. Strict format compliance was 250/500. The run file combines 479 checkpoint-reused records and 21 later records across run IDs `9363b0dd9aaf4b0da49857612870b990` and `da29c88e6eff4a29b7bb09d9fce7d5b6`; the logged rerun was not 500 fresh calls.

The private checkpoint directory contains 578 unique small-tier train math results (453 correct, 89 incorrect, 36 parse errors), not the full 1,500 train prompts. Separate 30-prompt validation pilots recorded 20/30 correct for small, 26/30 for medium, and 18/30 for small with strict code output. These pilot samples and the complete small validation set are descriptive evidence, not a frozen policy comparison. No frontier/paid generation, full medium tier, complete train labels, cache/cascade result, or held-out test result was produced.

The sanitized audit `evidence/day7/local-v2-coverage-audit-20261114.json` preserves counts, fingerprints, and run IDs without answer text. On 2026-11-19, `jev doctor` returned `ConnectError` for both local tiers; its raw sanitized report is `evidence/day7/mac-doctor-20261119.json`. The 10-prompt CLI rerun reused saved checkpoints and issued no generation calls. Frontier was not configured.

## Checkpoint reuse summary verification — 2026-11-19 America/Toronto

Run `cli-summary-focused-20261119T1922-0500`: `./.venv/bin/pytest -q tests/evaluation/test_command_summary.py tests/evaluation/test_runner.py tests/evaluation/test_checkpoint.py` passed **10 tests** in 0.07 seconds. The summary helper reports returned rows, checkpoint-reused rows, new backend attempts, and new responses separately. Raw test output is `evidence/testing/cli-summary-focused-20261119T1922-0500.txt`. No model or provider request was made.

Run `mac-docker-20261119-session`: `docker info --format '{{.ServerVersion}}'` exited 1 because the Docker API socket was absent. This is an availability check only; no containers or Kubernetes cluster were started. Sanitized output: `evidence/day7/mac-docker-20261119.json`.

Run `local-small-one-new-prompt-20261119`: after starting Ollama on loopback only, `jev doctor` found both configured local model tags installed. The bounded train command returned 579 rows: 578 checkpoint-reused and one newly generated small-tier response. The new math response was correct, format-compliant, and completed in 4.425 seconds; this single prompt is an availability smoke and does not estimate quality. Request/token limits, model digests, settings/template fingerprints, and the private result-file path are recorded in `evidence/day7/mac-local-eval-smoke-20261119.json`. Command output: `evidence/day7/local-small-one-new-prompt-20261119.txt`. No frontier or paid request was enabled.

## Full offline verification after checkpoint reporting change — 2026-11-19 America/Toronto

Run `offline-after-resume-summary-20261119T1926-0500`: `make verify` completed compileall and **150 tests passed** in 0.73 seconds, with one third-party Starlette deprecation warning. Raw output: `evidence/testing/offline-after-resume-summary-20261119T1926-0500.txt`. No model, provider, container, or Colab work was run.

Run `task-filter-focused-20261119T2214-0500`: focused selection, summary, runner, and checkpoint tests passed **12 tests** in 0.11 seconds after adding task filters to `eval-run`. Raw output: `evidence/testing/task-filter-focused-20261119T2214-0500.txt`. No model or provider call was made.

Run `offline-after-task-filter-20261119T2219-0500`: `make verify` completed compileall and **152 tests passed** in 0.89 seconds, with one third-party Starlette deprecation warning. Raw output: `evidence/testing/offline-after-task-filter-20261119T2219-0500.txt`. No additional model/provider call, container, or Colab job was started by the suite.

Run `prompt-id-filter-focused-20261119T2241-0500`: exact prompt selection, duplicate/unknown ID rejection, task filtering, resume summary, runner, and checkpoint checks passed **13 tests** in 0.14 seconds. Raw output: `evidence/testing/prompt-id-filter-focused-20261119T2241-0500.txt`. No model request was made by these tests.

Run `offline-after-prompt-id-filter-20261119T2246-0500`: `make verify` completed compileall and **153 tests passed** in 0.72 seconds, with one third-party Starlette deprecation warning. Raw output: `evidence/testing/offline-after-prompt-id-filter-20261119T2246-0500.txt`. No model/provider call, container, or Colab run was performed by the suite.

## Complete small-tier train coverage — 2026-11-19 America/Toronto

Three task-scoped `eval-run` result files cover all 1,500 train IDs with `qwen2.5:1.5b` at the saved v2 template/settings fingerprints. Aggregate outcomes: 991 correct, 453 incorrect, 54 parse errors, one persistent backend error, and one Docker sandbox timeout. Task counts: math 660 (521/96/43 correct/incorrect/parse error), choice 600 (352/248 correct/incorrect), and code 240 (118/109/11 correct/incorrect/parse error, plus one backend error and one evaluator timeout). The code recovery run reused 238 successful/parse-error checkpoints and reattempted the two errors; both outcomes repeated. An additional exact retry of `mbpp:573` also returned backend error. The timeout is a scored task execution limit, not a successful answer.

New model attempts were bounded by explicit request/token caps, serial concurrency, and zero retries; the exact caps, immutable run IDs, model digest, and private result-file paths are in `evidence/day7/small-train-full-audit-20261119.json`. Command summaries are preserved in the corresponding `evidence/day7/small-train-*.txt` files. Raw prompt text, references, and answers remain in ignored `runs/`. At the time of the small-tier run there was no medium result, frontier comparison, or test-split work.

## Medium-tier train evaluation start snapshot — 2026-11-19 America/Toronto

Run `medium-train-math-choice-20261119`: the serial local `qwen2.5:7b` evaluation targeted 660 train math and 600 train choice prompts with a 1,260-request cap, 2,887,016-token cap, 512 output tokens per request, and zero retries. At the 2026-11-19T23:24:45-05:00 runtime snapshot, 319 math checkpoints existed (313 correct, 6 incorrect); no choice prompts had yet been reached. Ollama reported the pinned digest loaded as 4.8 GB on GPU with 4,096-token context, and system memory free was 28%. The evaluation process was active at this snapshot and was later stopped at a user's request; this is interim progress, not a completed run or final quality result. Runtime metadata: `evidence/day7/medium-train-runtime-snapshot-20261119T2324-0500.json`. The CLI summary did not flush before interruption; raw per-prompt answers remain in ignored `runs/`, and interrupt output is recorded in the stop evidence below.

## Medium-tier train run paused at checkpoint — 2026-11-19 America/Toronto

At 23:38 America/Toronto, the serial medium train invocation was interrupted at the user's request so it can resume tomorrow. The final confirmed checkpoint inventory is 420 of 1,260 train IDs: math 409 correct, 10 incorrect, 1 parse error; choice 0. The checkpoint records span 2026-11-20T03:47:12Z through 04:37:01Z under run ID `530250b4989d4dd1bc9ca75c6014513d`; they contain 45,959 prompt tokens and 80,167 completion tokens in total. The interrupt landed while an async evaluation task awaited the semaphore, and the process exited 130. The runner and Ollama server were then stopped; memory free was 62%. Full sanitized details and the raw interrupt trace are in `evidence/day7/medium-train-stop-audit-20261119.json` and `evidence/day7/medium-train-interrupt-20261119T2338-0500.txt`. On resume, start Ollama on loopback and run the same command with `PYTHONUNBUFFERED=1`; it will reuse the 420 checkpoints and continue within the original request/token caps. This partial train run does not yet support a medium-tier result comparison.

## Completed medium-tier train math/choice — 2026-11-20 America/Toronto

Run `medium-train-math-choice-20261120` completed all 1,260 train IDs across two invocations. The resume used the original request cap of 1,260 and token cap of 2,887,016, reused 420 prompt checkpoints, and made 840 new backend attempts/responses with `qwen2.5:7b`; there were no backend/evaluator errors. Task outcomes: math 632 correct, 26 incorrect, 2 parse errors; choice 436 correct, 164 incorrect. Strict-format compliance was 644/660 for math and 599/600 for choice. The result file contains 1,260 unique prompt IDs. Same-ID comparison against small-tier train rows confirmed identical prompt, template, and settings fingerprints. Binary-only paired transitions are in the audit: among math rows scored by both tiers, medium changed 82 small-tier errors to correct and changed 7 small-tier correct rows to incorrect; for choice these counts were 116 and 32. This is train-split descriptive evidence, not validation, a routing threshold, or a generalization claim.

Recorded latency across the 1,260 returned rows was 3.531 seconds median and 10.535 seconds p95 (minimum 0.330 seconds); prompt/completion token usage summed to 165,661/127,948. The model digest, run IDs, exact caps, per-task dataset and template identities, strict-format counts, paired transitions, and all limitations are preserved in `evidence/day8/medium-train-math-choice-audit-20261120.json`. CLI output is `evidence/day7/medium-train-math-choice-resume-20261120.txt`; raw answers are in ignored `runs/day2-run-263a6f59ec7d493cbdf0dd205cbaaf21.jsonl`.

## Medium-tier validation math/choice — 2026-11-20 America/Toronto

Run `medium-validation-math-choice-20261120` completed all 420 validation prompts (math 207 correct/13 incorrect; choice 150 correct/49 incorrect/1 parse error). It used 420 requests under a 420-request and 961,536-token cap, with one local GPU model, concurrency one, and no retries. No backend/evaluator errors occurred. Against the saved small-tier rows for the same 220 math and 200 choice prompt IDs and matching fingerprints, the binary-only transition table is in the audit; medium corrected 24 small-tier math errors and 44 small-tier choice errors, while regressing 2 and 9 respectively. Nonbinary rows are excluded from these paired binary counts. Observed medium response latency was 3.643 seconds median and 10.976 seconds p95; the historical small validation result had 1.212 seconds median and 3.638 seconds p95. The small records span earlier invocations, so the timing comparison is descriptive and not a same-session load benchmark.

The full per-task counts, exact identities, caps, token usage, paired transitions, and limits are in `evidence/day8/medium-validation-math-choice-audit-20261120.json`. Raw CLI output: `evidence/day8/medium-validation-math-choice-20261120.txt`; private raw answers: `runs/day2-run-1024c23932c74897a9c95604c7f88836.jsonl`. Medium code validation is not yet complete, so no full-tier threshold was selected and no held-out test was accessed.

## Docker availability blocker — 2026-11-20 America/Toronto

After the medium math/choice runs, Docker Desktop's local daemon remained unavailable. The Desktop UI process was present, but `docker info` could not connect to `unix:///Users/ArwinKarir/.docker/run/docker.sock`. `docker desktop start` reported the application already running; status could not be retrieved; a 120-second CLI restart failed because stale UI/helper processes would not exit. No container or Kubernetes cluster was started. Consequently medium train code and validation code were not run in this session. Raw CLI observations: `evidence/day8/mac-docker-blocker-20261120.txt`; sanitized state and resume notes: `evidence/day8/mac-docker-blocker-20261120.json` and `docs/DAY8_HANDOFF.md`.

## Docker recovery and medium-tier train code — 2026-11-20 America/Toronto

On resume, terminating the stale Desktop UI/helper PIDs allowed `docker desktop start --detach` to start the daemon. `docker info` returned engine 29.6.2, aarch64, with 8,321,372,160 bytes assigned. The cached `python:3.12.7-slim-bookworm` image was linux/arm64 with image ID `sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d`.

Run `medium-train-code-20261120` completed 240 unique train code prompts using `qwen2.5:7b`: 156 correct, 73 incorrect (51 failed hidden tests and 22 crashes), and 11 ambiguous-code parse errors. There were no backend/evaluator errors. Strict format compliance was 203/240; prompt/completion usage was 16,354/18,644 tokens; response latency median was 2.243 seconds and p95 was 7.126 seconds. Compared with the small-tier train rows, all prompt IDs and template/settings fingerprints matched. Among prompts with binary outcomes for both tiers, medium corrected 45 small-tier errors and regressed on 12 small-tier correct answers; the 24 nonbinary-in-either rows were excluded. This is a train-split comparison only.

The full medium training split now covers all 1,500 prompts: 1,224 correct, 263 incorrect, 13 parse errors, zero backend/evaluator errors, and 1,487 binary labels. The combined train audit is `evidence/day8/medium-train-full-audit-20261120.json`; code detail and private raw result path are in `evidence/day8/medium-train-code-audit-20261120.json`. Command output: `evidence/day8/medium-train-code-20261120.txt`. `docker ps` showed no containers after the run. Validation code (80 prompts) remains outstanding.

Docker recovery records: `evidence/day8/docker-recovery-20261120.json` and `.txt`. The earlier startup failure remains preserved as historical evidence above.

## Medium-tier validation code and full validation coverage — 2026-11-20 America/Toronto

Run `medium-validation-code-20261120` initially recorded all 80 validation code IDs: 45 correct, 29 incorrect, 5 parse errors, and one `blocked` environment error for `mbpp:401`. A one-request exact prompt-ID recovery and a second one-request recovery each generated a response but returned the same environment error. This was the initial scoring classification; a later diagnostic and rescore below supersede it. No more generations were made for that ID.

The 80 IDs and fingerprints match the saved small-tier validation code rows. The initial audit had 12 nonbinary-in-either paired rows and 493 aggregate binary scores. Strict format compliance is 485/500. The initial paired audit is `evidence/day8/medium-validation-full-audit-20261120.json`, with per-stage details in `medium-validation-math-choice-audit-20261120.json` and `medium-validation-code-audit-20261120.json`.

The initial code run used 80 requests under an 80-request/103,736-token cap; two targeted recovery requests each used a 5,000-token cap, one request, and zero automatic retries. All 82 model responses are preserved privately under `runs/`; raw CLI outputs and the generic sandbox check are in `evidence/day8/`. No threshold was selected and the held-out test remains untouched.

Across 500 returned per-prompt evaluation records, duration (`ended_at - started_at`) had a 1.710-second median and 3.979-second p95 for small versus a 2.724-second median and 10.629-second p95 for medium. Small-tier rows span earlier invocations; these values are descriptive per-prompt evaluation durations, not a same-session load benchmark or full gateway routing latency. They are included in `evidence/day8/medium-validation-full-audit-20261120.json`.

## Pre-test freeze audit task-template correction — 2026-11-20 America/Toronto

The initial current-evidence audit (`freeze-audit-before-task-template-fix-20261120.json`) reported mixed generation identities for both local tiers because its identity tuple included a template fingerprint but not task identity. The evaluation intentionally uses different templates for math, choice, and code. Updated the audit to check model/revision/settings consistency per tier and template consistency per task, and to compare task-scoped template maps from freeze configuration. Six focused tests passed, including distinct task templates, within-task template drift, matching/mismatching scoped configuration, legacy one-template configuration, and mixed model identity.

The rerun (`freeze-audit-current-20261120.json` and its concise text summary) found zero identity issues. It still reports `ready_for_test=false`: required freeze fields remain absent and scored coverage is short for train/validation tiers; frontier has no observations, and small/medium are short of complete binary coverage. It counted manifest split sizes but did not read test prompt content or references. No threshold or held-out outcome was selected. Test output: `evidence/day8/freeze-audit-focused-tests-20261120.txt`.

## Reclassify the saved MBPP validation response — 2026-11-20 America/Toronto

A fresh attempt to run the saved `mbpp:401` response first found the Docker socket inaccessible from the restricted shell. With the authorized local Docker scorer, the already saved generated Python ran in a network-disabled container and emitted `SyntaxError: invalid syntax`; no model call was made. Python's syntax diagnostic does not contain the literal `Traceback`, so the sandbox previously treated it as `environment_error`. Added explicit `SyntaxError` recognition as a code crash and a regression test. The focused sandbox/scoring suite passed 6 tests.

The saved response now scores `incorrect` with score 0. Medium code validation is 45 correct, 30 incorrect, and 5 parse errors. Across 500 medium validation IDs, outcomes are 403 correct, 92 incorrect, and 6 parse errors (494 binary scores); no row is environment-blocked. Against small on binary-only code rows, both-incorrect increased to 26 and nonbinary-in-either decreased to 11. Full details are in the [rescore diagnostic](medium-validation-code-mbpp401-rescore-20261120.json), [reclassified code audit](medium-validation-code-audit-reclassified-20261120.json), and [reclassified full audit](medium-validation-full-audit-reclassified-20261120.json). The [updated freeze audit](freeze-audit-after-mbpp401-rescore-20261120.json) counts 494 medium validation scores, has no identity issues, and remains `ready_for_test=false` because required fields and full tier coverage remain absent. The raw model runs remain unchanged.
