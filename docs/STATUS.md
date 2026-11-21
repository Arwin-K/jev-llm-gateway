# Engineering status — 2026-10-27, America/Toronto

## Maintenance block — 2026-11-17 America/Toronto

Six maintenance fixes were completed as separate local commits: sandbox timeout outcomes are preserved when cleanup fails; checkpoint digest paths are validated; Locust launch failures leave terminal manifests; malformed event lines are counted while valid observations remain reportable; focused CI lint covers the checkpoint and sandbox paths; and reversed Locust intervals are rejected before throughput calculation. Focused offline checks passed for each code change. The final `make verify` run (run ID `maintenance-offline-20261117`) passed compileall and 149 tests, with one existing Starlette deprecation warning; raw output is `evidence/testing/maintenance-offline-20261117.txt`. The CI workflow itself was not run remotely. No model, provider, container, Colab, or load experiment was started.

The Day 1 gateway implements explicit-tier text chat, SSE, tracing, diagnostics, and a Colab serving notebook. `model=auto` and Jev routing are Day 3 work. No model inference, frontier call, Colab GPU run, training, or load test occurred.

| ID | Change | Verification and status |
| --- | --- | --- |
| D1-01 | Scope and runtime profiles | Full scope mapped. |
| D1-02 | Mac and Colab preflight | Sanitized Mac preflight; Colab GPU pending. |
| D1-03 | Package and CLI | Fresh venv install, import, CLI help, uv lock. |
| D1-04 | Backend configuration | Config invalid/disabled cases pass. |
| D1-05 | API contract | API contract tests pass; localhost health later returned HTTP 200. |
| D1-06 | Async HTTP transport | Mock HTTP forwarding passes. |
| D1-07 | Small Ollama adapter | Ollama small adapter offline-tested; real answer pending. |
| D1-08 | Medium Ollama adapter | Medium residency adapter offline-tested; live memory/load pending. |
| D1-09 | Frontier admission guard | Frontier budget admission tested; paid call disabled. |
| D1-10 | Nonstreaming dispatch | Explicit dispatch mock-tested; live backend pending. |
| D1-11 | SSE forwarding | Fragmented SSE and completion tested; live stream pending. |
| D1-12 | Deadlines and errors | Timeout and sanitized error tests pass. |
| D1-13 | Request traces | Secret-free trace structure tested. |
| D1-14 | Diagnostics and smoke | Doctor reports both models unavailable; smoke failure path tested. |
| D1-15 | Colab notebook | Notebook JSON and cell syntax validate; no Colab cells executed. |
| D1-16 | Runtime profiles | Core venv has no torch/CUDA/NVIDIA/vLLM packages. |
| D1-17 | Profile integration tests | Mac and Colab URL profiles pass offline integration; real models pending. |
| D1-18 | Setup and evidence | Quickstart and evidence ledger prepared; clean-reader walkthrough pending. |

Final offline suite after `uv sync --locked`: 15 passed, one third-party Starlette deprecation warning, 0.16 seconds; raw output is in `evidence/day1/mac-offline-20261027-1314.txt`. A brief loopback gateway returned HTTP 200 from `/healthz` under elevated sandbox permission; the default sandbox denied socket binding. `jev doctor` returned `ConnectError` for both Ollama tiers and `frontier.configured=false`; raw report is in `evidence/day1/mac-doctor-20261027-1314.json`.

## Unmet Day 1 gates and handoff

- Install/start native Ollama, check disk, pull the small then medium models, run bounded answers, and record model IDs, load time, `ollama ps`, and memory pressure. Only 18 GiB of disk was free at preflight.
- Supply a Colab GPU runtime and upload a committed source archive to run/export the notebook. GPU allocation, vLLM compatibility, and requests remain unverified.
- Supply frontier key/model/current rates and explicit positive caps before any paid call. Process-local caps do not replace provider account limits.
- Perform a clean-reader install and real-path smoke. Offline mock tests do not prove three-tier live routing.

