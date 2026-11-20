# Observed environments

## Maintenance verification — 2026-11-17

The existing `.venv` on the Mac used Python 3.14.5. `make verify` passed source compilation and 149 offline tests; its raw output is preserved at `evidence/testing/maintenance-offline-20261117.txt`. The focused Ruff command added to GitHub Actions was not executed locally because `uv` and `ruff` are unavailable on PATH. No external services, model endpoints, containers, or GPU were used for this maintenance check.

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

## Day 4 final Mac check — 2026-10-30 America/Toronto

The project venv ran 99 offline tests successfully. `jev doctor` again reported `ConnectError` for both Ollama tiers and `frontier.configured=false`; evidence is in `evidence/day4/`. The new HTTP integration tests used `httpx.MockTransport` and controlled Jev/cache fixtures, not provider requests. The cache's optional native dependencies and pinned model weights remain absent, so the runtime cache initialization and physical index behavior need a separate Mac validation run after installation.

## Day 5 Mac deployment check — 2026-10-31 America/Toronto

Observed `arm64`; the earlier hardware inventory identifies an M3 Pro with 18 GB unified memory. Docker Engine 29.6.2 was reachable with 8,321,372,160 bytes assigned to the daemon. Disk available fell from about 13 GiB at initial check to 5.8 GiB during kind testing; after the named cluster and its unused node image were removed, it was 8.3 GiB. Existing unrelated Docker containers and images were left intact. The project Compose containers were stopped with their two monitoring volumes retained.

The locked `python:3.12.7-slim-bookworm` ARM gateway image built and passed its actual `/healthz` container check. Compose used Prometheus v3.9.0 and Grafana 12.2.0 on loopback ports. `promtool` accepted the scrape configuration and four recording rules; the gateway target was up, and Grafana provisioned its dashboard. The kind v0.33.0 ARM CLI was downloaded to temporary storage and matched its official SHA-256. Its pinned Kubernetes v1.37.0 node image ran a project-only cluster with two ready gateway pods. The cluster and node image were removed after evidence collection.

Both the container and a pod resolved `host.docker.internal` for the Mac, but a request to native Ollama failed with `Network is unreachable`; in-pod `jev doctor` returned `ConnectError` for both local tiers and frontier unconfigured. The native `ollama` command and trained DistilBERT artifact remain absent. Locust 2.47.0 was installed into a temporary Python 3.14.5 venv and ran a two-request failure-path check; it has not run a real model workload. No Colab GPU, paid provider, MiniLM, native FAISS, or real model residency was available.

## Day 6 Mac and package check — 2026-11-01 America/Toronto

The execution host has Python 3.14.5 on Mac arm64; `docker` is available, while `nvidia-smi`, `nsys`, `ollama`, and `uv` were unavailable in PATH. The data volume had about 75 GiB free at the opening check, an improvement from Day 5; this is not a GPU or model-memory result. The relevant paid API/model environment keys were unset. No Colab runtime was accessible from this session.

The existing `.venv` has test dependencies but no `pip` or `ruff`; system Python has `pip` but initially lacked `hatchling`. Installing `hatchling==1.27.0` into `/tmp/jev-day6-build` required network access beyond the default sandbox. The standard wheel then built successfully and installed with runtime dependencies in `/tmp/jev-day6-fresh`; its CLI imported and `doctor` returned unavailable small/medium tiers plus unconfigured frontier. A separate clean local clone and fresh venv installed the test extra, ran 127 passing tests, and returned HTTP 200 from a temporary loopback `/healthz`. The first loopback bind inside the default sandbox failed with `operation not permitted`; the same bounded local check succeeded with the permitted bind. Neither check ran inference. The final source revision has a later environment-recording test; see the final `EXPERIMENTS.md` entry for its suite count.

## 2026-11-13 Mac update

Native Ollama 0.40.16 is installed at `/usr/local/bin/ollama` with `qwen2.5:1.5b` (986 MB download) and `qwen2.5:7b` (4.7 GB). Both run 100% on the GPU through the llama.cpp runner with a 4,096-token context. With default Ollama settings only one of the two stayed resident after sequential requests. Disk had 67 GiB free before the pulls. The Docker daemon was not running at this check. Evidence: `evidence/day7/mac-live-smoke-20261113.json`.


## 2026-11-16 local test environment

The existing project `.venv` uses Python 3.14.5 and pytest 9.1.1 and successfully ran the full offline suite. The `uv` executable is not on this Mac's PATH, so `make setup-test` was not run here; the current venv already contains the locked core/test runtime needed for `make verify`. A fresh checkout should install uv, then run `make setup-test`. Docker Compose configuration validation passed without starting containers. This check did not contact Ollama, Jev, frontier providers, Colab, or any model service.

## Local inference and evaluation update — 2026-11-19 America/Toronto

The ignored local `runs/` directory contains v2 real-answer observations dated 2026-11-13/14: a 500-prompt small-tier validation set, 578 small-tier train math checkpoints, and 30-prompt pilots for small, medium, and small with strict code output. Sanitized run IDs, model tags, fingerprints, and outcome counts are recorded in `evidence/day7/local-v2-coverage-audit-20261114.json`. These results are separate from the older Day 6 freeze audit and do not establish complete three-tier coverage or a final frozen comparison. The model tag is captured, but the output records do not include an immutable weight digest.

On 2026-11-19, an authorized `jev doctor` check returned `ConnectError` for both configured Ollama URLs; the sanitized output is `evidence/day7/mac-doctor-20261119.json`. A bounded 10-prompt CLI invocation reused existing checkpoint rows and did not issue generation requests. Frontier was unconfigured. This session made no paid calls and did not start Docker, Colab, model downloads, or other compute.

The runner's resumed-work summary is locally verified with Python 3.14.5 and the existing test environment. It reports checkpoint reuse, current backend attempts, and current responses separately. No dependency or model download was needed.

After the runner change, `make verify` passed **150 tests** with one existing Starlette deprecation warning. Compileall and the full local suite passed; raw output: `evidence/testing/offline-after-resume-summary-20261119T1926-0500.txt`.

The 2026-11-19 `docker info` check found no Docker Desktop daemon socket. Containerized code evaluation and local kind/Compose execution therefore cannot run in this session; no container or cluster was started. Sanitized output: `evidence/day7/mac-docker-20261119.json`.

Later on 2026-11-19, the installed Ollama 0.40.16 server was started on `127.0.0.1:11434` only. `/api/tags` reported `qwen2.5:1.5b` digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` and `qwen2.5:7b` digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`. The gateway doctor found both configured models installed. A bounded small-tier train smoke made one new request and reused 578 saved checkpoints. Sanitized run details: `evidence/day7/mac-local-eval-smoke-20261119.json`.
