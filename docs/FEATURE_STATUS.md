# Feature status

This table distinguishes implemented code from real backend verification. See [experiment evidence](EXPERIMENTS.md) for observed commands and outputs.

| Component | Implementation | Verification | Remaining work |
| --- | --- | --- | --- |
| Explicit-tier gateway API and streaming | Implemented | Offline contract, transport, dispatch, streaming, and error tests; loopback health check | Real generation and streaming answers |
| Small Ollama tier | Adapter and configured candidate tag | Offline adapter checks; live connection failed | Start Ollama, pull model, record actual identity and memory |
| Medium Ollama tier | Adapter and configured candidate tag | Offline adapter checks; live connection failed | Pull model and measure load, memory, and answer path |
| Frontier API | Compatible transport and process-local admission guard | Offline configuration and budget checks | Key, model, sourced rates, positive caps, and authorized paid check |
| Colab vLLM notebook | Prepared | Notebook structure and syntax checked | Actual GPU allocation and notebook execution |
| Versioned benchmark adapters and split index | Implemented | Pinned source files loaded; 2,500 unique IDs/groups; split counts checked | Assess semantic duplicates and dataset redistribution terms |
| Math, choice, and code scoring | Implemented | Edge-case tests; Docker pass/fail/crash/timeout fixtures | Human audit of model outputs and scorer corrections if needed |
| Bounded three-tier quality runner and resumption | Implemented | Offline budget/resume tests; two live local attempts failed to connect | Collect real train/validation outputs across all tiers |
| Cost accounting and hindsight labels | Implemented | Offline retry/cost/oracle tests | Real usage, sourced price inputs, complete training observations |
| Quality, serving, calibration, and router comparison reports | Implemented | Offline metric tests; validation replay produced zero plottable points | Real model answers, router decisions, sourced costs |
| Jev choice/success routing and DistilBERT fallback | Implemented; trained fallback artifact absent | Offline contract and failure tests; no live Jev or classifier run | Paid access, complete train/validation labels, Colab training, Mac artifact benchmark |
| Prompted LLM and Strands Decider comparisons | Implemented adapters | Offline typed/prompt contract checks; no live model run | Ollama and pinned Strands checkpoint/runtime |
| Verification cascades and semantic cache | Implemented as optional buffered modes and local pinned cache path | Offline contract, persistence-fixture, and HTTP integration tests; no live Jev, embedding, FAISS, or generator run | Select validation thresholds, install pinned model/FAISS, configure paid gates, and measure real behavior |
| Compose, Prometheus, Grafana, kind | Implemented local profiles | ARM image health, Compose scrape up, 14-panel Grafana provisioning, two kind pods ready; native Ollama unavailable from container/pod | Real backend connectivity and model residency; repeated multi-replica observation |
| Locust load and failure tests | Bounded scenarios and raw-event reporter implemented | Two-request backend-failure wiring check; pod replacement 39/40 successful API requests; Jev outage offline fixture | Ten-minute real steady, two-minute fivefold-rate spike, one-hour soak, live Jev outage |
| Offline CI regression | Workflow and 50 synthetic fixed HTTP cases implemented | Local 118-test suite and focused lint pass | Remote CI execution and clean-checkout confirmation |
| NVIDIA profiling and final report | Source-pinned Colab notebook, bounded benchmark/profile tools, comparison gates, coverage figure, and draft technical report implemented | Notebook syntax and offline tools tested; no NVIDIA execution | Colab allocation, actual baseline/profile/candidate, frozen held-out evaluation |
| Public release | Not requested | None | Destination and explicit publishing instruction |