Next Mac command after installing Ollama: `ollama pull qwen2.5:1.5b`, then `.venv/bin/jev doctor`; start `.venv/bin/jev serve` and run `.venv/bin/jev smoke --tier small`. No project job, training checkpoint, or paid request is running.

## Day 2 — 2026-10-28 America/Toronto

Sixteen substantive local commits cover D2-01 through D2-18, with D2-02–04 combined into one adapter commit to meet the requested 16-commit target. Implementation includes frozen manifest preparation, isolated code scoring, task scorers, bounded evaluation, resumption, audit export, hindsight labels, cost states, quality reports, and separate serving baselines. D2-18's real-measurement checkpoint is partial: source acquisition and sandbox fixtures succeeded, but configured generation tiers were unavailable, so no model answer quality or latency was measured. The test split remains unused. See `DAY2_HANDOFF.md` for counts, commands, and blockers.

## Day 3 — 2026-10-29 America/Toronto, block 1

D3-01 defines a shared decision with explicit probability event and identities. D3-02 adds fixed and request-ID-seeded random policies with eligibility gates. D3-03 prepares training labels only from complete, identity-compatible, real train observations. The existing private Day 2 run contains two validation backend errors and zero train results, so the current labeled training subset is **0 of 1,500**; class balance and trained accuracy cannot yet be measured. Local policy checks are offline fixtures, not backend inference.

## Day 3 block 2

D3-04 adds a repository-source Colab notebook and optional weighted DistilBERT trainer; code and CLI entry points are syntax and offline checked, but training is pending because the 1,500 train prompts have zero complete observed labels. D3-05 validates trained artifact provenance and compares predictions before and after reload in the real training path; no artifact exists to exercise that check. D3-06 adds an artifact-gated CPU/MPS inference adapter with explicit configuration compatibility. No Mac inference latency or memory can be measured without a trained artifact.

## Day 3 block 3

D3-07 adds bounded prompted-small routing with strict JSON parsing; no local Ollama inference was available. D3-08 adds a one-request TypeSafe System One client with explicit paid admission and offline contract fixtures, using the current official endpoint and schema. D3-09 adds typed Jev choice routing with versioned backend descriptions and preserves the choice distribution as a routing-choice probability, not generator-answer correctness. Jev credentials, model, rates, and positive caps are absent, so live Jev calls remain disabled.

## Day 3 block 4

D3-10 asks one typed success question per eligible generator in a single budgeted Jev request; thresholds require an explicit validation selection ID and none exists yet. D3-11 implements the official local Strands typed server path; checkpoint download and real serving remain blocked by unverified disk/memory headroom. D3-12 adds offline failure checks for ineligible selections, context limits, provider disablement, malformed decisions, deadlines, and budget denial. No test used a real decision service or paid backend.

## Day 3 block 5

D3-13 adds defined-event Brier, ECE, reliability bins, and SVG output. D3-14 selects thresholds only from saved validation cases with known costs and explicit quality/coverage objectives; no case set is available for a selection. D3-15 adds fixed/random/oracle/router validation replay and a cost-quality SVG. The real stored run produced ten policy coverage rows and **zero plotted points** because no answer was scored and no router selection was recorded. The held-out test was not loaded.

## Day 3 automatic dispatch

D3-17 accepts `model=auto` and dispatches the selected eligible tier through the existing nonstreaming or SSE path. Offline tests verify explicit-tier preservation, auto headers, trained-fallback failure semantics, ineligible frontier rejection, and streaming. The default Jev policy returns 503 here because its configured key/model/rates/caps and trained fallback artifact are absent; this is a deliberate closed state, not a successful live integration.

## Day 3 block 6 and handoff

D3-16 measured only fixed/random decision overhead on this Mac; the raw run ID and limits are in `EXPERIMENTS.md`. D3-17 integrated `model=auto` with an eligible-tier recheck, whole-request deadline, existing frontier reservation, SSE, and trace metadata. D3-18 freezes the implemented router configuration and evidence state in `config/day3-router.json` and `DAY3_HANDOFF.md`. The checkpoint offline suite passed 69 tests with one third-party Starlette deprecation warning. No paid decision or frontier call, training run, model answer, or held-out test evaluation occurred. All 18 Day 3 checkpoints have substantive local commits, though live/training portions remain blocked as described in the handoff.

