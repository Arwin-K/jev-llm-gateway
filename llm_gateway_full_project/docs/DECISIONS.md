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
