# Full project commit plan

Original target: at least 18 genuine commits on each of six work days, for at least 108 total. These are planning checkpoints, not the current Git subjects or a record of completed work. Day 2 was explicitly changed to 16 commits, with its three dataset adapters combined. More commits are appropriate for additional real fixes. Record actual completion and checks in docs/STATUS.md.

## Day 1 Mac application and Colab execution

| ID | Planned checkpoint topic | Change | Completion evidence |
| --- | --- | --- | --- |
| D1-01 | define full project scope and runtime profiles | Merge full-scope AGENTS.md and map the Mac, Colab, and API execution paths. | Scope checklist retains every original feature. |
| D1-02 | record M3 and notebook environment preflights | Inspect Mac memory/OS and generate the Colab GPU preflight. | Sanitized hardware and version reports; remote checks labeled separately. |
| D1-03 | initialize reproducible package and CLI | Set up uv, package metadata, dependency extras, and CLI entry points. | Clean environment imports the package and shows CLI help. |
| D1-04 | validate backend and policy configuration | Add typed config, environment secret references, and limits. | Invalid/missing configurations fail with useful messages. |
| D1-05 | add gateway API and health endpoints | Implement the text-chat request contract, health, readiness, and model registry endpoints. | Contract tests cover supported and rejected requests. |
| D1-06 | implement asynchronous backend transport | Add reusable async HTTP clients, lifecycle management, and bounded connections. | Offline transport tests demonstrate correct forwarding. |
| D1-07 | connect small Ollama model | Implement Mac small-backend launch/check instructions and real adapter. | One bounded real answer with model ID and runtime label. |
| D1-08 | connect medium Ollama model | Add medium-backend configuration and measure loading/memory feasibility. | Real answer and explicit residency/switching observations, or documented hardware blocker. |
| D1-09 | connect frontier API backend | Implement provider-compatible endpoint, usage parsing, secret handling, and spending controls. | Offline contract checks plus a real request only with configured budget/key. |
| D1-10 | implement nonstreaming gateway responses | Route manually selected tiers through the common API. | Requests reach the requested available backend. |
| D1-11 | implement streaming response forwarding | Forward SSE output without unnecessary full-response buffering. | Fragmented event and completion tests; real streaming smoke where accessible. |
| D1-12 | handle deadlines cancellation and backend errors | Propagate cancellation, release resources, and sanitize failures. | Timeout/cancellation/error-path checks pass. |
| D1-13 | record request traces and usage | Add request IDs, per-stage timestamps, backend identity, and cost status. | Each request creates a consistent secret-free record. |
| D1-14 | add doctor and bounded smoke commands | Validate configuration, model presence, connectivity, and a short request. | Commands explain missing dependencies without silently mocking. |
| D1-15 | add runnable Colab serving notebook | Create ordered setup, pinned-source install, vLLM launch, local client, export, and cleanup cells. | Notebook structure validates; record which cells were actually executed. |
| D1-16 | add Mac and Colab configuration profiles | Keep core CPU dependencies separate from NVIDIA/model-training extras. | Mac core installs without CUDA dependencies. |
| D1-17 | verify gateway integration across profiles | Add offline integration coverage and opt-in real checks. | Offline suite and at least available real-path evidence recorded. |
| D1-18 | publish local setup and checkpoint evidence | Write Mac quickstart, Colab instructions, known limits, and Day 1 status. | A clean reader can locate commands, required model downloads, and evidence. |


## Day 2 Complete benchmark and cost accounting

