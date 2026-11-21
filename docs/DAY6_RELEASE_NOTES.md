# Day 6 local checkpoint notes

The `day-six` branch prepares a reproducible NVIDIA serving investigation, protects the frozen quality evaluation boundary, and makes the repository easier to inspect from a clean checkout. It does **not** claim an executed GPU optimization or complete gateway research result.

## Added

- A source-revision/archive-hash-pinned Colab notebook, actual environment recorder, synthetic workload, bounded request-level vLLM benchmark, and optional separate Nsight Systems profile wrapper.
- A one-factor serving candidate gate requiring successful live baselines, plus an alternating-run comparator that retains errors, output lengths, throughput, latency, and GPU snapshots.
- A pre-test freeze audit with unique scored-coverage and generation-identity checks, a composed-system coverage audit, paired-group uncertainty helper, full-stage cost reconciliation, and a raw-audit SVG figure.
- A clean-checkout reproduction guide, technical report, portfolio evidence notes, provenance guidance, and full original-scope release audit.

## Verified locally

The latest source-tree Mac verification on 2026-11-21 compiled the project and passed 167 offline tests, with one existing Starlette deprecation warning. A one-request 16-token-cap loopback smoke returned HTTP 200 through `qwen2.5:1.5b`; it is connectivity evidence only. The Colab/NVIDIA notebook now has static syntax, loopback, measurement-separation, and cleanup tests, but no GPU runtime was provisioned. A previous wheel built and imported without CUDA, and an earlier clean-clone revision passed 127 tests; neither check represents the current revision. No tracked private run or benchmark source snapshot is included.

## Still required before research conclusions or publication

Collect compatible real train/validation answers across tiers, train and validate the fallback, freeze all policies and generation settings, then run the held-out test once. The latest freeze audit has incomplete binary coverage and missing fields, so the test gate remains closed. Obtain an actual Colab GPU allocation, run unprofiled baselines, collect a separate diagnostic trace where supported, test one evidence-motivated serving change, and repeat both conditions. Complete real cascade/cache/calibration/cost and sustained load comparisons, rights review of benchmark/model/provider terms, target-platform CI, and a publication destination. Repository code is MIT-licensed; no external release was made.

Current revision packaging remains blocked: `make build` exits 2 because `uv` is missing from PATH, and neither the test venv nor system Python has the `hatchling` build backend. No network installation was attempted. Raw result: `evidence/day9/package-build-blocker-20261121.txt`.
