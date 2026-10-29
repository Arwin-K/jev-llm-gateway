# Handwritten journal for the full Jev LLM gateway project

These are finished study notes arranged around the six build days and 108 commit checkpoints. You can copy the relevant passages into your handwritten journal. They explain the concepts behind the work; they do not claim that code has already been built, tests have passed, or experiments have produced particular results.

After each work session, use the supplied end-of-day prompt to generate an additional account of the actual implementation, debugging, and measurements. The project does not require a digital learning journal, quizzes, or personal reflection forms.

## Day 1 Understanding the system and connecting models

### Checkpoints 01 to 03 Architecture and environments

The project is an LLM gateway that accepts a request and coordinates the model services needed to answer it. The gateway and the models have different jobs. The gateway handles routing, policy, network requests, and records. The model server loads model weights and generates tokens. This separation lets the same gateway work with models on a Mac, an NVIDIA machine, or a hosted API.

The M3 Mac is the main development and application machine. Colab is a separate NVIDIA experiment environment. Results from one environment do not describe the other automatically.

### Checkpoints 04 to 06 Configuration and asynchronous requests

Configuration describes the available backends, their URLs, model identities, limits, and credentials. Validating it at startup catches errors before a real request reaches an unavailable model. Credentials stay separate from tracked configuration examples.

An asynchronous HTTP client can wait for a backend without blocking the entire gateway. This does not make the model itself generate faster. It lets the application handle other work while a network request is in progress. Reusing connections also avoids repeatedly establishing the same connection.

### Checkpoints 07 to 09 The three model tiers

The small and medium tiers are models that the project hosts. The frontier tier is reached through an API. A tier name describes its intended role, but it does not prove which model is best on a particular question. Their actual quality and latency must be measured.

On the Mac, Ollama provides the local generation service. On Colab, vLLM provides an NVIDIA serving path for experiments. Running two local models can introduce memory pressure or model-loading delays. Those delays belong in the performance record.

### Checkpoints 10 to 12 Streaming and failure boundaries

A nonstreaming request returns its answer after generation finishes. A streaming request delivers output incrementally. Time to first output measures the initial wait; total latency measures the full request. A streamed event is not always exactly one token, so event gaps must not be reported as true per-token timings without checking the interface.

Timeouts bound waiting. Cancellation stops unnecessary work when a caller leaves. Errors need a consistent structure so clients can distinguish an unavailable backend from an invalid request.

### Checkpoints 13 to 15 Evidence and notebook execution

Each request needs an ID and a record of the chosen backend, configuration, usage, timings, and outcome. A useful record makes it possible to trace a chart back to the requests that produced it. Missing usage data should stay missing rather than being replaced by a guessed token count.

A Colab notebook should import the repository code. Duplicating the gateway inside notebook cells would create two implementations that could drift apart. Setup, readiness checks, a bounded request, result export, and cleanup make a notebook experiment reproducible.

### Checkpoints 16 to 18 Portability and integration

The gateway's normal installation should work without NVIDIA dependencies. GPU serving and model training can use separate environments. This makes the application easier to install on a Mac and easier for someone else to fork.

A unit test verifies a component under controlled conditions. A real integration check verifies that components actually communicate with the intended service. Both matter, and a mocked success does not establish that a live model endpoint works.

## Day 2 Building an evaluation that can be trusted

### Checkpoints 01 to 03 Tasks and evaluation records

The benchmark combines tasks with automatically checkable answers. GSM8K tests mathematical problem solving, MMLU uses multiple-choice questions, and MBPP tests generated programs against tests. The tasks expose different strengths and weaknesses, which creates a reason to route between models.

Each evaluation row needs a stable prompt ID, task, split, model identity, generation settings, raw answer, score, and execution outcome. Keeping this information together makes later comparisons auditable.

### Checkpoints 04 to 06 Isolation and fixed splits

Generated programs need isolated execution with restricted resources and no network access. A program that produces an infinite loop should become a recorded timeout rather than hanging the evaluation machine.

Training, validation, and test sets have separate purposes. Training fits the classifier. Validation chooses settings and thresholds. The final test set estimates performance after those choices are frozen. Duplicates or closely related variants across splits can leak information and exaggerate results.