| ID | Planned checkpoint topic | Change | Completion evidence |
| --- | --- | --- | --- |
| D2-01 | define immutable evaluation records | Specify prompt IDs, task/split, output, outcome, model revision, timings, and cost fields. | Schema validates fixtures and preserves errors separately from wrong answers. |
| D2-02 | load versioned GSM8K prompts | Add a deterministic math dataset adapter with documented revision. | Known sample and answer provenance are reproducible. |
| D2-03 | load versioned MMLU prompts | Add multiple-choice task/subset handling and consistent templates. | Choice ordering and correct-letter extraction verified. |
| D2-04 | load MBPP coding benchmark | Add code-task data and test specification loading. | Dataset/license metadata and task IDs recorded. |
| D2-05 | isolate generated code evaluation | Run code tests in bounded network-disabled sandbox containers on the Mac. | Timeout/resource/exit handling checked; no model code runs directly on the host. |
| D2-06 | freeze deduplicated dataset splits | Create a 2000–3000-prompt target manifest and 60/20/20 splits. | Duplicates/related variants stay within a single split; test use is gated. |
| D2-07 | implement math answer scoring | Normalize valid numerical answers with explicit parser outcomes. | Extractor edge cases and units are audited. |
| D2-08 | implement multiple choice scoring | Parse supported answer forms without guessing ambiguous answers. | Malformed, truncated, and incorrect answers remain distinguishable. |
| D2-09 | integrate sandbox code task scoring | Connect model completions to code checks and structured results. | Known pass/fail/timeout fixtures are classified correctly. |
| D2-10 | add manual scoring audit export | Export 30–50 development answers per task for human review. | Audit corrections are documented before threshold selection. |
| D2-11 | add bounded three tier evaluation runner | Evaluate selected splits on all configured tiers with retries and token/request limits. | No paid job starts without explicit budget configuration. |
| D2-12 | checkpoint and resume evaluation runs | Fingerprint input/model/settings and avoid duplicate completed calls. | Interrupted development run resumes without corrupting records. |
| D2-13 | derive observed hindsight oracle labels | Label the cheapest observed successful tier and handle none-correct cases. | Oracle is reported as an offline bound for the measured outcomes. |
| D2-14 | calculate complete inference cost | Separate API usage, router/verifier costs, and provisioned compute scenarios. | Unknown rates remain unknown; idle capacity is not erased. |
| D2-15 | generate per tier quality reports | Report task/overall accuracy, completion/error rates, and sample counts. | Reports regenerate directly from stored results. |
| D2-16 | add controlled serving baseline runner | Separate quality evaluation from prompt-length/concurrency/arrival-rate workloads. | Client scheduling, warm-up, cache state, and output controls recorded. |
| D2-17 | report latency and throughput baselines | Compute TTFT, appropriate chunk/TPOT metrics, p50/p95, errors, and throughput. | Metric definitions and denominators are explicit. |
| D2-18 | checkpoint real train validation measurements | Run and preserve real train/validation outcomes within hardware/budget limits. | Report progress toward 2000+ total prompts; held-out test stays unused until Day 6. |


## Day 3 Jev and all router comparisons

