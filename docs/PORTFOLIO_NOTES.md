# Evidence-backed portfolio notes (draft)

These are proposed descriptions of the project, not claims of independent authorship or verified model superiority. Keep the evidence links with any quantitative claim and revisit wording after real experiments.

## Resume-safe statements

- Built a three-tier text gateway with explicit and automatic routing, a typed Jev decision boundary, artifact-gated DistilBERT fallback, bounded spending controls, verification cascades, and scoped semantic caching. A real v2 small-tier validation set scored 324/500 overall, with 50% strict-format compliance; this is a single-tier result, not a routing comparison. Evidence: `src/jev_gateway/`, [feature status](FEATURE_STATUS.md), [v2 coverage audit](../evidence/day7/local-v2-coverage-audit-20261114.json), and [current test evidence](../evidence/testing/maintenance-offline-20261117.txt).
- Built local observability and deployment paths with an ARM container, Compose/Prometheus/Grafana, kind, and bounded Locust workload definitions. In one Mac kind API pod-replacement check, 39 of 40 catalog requests returned HTTP 200 and one failed to connect over 4.8128 seconds. This is **API availability**, not inference capacity. Evidence: `evidence/day5/kind-pod-replacement-20261031.json` and [Day 5 handoff](DAY5_HANDOFF.md).
- Prepared a reproducible 2,500-prompt math/choice/code evaluation with 1,500 train, 500 validation, and 500 locked test prompts, explicit score/coverage records, and a freeze audit. The small tier has a complete 500-prompt validation result set and 578 train checkpoints; complete multi-tier labels and a frozen accuracy comparison are still absent. Evidence: [manifest index](day2-manifest-index.jsonl), [v2 coverage audit](../evidence/day7/local-v2-coverage-audit-20261114.json), and [technical report](TECHNICAL_REPORT.md).
- Prepared a source-pinned Colab vLLM benchmark and optional Nsight Systems diagnostic path that preserves request-level outcomes and blocks optimization without successful baselines. **No NVIDIA runtime or speedup has yet been measured.** Evidence: [notebook](../notebooks/day6_nvidia.ipynb) and [protocol](DAY6_PROTOCOL.md).

## Interview explanation prompts with supported answers

**Main bottleneck encountered.** The research bottleneck is incomplete compatible evidence: small-tier v2 validation is scored, but train coverage is partial and medium/frontier train and validation are incomplete. Ollama is currently unreachable, frontier and Jev are unconfigured, and no Colab GPU run occurred. Training, calibration, a fair frozen test, and an evidence-motivated GPU optimization therefore remain pending. There is no diagnosed GPU kernel bottleneck.

**Tradeoff.** Verification and semantic reuse may reduce repeated generation or harmful answers, but they add decision and embedding cost and can fail. The code therefore treats similarity as a candidate, scopes it by context/model identity, and requires explicit Jev applicability for verified reuse. An unavailable verifier fails closed. The tradeoff is implemented and fixture-tested; its empirical payoff is unknown.

**Actual debugging example.** The short Day 5 Locust run stopped after two failed backend requests in 1.884353 seconds while the periodic CSV still showed zero requests and `N/A` percentiles. The reporter was changed to preserve raw per-request events and flag the count mismatch. This is an observability bug and fix, not a throughput result. Evidence: [Day 5 experiment ledger](EXPERIMENTS.md) and `evidence/day5/locust-smoke-*20261031T194858Z.*`.

**Fair comparisons.** The project separates train, validation, and locked test; uses prompt/group identity, model/settings fingerprints, and independent scoring; retains failures and unknown costs; and requires paired workload/config checks for repeated NVIDIA runs. The Day 6 comparator refuses profiled timing runs and mismatched arrivals/concurrency. These controls describe a method; final comparisons have not been executed.

**What remains unproven.** Quality retention, dollar savings, harmful cache reuse, Jev calibration, DistilBERT accuracy, real inference capacity, and NVIDIA speedup are not established. The latest 152-test Mac suite and clean-clone health check establish software behavior and packaging only.
