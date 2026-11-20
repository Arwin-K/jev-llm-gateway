# Engineering decisions

Record actual decisions, context, alternatives, evidence, affected code/configuration, and revisit conditions. The project retains the original full feature scope.

## Day 1

- Explicit tier names are the public API for now. `auto` requires the Jev router in Day 3. Backend completion JSON is preserved; routing metadata is in headers.
- Native Ollama is the Mac self-hosted runtime. Candidate tags followed the 18 GB unified-memory and 18 GiB free-disk preflight, but actual residency is unmeasured. Sequential quality runs cannot prove simultaneous routing latency.
- Core Python dependencies exclude training and GPU serving. Optional training/embedding groups and notebook-only vLLM stay separate. Revisit versions after a real Colab GPU preflight.
- Frontier admission requires explicit positive caps and prices. Counters are process local and estimated tokens may differ from provider billing. Revisit for durable multi-worker accounting before production.
- SSE forwards without full-body buffering. Once headers are sent, a midstream backend failure cannot become an ordinary JSON error; trace it as interruption. Revisit precise client-visible failure semantics.


## Day 2

- Use pinned source files and explicit preparation instead of making normal tests download benchmarks. The row API returned HTTP 429, while revision-specific Parquet and JSON files were retrievable. Raw dataset text remains ignored; only the ID/hash index is committed.
- Make project train/validation/test labels distinct from official source split names. A fixed seed and exact normalized-text grouping produce the 2,500-prompt target; semantic duplicate detection remains a later risk assessment.
- Use Docker-only MBPP scoring with no host fallback. Confirmed local pass/fail/crash/timeout behavior; containers are risk reduction, not an absolute boundary.
- Reuse only compatible completed results, preserving original identity and timestamps. Failures remain retryable. Reports require an explicit saved run file so failed attempts are not silently lost behind successful checkpoints.

## Day 3 local classifier

- The DistilBERT adapter loads only an artifact marked `trained_distilbert` with saved weights, tokenizer, labels, train/validation provenance, and matching backend model identities. Operators must also supply the generation-settings fingerprint from the training records as `JEV_ROUTER_TRAINING_FINGERPRINT`. The gateway does not infer that an arbitrary pretrained checkpoint is a trained fallback. CPU is the portable Mac default; MPS is an explicit optional device. No actual artifact or Mac classifier latency exists yet because training labels are unavailable.

- Jev uses the verified official `POST /v1/systemone` HTTP contract directly through the core `httpx` dependency. A separate process-local reservation gate requires `TYPESAFE_API_KEY`, a configured decision model, sourced positive rates, and positive request/token/USD caps. No rates are assumed and retries are disabled so one reserved admission corresponds to at most one request. The official API schema and Python SDK were checked on 2026-10-29: https://api.typesafe.ai/openapi.json and https://github.com/typesafe-ai/typesafe-sdk-python/blob/main/README.md. No live Jev request was made.

- `model=auto` defaults to Jev choice, with only a compatible trained DistilBERT artifact as the production fallback. If either decision is unavailable, auto returns 503. Explicit tiers bypass routing. After a decision, the gateway rechecks eligibility, deadline, and frontier budget before generation; the existing SSE forwarding and cancellation path remains intact. Operators may select fixed/random/prompted/Strands policies by configuration for comparison. The default Jev path remains disabled until its paid admission conditions are configured.

- Calibration reports require one declared event per binary report. Oracle-tier distributions, named-generator success probabilities, and realized selected-generator correctness use different labels and cannot share an ECE denominator. Validation tuning requires complete selected-result coverage, known observed cost, and a stated correct-completion objective; without these it returns no selected threshold. The current data support only coverage reporting.

- The bounded router decision collector saves selected and error rows without calling a generation backend. Jev collection additionally requires an explicit `--paid-enabled` flag, a positive per-run USD cap, a decision count cap, configured credentials/model, and positive rates tied to an HTTPS source URL and ISO effective date. Calibration reports read these decisions and independent validation scores; absent scored coverage produces `insufficient_data` instead of numerical calibration metrics.

## Day 4 verification boundary

- Answer verification asks whether the supplied generated answer satisfies the request and applicable instructions. The Jev judgment is a probability about that event, not an independent correctness label. Thresholds need a source identity and will be selected from validation records when available. Verification failure defaults to a terminal closed result; an explicitly configured `return_unverified` mode is labeled as such. Cascade outputs remain buffered until a stage is accepted, so rejected answers cannot leak through SSE as provisional final output.

- Verified paths use one per-request deadline and cumulative request, token, and USD reservations across route, generation, and verification stages. Jev and frontier retain their separate process-local admission guards as additional ceilings. Local model capacity cost remains unknown, not zero; a zero USD cap admits local-only work but no paid stage. The transport performs one call per stage, avoiding nested retries. Verified modes buffer generation and therefore increase time to first visible output until an answer is accepted.

## Day 4 cache scope

- Cache scope hashes exact system/developer instructions, prior conversation, configured local namespace, policy/model catalog identity, generation settings, and embedding revision. Only the final user message varies for semantic retrieval. The namespace is a local configuration partition, not an authentication system. Entry scope, expiry, acceptance, and embedding identity are checked before stored question/answer text can be sent to Jev. Default reuse requires a verified accepted entry; unverified reuse is a separately labeled experimental mode.

