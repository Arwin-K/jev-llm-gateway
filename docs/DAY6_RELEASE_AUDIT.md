# Local Day 6 release audit

**Disposition:** technically reviewable local checkpoint with packaging follow-up through 2026-11-22; **not** a fully verified research result or publishable release. This audit does not authorize a push or external publication.

| Original deliverable | Implementation / offline evidence | Real evidence or blocker |
| --- | --- | --- |
| Three-tier gateway, streaming, tracing | Implemented; API/transport tests and current full suite | Small and medium real local benchmark runs exist; one 16-token-cap small-tier loopback smoke returned HTTP 200. Frontier remains unconfigured. |
| Native Mac small/medium backends | Ollama adapters and installed model tags | `qwen2.5:1.5b` and `qwen2.5:7b` are installed. Small-tier smoke succeeded; both local quality datasets have 1,500 train and 500 validation prompt records, with parse/runtime failures kept separate. |
| Frontier/Jev APIs and paid guards | Typed adapters, budget checks, fail-closed tests | No credentials, configured models/rates, or positive paid-run cap; no real Jev decision/verifier or frontier request. |
| 2,000+ benchmark prompts and scorer | 2,500 prompt IDs indexed across math, choice, and code; isolated code scorer | Small train: 991 correct, 453 incorrect, 54 parse errors, one backend error, one evaluator timeout. Medium train: 1,224 correct, 263 incorrect, 13 parse errors. Small validation: 324 correct, 157 incorrect, 19 parse errors. Medium validation: 402 correct, 92 incorrect, 6 parse errors. These are local generator results, not routing outcomes. |
| Fixed/random, prompted, Jev, DistilBERT, Strands | Adapters and fixed/random/prompted comparisons; offline fixtures | Prompted-small v4 made 500/500 validation decisions, all small, matching the fixed-small baseline. No trained DistilBERT artifact, live Jev comparison, or Strands run. |
| Calibration | Binary/multiclass methods and reliability-figure code | No matching live router probability predictions; no empirical router calibration result. |
| Verification/cascade/hybrid | Buffered paths and fixture HTTP tests | No real Jev or end-to-end verifier/cascade comparison. |
| Scoped semantic cache | Scope/index/check protocol and fixture tests | No real embedding/FAISS model, index, or reuse result. |
| Docker, Compose, kind, monitoring | ARM image health, Compose scrape, Grafana panels, kind checks | No gateway model inference in containers/pods. Docker is available locally; no container was running at the 2026-11-21 preflight. |
| Locust and resilience | Bounded schedules, raw event reporting, fixture outage | A two-request smoke returned HTTP 502; planned steady/spike/soak and live Jev outage experiments remain unrun. |
| CI and installation | Current local suite: 174 tests; current revision wheel built, installed in a fresh non-CUDA Python 3.14 venv, CLI/import/`pip check` passed | Remote CI is unrun. Default PATH lacks `uv`; package build used isolated temporary `uv`/`hatchling`. |
| NVIDIA performance | Source-pinned Colab notebook and benchmark/profile/comparison tools; static syntax, loopback, separation, cleanup tests | No Colab GPU allocation, vLLM baseline, trace, or candidate run. |
| Frozen held-out quality comparison | Freeze audit, locked test split | Latest audit: small has 1,444/1,500 binary train and 481/500 binary validation outcomes; medium has 1,487/1,500 and 494/500; frontier has none. Identity checks are clean, but 11 freeze fields are missing and all six tier/split coverage requirements are short. `ready_for_test=false`; no test prompt or answer was used. |
| Costs and figures | Stage ledger, raw audit and coverage figure code | API charges, real capacity cost, and quality/cost operating curves remain unknown. |
| Technical report and reproduction | Local report, clean-checkout guide, evidence and provenance notes | Report is updated to current local evidence; target-platform clean install, remote CI, and publication rights review remain outstanding. |

## Integrity checks

The tracked MIT `LICENSE` is declared by `pyproject.toml` and `CONTRIBUTING.md` for repository code and documentation. It does not grant rights to benchmark datasets, model weights, provider outputs, or external services; those require separate review. No private `runs/` file or `data/day2_sources/` snapshot is tracked. The current wheel contains 86 members and no CUDA/torch-named members; it was built from source revision `c3eb8c80f7178d01b858eef53363836cdf2e4617` using temporary build tools, then installed with test extras in a fresh non-CUDA environment. Three tracked notebooks have no saved execution outputs. The post-rescore freeze audit counts split IDs, including the test count, without using held-out prompt text or answers for policy development. No test record exists and the test was not executed or tuned against.

## Publication checklist

- Review the MIT license scope together with the current benchmark, model, and provider terms.
- Configure Jev/frontier credentials, models, sourced rates, and explicit positive caps before any paid call; obtain a compatible trained DistilBERT artifact and real decision observations.
- Resolve missing scored outcomes without changing the frozen prompt identities, select policies only on validation, fill every required freeze field, and keep the test locked until coverage is complete.
- Obtain an actual Colab GPU allocation, run unprofiled baselines, collect a separate diagnostic trace where supported, test one evidence-motivated serving change, and repeat both conditions.
- Complete real cascade/cache/calibration/cost and sustained-load comparisons; run target-platform CI checks.
- Review private artifacts, secrets, model outputs, source terms, and a specific destination before any push or release.

The 2026-11-21 `make build` attempt exited 2 because `uv` was missing and produced no wheel; that historical record remains accurate. On 2026-11-22, the same source revision was built with isolated temporary `uv`/`hatchling`, and the resulting wheel passed fresh non-CUDA install, CLI/import, dependency, and 174-test checks. `make build` itself remains unverified with the default PATH. Full evidence and hashes: `evidence/day10/package-build-install-20261122.txt`.
