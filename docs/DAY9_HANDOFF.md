# Day 9 work-session handoff — 2026-11-21 America/Toronto

**Project plan position:** Day 6, checkpoint D6-18. This is a local resume point, not project completion or release approval.

## Work completed today

- D6-06 fixes evaluation output collisions: the CLI reserves the private output path before making any router calls. A regression test verifies an existing file is preserved and no router call occurs.
- D6-07 adds tests for the prompted v4 audit helper's split/version checks, duplicate IDs, usage/task summaries, and saved-result joins.
- D6-08 runs `make verify`: compileall and 165 tests passed, with one existing Starlette/httpx deprecation warning.
- D6-09 adds static checks for the NVIDIA notebook's Python cells, loopback bind, baseline/profile separation, and cleanup.
- D6-10 updates the freeze handoff to the post-`mbpp:401` rescore. Small has 1,444/1,500 binary train and 481/500 binary validation outcomes; medium has 1,487/1,500 and 494/500; frontier has none. No identity issues, but 11 freeze fields are missing and all six coverage targets are short. The held-out test remains locked.
- D6-11 runs `make verify`: compileall and 167 tests passed, one existing warning.
- D6-12 records a read-only Mac preflight: Docker 29.6.2/aarch64, both Ollama models installed, 40% system memory free, 79 GiB disk available; no containers or loaded models.
- D6-13 sends one local small-tier smoke request (16-token cap) through the loopback gateway to `qwen2.5:1.5b`; HTTP 200 and `Hello!`. The gateway was stopped and the model unloaded afterward.
- D6-14 wraps the NVIDIA notebook workload, baselines, and optional diagnostic profile in `try/finally` cleanup. Static tests pass; no Colab/GPU execution occurred.
- D6-15 runs `make verify`: compileall and 167 tests passed in 0.85 seconds, one existing warning.
- D6-16 corrects stale release/license statements. The repository code/docs have an MIT license; benchmark/model/provider rights are separate. The release audit reflects current local outcomes and the closed freeze gate.
- D6-17 attempts `make build`, which exits 2 because `uv` is missing. No current-revision wheel was produced; no network install was attempted.
- D6-18 records this resume point. Today has 13 real local commits including this one; the 18-commit target was not reached, and no artificial commits were added.

## Next steps

1. In an approved local environment with the project's `uv` build tool available, run `make build`; install the wheel into a clean non-CUDA environment and verify package/CLI startup.
2. Do not open the held-out split until all required freeze fields and eligible-tier train/validation coverage are complete. The latest audit is `evidence/day8/freeze-audit-after-mbpp401-rescore-20261120.json`.
3. Jev/frontier comparisons require configured credentials, model identities, sourced rates, and explicit positive caps. DistilBERT requires a compatible trained artifact. Colab DistilBERT/vLLM work requires a user-provided runtime; none was provisioned.
4. Continue real cascade/cache/calibration/load comparisons only when their provider/model prerequisites are available. Keep paid paths disabled until explicitly configured.

## Latest verification and runtime state

`make verify` last passed 167 tests: `evidence/testing/offline-suite-day9-post-cleanup-20261121.txt`. The single local smoke is documented in `evidence/day9/small-gateway-smoke-20261121.txt`; its gateway and Ollama model were stopped/unloaded. No containers remain running. Current build blocker: `evidence/day9/package-build-blocker-20261121.txt`.

The previous project handoff remains at [`DAY8_HANDOFF.md`](DAY8_HANDOFF.md). The updated technical report is [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md). All release notes are local; nothing was published.