Post-merge follow-up adds bounded validation decision collection and a calibration-report CLI. A local fixed-policy command produced one selection without a generation call; the matching calibration report correctly returned insufficient data. Jev decision rates now require an HTTPS source URL and effective date in addition to positive caps. These are additional substantive fixes after the 18 checkpoint commits.

The post-merge follow-up suite passed 72 tests with one third-party Starlette deprecation warning; raw output is `evidence/day3/mac-offline-20261029-followup.txt`.

## Day 4 block 1 — 2026-10-30 America/Toronto

D4-01 adds a typed Jev Noul judgment for whether one generated answer satisfies its request and applicable instructions; no benchmark reference is sent. D4-02 adds explicit acceptance and verification-failure outcomes, with no implicit acceptance. D4-03 adds a finite buffered small→medium→frontier cascade that records each generation and judgment attempt. Focused tests use controlled fixtures. No live Jev or generator call was possible at this checkpoint because credentials and Ollama are unavailable.

## Day 4 block 2

D4-04 composes explicit route-first, cascade-only, and route-then-verify hybrid modes. D4-05 introduces one cumulative request ledger for generation and Jev stages plus existing process admission guards; verified output remains buffered. D4-06 adds a validation comparison reader that matches accepted answer hashes and model/settings identity to independent Day 2 scores, and reports real end-to-end timing only from recorded executions. No complete real Day 4 execution records exist yet, so it has no validation quality result.

## Day 4 block 3

D4-07 reports verifier false acceptance, false rejection, wrong accepted fraction, coverage, and failures against independently scored validation answers. D4-08 adds an optional, pinned, local-files-only MiniLM encoder; no real model is installed. D4-09 adds a single-writer, checksum-validated FAISS persistence path with normalized cosine semantics. The current Mac venv lacks torch, sentence-transformers, NumPy, and FAISS, so embedding and native FAISS behavior remain unverified. Focused checks use fixture models/indexes only.

## Day 4 block 4

D4-10 hashes exact instructions, prior conversation, local namespace, generation settings, model/policy identities, and embedding revision into cache scope. D4-11 returns thresholded cosine candidates only after scope/freshness filtering; similarity is not answer validity. D4-12 asks a versioned Jev Noul applicability question for a scoped candidate and treats unavailable/malformed checks as a miss. Fixture tests confirm another scope's stored answer is never sent to Jev. There is no real embedding index or live Jev candidate check yet.

## Day 4 block 5

D4-13 gates insertion on accepted, fresh, compatible answers and provides eviction, invalidation, and reset. D4-14 adds 12 hand-authored grouped validation cases with answer-changing near misses. D4-15 reports retrieval coverage, accepted reuse, harmful reuse, exact-reference answer quality, failures, and known cost/latency separately by real or fixture origin. The current CLI preflight found zero real observations, so no cache threshold or quality result has been selected.

## Day 4 block 6 and handoff

D4-16 adds context/model/embedding drift, corrupt-index lock release, and verifier-outage regressions; earlier cache tests cover empty/restored indexes, namespace, expiry, and grouped near misses. D4-17 exposes optional buffered `route_first`, `cascade`, and `hybrid` execution with off/verified/experimental-similarity cache modes. It preserves legacy explicit-tier, auto, and SSE behavior under the default mode. Paid verification is gated by an explicit flag, configured Jev access, and positive cumulative caps. Offline HTTP fixtures verify cache-hit generation avoidance, candidate miss fallback, accepted-only insertion, escalation, and gates. D4-18 records the actual operating contract in `DAY4_HANDOFF.md`.

The final offline suite passed 99 tests with one third-party Starlette warning; raw output is `evidence/day4/mac-offline-20261030-1838.txt`. Doctor reported both Ollama tiers unreachable and frontier unconfigured in `evidence/day4/mac-doctor-20261030-1838.json`. No real Jev, generator, embedding, FAISS, or end-to-end performance check succeeded. There are 18 substantive Day 4 checkpoint commits after this handoff commit. The held-out test remains unused.