- Cache insertion requires an accepted nonempty answer, compatible embedding identity, and a future expiry. Verified acceptance is the default storage gate; unverified storage requires an explicit experimental flag. Invalidation and reset rebuild a new FAISS generation and atomically move the current pointer. Eviction removes the oldest entries at the configured cap. Rejected, partial, cancelled, and failed outputs do not enter insertion.

## Day 4 HTTP integration

- New buffered modes are opt-in request fields. The default path retains standard explicit/auto dispatch and streaming. The new path rejects SSE before work, preventing rejected generation tokens from escaping. `route_first` returns a labeled unverified answer; cascade and hybrid only return accepted verified answers. The HTTP path uses fail-closed verifier behavior, although the lower-level acceptance contract exposes an explicit unverified failure policy for experiments.
- Verified cache hits skip generation; misses and cache errors continue to generation within the same deadline. A cache answer must still match the current eligible tier and backend model. Insertions follow an accepted verified generation and failures are traceable without discarding the accepted answer. Unknown cache-hit usage is returned as unknown. Similarity-only reuse needs an explicit experimental configuration flag.
- Paid execution requires a separate positive per-request run cap and enable flag in addition to the provider's process cap. The Jev verifier and router share one client when the configured router is Jev, but neither provider caps nor the cache lock are durable distributed coordination. Revisit multi-worker budgeting and shared cache architecture before deployment beyond one local worker. No real threshold has yet been selected.

## Day 5 deployment and resilience

- The gateway image installs locked core dependencies and runs as a nonroot ARM container. Ollama model servers, weights, and secrets remain external. Compose uses `host.docker.internal`, but an actual container and kind pod returned `Network is unreachable` while Ollama was absent; no backend connectivity is inferred from DNS alone. Local monitoring ports bind to loopback, and the kind Service is ClusterIP.
- `/healthz` is process liveness. `/readyz` is process readiness and explicitly leaves backend availability unchecked; it returns 503 when a configured DistilBERT router or explicitly required trained fallback cannot load. It does not prove model residency. Jev failures are counted by a process-local circuit breaker: three qualifying failures open it by default, then one probe after 30 seconds may close it. Routing may use only a compatible trained DistilBERT artifact as fallback. Answer verification does not use the classifier as a verifier and remains fail closed.
- HTTP admission bounds active work and queue length per process; queue time consumes the same request deadline. Backend transports have zero automatic retries. For buffered `model=auto` standard requests, explicit `JEV_AVAILABILITY_FAILOVER_ENABLED=true` permits at most one eligible local alternate after a retryable network or 5xx failure. Explicit tiers, streaming after bytes, 4xx failures, and implicit paid upgrades are excluded. This availability policy is distinct from quality escalation.
- Metrics use bounded labels and in-memory fixed-size histogram buckets; one client request is counted once even if it has multiple generation attempts. First-output timing exists only for streamed answers. Unknown usage/cost remains unknown; USD reservation series is an estimate, not provider billing. Replica p95 uses summed histogram buckets. Detailed request IDs and stage records remain in logs.
- The kind manifest defaults to two pods with cache off and paid execution off. Each pod has separate process-local metrics, budget counters, breaker, and optional cache state. No writable FAISS directory is shared. A globally enforced paid budget or shared cache would require a coordinated service; two gateway replicas do not increase external Ollama capacity. The 40-request replacement check observed one error, so recovery is not represented as zero-error.
- Locust uses a closed-loop user schedule with explicit request and output-token ceilings; user-count changes do not establish offered-rate changes. Paid-capable runs require positive provider process caps whose sum fits within a declared run USD ceiling, but the runner cannot verify caps in a separately configured gateway or coordinate replicas. Real paid multi-replica load remains blocked until a shared ledger or external provider cap exists. Raw per-request events are retained because Locust's periodic CSV can remain stale in very short capped runs.

## Day 6 evidence and release decisions

- The NVIDIA serving workload is deterministic synthetic text and is separate from benchmark quality prompts. All benchmark request outcomes remain in raw per-run JSON. A separate `diagnostic_only` flag prevents Nsight-profiled traffic from entering headline timing comparisons. Before/after `nvidia-smi` snapshots are observations, not a utilization trace or kernel diagnosis.
- A serving candidate requires three successful compatible real baselines and an explicit observation, explanation, expected benefit, and regression risk. It changes one batch-token budget. No candidate was created in the absence of a baseline. Repetitions must alternate and match workload, arrival, concurrency, warm-up, timeout, and request count.
- The held-out test remains locked. The freeze audit checks full unique scored train/validation tier coverage, required freeze fields, one model/settings identity per tier, and stable template identities within each task. A tier may use different templates across math, choice, and code; freeze configuration records those task-scoped templates. The existing unscored/error rows cannot satisfy coverage. No test result may be used to tune the same purported frozen comparison.
- Cost reconciliation keeps recorded charges, sourced dated API estimates, modeled allocated GPU capacity, and unknown stages separate. Unknown rejected attempts prevent a complete total claim. A local package health check cannot substitute for a successful model or provider request.
- The project has no declared license. The local technical report and portfolio notes are drafts, not a publication instruction. A public release requires rights review, complete real experiments appropriate to its claims, and a specified destination.