| ID | Planned checkpoint topic | Change | Completion evidence |
| --- | --- | --- | --- |
| D3-01 | define interchangeable router contract | Return tier, policy/version, probability event, latency, and fallback reason. | A common contract covers every online router. |
| D3-02 | implement fixed and seeded random baselines | Add always-small, always-medium, always-frontier, and random policies. | Selections are reproducible and honor available capabilities. |
| D3-03 | prepare DistilBERT training labels | Use train-split oracle labels and handle none-correct/imbalance explicitly. | No validation/test rows enter training. |
| D3-04 | fine tune DistilBERT router | Train on Colab with logged seed, checkpoint, hyperparameters, and validation. | A real training run or its exact access blocker is recorded. |
| D3-05 | export portable trained router artifact | Save tokenizer, weights, label map, model identities, and evaluation metadata. | Artifact reload produces consistent decisions on fixtures. |
| D3-06 | serve DistilBERT as Mac fallback router | Run the trained classifier on CPU or a verified supported Mac device. | Mac decision latency and memory measured separately from Colab. |
| D3-07 | implement prompted small LLM router | Ask the small model to choose among defined backend capabilities. | Parse invalid outputs explicitly and record generation overhead. |
| D3-08 | implement official Jev client | Use current official SDK/API contract, typed answers, deadlines, and usage. | Offline contract tests and opt-in real request evidence. |
| D3-09 | implement Jev choice routing | Describe actual models and request a tier choice. | Question version and returned probabilities are stored. |
| D3-10 | implement Jev probability threshold routing | Ask explicit small/medium success questions and apply validation thresholds. | Probability event is defined; sequential calls count toward cost/latency. |
| D3-11 | integrate self hosted Strands Decider comparison | Use the current official checkpoint/runtime and a separate decision adapter. | Do not assume typed decisions use generic text-generation vLLM serving. |
| D3-12 | verify router contracts and unavailable tiers | Cover invalid decisions, excessive context, disabled providers, and deadlines. | Tests do not silently upgrade to paid backends. |
| D3-13 | implement calibration measurement | Add reliability plots, ECE, and Brier score for well-defined outcomes. | Do not treat distribution concentration as correctness probability. |
| D3-14 | tune router operating points on validation | Select policies/thresholds under explicit cost and quality objectives. | Freeze tuning inputs; hold test evaluation for Day 6. |
| D3-15 | plot validation cost quality frontiers | Compare all routers with fixed baselines and observed oracle reference. | Include actual sample counts, costs, and probability semantics. |
| D3-16 | benchmark routing overhead on Mac | Measure decision-only p50/p95 and full request overhead. | Warm-up, classifier/device, and model load state documented. |
| D3-17 | dispatch gateway requests through selected router | Integrate policy selection and deterministic fallback under a bounded deadline. | Real requests take the selected backend path where accessible. |
| D3-18 | freeze router configs and comparison evidence | Save policy/model/question versions and the validation summary. | All original comparison methods have implemented/verified/pending status. |


## Day 4 Verification cascades and semantic cache

| ID | Planned checkpoint topic | Change | Completion evidence |
| --- | --- | --- | --- |
| D4-01 | implement Jev answer verifier | Define the prompt-answer correctness event and typed verifier interface. | Verifier outputs and usage are recorded without claiming ground truth. |
| D4-02 | add verifier acceptance policy | Apply configurable thresholds and explicit timeout/failure behavior. | False accept and false reject definitions are testable. |
| D4-03 | implement multi tier verification cascade | Try small, verify, escalate to medium, then frontier as configured. | Bound attempts and retain every attempt's cost and latency. |
| D4-04 | implement route then verify hybrid | Route first, verify eligible outputs, and escalate under the same policy. | Hybrid behavior uses the shared execution trace. |
| D4-05 | enforce cumulative cascade budgets | Carry one deadline and spending/token budget across all attempts. | No retry multiplication or partial streaming before final acceptance. |
| D4-06 | evaluate cascade quality and overhead | Add validation runner for route-first, cascade, and hybrid. | Compare full costs and live latency separately from offline replay. |
| D4-07 | report verifier error tradeoffs | Compute false-accept/reject rates with explicit denominators. | Use scored answers rather than the verifier's own opinions as labels. |
| D4-08 | add portable embedding model adapter | Load a documented compact encoder with pinned revision. | Embedding shape, normalization, latency, and model identity recorded. |
| D4-09 | implement persistent FAISS answer index | Store vectors with answer metadata and bounded persistence behavior. | ARM installation and save/reload path are actually checked. |
| D4-10 | isolate cache request scope and validity | Key system instructions, conversation context, model/policy revision, and generation options. | Cross-context reuse and invalid entries are rejected. |
| D4-11 | retrieve similarity candidate matches | Expose thresholded candidate lookup without automatic answer acceptance. | Similarity scores and empty-index cases checked. |
| D4-12 | verify cache candidates with Jev | Confirm stored answer applicability before returning a candidate. | Verification overhead and false-match decisions recorded. |
| D4-13 | store accepted outputs and manage cache lifecycle | Add insertion, TTL/eviction, reset, and safe metadata updates. | Rejected or incompatible entries do not contaminate future requests. |
| D4-14 | create paraphrase and near miss cache benchmark | Build separate same-meaning, near-miss, and unrelated groups. | Related examples stay within one split; provenance recorded. |
| D4-15 | evaluate verified versus similarity only caching | Measure hit rate, false hits, latency, and cost on validation. | Distinct accuracy and false-hit denominators reported. |
| D4-16 | verify cache persistence and context isolation | Exercise restarts, incompatible config, near misses, and cache disablement. | Tests demonstrate the full validity rules. |
| D4-17 | integrate cache routing cascade execution path | Compose cache lookup, router, generation, verification, tracing, and return. | Each configurable mode has an end-to-end path. |
| D4-18 | record full request path and validation evidence | Document route/cascade/cache modes and known tradeoffs. | Generate copy-ready Day 4 notes from completed code and observed outputs. |


