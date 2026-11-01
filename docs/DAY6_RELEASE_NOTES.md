# Day 6 local checkpoint notes

The `day-six` branch prepares a reproducible NVIDIA serving investigation, protects the frozen quality evaluation boundary, and makes the repository easier to inspect from a clean checkout. It does **not** claim an executed GPU optimization or complete gateway research result.

## Added

- A source-revision/archive-hash-pinned Colab notebook, actual environment recorder, synthetic workload, bounded request-level vLLM benchmark, and optional separate Nsight Systems profile wrapper.
- A one-factor serving candidate gate requiring successful live baselines, plus an alternating-run comparator that retains errors, output lengths, throughput, latency, and GPU snapshots.
- A pre-test freeze audit with unique scored-coverage and generation-identity checks, a composed-system coverage audit, paired-group uncertainty helper, full-stage cost reconciliation, and a raw-audit SVG figure.
- A clean-checkout reproduction guide, technical report, portfolio evidence notes, provenance guidance, and full original-scope release audit.

## Verified locally

The latest Mac offline suite passed 129 tests. A final wheel built and imported in an isolated standard-dependency environment without CUDA. An earlier clean-clone revision installed with the test extra, passed 127 tests, and returned HTTP 200 on loopback `/healthz`. These checks did not run a model. No tracked private run or benchmark source snapshot was found in the repository inventory.

## Still required before research conclusions or publication

Collect compatible real train/validation answers across tiers, train and validate the fallback, freeze all policies and generation settings, then run the held-out test once. Obtain an actual Colab GPU allocation, run unprofiled baselines, collect a separate diagnostic trace where supported, test one evidence-motivated serving change, and repeat both conditions. Complete real cascade/cache/calibration/cost and sustained load comparisons, rights review, target-platform CI, and a publication destination. The project has no declared license and no external release was made.