## Answer-format templates v2 and final-answer scoring (2026-11-13)

**Status:** decided and implemented; supersedes the open entry recorded earlier the same day.

The first live pilot scored 0 of 10 because local models rarely end with a bare `Answer: <number>` line (`evidence/day7/answer-format-probe-20261113.txt`). A ten-prompt MBPP probe also showed the hidden-test protocol mostly measured whether the model guessed the function name: 2/10 passed without the name and 7/10 with it.

Decision:

- **Templates v2.** Math and choice put the format instruction after the content (`Answer: <number>` / `Answer: <letter>`). Code prompts name the one non-builtin function the hidden tests call (399 of 400 selected tasks); tests stay private. v1 templates remain in code and reproduce the v1 manifest byte for byte (SHA-256 `11b997a0…`, preserved at `runs/day2-manifest-v1.jsonl`).
- **Selection is template-independent.** Deduplication, selection and split assignment always use the v1 rendering; `eval-prepare --previous` refuses any change in prompt IDs or splits. The v2 manifest (`d92b9f0a…`) has the same 2,500 IDs, splits and group IDs.
- **Final-answer scoring.** Math accepts every `Answer:` marker and `\boxed{}` when they agree on one number, allowing units, currency and thousands separators; it rejects no marker, further digits after the number, or conflicting values. Choice accepts decorated `Answer: X` lines but rejects option lists and lowercase words. Code accepts exactly one fenced block even with surrounding explanation; several blocks remain ambiguous.
- **Strict compliance is kept, not hidden.** Each result records `format_compliant` from the v1 strict reader (or code-only output), and `eval-report` shows `strict_format_rate`.
- **Output limit.** `eval-run` defaults to 512 output tokens; 256 truncated a pilot answer.

Results recorded under v1 templates have different template fingerprints and are excluded from routing labels by the existing identity checks.

## Maintenance decisions — 2026-11-17 America/Toronto

- Keep failure evidence explicit: sandbox cleanup must not replace the original timeout; failed Locust launches must leave a terminal manifest; malformed raw request lines must be counted while valid rows remain reportable; and reversed timestamps must not produce throughput metrics.
- Validate checkpoint IDs as lowercase SHA-256 digests before using them as filesystem paths. Include the checkpoint and sandbox changes in the existing focused CI lint scope.
- These are local reliability fixes. They do not establish provider, model, Colab, container, or load-test success.

## Evaluation run reporting — 2026-11-19 America/Toronto

- `jev eval-run` reports returned result rows separately from rows restored from immutable checkpoints, backend attempts made in the current invocation, and new responses. A resumed run must not present reused answers as fresh model work. Per-attempt timestamps and source run IDs remain in the result records.
- Evidence: a 10-row invocation on 2026-11-19 returned 10 checkpoint-reused rows and made no backend calls; see the raw ignored file noted in `STATUS.md`. Focused summary, runner, and checkpoint tests passed.
- Add repeatable `--task` filtering before the prompt limit. This lets operators collect math/choice while Docker-based code scoring is unavailable, without changing source ordering, split assignment, checkpoint identity, or the held-out test gate.
- Add exact `--prompt-id` selection before the prompt limit so an operator can retry one unresolved failure without reissuing the rest of a task batch. Unknown IDs, IDs outside the selected split/tasks, and duplicate IDs are rejected.
- For a user-requested overnight pause, stop a serial evaluation after its latest durable per-prompt checkpoints, preserve the partial outcomes as incomplete, and resume with the identical split/task/model/settings and caps so existing checkpoint rows are reused. The 2026-11-19 medium-tier run has 420 of 1,260 train math/choice rows checkpointed; the runner and Ollama server were stopped. The verified resume command and stop evidence are in `evidence/day7/medium-train-stop-audit-20261119.json`.
- Compare tiers on identical prompt IDs and fingerprints, but keep train-only paired outcomes descriptive; use saved validation records for any calibration, cascade, or routing-threshold decision. The 2026-11-20 small/medium train comparison covered identical math/choice IDs, while the held-out test remained untouched; see `evidence/day8/medium-train-math-choice-audit-20261120.json`.
- Keep the medium validation comparison descriptive and provisional until the full freeze requirements are met. All 500 medium validation IDs now have records, with 494 binary scores and six parse errors. The saved `mbpp:401` response was re-run through the Docker scorer and produced a Python `SyntaxError`; the sandbox now classifies that as a code crash/incorrect answer. No threshold was selected, and the held-out gate remains closed for incomplete coverage and missing freeze configuration.
- Do not replace failed Docker-backed code scoring with an unisolated local execution or a mock. If the Desktop daemon is unavailable, record the affected code stage as blocked and continue with independent math/choice work. The 2026-11-20 daemon startup/restart failure is recorded in `evidence/day8/mac-docker-blocker-20261120.json`.
