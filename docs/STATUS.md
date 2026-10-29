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
