# Engineering status — 2026-10-27, America/Toronto

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