## Day 5 — 2026-10-31 America/Toronto

D5-01 through D5-18 have implementation commits on `day-five`, plus genuine follow-up fixes for locked image dependencies, paid-load cap interpretation, and short Locust raw events. The Day 5 gateway now has a nonroot ARM image, Compose and kind local deployment paths, process-level Prometheus metrics and Grafana dashboards, Jev circuit breaker and trained-router fallback boundary, bounded admission, and opt-in local availability failover. The load runner defines steady, spike, and soak schedules, but all three sustained real inference experiments remain pending because both native Ollama tiers are unavailable. No real Jev call, trained fallback inference, or paid call occurred.

The final offline Mac suite returned **119 passed, one Starlette deprecation warning, 0.92 seconds**; raw output is `evidence/day5/mac-offline-20261031.txt`. The ARM image built and passed a real container health check. Prometheus's Compose scrape target was `up`; a bounded request returned HTTP 502 and emitted a matching request/attempt metric. Grafana provisioned 14 panels, and all 17 PromQL expressions parsed against the running server. A named kind cluster ran two ready pods; its project Service returned `/v1/models` while one pod was deleted. The 40-request in-cluster API check observed **39 HTTP 200** and **one `URLError`**, with 4.8128 seconds of traffic; it did not call a model. The replacement reached readiness. Raw timeline: `evidence/day5/kind-pod-replacement-20261031.json`.

The two-request Locust wiring check ran for **1.884353 seconds** and observed **two HTTP 502 failures** against unavailable Ollama; it is explicitly shorter than the planned ten-minute steady run. The first attempt revealed stale periodic CSV data and `N/A` percentiles, so the reporter now preserves per-request raw events and flags the count mismatch. Evidence is in `evidence/day5/locust-smoke-*20261031T194858Z.*`; no real inference throughput claim follows from it. Jev outage/recovery and verifier fail-closed checks used controlled offline fixtures only. The remote CI workflow has not run.

The project kind cluster and Compose containers were stopped after checks; their project images and Compose monitoring volumes remain. At final check the Mac data volume had **8.3 GiB free** and Docker Desktop's daemon memory allocation was **8,321,372,160 bytes**. Backend networking from the actual container and pod failed with `Network is unreachable`; `kind doctor` reports `ConnectError` for both tiers and frontier unconfigured. The trained DistilBERT artifact, real verifier/cache thresholds, and held-out test remain untouched. See `DAY5_HANDOFF.md` for working commands and Day 6 gates.

## Day 6 — 2026-11-01 America/Toronto

The `day-six` branch adds source-pinned NVIDIA environment, synthetic workload, bounded benchmark, optional focused profiler, guarded one-factor candidate, repeated-run comparator, pre-test freeze/identity audit, composed-system coverage audit, cost-stage reconciliation, paired-group uncertainty helper, and a raw-audit coverage SVG. These tools were exercised with offline tests and the existing local evidence; **no Colab GPU, Nsight trace, vLLM run, serving optimization, or held-out evaluation occurred**. The freeze audit reports 1,500 train, 500 validation, 500 test manifest prompts, zero scored train/validation observations for each tier, and all required freeze fields missing. The test remains locked.

The fresh wheel installed in a separate Python 3.14 venv without CUDA. A local clean clone installed with the test extra, passed 127 offline tests with one third-party warning, and served `/healthz` as HTTP 200 on a temporary loopback port after a sandbox bind restriction was lifted for that check. Native Ollama was unavailable, so no bounded real model answer succeeded. The release draft, reproduction guide, provenance guidance, and portfolio notes are local only. See `TECHNICAL_REPORT.md`, `DAY6_REPRO.md`, and `DAY6_RELEASE_AUDIT.md` for limits and next steps.

## 2026-11-13 America/Toronto — first live local models