### Checkpoints 07 to 09 Scoring is part of the experiment

An answer extractor converts a model response into something the scoring rule can check. It must handle supported formatting without silently guessing. A correct answer phrased differently can expose an extractor bug. A truncated answer, invalid format, timeout, and mathematically incorrect answer are different outcomes.

Code tasks need the same distinction. Failing a test is evidence about the generated program, while a broken sandbox is an evaluation infrastructure failure.

### Checkpoints 10 to 12 Auditing and resumable runs

Manually auditing a sample of scored answers checks whether the automatic pipeline matches the intended task. A scorer bug can invalidate every later routing comparison, so it is worth finding early.

Long evaluations need checkpoints. A resumable runner should reuse a completed result only when the prompt, model revision, and generation settings match. Reusing an answer from a different configuration would mix experiments. The original run identity and timestamp should remain attached to reused results.

### Checkpoints 13 to 15 Oracle labels and costs

The hindsight oracle chooses the cheapest model that answered each evaluated prompt correctly. It is an offline reference that uses information unavailable before generation. It describes an opportunity in the measured dataset, not a deployable perfect router.

Self-hosted cost and API cost also differ. An allocated GPU may cost money while idle. Sending fewer requests to it does not automatically reduce the bill. Routing costs must include decision calls, verification calls, and rejected generation attempts.

### Checkpoints 16 to 18 Performance baselines

Correctness evaluation asks whether answers are right. A serving benchmark asks how the system behaves under a defined workload. Prompt length, output length, concurrency, arrival rate, warm-up, and cache state can all change latency and throughput.

Percentiles describe a latency distribution. The median describes a typical request, while higher percentiles expose slower requests. Throughput needs a clear unit and measurement interval. Failed requests must be reported alongside successful-request speed so dropping work cannot masquerade as an improvement.

## Day 3 Comparing Jev and the other routers

### Checkpoints 01 to 03 Contracts and baselines

A shared router interface lets different decision methods operate behind the same gateway. Each decision should identify the selected tier, policy version, time spent deciding, and any fallback. If it returns a probability, the event that probability refers to must be defined.

Always-small, always-medium, always-frontier, and random routing establish reference points. A sophisticated router needs to demonstrate a useful tradeoff against these baselines on the same workload. Complexity alone is not evidence of value.

### Checkpoints 04 to 06 The trained fallback router

DistilBERT is fine-tuned to predict labels derived from the evaluated training prompts. Class imbalance can make a classifier prefer a common tier, so its training and evaluation should expose the distribution of labels. Validation data helps choose settings but must not become additional training data accidentally.

The saved artifact needs the tokenizer, weights, label mapping, model identities, and training configuration. Those details determine what its outputs mean. Colab training speed and Mac decision latency are separate measurements.

### Checkpoints 07 to 09 Prompted routing and Jev

A prompted LLM router generates a routing answer, so its own generation time becomes overhead. Jev instead exposes typed decisions. The project tests whether its choices offer a better cost, quality, or latency tradeoff for this workload.

A choice question can select a tier directly. The description of each tier should refer to the actual configured backend. A generic statement that small models handle easy questions does not establish which tasks a particular model can solve.

### Checkpoints 10 to 12 Probabilities and the open decision model

A yes/no routing question can ask whether a specified backend is likely to answer correctly. A threshold then turns that probability into a decision. Asking about several tiers may require multiple calls, and every call belongs in latency and cost accounting.

The self-hosted Strands Decider comparison tests another decision-model approach. Its official runtime and output format must be checked. A model with a specialized decision head should not be assumed to work as ordinary text generation merely because its weights are available.

### Checkpoints 13 to 15 Calibration and operating points

Calibration compares predicted probabilities with observed frequencies for a defined event. If a group of predictions assigns roughly 80 percent probability to an event, calibration asks whether that event occurs roughly 80 percent of the time.

A peaked choice distribution is not automatically an 80 percent chance that the generated answer will be correct. The experiment must distinguish predicting an oracle label from predicting backend answer success. Threshold selection creates different cost and quality operating points, which are chosen on validation data.

### Checkpoints 16 to 18 Decision overhead and dispatch

