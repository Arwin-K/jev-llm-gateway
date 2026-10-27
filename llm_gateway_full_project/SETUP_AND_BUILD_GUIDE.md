# Full Jev gateway project on M3 and Colab

This guide replaces the earlier reduced-scope plans. It preserves the complete original project and organizes it into six intensive build days, each with at least 18 meaningful commit checkpoints. The planned minimum is 108 commits.

Your learning journal is handwritten. The separate HANDWRITTEN_JOURNAL.md contains finished concept notes you can copy. The end-of-day prompt produces complete journal prose grounded in the work and results actually observed. No digital personal journal, mastery tracker, quizzes, or reflection forms are required.

All original components remain in scope. Six days is an aggressive execution target, not a guarantee that provider access, notebook quotas, full evaluations, and every integration check will finish. Record an access-dependent feature as implemented but unverified when appropriate; never relabel it as a completed real integration.

## What full scope means

| Original deliverable | Required implementation and evidence |
| --- | --- |
| Small and medium self-hosted models plus frontier API | Real backend configurations and available integration checks; actual model identities |
| Jev routing | Choice and success-probability designs with versioned questions |
| Trained fallback | Actual DistilBERT fine-tuning and reloadable runtime artifact |
| Other routers | Fixed tiers, random, prompted LLM, self-hosted Strands Decider, offline oracle reference |
| Full evaluation | 2000+ prompts across math, multiple-choice, and coding tasks, all three tiers |
| Calibration and latency | Defined probability events, reliability diagrams, ECE, router overhead |
| Answer verification | Jev verifier, cascade, hybrid, false-accept/reject measurements |
| Semantic cache | Compact embeddings, persistent FAISS index, context validity, Jev candidate verification |
| Monitoring | Prometheus and Grafana for request stages, cache, spending, errors, and fallback |
| Reliability | Deadlines, bounded retries, circuit breaker, trained fallback, eligible model failover |
| Deployment | Mac application, Docker Compose, local kind Kubernetes, replica failure test |
| Load tests | 10-minute steady, fivefold 2-minute spike, one-hour soak |
| CI | Lint/tests and 50 fixed mocked regression prompts |
| Technical findings | Reproducible report, figures, README/demo, accurate resume notes, publication drafts |
| NVIDIA investigation | Colab vLLM baseline, profiling where supported, controlled repeated comparison |
| Forkable repository | Installable gateway, configuration examples, notebooks, compatibility/provenance guidance |

The M3 adaptation changes the local generation runtime to native Ollama. Colab retains the NVIDIA/vLLM experiment path. The specialized open decision model uses its verified official inference runtime, which need not be a generative vLLM server. These runtime changes preserve the original experiments rather than removing features.

## What runs where

| Component | Mac | Colab |
| --- | --- | --- |
| Development and everyday gateway | Main application | Same source for notebook-local tests |
| Small/medium models | Native Ollama when memory permits | Compatible vLLM GPU configurations |
| DistilBERT | Exported trained artifact for fallback | Fine-tuning and evaluation |
| Strands Decider | Supported official Mac/CPU runtime if feasible | Supported official GPU runtime if feasible |
| Embeddings and FAISS cache | Normal application | Optional cross-environment verification |
| Generated-code scoring | Isolated bounded Docker sandbox | Generate/export answers for later sandbox scoring |
| Docker, Grafana, Prometheus, kind | Deployment and failure tests | Not a workaround for notebook limits |
| NVIDIA profiling | Not applicable to M3 execution | Actual allocated NVIDIA GPU |
| Jev and frontier APIs | Configured external services | Optional bounded evaluation calls |

A Colab notebook is an interactive testing environment. Keep server, gateway, and client in that runtime when testing there. The Mac app must not depend on a permanent notebook URL or public tunnel.

Do not assume two generation models, a classifier, an embedding model, a decision model, Docker, and Kubernetes all fit in memory simultaneously. Inspect actual unified memory and profile resource use. Stage experiments and deployment tests as necessary. Sequential model evaluation is valid for collecting outcomes but is not evidence of live multi-model routing latency. Full live verification needs actual reachable backends.

## Setup order

1. Extract the new starter into a new folder, or merge its prompts/instructions into your existing repository with Codex. Preserve your existing work.
2. Install VS Code, Git, uv, and the Codex IDE integration.
3. Install Ollama for Apple Silicon and start the native application.
4. Install Docker Desktop for Apple Silicon. Use its normal installation and account/license flow.
5. If Homebrew is already installed, install the local cluster tools with brew install kind kubectl. Otherwise follow their official installers.
6. Open the actual project folder in VS Code and sign in to Codex normally.
7. Run the bootstrap prompt, then the Day 1 prompt. Complete/check/commit each checkpoint rather than generating the entire repository in one opaque step.
8. Configure your own Jev and frontier accounts/keys and a run budget. Do not put keys in prompts or tracked files.
9. Open the Colab notebook generated on Day 1, choose an available GPU runtime, run preflight cells, and save the actual allocation.
10. Keep notebook results, trained artifacts, and immutable raw logs exported before sessions disappear.

For a new repository, the gateway initialization starts with:

~~~bash
git init
uv python install 3.12
uv init --bare --python 3.12
~~~

Let Day 1 establish actual core and optional dependency groups. Core gateway installation should not pull CUDA packages. Training, embeddings, decision models, GPU serving, and evaluation extras are installed only in their required environments.

Do not rerun initialization over an existing pyproject.toml or replace established Git settings. Codex should inspect and adapt.

Check Mac tools:

~~~bash
git --version
uv --version
ollama --version
docker --version
docker compose version
kind version
kubectl version --client
~~~

A tool version check does not prove the application or backend works. The checkpoint plan includes real smoke checks.

Use a small instruction model around 1–3B and an appropriate quantized medium model around 7–8B as the original role targets, subject to actual memory and supported model cards. Configure actual IDs after preflight. If hardware cannot sustain the intended setup, record the required resource and live-verification blocker; do not silently drop the medium tier or report sequential runs as simultaneous serving.

Recommended ports: gateway 8080, native Ollama 11434, Colab small vLLM 8000, optional second notebook server 8001. Container/pod-to-host addresses must be verified; localhost inside a container refers to that container.

## Commit workflow

The requirement is at least 18 real commits per work day. The plan supplies 18 coherent implementation checkpoints daily, grouped into six work blocks of three. Additional real bug fixes or documentation corrections can create more commits.

For each checkpoint:
1. Implement the behavior or substantive artifact.
2. Run the appropriate focused verification.
3. Review and stage only the related diff.
4. Commit with the checkpoint ID and descriptive subject.
5. Record actual evidence and proceed.

A real checkpoint can include production code with its related test and documentation. Do not split every line into separate commits. Do not create empty commits, reverse changes artificially, or modify timestamps to fill a quota. Actual failures and blocked access remain visible.

Use actual committer timestamps to count daily work in America/Toronto. Do not backdate activity. A day with unresolved infrastructure can fall short of its target; that is a scheduling fact to report, not a number to invent.

Local commits are authorized by this plan. Publishing to a remote remains tied to the destination and instructions you provide. Preserve truthful authorship and existing repository rules.

## Handwritten journal workflow

Use HANDWRITTEN_JOURNAL.md as ready-to-copy study notes. It has six entries, each divided into six small passages aligned with groups of three commits.

At the end of a session, paste prompts/end_day_journal.md. Codex should inspect the actual repository and outputs, then write a complete entry in chat covering the changes, concepts, tradeoffs, observed bugs, checks/results, limitations, and next step.

It should not ask you to fill a template. It should not invent completed work, personal mastery, independent authorship, or measurements. Prewritten concept explanations can be copied immediately; experiment conclusions require the actual experiment.

Engineering files such as docs/STATUS.md and docs/EXPERIMENTS.md still track code state and evidence. They are not a digital personal-learning system.

## Before starting

Paste prompts/00_bootstrap.md. It supersedes earlier instructions that deferred original components. Then paste one daily prompt at a time in the same repository.

The guide and starter describe requested work. Preparing them did not implement the gateway, create application commits, train a model, execute a load test, or perform a GPU benchmark.