Native Ollama now serves `qwen2.5:1.5b` and `qwen2.5:7b`; `jev smoke` returned real answers for both tiers through the gateway, the first successful live generation in this project. A 10-prompt validation pilot scored zero because every math answer failed the strict answer-format parser. Full train/validation runs are paused on that open decision (`DECISIONS.md`). Docker must be running before code tasks can be scored. Frontier, Jev, DistilBERT training, Colab GPU and the held-out test are unchanged.


## 2026-11-16 — testing entry points

Added a Make-based local/CI entry point for the existing locked test extra: `make setup-test`, `make verify`, `make build`, and optional `make compose-config`. `make verify` compiles all project Python paths then runs the full offline pytest suite. Compose validation parses configuration only; it does not start services. Local verification used the existing Python 3.14.5 `.venv`: **141 passed**, with one third-party Starlette deprecation warning; syntax compilation and Compose configuration validation also passed. Raw pytest output: `evidence/testing/offline-suite-20261116.txt`. CI now uses the same setup, compile, test, and package-build targets. No live provider, paid API, model evaluation, or external service was used. `uv` is not currently on this Mac's PATH, so a fresh environment still needs uv installed before `make setup-test`; the existing `.venv` is already test-ready.

## 2026-11-19 — reconcile saved v2 model runs

The answer-format decision was implemented on 2026-11-13; the older note above saying evaluation was paused on that decision was stale. Ignored local evidence contains three v2 pilots, one complete 500-prompt small-tier validation set, and partial small-tier training results. The validation set has 220 math, 200 choice, and 80 code prompts; outcomes were 324 correct, 157 incorrect, and 19 parse errors. Strict format compliance was 250/500. The 500-row result file combines 479 prior checkpoint records and 21 records from a later invocation, so it is one complete compatible validation set but not 500 new calls from one run. A further 10-prompt CLI invocation reused saved checkpoints and made no new model calls.

The small-tier training run now covers all 1,500 train prompt IDs across math, choice, and code. It produced 991 correct, 453 incorrect, 54 parse-error, one persistent backend-error, and one sandbox-timeout evaluator-error outcome. Thus 1,444 rows have ordinary binary scores; the 56 remaining rows are not silently relabeled. The backend error for `mbpp:573` repeated across three attempts, including an exact-prompt retry. There is still no complete medium or frontier train/validation result set, and the held-out test remains untouched. Sanitized counts and immutable run IDs are in [the full small-tier training audit](../evidence/day7/small-train-full-audit-20261119.json); raw answers remain private under ignored `runs/`.

On 2026-11-19, `jev doctor` could not connect to either Ollama tier; frontier remains unconfigured. Raw report: `evidence/day7/mac-doctor-20261119.json`. No additional generation was possible in this session. Docker, Colab, paid provider access, Jev API access, and sustained serving experiments remain to be checked or supplied before their dependent work can run.

The installed Ollama server was started with an explicit `127.0.0.1:11434` bind. Both installed model digests were verified. A one-request availability smoke returned a correct response in 4.43 seconds; it is not a quality estimate. Full training coverage was then collected for the small tier, with a bounded recovery attempt for the two errors. See `evidence/day7/mac-local-eval-smoke-20261119.json` and `evidence/day7/small-train-full-audit-20261119.json`.

The evaluation CLI now distinguishes result rows restored from checkpoints from backend attempts and responses made in the current invocation. This prevents a resumed command from implying that restored answers were generated again. Focused summary/runner/checkpoint verification passed 10 tests; raw output: `evidence/testing/cli-summary-focused-20261119T1922-0500.txt`. A Docker daemon availability check also failed because its API socket was absent; see `evidence/day7/mac-docker-20261119.json`. No container was started.

Added repeatable `eval-run --task` filters so compatible math/choice runs can proceed independently of Docker-based code scoring. The filter runs before the maximum prompt count and preserves manifest order. Focused selection, summary, runner, and checkpoint checks passed 12 tests; `make verify` then passed 152 tests with one third-party warning. Raw output: `evidence/testing/offline-after-task-filter-20261119T2219-0500.txt`.