The router's decision time is only one part of a request. Total latency also includes queueing, generation, verification, and network work. Historical p95 values cannot simply be added to obtain the p95 of a routed system.

The final gateway dispatch uses the chosen policy but still checks backend availability, capability, context limits, and resource rules. Saving policy and question versions makes it possible to reproduce the decisions later.

## Day 4 Verifying answers and reusing work

### Checkpoints 01 to 03 Verification and cascades

A router decides before seeing the generated answer. A verifier judges an answer after it exists. These are different tasks. In a cascade, the system starts with a cheaper model, checks its output, and moves to a stronger configured tier when the answer is rejected.

A false accept allows a wrong answer through. A false reject discards an answer that was already correct. These mistakes have different consequences. The verifier's opinion is not ground truth; its decisions must be compared with independently scored answers.

### Checkpoints 04 to 06 Hybrid execution and cumulative budgets

The hybrid combines a routing decision with verification afterward. This can avoid some unnecessary generation, but it also adds decision stages. Its usefulness must be tested against route-first and cascade-only execution.

The full chain shares a deadline and a resource budget. Each rejected answer has already consumed time and tokens. A verified cascade generally cannot stream an unaccepted answer to the user and later replace it without changing the API's behavior. That tradeoff should be explicit.

### Checkpoints 07 to 09 Embeddings and the answer index

Embeddings represent text as vectors. Similar vectors can suggest similar meaning, allowing the cache to retrieve an answer even when the wording changes. FAISS provides an index for vector search, while metadata connects a vector to its stored answer and context.

Embedding-model identity, vector normalization, dimensions, and index persistence affect retrieval behavior. A saved index must be interpreted with compatible metadata and the same embedding configuration.

### Checkpoints 10 to 12 Similarity is a candidate signal

Two questions can have nearly identical wording and different correct answers. Similarity therefore identifies a candidate reuse opportunity rather than proving that an answer is valid.

The cache must also respect system instructions, conversation context, generation settings, and model or policy changes. Jev can verify whether a candidate answer applies to the new request, but that check still has its own error rate, latency, and cost.

### Checkpoints 13 to 15 Cache lifecycle and evaluation

Cache entries need insertion rules, expiry or eviction, and a way to reset incompatible data. Storing a rejected answer or reusing an answer under the wrong context can contaminate later requests.

The cache benchmark separates true paraphrases, near misses, and unrelated prompts. Hit rate measures reuse, while false-hit rate measures harmful reuse under an explicit denominator. A higher hit rate is useful only when the accepted answers remain sufficiently accurate.

### Checkpoints 16 to 18 The composed request path

The complete request path checks a cache candidate, verifies reuse when configured, routes a miss, generates an answer, optionally verifies or escalates it, and records the outcome. Each stage contributes to the final user experience.

Testing the whole path catches interactions that isolated component tests miss. For example, a cache hit should not trigger unnecessary generation, and a failed verifier should follow a documented policy rather than disappearing from the records.

## Day 5 Keeping the service observable and reliable

### Checkpoints 01 to 03 Containers and metrics

A container packages the gateway's runtime dependencies. It does not automatically contain or provide a GPU model server. Backend addresses still identify where inference actually runs. Inside a container, localhost refers to that container rather than the Mac host.

Metrics summarize behavior across requests. Counters track events, and histograms describe distributions such as latency. Labels should have bounded values; using complete prompts as labels would make monitoring expensive and expose request content.

### Checkpoints 04 to 06 Timeouts and circuit breakers

A timeout limits how long one operation waits. A retry attempts a suitable failed operation again. A circuit breaker stops repeatedly calling a failing dependency and later probes whether it has recovered.

When Jev is unavailable, the trained fallback router can preserve a request path. That does not guarantee identical quality, latency, or cost. Fallback behavior needs its own evidence. Retrying after answer bytes have already streamed can duplicate output, so the failure boundary matters.

### Checkpoints 07 to 09 Monitoring under load

Prometheus collects metrics and Grafana presents them. Useful panels connect request rate, latency, errors, selected tiers, verification, cache behavior, fallback, and spending. A dashboard is most useful when it helps explain what changed during a real event.

A load generator needs a specified workload, request rate, concurrency limit, and duration. If the client itself falls behind, the measurement should distinguish delayed sending from backend queueing.