## Bootstrap prompt

~~~text
Apply this revised project direction to the current repository. This is a planning/setup task before Day 1; do not prematurely implement or commit all daily work.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


Create or merge AGENTS.md with this contract and create the engineering evidence files. Use docs/COMMIT_PLAN.md as the 108-checkpoint plan and docs/STATUS.md to track actual implementation, verification, blockers, and checkpoint completion.

Inspect the M3 Mac's OS, unified memory, available disk, and installed tools. Prepare a Colab preflight that records its actual GPU allocation and versions. Select supported small/medium model candidates only after assessing memory. Keep two self-hosted tiers and the frontier tier in the full acceptance requirements; if simultaneous residency cannot work, document sequential evaluation separately from live routing and identify the real resource requirement rather than silently removing a tier.

Check current official Ollama, vLLM, TypeSafe, model, DistilBERT/Transformers, Strands Decider, FAISS, Docker, and kind instructions as each integration is implemented. Do not assume specialized decision-model heads work through an ordinary generative chat server. Keep Jev central.

Prepare reproducible gateway and serving/training environments. Add platform-specific install/start/stop instructions, configuration examples, and clear secret handling. Use native Ollama on the Mac and notebook-local vLLM for NVIDIA experiments. Do not make Colab a public tunnel backend for the Mac application.

Explain the exact setup sequence and the first three actions. Then wait for the Day 1 prompt. Report readiness and manual access needs honestly. Do not ask me to adopt a digital journal.

~~~

## All 108 commit checkpoints

Target: at least 18 genuine commits on each of six work days, for at least 108 total. These are checkpoints to execute, not a record of completed work. More commits are appropriate for additional real fixes. Record actual completion and checks in docs/STATUS.md.

## Day 1 Mac application and Colab execution

| ID | Commit subject | Change | Completion evidence |
| --- | --- | --- | --- |
| D1-01 | docs: define full project scope and runtime profiles | Merge full-scope AGENTS.md and map the Mac, Colab, and API execution paths. | Scope checklist retains every original feature. |
| D1-02 | chore: record M3 and notebook environment preflights | Inspect Mac memory/OS and generate the Colab GPU preflight. | Sanitized hardware and version reports; remote checks labeled separately. |
| D1-03 | build: initialize reproducible package and CLI | Set up uv, package metadata, dependency extras, and CLI entry points. | Clean environment imports the package and shows CLI help. |
| D1-04 | feat: validate backend and policy configuration | Add typed config, environment secret references, and limits. | Invalid/missing configurations fail with useful messages. |
| D1-05 | feat: add gateway API and health endpoints | Implement the text-chat request contract, health, readiness, and model registry endpoints. | Contract tests cover supported and rejected requests. |
| D1-06 | feat: implement asynchronous backend transport | Add reusable async HTTP clients, lifecycle management, and bounded connections. | Offline transport tests demonstrate correct forwarding. |
| D1-07 | feat: connect small Ollama model | Implement Mac small-backend launch/check instructions and real adapter. | One bounded real answer with model ID and runtime label. |
| D1-08 | feat: connect medium Ollama model | Add medium-backend configuration and measure loading/memory feasibility. | Real answer and explicit residency/switching observations, or documented hardware blocker. |
| D1-09 | feat: connect frontier API backend | Implement provider-compatible endpoint, usage parsing, secret handling, and spending controls. | Offline contract checks plus a real request only with configured budget/key. |
| D1-10 | feat: implement nonstreaming gateway responses | Route manually selected tiers through the common API. | Requests reach the requested available backend. |
| D1-11 | feat: implement streaming response forwarding | Forward SSE output without unnecessary full-response buffering. | Fragmented event and completion tests; real streaming smoke where accessible. |
| D1-12 | fix: handle deadlines cancellation and backend errors | Propagate cancellation, release resources, and sanitize failures. | Timeout/cancellation/error-path checks pass. |
| D1-13 | feat: record request traces and usage | Add request IDs, per-stage timestamps, backend identity, and cost status. | Each request creates a consistent secret-free record. |
| D1-14 | feat: add doctor and bounded smoke commands | Validate configuration, model presence, connectivity, and a short request. | Commands explain missing dependencies without silently mocking. |
| D1-15 | feat: add runnable Colab serving notebook | Create ordered setup, pinned-source install, vLLM launch, local client, export, and cleanup cells. | Notebook structure validates; record which cells were actually executed. |
| D1-16 | feat: add Mac and Colab configuration profiles | Keep core CPU dependencies separate from NVIDIA/model-training extras. | Mac core installs without CUDA dependencies. |
| D1-17 | test: verify gateway integration across profiles | Add offline integration coverage and opt-in real checks. | Offline suite and at least available real-path evidence recorded. |
| D1-18 | docs: publish local setup and checkpoint evidence | Write Mac quickstart, Colab instructions, known limits, and Day 1 status. | A clean reader can locate commands, required model downloads, and evidence. |


## Day 2 Complete benchmark and cost accounting

| ID | Commit subject | Change | Completion evidence |
| --- | --- | --- | --- |
| D2-01 | feat: define immutable evaluation records | Specify prompt IDs, task/split, output, outcome, model revision, timings, and cost fields. | Schema validates fixtures and preserves errors separately from wrong answers. |
| D2-02 | feat: load versioned GSM8K prompts | Add a deterministic math dataset adapter with documented revision. | Known sample and answer provenance are reproducible. |
| D2-03 | feat: load versioned MMLU prompts | Add multiple-choice task/subset handling and consistent templates. | Choice ordering and correct-letter extraction verified. |
| D2-04 | feat: load MBPP coding benchmark | Add code-task data and test specification loading. | Dataset/license metadata and task IDs recorded. |
| D2-05 | feat: isolate generated code evaluation | Run code tests in bounded network-disabled sandbox containers on the Mac. | Timeout/resource/exit handling checked; no model code runs directly on the host. |
| D2-06 | feat: freeze deduplicated dataset splits | Create a 2000–3000-prompt target manifest and 60/20/20 splits. | Duplicates/related variants stay within a single split; test use is gated. |
| D2-07 | feat: implement math answer scoring | Normalize valid numerical answers with explicit parser outcomes. | Extractor edge cases and units are audited. |
| D2-08 | feat: implement multiple choice scoring | Parse supported answer forms without guessing ambiguous answers. | Malformed, truncated, and incorrect answers remain distinguishable. |
| D2-09 | feat: integrate sandbox code task scoring | Connect model completions to code checks and structured results. | Known pass/fail/timeout fixtures are classified correctly. |
| D2-10 | test: add manual scoring audit export | Export 30–50 development answers per task for human review. | Audit corrections are documented before threshold selection. |
| D2-11 | feat: add bounded three tier evaluation runner | Evaluate selected splits on all configured tiers with retries and token/request limits. | No paid job starts without explicit budget configuration. |
| D2-12 | feat: checkpoint and resume evaluation runs | Fingerprint input/model/settings and avoid duplicate completed calls. | Interrupted development run resumes without corrupting records. |
| D2-13 | feat: derive observed hindsight oracle labels | Label the cheapest observed successful tier and handle none-correct cases. | Oracle is reported as an offline bound for the measured outcomes. |
| D2-14 | feat: calculate complete inference cost | Separate API usage, router/verifier costs, and provisioned compute scenarios. | Unknown rates remain unknown; idle capacity is not erased. |
| D2-15 | feat: generate per tier quality reports | Report task/overall accuracy, completion/error rates, and sample counts. | Reports regenerate directly from stored results. |
| D2-16 | feat: add controlled serving baseline runner | Separate quality evaluation from prompt-length/concurrency/arrival-rate workloads. | Client scheduling, warm-up, cache state, and output controls recorded. |
| D2-17 | feat: report latency and throughput baselines | Compute TTFT, appropriate chunk/TPOT metrics, p50/p95, errors, and throughput. | Metric definitions and denominators are explicit. |
| D2-18 | data: checkpoint real train validation measurements | Run and preserve real train/validation outcomes within hardware/budget limits. | Report progress toward 2000+ total prompts; held-out test stays unused until Day 6. |