Added exact `eval-run --prompt-id` targeting for recovery of one unresolved row, with validation against the requested split/task and duplicate-ID rejection. Focused summary, selection, runner, and checkpoint tests passed 13 tests; raw output: `evidence/testing/prompt-id-filter-focused-20261119T2241-0500.txt`. The subsequent full `make verify` passed 153 tests with one third-party warning; raw output: `evidence/testing/offline-after-prompt-id-filter-20261119T2246-0500.txt`.

After the small-tier coverage run, a bounded medium-tier training evaluation began. It targets all 660 math and 600 choice prompts in the frozen train split, with a 1,260-request cap, a 2,887,016-token cap, 512 output tokens per request, concurrency one, and no retries. The pinned local model is `qwen2.5:7b`, digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`. An earlier progress snapshot recorded 310 math prompts (304 correct, 6 incorrect); the later overnight stop point below supersedes those interim counts. Raw answers stay in ignored `runs/`.

## Medium-tier overnight resume point — 2026-11-19 America/Toronto

The medium train math/choice run was stopped at the user's request after confirming 420 durable prompt checkpoints: math 409 correct, 10 incorrect, 1 parse error; choice 0 reached. The runner and loopback Ollama server are both stopped, and system memory free returned to 62%. The process exit was an interrupt while an evaluation task waited on the serial concurrency semaphore; completed checkpoint files remain intact under ignored `runs/day2-checkpoints/`. This is a partial train result, not a complete tier comparison. The exact run/model identity, limits, stop record, raw interrupt output, and copy-ready resume command are in [the stop audit](../evidence/day7/medium-train-stop-audit-20261119.json) and [Day 7 handoff](DAY7_HANDOFF.md).

## Day 8 — 2026-11-20 America/Toronto

Resumed the medium-tier train math/choice evaluation with the same local model, settings, request/token caps, and 420 checkpoints. The run returned all 1,260 unique train IDs: math 632 correct, 26 incorrect, 2 parse errors; choice 436 correct, 164 incorrect. It reused 420 checkpoints and made 840 new requests/responses, with no backend or evaluator errors. The small/medium paired train audit confirms identical prompt IDs and task/template/settings fingerprints; it is descriptive train evidence only. Full counts, paired outcome transitions, strict-format counts, observed latency, caps, and private result path are in [the medium math/choice audit](../evidence/day8/medium-train-math-choice-audit-20261120.json). Raw answers remain in ignored `runs/`.

Medium train code completed all 240 train IDs: 156 correct, 73 incorrect, 11 parse errors, and no backend/evaluator errors. Small/medium train code prompt IDs and fingerprints match. Across the full medium train split, all 1,500 prompts now have records: 1,224 correct, 263 incorrect, and 13 parse errors, yielding 1,487 binary scored labels. See [the code audit](../evidence/day8/medium-train-code-audit-20261120.json) and [the combined train audit](../evidence/day8/medium-train-full-audit-20261120.json). Training results remain descriptive and were not used to select a threshold.

The medium validation math/choice stage completed all 420 matching validation IDs: math 207 correct and 13 incorrect; choice 150 correct, 49 incorrect, and 1 parse error. It made 420 bounded local responses without backend/evaluator errors. The subsequent code stage produced records for all 80 code IDs: 45 correct, 29 incorrect, 5 parse errors, and one initially blocked `environment_error` for `mbpp:401`. A later diagnostic below supersedes that classification. Paired validation IDs/fingerprints match the small-tier results. Initial audit: [medium validation](../evidence/day8/medium-validation-full-audit-20261120.json); task details: [initial code audit](../evidence/day8/medium-validation-code-audit-20261120.json). The held-out test remains untouched.

Docker blocked the independent medium code stages. The Desktop UI process was present, but its daemon socket was unreachable; `docker desktop start` said it was already running, status could not be retrieved, and `docker desktop restart --timeout 120` failed to stop stale UI/helper processes. No container or cluster was started. Ollama was stopped at session close and system memory free was 76%. The exact blocker and next steps are in [the Docker evidence](../evidence/day8/mac-docker-blocker-20261120.json) and [Day 8 handoff](DAY8_HANDOFF.md).

After resuming, the stale Docker UI/helper processes were terminated and `docker desktop start --detach` brought up engine 29.6.2 (aarch64; 8,321,372,160 bytes assigned). The cached ARM image matched ID `sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d`. Medium train code completed 240 prompts with no runtime errors; validation code produced all 80 prompt records with one unresolved environment error. The local validation comparison now has all 500 prompt IDs, but one code row remains unscored, so no threshold was selected. Recovery evidence: `evidence/day8/docker-recovery-20261120.json`.

The current pre-test freeze audit exposed a false positive: it treated the intentionally distinct math, choice, and code templates as mixed identities. The audit now requires a stable model/settings identity per tier and a stable template within each task, and accepts task-scoped template maps in freeze configuration. Its rerun reports no identity issues while preserving `ready_for_test=false`: the freeze fields are still missing and train/validation scored coverage remains incomplete for every tier. The held-out test was not used. Six focused freeze tests passed; evidence is in `evidence/day8/freeze-audit-before-task-template-fix-20261120.json` and `evidence/day8/freeze-audit-current-20261120.json`.

Re-ran the already saved `mbpp:401` response through the network-disabled Docker scorer, without a model request. The interpreter emitted `SyntaxError: invalid syntax`; the sandbox's stderr classifier missed that marker and mislabeled the code failure as an environment error. Added `SyntaxError` as a code crash, with six focused sandbox/scoring tests passing. The response now scores incorrect/0; medium validation outcomes are 402 correct, 92 incorrect, and 6 parse errors (494 binary scores). The full validation freeze audit now counts 494 scored medium prompts, reports no identity issues, and remains closed for missing freeze fields and incomplete coverage. Evidence: [scoring diagnostic](../evidence/day8/medium-validation-code-mbpp401-rescore-20261120.json), [reclassified code audit](../evidence/day8/medium-validation-code-audit-reclassified-20261120.json), [reclassified full audit](../evidence/day8/medium-validation-full-audit-reclassified-20261120.json), and [updated freeze audit](../evidence/day8/freeze-audit-after-mbpp401-rescore-20261120.json).

A validation-only paired-group bootstrap used 476 prompt IDs with binary outcomes from both local tiers. Medium minus small accuracy was +14.1 percentage points (95% bootstrap interval +10.5 to +17.6 pp), with task estimates +10.6 pp math, +17.6 pp choice, and +14.5 pp code. The seeded 2,000-repetition analysis was reproducible on a second run. It is prompt-weighted descriptive generator evidence, not a Jev routing result, selected threshold, or held-out estimate. See `evidence/day8/medium-validation-paired-group-bootstrap-20261120.json`.

Manifest `load(path, split='validation')` now validates only records belonging to the requested split, so a malformed held-out record cannot be instantiated during development evaluation. The explicit `load(..., 'test')` permission gate remains in place. Focused manifest, runner, and command-summary verification passed 11 tests; output is `evidence/testing/manifest-split-validation-focused-20261120.txt`.

Replayed the fixed-tier and seeded-random baselines on saved validation outcomes. Always-medium produced 402/500 correct completions (80.4%; 402/494 binary accuracy 81.4%); always-small produced 324/500 (64.8%; 324/481 binary accuracy 67.4%). Seeded random selected an unavailable frontier tier for 170 prompts; its observed 234/500 correct completions include the missing selections as not completed, with 322 binary outcomes and 8 parse errors among the 330 observed results. Charge data remains unknown. This is a local baseline comparison, not a routed policy or cost-quality conclusion. Full report: `evidence/day8/medium-validation-fixed-random-baselines-20261120.json`.

The local prompted-small router v1 then made all 500 validation decisions: it selected small for 250 and returned `RoutingError` for 250; all selected decisions chose small. Exact-ID diagnostics on one failed math and one failed choice prompt both reported `JSONDecodeError`. A disjoint 30-prompt train pilot for prompt v2 had 19 selections and 11 JSON decode errors (all 10 choice prompts failed, while 10/10 math and 9/10 code prompts selected small). V2 has not been evaluated on validation. The audit joins saved generator outcomes only for the 250 successful route selections and records the no-generation/unknown-error limits: `evidence/day8/prompted-small-audit-20261120.json`. The decision collector now supports explicit train or validation splits, exact prompt IDs, and safe wrapped-cause categories; focused tests passed.

After the D4/D5 changes, `make verify` compiled project Python paths and passed all 162 offline tests. The only warning is the existing Starlette `TestClient`/httpx deprecation; no live provider was invoked. Full output: `evidence/testing/offline-suite-day8-20261120.txt`.

The prompted-small router is now version 4: request text is encoded as quoted JSON data, the system instruction explicitly forbids answering the request, and the local OpenAI-compatible call asks Ollama for a JSON schema whose tier enum is restricted to currently eligible choices. The collector stores malformed completion text only in ignored private run records for diagnosis. Thirty disjoint train prompts (10 per task) selected small with no errors. A later 500-prompt validation run selected small on all 500, with no errors; matched saved small-generator results were 324 correct, 157 incorrect, and 19 parse errors. This outcome matches the always-small baseline, so v4 demonstrates reliable decision formatting but no routing lift. The decision run generated no answers and used no paid provider. Raw run hashes and task/latency/token summaries are in `evidence/day8/prompted-small-v4-audit-20261120.json`; the first validation attempt recorded 500 connection errors because the restricted shell could not reach Ollama. A later inference invocation could not save because the output path already existed, so its decisions are not part of evidence. The successful capped local run was captured under a fresh immutable run ID. After v4, `make verify` compiled the project and passed all 162 offline tests with one existing Starlette deprecation warning; output: `evidence/testing/offline-suite-day8-post-v4-20261120.txt`.

On 2026-11-21, the routing evaluator was corrected to reserve its exclusive output path before making any decision calls. A regression test confirms an existing output is preserved and rejected without invoking the router; four focused evaluator tests pass. This prevents repeating yesterday's uncaptured 500-call run when a destination collision occurs. Raw focused output: `evidence/testing/evaluate-output-collision-20261121.txt`.

The v4 prompted-router audit helper now has focused regression coverage for split/version identity, duplicate prompt IDs, task summaries, token accounting, and joins to saved outcomes. Both helper tests pass; raw output: `evidence/testing/prompted-router-audit-focused-20261121.txt`.

After D6-06/D6-07, `make verify` compiled all project Python paths and passed 165 offline tests in 0.82 seconds, with the same Starlette/httpx deprecation warning. No live model/provider was contacted. Output: `evidence/testing/offline-suite-day9-20261121.txt`.

D6-09 adds offline structural checks for the NVIDIA notebook. Both tests pass: code cells compile, serving is explicitly loopback-bound, baseline/profile runs are distinguished, and cleanup statements are present. This verifies notebook source only; no Colab cell, GPU, package install, or vLLM server was run. Evidence: `evidence/testing/day6-colab-notebook-focused-20261121.txt`.

The latest freeze gate must use the post-rescore audit: small has 1,444/1,500 binary train and 481/500 binary validation outcomes; medium has 1,487/1,500 and 494/500; frontier has none. There are no identity issues, but all six tier/split coverage requirements are short and all required freeze fields are absent, so `ready_for_test=false`. The earlier `freeze-audit-current-20261120.json` predates the `mbpp:401` correction; the latest evidence is `evidence/day8/freeze-audit-after-mbpp401-rescore-20261120.json`.

After D6-09/D6-10, `make verify` compiled the repository and passed 167 offline tests in 1.20 seconds, with the existing Starlette/httpx deprecation warning. No external compute, model, or provider was used. Output: `evidence/testing/offline-suite-day9-post-notebook-20261121.txt`.

The 2026-11-21 local preflight confirms Docker and both Ollama model files are installed, but neither a container nor an Ollama model is currently running/loaded. Memory free was 40%; no inference was started. Details and sandbox distinction: `evidence/day9/local-runtime-preflight-20261121.txt`.