### Checkpoints 10 to 12 Steady spike and soak tests

Steady load measures normal sustained behavior. A spike measures the response to a sudden increase in demand. A soak test examines longer-term stability, such as memory growth, resource leaks, or accumulated errors.

All three need saved workload settings and raw outcomes. Fast successful requests do not compensate for a hidden increase in errors. A test that completes for an hour supports a specific stability observation; it does not prove the service can run indefinitely.

### Checkpoints 13 to 15 Kubernetes and state

A Kubernetes Deployment maintains a desired set of gateway replicas. A Service gives clients a stable way to reach them. Readiness determines whether a replica should receive traffic.

Replicas raise state questions. Separate in-memory caches are not automatically shared, and multiple processes should not write the same mutable FAISS files without coordination. The design must either provide safe shared state or describe the per-replica behavior. Deleting a pod under traffic tests actual recovery.

### Checkpoints 16 to 18 Failure evidence and continuous checks

A controlled Jev outage can reveal whether the circuit breaker opens, fallback traffic increases, and recovery happens as intended. Logs, metrics, and request records should tell a consistent story.

Continuous integration checks deterministic behavior on future changes. Mocked regression prompts help detect code regressions without paid calls, but they do not establish that a remote provider still works. Real integration checks remain a separate, explicitly enabled verification step.

## Day 6 Explaining performance and making the project reusable

### Checkpoints 01 to 03 Reproducible GPU investigation

A performance result is tied to hardware, model revision, software versions, workload, and measurement settings. A Colab allocation must be recorded because a later session may provide a different GPU or environment.

A profiler reveals execution behavior, while a benchmark measures performance under a defined method. Profiling can add overhead, so headline timing should come from appropriate unprofiled runs. A missing profiler permission is a limitation to record rather than a reason to invent kernel-level conclusions.

### Checkpoints 04 to 06 Controlled changes and held out evaluation

A useful optimization experiment changes one factor while holding the relevant conditions fixed. Repeated baseline and candidate runs help reveal ordinary variability. Producing fewer output tokens, using warm cache entries, or failing more requests can create an apparent speedup without improving the intended workload.

The held-out router evaluation happens after model settings, routing questions, and thresholds are frozen. The final test estimates the selected system's behavior. Repeatedly changing the policy in response to test results weakens that interpretation.

### Checkpoints 07 to 09 Quality cost and uncertainty

Cascade and cache comparisons need the same care as routing comparisons. A verification strategy that lowers visible errors may increase latency and generation cost. A cache that reduces generation calls may still spend time on embeddings and candidate checks.

Reported cost should distinguish actual API usage from modeled GPU capacity scenarios. Accuracy also needs its sample count and uncertainty. Relative accuracy retention can hide an absolute change, so both forms should be explained when used.

### Checkpoints 10 to 12 Reports and installation

A chart should be generated from saved records rather than manually entered headline numbers. Units, sample counts, configurations, and input paths explain what the chart actually represents.

A reusable repository needs a clean installation path, clear model setup, configuration examples, a doctor command, and a documented demo. The model weights and credentials should remain external resources rather than hidden requirements inside the repository.

### Checkpoints 13 to 15 Reproduction and communication

A clean checkout tests the instructions from another user's perspective. This can uncover assumptions about local files, cached downloads, working directories, or unpublished artifacts.

A technical report should explain what was tested, why the comparison was fair, what changed, and where the findings stop applying. Mac inference results, Colab NVIDIA results, mocked checks, and replayed evaluations should remain identifiable.

### Checkpoints 16 to 18 Evidence and project ownership

A defensible project story connects a problem, a design choice, a measurement, and a conclusion. Resume statements should use only numbers that can be traced to saved evidence. Code generated with assistance still needs review and an explanation of how it behaves.

The final contribution history records meaningful changes. The learning record explains the reasoning behind those changes. A full feature checklist, reproducible commands, honest limitations, and clear artifact provenance make the repository useful to someone who wants to fork and adapt it.

## Prompt for an actual end of day journal entry

Paste prompts/end_day_journal.md after the day's work. It will produce finished prose based on the real repository and observations, adding the specific implementation details that cannot be known in advance.

