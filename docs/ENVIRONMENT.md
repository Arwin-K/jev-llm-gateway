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

## Strands Decider comparison requirements

The official [Strands Decider inference guide](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md), checked 2026-10-29, documents a local `strands-decider serve CHECKPOINT --device mps --port 8099` typed `POST /v1/systemone` endpoint. It is a decision model, not a chat completion server. The adapter requires a loopback URL, explicit served model name, checkpoint identity, and device; the server should be launched with its strict-window option for comparisons. The current reference 2B checkpoint also downloads a roughly 4.5 GB base model. With this Mac's 18 GB memory and previously observed 18 GiB free disk, no checkpoint download, server start, memory measurement, or real inference was attempted. The typed HTTP path is fixture-tested only.

## Day 3 Mac check — 2026-10-29 America/Toronto

`jev doctor` still returned `ConnectError` for `qwen2.5:1.5b` and `qwen2.5:7b`; frontier was unconfigured. `ollama` and `uv` were absent from PATH. The available fixed/random decision benchmark ran on macOS 26.5.2 arm64 with no model loaded; run ID and latency results are in `EXPERIMENTS.md`. Process `ru_maxrss` was 31,424,512 bytes before and after that benchmark, a process high-water mark rather than per-policy allocation. Colab, Jev, Strands, and DistilBERT model paths were not measured.

## Day 4 embedding preflight — 2026-10-30 America/Toronto

The core Mac venv has no `torch`, `transformers`, `sentence_transformers`, or `faiss` import. No model weight download or real embedding inference was attempted. The optional adapter requires an immutable revision of [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), whose model card states Apache-2.0 and 384 dimensions; it defaults to local-files-only CPU loading and checks the loaded model's sequence length and normalized output. The [Sentence Transformers API](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html) documents revision pinning, local-files-only loading, and normalized encoding. Sources checked 2026-10-30. Fixture tests do not establish Mac package or model compatibility.

## Day 4 FAISS preflight — 2026-10-30 America/Toronto

`faiss` and NumPy are absent from the core Mac venv, so no native ARM import, save/reload, or search timing is claimed. The optional index uses `IndexFlatIP` over unit-normalized float32 vectors, making its inner-product score cosine similarity under the [official FAISS metric guidance](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances). The [FAISS I/O guide](https://github.com/facebookresearch/faiss/wiki/Index-IO%2C-cloning-and-hyper-parameter-tuning) documents `write_index`/`read_index`. A fake index tests this repository's version-pointer, checksum, and metadata mapping code only. A process-lifetime file lock prevents a second writer; deployment must not assume shared mutable cache state across replicas. Sources checked 2026-10-30.
