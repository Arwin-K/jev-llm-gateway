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
