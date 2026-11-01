# Local Day 6 release audit

**Disposition:** technically reviewable local checkpoint, **not** a fully verified research result or publishable release. This audit does not authorize a push or external publication.

| Original deliverable | Implementation / offline evidence | Real evidence or blocker |
| --- | --- | --- |
| Three-tier gateway, streaming, tracing | Implemented; offline API/transport tests | Real generation blocked by unavailable Ollama and unconfigured frontier |
| Native Mac small/medium backends | Adapters and model tags configured | No loaded model or successful answer |
| Frontier/Jev APIs and paid guards | Typed adapters, budget checks, fail-closed tests | No credentials, model/rates, or positive paid run budget |
| 2,000+ benchmark prompts and scorer | 2,500 indexed; math/choice/code and sandbox tests | Two failed validation attempts; zero scored answers |
| Fixed/random, prompted, Jev, DistilBERT, Strands | Policy code and fixture tests; decision-only fixed/random Mac timing | No trained artifact or live model/decision comparison |
| Calibration | Binary/multiclass methods and reliability SVG code | Zero matching samples; no ECE/Brier empirical result |
| Verification/cascade/hybrid | Buffered paths and fixture HTTP tests | No real answer/verifier comparison |
| Scoped semantic cache | Scope/index/check protocol and fixture tests | No real embedding/FAISS model or reuse result |
| Docker, Compose, kind, monitoring | Real ARM image health, Compose scrape, Grafana panels, kind pods | No model inference in containers/pods |
| Locust and resilience | Bounded schedules, raw event reporting, fixture outage | Two short failed requests; steady/spike/soak and live Jev outage pending |
| CI | Workflow and synthetic regressions; local and clean-clone offline tests | Remote CI unrun; Linux platform not locally verified |
| NVIDIA performance | Source-pinned notebook and benchmark/profile/comparison tools | No GPU allocation, vLLM baseline, trace, or candidate |
| Frozen held-out quality comparison | Freeze and identity audit, locked test | Zero scored training/validation coverage; no final policy freeze |
| Costs and figures | Stage ledger and raw-audit coverage SVG | API charges, real capacity, quality/cost curves unknown |
| Technical report and reproduction | Local report, clean-clone walkthrough, commands | Results explicitly limited to existing evidence |

## Integrity checks

At this audit, tracked private `runs/` files and `data/day2_sources/` files: **zero**. The built wheel contained **85 members** and no CUDA/torch-named members. There is no project `LICENSE` file; `CONTRIBUTING.md` records no declared license. A tracked-file secret-pattern scan for common API key and private-key forms returned no matches; it is a heuristic, not a guarantee. Three tracked notebooks have no saved execution outputs. The freeze audit parsed the private manifest to count split IDs, including test IDs, but did not use test prompt text or answers for policy development. The inspected real run has no test records; the test was not executed or used to tune a policy. Do not call the final test “completed.”

## Publication checklist

- Decide a project license and review dataset/model/provider redistribution terms.
- Resolve and record native backend, Jev, frontier, embedding, and Colab model identities; collect compatible real training/validation records and train/reload the fallback.
- Select thresholds only on validation, freeze all generation/routing/scoring settings, and run the held-out comparison once without tuning on test.
- Execute the controlled NVIDIA baseline, diagnostic profile, one evidence-motivated change, and alternating repetitions; preserve every raw result and failed run.
- Complete real cascade/cache/calibration/cost and sustained load evidence; rerun package/CI checks on the intended publication platform.
- Review private artifacts, provider secrets, model outputs, source terms, and destination before any push or release.