## Day 5 Monitoring deployment and failure tests

| ID | Planned checkpoint topic | Change | Completion evidence |
| --- | --- | --- | --- |
| D5-01 | containerize the gateway for supported architectures | Build the gateway image with external configurable model endpoints. | Mac ARM image starts and passes health checks. |
| D5-02 | add Compose gateway Prometheus Grafana stack | Provide a one-command observability deployment. | Container-to-host model URLs are explicitly tested. |
| D5-03 | instrument request stage metrics | Add counters/histograms for tiers, routing, verification, errors, cache, and spend. | Labels are bounded and private prompts are not metric labels. |
| D5-04 | implement Jev circuit breaker and fallback | Add closed/open/half-open behavior with trained DistilBERT fallback. | Controlled failure tests exercise recovery. |
| D5-05 | bound concurrency and retry behavior | Add backpressure, deadlines, retry jitter, and cancellation semantics. | Retries are capped and output already streamed is not replayed. |
| D5-06 | implement model backend failover policy | Define eligible next-tier behavior and cost/privacy/capability checks. | Unavailable-backend paths remain explicit. |
| D5-07 | configure metrics scraping and aggregation | Scrape gateway and available serving metrics with correct instance labels. | Replica counters/latencies aggregate without double-counting. |
| D5-08 | add operational Grafana dashboards | Visualize tier requests, latency, cache, errors, escalation, fallback, and cost. | Dashboard queries are validated against emitted metrics. |
| D5-09 | implement bounded Locust load scenarios | Add repeatable steady, spike, and soak workloads with recorded parameters. | No run starts beyond configured resource/API limits. |
| D5-10 | record ten minute steady load | Run the documented steady workload against real eligible backends. | Save throughput, latency, error rate, and workload placement. |
| D5-11 | record fivefold two minute load spike | Increase arrival load to five times baseline for two minutes. | Measure overload/queueing behavior and recovery. |
| D5-12 | record one hour soak test | Run bounded moderate traffic for an hour where resources permit. | Capture stability and memory trends, not just a final average. |
| D5-13 | add local kind Kubernetes manifests | Define gateway Deployment, Service, probes, and resource settings. | Local cluster deployment is verified on the Mac. |
| D5-14 | configure external backends and replica state | Resolve host/model reachability, secrets, and per-pod versus shared state. | Do not assume a container's localhost is the Mac or share mutable FAISS files unsafely. |
| D5-15 | verify gateway pod replacement under traffic | Delete one gateway pod and observe replacement/readiness. | Record errors during recovery; do not promise zero errors. |
| D5-16 | verify Jev outage during load | Inject a controlled Jev failure and observe breaker/fallback/recovery. | Dashboard and saved traces show actual behavior. |
| D5-17 | add deterministic offline regression workflow | Run linting, meaningful tests, and 50 fixed mocked prompts on pushes. | No CI secrets or paid calls are required for standard checks. |
| D5-18 | record deployment and failure runbooks | Document start/stop, replica/cache limits, failures, and load evidence. | Every resilience claim links to an observed check or is marked pending. |