## Day 3 Jev and all router comparisons

| ID | Commit subject | Change | Completion evidence |
| --- | --- | --- | --- |
| D3-01 | feat: define interchangeable router contract | Return tier, policy/version, probability event, latency, and fallback reason. | A common contract covers every online router. |
| D3-02 | feat: implement fixed and seeded random baselines | Add always-small, always-medium, always-frontier, and random policies. | Selections are reproducible and honor available capabilities. |
| D3-03 | feat: prepare DistilBERT training labels | Use train-split oracle labels and handle none-correct/imbalance explicitly. | No validation/test rows enter training. |
| D3-04 | feat: fine tune DistilBERT router | Train on Colab with logged seed, checkpoint, hyperparameters, and validation. | A real training run or its exact access blocker is recorded. |
| D3-05 | feat: export portable trained router artifact | Save tokenizer, weights, label map, model identities, and evaluation metadata. | Artifact reload produces consistent decisions on fixtures. |
| D3-06 | feat: serve DistilBERT as Mac fallback router | Run the trained classifier on CPU or a verified supported Mac device. | Mac decision latency and memory measured separately from Colab. |
| D3-07 | feat: implement prompted small LLM router | Ask the small model to choose among defined backend capabilities. | Parse invalid outputs explicitly and record generation overhead. |
| D3-08 | feat: implement official Jev client | Use current official SDK/API contract, typed answers, deadlines, and usage. | Offline contract tests and opt-in real request evidence. |
| D3-09 | feat: implement Jev choice routing | Describe actual models and request a tier choice. | Question version and returned probabilities are stored. |
| D3-10 | feat: implement Jev probability threshold routing | Ask explicit small/medium success questions and apply validation thresholds. | Probability event is defined; sequential calls count toward cost/latency. |
| D3-11 | feat: integrate self hosted Strands Decider comparison | Use the current official checkpoint/runtime and a separate decision adapter. | Do not assume typed decisions use generic text-generation vLLM serving. |
| D3-12 | test: verify router contracts and unavailable tiers | Cover invalid decisions, excessive context, disabled providers, and deadlines. | Tests do not silently upgrade to paid backends. |
| D3-13 | feat: implement calibration measurement | Add reliability plots, ECE, and Brier score for well-defined outcomes. | Do not treat distribution concentration as correctness probability. |
| D3-14 | feat: tune router operating points on validation | Select policies/thresholds under explicit cost and quality objectives. | Freeze tuning inputs; hold test evaluation for Day 6. |
| D3-15 | feat: plot validation cost quality frontiers | Compare all routers with fixed baselines and observed oracle reference. | Include actual sample counts, costs, and probability semantics. |
| D3-16 | feat: benchmark routing overhead on Mac | Measure decision-only p50/p95 and full request overhead. | Warm-up, classifier/device, and model load state documented. |
| D3-17 | feat: dispatch gateway requests through selected router | Integrate policy selection and deterministic fallback under a bounded deadline. | Real requests take the selected backend path where accessible. |
| D3-18 | docs: freeze router configs and comparison evidence | Save policy/model/question versions and the validation summary. | All original comparison methods have implemented/verified/pending status. |


## Day 4 Verification cascades and semantic cache

| ID | Commit subject | Change | Completion evidence |
| --- | --- | --- | --- |
| D4-01 | feat: implement Jev answer verifier | Define the prompt-answer correctness event and typed verifier interface. | Verifier outputs and usage are recorded without claiming ground truth. |
| D4-02 | feat: add verifier acceptance policy | Apply configurable thresholds and explicit timeout/failure behavior. | False accept and false reject definitions are testable. |
| D4-03 | feat: implement multi tier verification cascade | Try small, verify, escalate to medium, then frontier as configured. | Bound attempts and retain every attempt's cost and latency. |
| D4-04 | feat: implement route then verify hybrid | Route first, verify eligible outputs, and escalate under the same policy. | Hybrid behavior uses the shared execution trace. |
| D4-05 | feat: enforce cumulative cascade budgets | Carry one deadline and spending/token budget across all attempts. | No retry multiplication or partial streaming before final acceptance. |
| D4-06 | feat: evaluate cascade quality and overhead | Add validation runner for route-first, cascade, and hybrid. | Compare full costs and live latency separately from offline replay. |
| D4-07 | feat: report verifier error tradeoffs | Compute false-accept/reject rates with explicit denominators. | Use scored answers rather than the verifier's own opinions as labels. |
| D4-08 | feat: add portable embedding model adapter | Load a documented compact encoder with pinned revision. | Embedding shape, normalization, latency, and model identity recorded. |
| D4-09 | feat: implement persistent FAISS answer index | Store vectors with answer metadata and bounded persistence behavior. | ARM installation and save/reload path are actually checked. |
| D4-10 | feat: isolate cache request scope and validity | Key system instructions, conversation context, model/policy revision, and generation options. | Cross-context reuse and invalid entries are rejected. |
| D4-11 | feat: retrieve similarity candidate matches | Expose thresholded candidate lookup without automatic answer acceptance. | Similarity scores and empty-index cases checked. |
| D4-12 | feat: verify cache candidates with Jev | Confirm stored answer applicability before returning a candidate. | Verification overhead and false-match decisions recorded. |
| D4-13 | feat: store accepted outputs and manage cache lifecycle | Add insertion, TTL/eviction, reset, and safe metadata updates. | Rejected or incompatible entries do not contaminate future requests. |
| D4-14 | data: create paraphrase and near miss cache benchmark | Build separate same-meaning, near-miss, and unrelated groups. | Related examples stay within one split; provenance recorded. |
| D4-15 | feat: evaluate verified versus similarity only caching | Measure hit rate, false hits, latency, and cost on validation. | Distinct accuracy and false-hit denominators reported. |
| D4-16 | test: verify cache persistence and context isolation | Exercise restarts, incompatible config, near misses, and cache disablement. | Tests demonstrate the full validity rules. |
| D4-17 | feat: integrate cache routing cascade execution path | Compose cache lookup, router, generation, verification, tracing, and return. | Each configurable mode has an end-to-end path. |
| D4-18 | docs: record full request path and validation evidence | Document route/cascade/cache modes and known tradeoffs. | Generate copy-ready Day 4 notes from completed code and observed outputs. |


## Day 5 Monitoring deployment and failure tests

| ID | Commit subject | Change | Completion evidence |
| --- | --- | --- | --- |
| D5-01 | build: containerize the gateway for supported architectures | Build the gateway image with external configurable model endpoints. | Mac ARM image starts and passes health checks. |
| D5-02 | build: add Compose gateway Prometheus Grafana stack | Provide a one-command observability deployment. | Container-to-host model URLs are explicitly tested. |
| D5-03 | feat: instrument request stage metrics | Add counters/histograms for tiers, routing, verification, errors, cache, and spend. | Labels are bounded and private prompts are not metric labels. |
| D5-04 | feat: implement Jev circuit breaker and fallback | Add closed/open/half-open behavior with trained DistilBERT fallback. | Controlled failure tests exercise recovery. |
| D5-05 | feat: bound concurrency and retry behavior | Add backpressure, deadlines, retry jitter, and cancellation semantics. | Retries are capped and output already streamed is not replayed. |
| D5-06 | feat: implement model backend failover policy | Define eligible next-tier behavior and cost/privacy/capability checks. | Unavailable-backend paths remain explicit. |
| D5-07 | build: configure metrics scraping and aggregation | Scrape gateway and available serving metrics with correct instance labels. | Replica counters/latencies aggregate without double-counting. |
| D5-08 | feat: add operational Grafana dashboards | Visualize tier requests, latency, cache, errors, escalation, fallback, and cost. | Dashboard queries are validated against emitted metrics. |
| D5-09 | test: implement bounded Locust load scenarios | Add repeatable steady, spike, and soak workloads with recorded parameters. | No run starts beyond configured resource/API limits. |
| D5-10 | perf: record ten minute steady load | Run the documented steady workload against real eligible backends. | Save throughput, latency, error rate, and workload placement. |
| D5-11 | perf: record fivefold two minute load spike | Increase arrival load to five times baseline for two minutes. | Measure overload/queueing behavior and recovery. |
| D5-12 | perf: record one hour soak test | Run bounded moderate traffic for an hour where resources permit. | Capture stability and memory trends, not just a final average. |
| D5-13 | deploy: add local kind Kubernetes manifests | Define gateway Deployment, Service, probes, and resource settings. | Local cluster deployment is verified on the Mac. |
| D5-14 | deploy: configure external backends and replica state | Resolve host/model reachability, secrets, and per-pod versus shared state. | Do not assume a container's localhost is the Mac or share mutable FAISS files unsafely. |
| D5-15 | test: verify gateway pod replacement under traffic | Delete one gateway pod and observe replacement/readiness. | Record errors during recovery; do not promise zero errors. |
| D5-16 | test: verify Jev outage during load | Inject a controlled Jev failure and observe breaker/fallback/recovery. | Dashboard and saved traces show actual behavior. |
| D5-17 | ci: add deterministic offline regression workflow | Run linting, meaningful tests, and 50 fixed mocked prompts on pushes. | No CI secrets or paid calls are required for standard checks. |
| D5-18 | docs: record deployment and failure runbooks | Document start/stop, replica/cache limits, failures, and load evidence. | Every resilience claim links to an observed check or is marked pending. |


