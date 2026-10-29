# Engineering decisions

Record actual decisions, context, alternatives, evidence, affected code/configuration, and revisit conditions. The project retains the original full feature scope.

## Day 1

- Explicit tier names are the public API for now. `auto` requires the Jev router in Day 3. Backend completion JSON is preserved; routing metadata is in headers.
- Native Ollama is the Mac self-hosted runtime. Candidate tags followed the 18 GB unified-memory and 18 GiB free-disk preflight, but actual residency is unmeasured. Sequential quality runs cannot prove simultaneous routing latency.
- Core Python dependencies exclude training and GPU serving. Optional training/embedding groups and notebook-only vLLM stay separate. Revisit versions after a real Colab GPU preflight.
- Frontier admission requires explicit positive caps and prices. Counters are process local and estimated tokens may differ from provider billing. Revisit for durable multi-worker accounting before production.
- SSE forwards without full-body buffering. Once headers are sent, a midstream backend failure cannot become an ordinary JSON error; trace it as interruption. Revisit precise client-visible failure semantics.

