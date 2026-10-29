# Observed environments

## Mac preflight, 2026-10-27 America/Toronto

Observed via `system_profiler`, `sw_vers`, `df -h .`, and PATH checks: MacBook Pro Mac15,6; Apple M3 Pro (11 CPU cores); 18 GB unified memory; macOS 26.5.2 (25F84); 18 GiB available on a 460 GiB data volume (96% used). Python 3.14.5 and Docker CLI 29.6.2 are present. `uv`, `ollama`, and `kind` are absent from PATH; `kubectl` is present. `sysctl hw.memsize` was blocked by the sandbox, so the memory value is from `system_profiler`. No serial number, UUID, or username is retained here.

Model candidates after memory and disk review: native Ollama `qwen2.5:1.5b` (listed 986 MB) and `qwen2.5:7b` (listed 4.7 GB). These are download sizes, not measured residency. With only 18 GiB free disk and 18 GB unified memory, concurrent loaded models plus future services require profiling; no simultaneous-residency claim is made. Sources: https://ollama.com/library/qwen2.5 and https://docs.ollama.com/macos (consulted 2026-10-27).

## Colab preflight

`notebooks/colab_preflight.py` records Python, platform, NVIDIA GPU memory/driver, and CUDA compiler on the actual notebook host. It has not been run in Colab. GPU type, memory, quota, and package compatibility remain unknown. Mac results never substitute for Colab checks.


## Day 2 Mac checks, 2026-10-28 America/Toronto

Docker Engine 29.6.2 was reachable under authorized socket access. The pinned Python 3.12.7 slim Bookworm image was pulled and used for four controlled sandbox fixtures; its observed digest is recorded in `DAY2_HANDOFF.md`. The local project venv is Python 3.14.5; optional DuckDB 1.5.6 read pinned Parquet source files. Ollama was not reachable even outside the restricted shell sandbox; frontier credentials/model were not configured. No Colab runtime was available.

## Day 3 training availability — 2026-10-29 America/Toronto

The core Mac venv has no installed `torch` or `transformers`; those remain in the optional `training` extra. The private stored Day 2 run has zero train records and only two failed validation attempts. The Colab notebook and trainer are runnable code paths, but no GPU session, pretrained checkpoint download, training run, or portable trained artifact has been executed. A pinned DistilBERT source revision and complete real train/validation labels are required before training.