## Day 6 GPU investigation final evaluation and release

| ID | Commit subject | Change | Completion evidence |
| --- | --- | --- | --- |
| D6-01 | perf: pin Colab NVIDIA serving environment | Record GPU allocation, model/runtime revisions, and configuration. | The notebook imports the same source revision as the reported experiment. |
| D6-02 | perf: capture controlled vLLM baseline | Run a fixed workload with defined lengths, warm-up, cache, and arrival/concurrency. | Preserve raw results and model/server metadata. |
| D6-03 | perf: capture focused GPU execution profile | Collect Nsight Systems or supported profiler evidence on the real GPU. | Record permission/tool limits; keep profiled timings separate. |
| D6-04 | perf: implement one evidence motivated serving change | Change batching/token budget, memory allocation, or another supported observed bottleneck. | A falsifiable hypothesis and exact config/code difference are recorded. |
| D6-05 | perf: compare repeated baseline and candidate runs | Repeat controlled unprofiled timings and report variability. | Retain regressions; no speedup claim without supporting data. |
| D6-06 | eval: run frozen held out router comparison | Evaluate all original policies after configurations and question wording are frozen. | Complete 2000+ total manifest coverage across all three tiers, or report the remaining gap. |
| D6-07 | eval: run held out cascade and cache comparisons | Evaluate cascade/hybrid and verified/unverified cache with frozen thresholds. | No related examples leak into tuning or training. |
| D6-08 | eval: finalize calibration and router timing report | Report defined-event calibration, quality, overhead, and sample uncertainty. | Avoid comparing incompatible confidence meanings. |
| D6-09 | eval: reconcile complete cost and capacity scenarios | Include all model/router/verifier attempts and idle/provisioned GPU assumptions. | Measured spend and modeled capacity costs remain distinct. |
| D6-10 | report: regenerate final figures from raw records | Build quality/cost, reliability, latency, cache, and performance charts. | Each figure has units, sample counts, and linked input records. |
| D6-11 | docs: finish exact reproducibility and demo commands | Provide Mac, Colab, Compose, and kind workflows plus a five-minute demo. | Command paths and configuration examples match the code. |
| D6-12 | build: verify installable package and CLI | Build/install the package in a fresh environment and verify entry points. | Normal gateway installation does not require CUDA. |
| D6-13 | test: verify supported platform and release checks | Run the affected offline suite plus Mac/Linux CI configurations. | State which environments actually executed. |
| D6-14 | test: perform clean clone user walkthrough | Use a clean checkout to test install, doctor, backend setup, and a real request. | Document prerequisites and blockers encountered by a new user. |
| D6-15 | docs: write public technical findings | Explain methods, all-router comparisons, cascade/cache results, failures, and limitations. | Claims match saved evidence; publication destination remains user-controlled. |
| D6-16 | docs: prepare evidence backed resume and interview notes | Draft accurate bullets and explanations of tradeoffs and debugging. | Use only verified numbers; distinguish implemented from tested. |
| D6-17 | docs: add contributor and artifact provenance guidance | Document code license choice, model/data terms, configs, trained artifacts, and retraining. | Forks can substitute models and understand policy compatibility. |
| D6-18 | release: checkpoint full project and publication checklist | Audit full-scope acceptance, secrets, artifact sizes, command validity, and local commit history. | Create a local release checkpoint; publish only to a specified authorized destination. |


## Daily Codex prompts

### Day 1 Mac application and Colab execution

Paste this entire prompt into Codex in the same project repository.

~~~text
Continue Day 1 of the FULL original Jev project. Read AGENTS.md, docs/STATUS.md, docs/COMMIT_PLAN.md, current source, and relevant experiment outputs. Resolve any earlier dependency that blocks today's work without reverting to the reduced-scope plan.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


TODAY'S ENGINEERING REQUIREMENTS

Build the real user path first. Implement a documented text-only chat API at /v1/chat/completions with model=auto later and explicit-tier dispatch now. Preserve standard response semantics, add streaming, and expose routing metadata without breaking ordinary clients. Implement CLI serve/doctor/smoke commands and configuration examples.

Small and medium are self-hosted backends. Use native Ollama on the Mac with actual model identities and memory/loading observations. Implement the frontier API transport and current budget controls. Record partial availability without claiming the full three-tier live path is verified.

Create a genuine runnable Colab notebook that imports the same package, inspects the GPU, installs a compatible pinned environment, starts vLLM, checks readiness, makes bounded requests, exports results, and cleans up. Do not duplicate application code in cells.

Use the exact 18 checkpoints below. A final feature label requires evidence; offline contracts and real checks must stay distinct.

CHECKPOINTS

D1-01: docs: define full project scope and runtime profiles
Change: Merge full-scope AGENTS.md and map the Mac, Colab, and API execution paths.
Evidence: Scope checklist retains every original feature.

D1-02: chore: record M3 and notebook environment preflights
Change: Inspect Mac memory/OS and generate the Colab GPU preflight.
Evidence: Sanitized hardware and version reports; remote checks labeled separately.

D1-03: build: initialize reproducible package and CLI
Change: Set up uv, package metadata, dependency extras, and CLI entry points.
Evidence: Clean environment imports the package and shows CLI help.

D1-04: feat: validate backend and policy configuration
Change: Add typed config, environment secret references, and limits.
Evidence: Invalid/missing configurations fail with useful messages.

D1-05: feat: add gateway API and health endpoints
Change: Implement the text-chat request contract, health, readiness, and model registry endpoints.
Evidence: Contract tests cover supported and rejected requests.

D1-06: feat: implement asynchronous backend transport
Change: Add reusable async HTTP clients, lifecycle management, and bounded connections.
Evidence: Offline transport tests demonstrate correct forwarding.

D1-07: feat: connect small Ollama model
Change: Implement Mac small-backend launch/check instructions and real adapter.
Evidence: One bounded real answer with model ID and runtime label.

D1-08: feat: connect medium Ollama model
Change: Add medium-backend configuration and measure loading/memory feasibility.
Evidence: Real answer and explicit residency/switching observations, or documented hardware blocker.

D1-09: feat: connect frontier API backend
Change: Implement provider-compatible endpoint, usage parsing, secret handling, and spending controls.
Evidence: Offline contract checks plus a real request only with configured budget/key.

D1-10: feat: implement nonstreaming gateway responses
Change: Route manually selected tiers through the common API.
Evidence: Requests reach the requested available backend.

D1-11: feat: implement streaming response forwarding
Change: Forward SSE output without unnecessary full-response buffering.
Evidence: Fragmented event and completion tests; real streaming smoke where accessible.

D1-12: fix: handle deadlines cancellation and backend errors
Change: Propagate cancellation, release resources, and sanitize failures.
Evidence: Timeout/cancellation/error-path checks pass.