## Day 6 GPU investigation final evaluation and release

| ID | Planned checkpoint topic | Change | Completion evidence |
| --- | --- | --- | --- |
| D6-01 | pin Colab NVIDIA serving environment | Record GPU allocation, model/runtime revisions, and configuration. | The notebook imports the same source revision as the reported experiment. |
| D6-02 | capture controlled vLLM baseline | Run a fixed workload with defined lengths, warm-up, cache, and arrival/concurrency. | Preserve raw results and model/server metadata. |
| D6-03 | capture focused GPU execution profile | Collect Nsight Systems or supported profiler evidence on the real GPU. | Record permission/tool limits; keep profiled timings separate. |
| D6-04 | implement one evidence motivated serving change | Change batching/token budget, memory allocation, or another supported observed bottleneck. | A falsifiable hypothesis and exact config/code difference are recorded. |
| D6-05 | compare repeated baseline and candidate runs | Repeat controlled unprofiled timings and report variability. | Retain regressions; no speedup claim without supporting data. |
| D6-06 | run frozen held out router comparison | Evaluate all original policies after configurations and question wording are frozen. | Complete 2000+ total manifest coverage across all three tiers, or report the remaining gap. |
| D6-07 | run held out cascade and cache comparisons | Evaluate cascade/hybrid and verified/unverified cache with frozen thresholds. | No related examples leak into tuning or training. |
| D6-08 | finalize calibration and router timing report | Report defined-event calibration, quality, overhead, and sample uncertainty. | Avoid comparing incompatible confidence meanings. |
| D6-09 | reconcile complete cost and capacity scenarios | Include all model/router/verifier attempts and idle/provisioned GPU assumptions. | Measured spend and modeled capacity costs remain distinct. |
| D6-10 | regenerate final figures from raw records | Build quality/cost, reliability, latency, cache, and performance charts. | Each figure has units, sample counts, and linked input records. |
| D6-11 | finish exact reproducibility and demo commands | Provide Mac, Colab, Compose, and kind workflows plus a five-minute demo. | Command paths and configuration examples match the code. |
| D6-12 | verify installable package and CLI | Build/install the package in a fresh environment and verify entry points. | Normal gateway installation does not require CUDA. |
| D6-13 | verify supported platform and release checks | Run the affected offline suite plus Mac/Linux CI configurations. | State which environments actually executed. |
| D6-14 | perform clean clone user walkthrough | Use a clean checkout to test install, doctor, backend setup, and a real request. | Document prerequisites and blockers encountered by a new user. |
| D6-15 | write public technical findings | Explain methods, all-router comparisons, cascade/cache results, failures, and limitations. | Claims match saved evidence; publication destination remains user-controlled. |
| D6-16 | prepare evidence backed resume and interview notes | Draft accurate bullets and explanations of tradeoffs and debugging. | Use only verified numbers; distinguish implemented from tested. |
| D6-17 | add contributor and artifact provenance guidance | Document code license choice, model/data terms, configs, trained artifacts, and retraining. | Forks can substitute models and understand policy compatibility. |
| D6-18 | checkpoint full project and publication checklist | Audit full-scope acceptance, secrets, artifact sizes, command validity, and local commit history. | Create a local release checkpoint; publish only to a specified authorized destination. |


Day 2 execution note (2026-10-28): the user requested 16 commits instead of this plan's 18. D2-02 through D2-04 were combined into one substantive dataset-adapter commit; all remaining Day 2 checkpoint IDs have their own commits. The D2-18 live model measurement portion is explicitly blocked by unavailable Ollama and unconfigured frontier access; see `docs/DAY2_HANDOFF.md`.