D1-13: feat: record request traces and usage
Change: Add request IDs, per-stage timestamps, backend identity, and cost status.
Evidence: Each request creates a consistent secret-free record.

D1-14: feat: add doctor and bounded smoke commands
Change: Validate configuration, model presence, connectivity, and a short request.
Evidence: Commands explain missing dependencies without silently mocking.

D1-15: feat: add runnable Colab serving notebook
Change: Create ordered setup, pinned-source install, vLLM launch, local client, export, and cleanup cells.
Evidence: Notebook structure validates; record which cells were actually executed.

D1-16: feat: add Mac and Colab configuration profiles
Change: Keep core CPU dependencies separate from NVIDIA/model-training extras.
Evidence: Mac core installs without CUDA dependencies.

D1-17: test: verify gateway integration across profiles
Change: Add offline integration coverage and opt-in real checks.
Evidence: Offline suite and at least available real-path evidence recorded.

D1-18: docs: publish local setup and checkpoint evidence
Change: Write Mac quickstart, Colab instructions, known limits, and Day 1 status.
Evidence: A clean reader can locate commands, required model downloads, and evidence.

At close, reconcile completed checkpoint IDs with actual local Git commits and checks. State today's actual commit count in America/Toronto, unmet gates, and exact next actions. Generate my finished handwritten entry using prompts/end_day_journal.md and output it directly in chat. Do not replace the journal prose with questions or blank fields.
~~~


### Day 2 Complete benchmark and cost accounting

Paste this entire prompt into Codex in the same project repository.

~~~text
Continue Day 2 of the FULL original Jev project. Read AGENTS.md, docs/STATUS.md, docs/COMMIT_PLAN.md, current source, and relevant experiment outputs. Resolve any earlier dependency that blocks today's work without reverting to the reduced-scope plan.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


TODAY'S ENGINEERING REQUIREMENTS

Restore all original benchmark task families: GSM8K, MMLU, and MBPP or a justified documented equivalent coding set. Target a fixed 2000–3000-prompt manifest scored across all three tiers by the final evaluation. Start with a small development smoke to catch parser errors, then launch bounded resumable jobs.

Implement code scoring in a resource-limited network-disabled Mac sandbox; never execute generated code directly in the host Python process. The Colab notebook may produce code outputs for later isolated scoring on the Mac. Do not use containers to bypass Colab restrictions.

Deduplicate/group related prompts before freezing 60/20/20 splits. Train and validate now; reserve final held-out scoring/analysis for Day 6. Audit 30–50 development scores per task. Save model revisions, all outputs, usage, failures, and configuration fingerprints. Derive observed oracle labels, including none-correct cases.

Implement complete cost accounting and a separate serving baseline workload. Start long-running bounded jobs early enough to checkpoint them; continue independent implementation while jobs run. Report actual sample coverage rather than claiming the target was reached.

CHECKPOINTS

D2-01: feat: define immutable evaluation records
Change: Specify prompt IDs, task/split, output, outcome, model revision, timings, and cost fields.
Evidence: Schema validates fixtures and preserves errors separately from wrong answers.

D2-02: feat: load versioned GSM8K prompts
Change: Add a deterministic math dataset adapter with documented revision.
Evidence: Known sample and answer provenance are reproducible.

D2-03: feat: load versioned MMLU prompts
Change: Add multiple-choice task/subset handling and consistent templates.
Evidence: Choice ordering and correct-letter extraction verified.

D2-04: feat: load MBPP coding benchmark
Change: Add code-task data and test specification loading.
Evidence: Dataset/license metadata and task IDs recorded.

D2-05: feat: isolate generated code evaluation
Change: Run code tests in bounded network-disabled sandbox containers on the Mac.
Evidence: Timeout/resource/exit handling checked; no model code runs directly on the host.

D2-06: feat: freeze deduplicated dataset splits
Change: Create a 2000–3000-prompt target manifest and 60/20/20 splits.
Evidence: Duplicates/related variants stay within a single split; test use is gated.

D2-07: feat: implement math answer scoring
Change: Normalize valid numerical answers with explicit parser outcomes.
Evidence: Extractor edge cases and units are audited.

D2-08: feat: implement multiple choice scoring
Change: Parse supported answer forms without guessing ambiguous answers.
Evidence: Malformed, truncated, and incorrect answers remain distinguishable.

D2-09: feat: integrate sandbox code task scoring
Change: Connect model completions to code checks and structured results.
Evidence: Known pass/fail/timeout fixtures are classified correctly.

D2-10: test: add manual scoring audit export
Change: Export 30–50 development answers per task for human review.
Evidence: Audit corrections are documented before threshold selection.

D2-11: feat: add bounded three tier evaluation runner
Change: Evaluate selected splits on all configured tiers with retries and token/request limits.
Evidence: No paid job starts without explicit budget configuration.

D2-12: feat: checkpoint and resume evaluation runs
Change: Fingerprint input/model/settings and avoid duplicate completed calls.
Evidence: Interrupted development run resumes without corrupting records.

D2-13: feat: derive observed hindsight oracle labels
Change: Label the cheapest observed successful tier and handle none-correct cases.
Evidence: Oracle is reported as an offline bound for the measured outcomes.

D2-14: feat: calculate complete inference cost
Change: Separate API usage, router/verifier costs, and provisioned compute scenarios.
Evidence: Unknown rates remain unknown; idle capacity is not erased.

D2-15: feat: generate per tier quality reports
Change: Report task/overall accuracy, completion/error rates, and sample counts.
Evidence: Reports regenerate directly from stored results.

D2-16: feat: add controlled serving baseline runner
Change: Separate quality evaluation from prompt-length/concurrency/arrival-rate workloads.
Evidence: Client scheduling, warm-up, cache state, and output controls recorded.

D2-17: feat: report latency and throughput baselines
Change: Compute TTFT, appropriate chunk/TPOT metrics, p50/p95, errors, and throughput.
Evidence: Metric definitions and denominators are explicit.

D2-18: data: checkpoint real train validation measurements
Change: Run and preserve real train/validation outcomes within hardware/budget limits.
Evidence: Report progress toward 2000+ total prompts; held-out test stays unused until Day 6.

At close, reconcile completed checkpoint IDs with actual local Git commits and checks. State today's actual commit count in America/Toronto, unmet gates, and exact next actions. Generate my finished handwritten entry using prompts/end_day_journal.md and output it directly in chat. Do not replace the journal prose with questions or blank fields.
~~~


### Day 3 Jev and all router comparisons

Paste this entire prompt into Codex in the same project repository.

~~~text
Continue Day 3 of the FULL original Jev project. Read AGENTS.md, docs/STATUS.md, docs/COMMIT_PLAN.md, current source, and relevant experiment outputs. Resolve any earlier dependency that blocks today's work without reverting to the reduced-scope plan.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


TODAY'S ENGINEERING REQUIREMENTS

Implement every original routing comparison: fixed tiers, random, hindsight oracle for offline analysis, trained DistilBERT, prompted small LLM, Jev choice, Jev success-probability thresholds, and self-hosted Strands Decider using its current official runtime/checkpoint.

Fine-tune DistilBERT on train data in Colab, tune on validation, export weights/tokenizer/label mapping/backend identities, and run it as the Mac fallback. Keep its own dependencies in an appropriate optional runtime; the gateway core should not require the training stack. Generic lightweight heuristics can supplement but do not replace the requested trained model.

Use current TypeSafe contracts. Define an actual outcome for each probability being calibrated; distinguish oracle-label classification from backend answer correctness. A vendor confidence/concentration statistic is not automatically correctness probability. Implement reliability diagrams, ECE, Brier score, and measured router latency.

Use validation to choose and freeze question wording and thresholds. Keep exact router/model/artifact identities. If Jev or other access is missing, implement and contract-test the integration but list live comparison as blocked, not completed.

CHECKPOINTS

D3-01: feat: define interchangeable router contract
Change: Return tier, policy/version, probability event, latency, and fallback reason.
Evidence: A common contract covers every online router.

D3-02: feat: implement fixed and seeded random baselines
Change: Add always-small, always-medium, always-frontier, and random policies.
Evidence: Selections are reproducible and honor available capabilities.

D3-03: feat: prepare DistilBERT training labels
Change: Use train-split oracle labels and handle none-correct/imbalance explicitly.
Evidence: No validation/test rows enter training.

D3-04: feat: fine tune DistilBERT router
Change: Train on Colab with logged seed, checkpoint, hyperparameters, and validation.
Evidence: A real training run or its exact access blocker is recorded.

D3-05: feat: export portable trained router artifact
Change: Save tokenizer, weights, label map, model identities, and evaluation metadata.
Evidence: Artifact reload produces consistent decisions on fixtures.

D3-06: feat: serve DistilBERT as Mac fallback router
Change: Run the trained classifier on CPU or a verified supported Mac device.
Evidence: Mac decision latency and memory measured separately from Colab.

D3-07: feat: implement prompted small LLM router
Change: Ask the small model to choose among defined backend capabilities.
Evidence: Parse invalid outputs explicitly and record generation overhead.

D3-08: feat: implement official Jev client
Change: Use current official SDK/API contract, typed answers, deadlines, and usage.
Evidence: Offline contract tests and opt-in real request evidence.

D3-09: feat: implement Jev choice routing
Change: Describe actual models and request a tier choice.
Evidence: Question version and returned probabilities are stored.

D3-10: feat: implement Jev probability threshold routing
Change: Ask explicit small/medium success questions and apply validation thresholds.
Evidence: Probability event is defined; sequential calls count toward cost/latency.

D3-11: feat: integrate self hosted Strands Decider comparison
Change: Use the current official checkpoint/runtime and a separate decision adapter.
Evidence: Do not assume typed decisions use generic text-generation vLLM serving.

D3-12: test: verify router contracts and unavailable tiers
Change: Cover invalid decisions, excessive context, disabled providers, and deadlines.
Evidence: Tests do not silently upgrade to paid backends.

D3-13: feat: implement calibration measurement
Change: Add reliability plots, ECE, and Brier score for well-defined outcomes.
Evidence: Do not treat distribution concentration as correctness probability.

D3-14: feat: tune router operating points on validation
Change: Select policies/thresholds under explicit cost and quality objectives.
Evidence: Freeze tuning inputs; hold test evaluation for Day 6.

D3-15: feat: plot validation cost quality frontiers
Change: Compare all routers with fixed baselines and observed oracle reference.
Evidence: Include actual sample counts, costs, and probability semantics.

D3-16: feat: benchmark routing overhead on Mac
Change: Measure decision-only p50/p95 and full request overhead.
Evidence: Warm-up, classifier/device, and model load state documented.

D3-17: feat: dispatch gateway requests through selected router
Change: Integrate policy selection and deterministic fallback under a bounded deadline.
Evidence: Real requests take the selected backend path where accessible.

D3-18: docs: freeze router configs and comparison evidence
Change: Save policy/model/question versions and the validation summary.
Evidence: All original comparison methods have implemented/verified/pending status.

At close, reconcile completed checkpoint IDs with actual local Git commits and checks. State today's actual commit count in America/Toronto, unmet gates, and exact next actions. Generate my finished handwritten entry using prompts/end_day_journal.md and output it directly in chat. Do not replace the journal prose with questions or blank fields.
~~~


### Day 4 Verification cascades and semantic cache

Paste this entire prompt into Codex in the same project repository.

~~~text
Continue Day 4 of the FULL original Jev project. Read AGENTS.md, docs/STATUS.md, docs/COMMIT_PLAN.md, current source, and relevant experiment outputs. Resolve any earlier dependency that blocks today's work without reverting to the reduced-scope plan.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


TODAY'S ENGINEERING REQUIREMENTS

Build the complete cache, route, generate, verify, and escalate path. Keep Jev as verifier for both generated answers and semantic-cache candidates. Implement route-first, cascade-only, and route-then-verify modes, with explicit handling of verifier failure.

Share one cumulative deadline and cost/token budget across attempts. Include rejected generations, repeated decisions, and verifier calls in totals. Prevent retry multiplication. For verification modes, buffer a candidate until accepted or explicitly document a different response contract; never leak a rejected answer as final streamed output.

Implement a compact embedding adapter and persistent FAISS-based candidate retrieval with metadata. Enforce request/context/policy compatibility, TTL/eviction, reset, and safe writes. Record the actual Mac ARM install result. Do not reuse an answer merely because vector similarity is high.

Build separate paraphrase, near-miss, and unrelated cache groups without split leakage. Compare similarity-only and Jev-verified caching. Evaluate verifier false accepts/rejects, cascade/hybrid quality, latency, and full costs on validation. Preserve the held-out cache set for Day 6.

CHECKPOINTS

D4-01: feat: implement Jev answer verifier
Change: Define the prompt-answer correctness event and typed verifier interface.
Evidence: Verifier outputs and usage are recorded without claiming ground truth.

D4-02: feat: add verifier acceptance policy
Change: Apply configurable thresholds and explicit timeout/failure behavior.
Evidence: False accept and false reject definitions are testable.

D4-03: feat: implement multi tier verification cascade
Change: Try small, verify, escalate to medium, then frontier as configured.
Evidence: Bound attempts and retain every attempt's cost and latency.

D4-04: feat: implement route then verify hybrid
Change: Route first, verify eligible outputs, and escalate under the same policy.
Evidence: Hybrid behavior uses the shared execution trace.

D4-05: feat: enforce cumulative cascade budgets
Change: Carry one deadline and spending/token budget across all attempts.
Evidence: No retry multiplication or partial streaming before final acceptance.

D4-06: feat: evaluate cascade quality and overhead
Change: Add validation runner for route-first, cascade, and hybrid.
Evidence: Compare full costs and live latency separately from offline replay.

D4-07: feat: report verifier error tradeoffs
Change: Compute false-accept/reject rates with explicit denominators.
Evidence: Use scored answers rather than the verifier's own opinions as labels.

D4-08: feat: add portable embedding model adapter
Change: Load a documented compact encoder with pinned revision.
Evidence: Embedding shape, normalization, latency, and model identity recorded.

D4-09: feat: implement persistent FAISS answer index
Change: Store vectors with answer metadata and bounded persistence behavior.
Evidence: ARM installation and save/reload path are actually checked.

D4-10: feat: isolate cache request scope and validity
Change: Key system instructions, conversation context, model/policy revision, and generation options.
Evidence: Cross-context reuse and invalid entries are rejected.

D4-11: feat: retrieve similarity candidate matches
Change: Expose thresholded candidate lookup without automatic answer acceptance.
Evidence: Similarity scores and empty-index cases checked.

D4-12: feat: verify cache candidates with Jev
Change: Confirm stored answer applicability before returning a candidate.
Evidence: Verification overhead and false-match decisions recorded.

D4-13: feat: store accepted outputs and manage cache lifecycle
Change: Add insertion, TTL/eviction, reset, and safe metadata updates.
Evidence: Rejected or incompatible entries do not contaminate future requests.

D4-14: data: create paraphrase and near miss cache benchmark
Change: Build separate same-meaning, near-miss, and unrelated groups.
Evidence: Related examples stay within one split; provenance recorded.

D4-15: feat: evaluate verified versus similarity only caching
Change: Measure hit rate, false hits, latency, and cost on validation.
Evidence: Distinct accuracy and false-hit denominators reported.

D4-16: test: verify cache persistence and context isolation
Change: Exercise restarts, incompatible config, near misses, and cache disablement.
Evidence: Tests demonstrate the full validity rules.

D4-17: feat: integrate cache routing cascade execution path
Change: Compose cache lookup, router, generation, verification, tracing, and return.
Evidence: Each configurable mode has an end-to-end path.

D4-18: docs: record full request path and validation evidence
Change: Document route/cascade/cache modes and known tradeoffs.
Evidence: Generate copy-ready Day 4 notes from completed code and observed outputs.

At close, reconcile completed checkpoint IDs with actual local Git commits and checks. State today's actual commit count in America/Toronto, unmet gates, and exact next actions. Generate my finished handwritten entry using prompts/end_day_journal.md and output it directly in chat. Do not replace the journal prose with questions or blank fields.
~~~


### Day 5 Monitoring deployment and failure tests

Paste this entire prompt into Codex in the same project repository.

~~~text
Continue Day 5 of the FULL original Jev project. Read AGENTS.md, docs/STATUS.md, docs/COMMIT_PLAN.md, current source, and relevant experiment outputs. Resolve any earlier dependency that blocks today's work without reverting to the reduced-scope plan.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


TODAY'S ENGINEERING REQUIREMENTS

Complete the original deployment and reliability scope on the Mac: an ARM-compatible gateway image, Docker Compose with Prometheus/Grafana, kind Kubernetes Deployment/Service/probes/resources, Locust workloads, circuit breakers, retries, backpressure, and CI.

Keep Ollama native on the host and verify container/pod-to-host reachability explicitly. Container localhost is not the Mac. Resolve external model endpoints without publishing unauthenticated ports. Specify whether classifier/cache/breaker state is per replica or shared; do not concurrently write one mutable FAISS index from several pods unsafely.

Instrument stages with bounded labels and correct multi-instance aggregation. Test Jev outage with trained-router fallback and model failover under policy/resource constraints. Run the original steady 10-minute, fivefold spike 2-minute, and one-hour soak scenarios within configured caps. Run long scenarios as bounded jobs so progress remains visible.

Delete a gateway pod under load and record actual recovery/errors. Add offline CI and 50 fixed mocked regression prompts. Contract tests must not be presented as external provider or GPU validation.

CHECKPOINTS

D5-01: build: containerize the gateway for supported architectures
Change: Build the gateway image with external configurable model endpoints.
Evidence: Mac ARM image starts and passes health checks.

D5-02: build: add Compose gateway Prometheus Grafana stack
Change: Provide a one-command observability deployment.
Evidence: Container-to-host model URLs are explicitly tested.

D5-03: feat: instrument request stage metrics
Change: Add counters/histograms for tiers, routing, verification, errors, cache, and spend.
Evidence: Labels are bounded and private prompts are not metric labels.

D5-04: feat: implement Jev circuit breaker and fallback
Change: Add closed/open/half-open behavior with trained DistilBERT fallback.
Evidence: Controlled failure tests exercise recovery.

D5-05: feat: bound concurrency and retry behavior
Change: Add backpressure, deadlines, retry jitter, and cancellation semantics.
Evidence: Retries are capped and output already streamed is not replayed.

D5-06: feat: implement model backend failover policy
Change: Define eligible next-tier behavior and cost/privacy/capability checks.
Evidence: Unavailable-backend paths remain explicit.

D5-07: build: configure metrics scraping and aggregation
Change: Scrape gateway and available serving metrics with correct instance labels.
Evidence: Replica counters/latencies aggregate without double-counting.

D5-08: feat: add operational Grafana dashboards
Change: Visualize tier requests, latency, cache, errors, escalation, fallback, and cost.
Evidence: Dashboard queries are validated against emitted metrics.

D5-09: test: implement bounded Locust load scenarios
Change: Add repeatable steady, spike, and soak workloads with recorded parameters.
Evidence: No run starts beyond configured resource/API limits.

D5-10: perf: record ten minute steady load
Change: Run the documented steady workload against real eligible backends.
Evidence: Save throughput, latency, error rate, and workload placement.

D5-11: perf: record fivefold two minute load spike
Change: Increase arrival load to five times baseline for two minutes.
Evidence: Measure overload/queueing behavior and recovery.

D5-12: perf: record one hour soak test
Change: Run bounded moderate traffic for an hour where resources permit.
Evidence: Capture stability and memory trends, not just a final average.

D5-13: deploy: add local kind Kubernetes manifests
Change: Define gateway Deployment, Service, probes, and resource settings.
Evidence: Local cluster deployment is verified on the Mac.

D5-14: deploy: configure external backends and replica state
Change: Resolve host/model reachability, secrets, and per-pod versus shared state.
Evidence: Do not assume a container's localhost is the Mac or share mutable FAISS files unsafely.

D5-15: test: verify gateway pod replacement under traffic
Change: Delete one gateway pod and observe replacement/readiness.
Evidence: Record errors during recovery; do not promise zero errors.

D5-16: test: verify Jev outage during load
Change: Inject a controlled Jev failure and observe breaker/fallback/recovery.
Evidence: Dashboard and saved traces show actual behavior.

D5-17: ci: add deterministic offline regression workflow
Change: Run linting, meaningful tests, and 50 fixed mocked prompts on pushes.
Evidence: No CI secrets or paid calls are required for standard checks.

D5-18: docs: record deployment and failure runbooks
Change: Document start/stop, replica/cache limits, failures, and load evidence.
Evidence: Every resilience claim links to an observed check or is marked pending.

At close, reconcile completed checkpoint IDs with actual local Git commits and checks. State today's actual commit count in America/Toronto, unmet gates, and exact next actions. Generate my finished handwritten entry using prompts/end_day_journal.md and output it directly in chat. Do not replace the journal prose with questions or blank fields.
~~~


### Day 6 GPU investigation final evaluation and release

Paste this entire prompt into Codex in the same project repository.

~~~text
Continue Day 6 of the FULL original Jev project. Read AGENTS.md, docs/STATUS.md, docs/COMMIT_PLAN.md, current source, and relevant experiment outputs. Resolve any earlier dependency that blocks today's work without reverting to the reduced-scope plan.

FULL PROJECT CONTRACT

This is the complete original Jev gateway project, adapted to an M3 MacBook and Colab. Preserve every original feature. Jev is the principal decision router and verifier. DistilBERT is the trained fallback and comparison. Include prompted LLM and self-hosted decision-model comparisons, fixed/random baselines, 2000+ prompt evaluation, calibration, verification cascades, semantic caching, Docker, kind Kubernetes, Prometheus/Grafana, Locust, CI, and the final technical report.

Mac: application, native Ollama small/medium backends when memory permits, portable classifier/embedding inference, code-evaluation sandbox, local containers/Kubernetes. Colab: GPU model evaluation, DistilBERT training, vLLM/NVIDIA experiments. Frontier and Jev are configured APIs. Core gateway installs without CUDA. Profile and preserve Mac/Colab results separately. A running notebook is not a permanent service dependency.

Inspect the actual repository and applicable instructions first. Merge this scope into existing project guidance and remove earlier "defer/optional/stretch" scope exclusions for original components. Preserve existing user files. Do not delete old personal notes, but stop implementing the previously proposed digital learning-journal system.

COMMITS

I authorize meaningful local Git commits for the work in the supplied checkpoint plan. Target at least 18 real commits per work day. Use D1-01 through D6-18 as checkpoint identifiers in commit messages/body; additional genuine fixes may add commits. Stage only the coherent change being committed. Include its relevant tests/docs when appropriate. Do not use empty commits, formatting churn, artificial reversals, backdated timestamps, or falsified authorship to reach the count.

Use actual commit timestamps and count work days in America/Toronto. Do not rewrite history. If identity is unconfigured, tell me the exact Git setup needed rather than inventing it. If a dependency blocks a checkpoint, implement independent checkpoints, record the blocker, and report the actual count rather than asserting 18 completed commits.

WORKFLOW AND EVIDENCE

Work in six blocks of three checkpoints per day. Implement, verify at the right scope, and commit each checkpoint. Keep full-suite repetition proportional to changes. Continue to the next block without requiring a routine confirmation. Give a concise progress update after each block.

Maintain docs/STATUS.md, docs/ENVIRONMENT.md, docs/DECISIONS.md, and docs/EXPERIMENTS.md for engineering evidence. They are not my personal journal. Preserve raw outputs and immutable run identifiers. Do not invent successful integrations, training runs, benchmark figures, source visits, or commit hashes.

Keep paid runs disabled until credentials, models, and an explicit positive run budget/request/token cap are configured. Do not provision compute, expose public model ports, or publish externally without the relevant user instruction and destination. Offline tests are the default. Missing provider/hardware access must be visible and must not be disguised with mocks.

My learning journal is handwritten. At session/day close generate complete copy-ready prose using prompts/end_day_journal.md. No journal CLI, reflection forms, quizzes, mastery tracker, or note-taking application is needed.


TODAY'S ENGINEERING REQUIREMENTS

Complete full-scope verification and reporting. Do not remove uncompleted features from the acceptance checklist to claim a smaller project is done.

Run a controlled Colab NVIDIA experiment using the pinned source/model/server environment. Capture a short permitted GPU profile, identify a plausible bottleneck, and test one supported serving change. Compare repeated unprofiled baseline/candidate runs with matched workload, lengths, cache state, and resource placement. Retain negative results.

Freeze all models, prompts, policies, thresholds, cache settings, and scorers before final held-out evaluation. Complete the 2000+ prompt three-tier coverage and all router/cascade/cache/calibration comparisons when resources permit. If any checks remain blocked, identify the exact gap and do not manufacture final values.

Regenerate all final charts from raw records. Separate Mac, Colab, mock, replay, and estimated results. Include absolute accuracy differences, uncertainty, full attempt costs, and provisioned-capacity assumptions.

Verify install/build, clean-clone Mac quickstart, Colab notebook, Compose, kind, CI, and the five-minute demo. Prepare the full public report, README, contribution/artifact guidance, evidence-backed resume bullets, and two social-post drafts. A local release checkpoint is authorized. Publish only when a concrete destination and corresponding user instruction are present; do not send unsolicited messages to third parties.

CHECKPOINTS

D6-01: perf: pin Colab NVIDIA serving environment
Change: Record GPU allocation, model/runtime revisions, and configuration.
Evidence: The notebook imports the same source revision as the reported experiment.

D6-02: perf: capture controlled vLLM baseline
Change: Run a fixed workload with defined lengths, warm-up, cache, and arrival/concurrency.
Evidence: Preserve raw results and model/server metadata.

D6-03: perf: capture focused GPU execution profile
Change: Collect Nsight Systems or supported profiler evidence on the real GPU.
Evidence: Record permission/tool limits; keep profiled timings separate.

D6-04: perf: implement one evidence motivated serving change
Change: Change batching/token budget, memory allocation, or another supported observed bottleneck.
Evidence: A falsifiable hypothesis and exact config/code difference are recorded.

D6-05: perf: compare repeated baseline and candidate runs
Change: Repeat controlled unprofiled timings and report variability.
Evidence: Retain regressions; no speedup claim without supporting data.

D6-06: eval: run frozen held out router comparison
Change: Evaluate all original policies after configurations and question wording are frozen.
Evidence: Complete 2000+ total manifest coverage across all three tiers, or report the remaining gap.

D6-07: eval: run held out cascade and cache comparisons
Change: Evaluate cascade/hybrid and verified/unverified cache with frozen thresholds.
Evidence: No related examples leak into tuning or training.

D6-08: eval: finalize calibration and router timing report
Change: Report defined-event calibration, quality, overhead, and sample uncertainty.
Evidence: Avoid comparing incompatible confidence meanings.

D6-09: eval: reconcile complete cost and capacity scenarios
Change: Include all model/router/verifier attempts and idle/provisioned GPU assumptions.
Evidence: Measured spend and modeled capacity costs remain distinct.

D6-10: report: regenerate final figures from raw records
Change: Build quality/cost, reliability, latency, cache, and performance charts.
Evidence: Each figure has units, sample counts, and linked input records.

D6-11: docs: finish exact reproducibility and demo commands
Change: Provide Mac, Colab, Compose, and kind workflows plus a five-minute demo.
Evidence: Command paths and configuration examples match the code.

D6-12: build: verify installable package and CLI
Change: Build/install the package in a fresh environment and verify entry points.
Evidence: Normal gateway installation does not require CUDA.

D6-13: test: verify supported platform and release checks
Change: Run the affected offline suite plus Mac/Linux CI configurations.
Evidence: State which environments actually executed.

D6-14: test: perform clean clone user walkthrough
Change: Use a clean checkout to test install, doctor, backend setup, and a real request.
Evidence: Document prerequisites and blockers encountered by a new user.

D6-15: docs: write public technical findings
Change: Explain methods, all-router comparisons, cascade/cache results, failures, and limitations.
Evidence: Claims match saved evidence; publication destination remains user-controlled.

D6-16: docs: prepare evidence backed resume and interview notes
Change: Draft accurate bullets and explanations of tradeoffs and debugging.
Evidence: Use only verified numbers; distinguish implemented from tested.

D6-17: docs: add contributor and artifact provenance guidance
Change: Document code license choice, model/data terms, configs, trained artifacts, and retraining.
Evidence: Forks can substitute models and understand policy compatibility.

D6-18: release: checkpoint full project and publication checklist
Change: Audit full-scope acceptance, secrets, artifact sizes, command validity, and local commit history.
Evidence: Create a local release checkpoint; publish only to a specified authorized destination.

At close, reconcile completed checkpoint IDs with actual local Git commits and checks. State today's actual commit count in America/Toronto, unmet gates, and exact next actions. Generate my finished handwritten entry using prompts/end_day_journal.md and output it directly in chat. Do not replace the journal prose with questions or blank fields.
~~~


## Generate the actual daily handwritten entry

~~~text
Generate my finished handwritten journal entry for today's actual project work. I will copy the prose into a physical journal.

Read AGENTS.md, docs/STATUS.md, today's relevant diff and commits, the corresponding concept notes in HANDWRITTEN_JOURNAL.md, and the actual test/experiment outputs. Do not assume that a planned checkpoint was completed.

Write approximately 500–800 words in connected, clear paragraphs, suitable for copying by hand. Use a short title and explain:
- What the system now does and the changes actually made.
- The main concepts behind those changes, with concrete examples from this code.
- Why the design choices were made and the important tradeoffs.
- An actual bug or unexpected observation if one occurred; do not invent one.
- Checks and measurements actually performed, with exact verified numbers and units where available.
- What remains unfinished and the next technical question.

Make it a complete entry, not a template, checklist, quiz, or reflection form. Do not ask me to fill blanks. Do not create a journal app, tracking database, or personal-learning dashboard.

You may use first person for my project goal or supplied reflections, but do not claim I personally wrote Codex-generated code, independently discovered something, or mastered a topic without evidence. Prefer factual wording such as "The gateway now..." and "The important distinction is...".

If something was not executed, say so plainly. Explain the relevant concept without pretending there was a result. Keep mock, real, estimated, and replayed evidence distinct. Do not fabricate measurements or commit counts.

Output the full copy-ready entry directly in chat. Keep internal evidence references in a short separate line afterward so the main prose remains easy to copy. Update engineering status separately if needed; no digital personal journal is required.

~~~

## Official references for implementation

Use official current-version instructions and record sources actually consulted. Older guide claims about price, access, schema, and model runtimes are not automatically current.

- Codex IDE: https://learn.chatgpt.com/docs/ide
- Codex project instructions: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- uv: https://docs.astral.sh/uv/
- Ollama Mac: https://docs.ollama.com/macos
- Ollama API compatibility: https://docs.ollama.com/api/openai-compatibility
- vLLM installation: https://docs.vllm.ai/en/stable/getting_started/installation/gpu/
- vLLM benchmarking: https://docs.vllm.ai/en/stable/benchmarking/cli/
- TypeSafe: https://docs.typesafe.ai/introduction
- Strands Decider: https://github.com/strands-labs/strands-decider
- Docker Desktop Mac: https://docs.docker.com/desktop/setup/install/mac-install/
- kind: https://kind.sigs.k8s.io/docs/user/quick-start/
- Colab: https://research.google.com/colaboratory/faq.html

## Completion audit

At project close list each full-scope deliverable as implemented, offline-tested, real-tested, or blocked, with evidence. Report actual commit counts and sample counts. A missing API key is not a passing live integration test, and a selected configuration is not an observed performance result.

A release is ready when another person can install the gateway, configure their own backends and keys, understand the supplied routing artifacts, run the documented modes, inspect the evaluation, and reproduce the relevant experiments under the stated resource conditions.

