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

After checkpoint summary reporting, `make verify` passed **150 tests** with one existing Starlette deprecation warning. After task-filter support, it passed **152 tests**; after exact prompt-ID selection, it passed **153 tests** with the same warning. Latest raw output: `evidence/testing/offline-after-prompt-id-filter-20261119T2246-0500.txt`.

The 2026-11-19 `docker info` check found no Docker Desktop daemon socket. Containerized code evaluation and local kind/Compose execution therefore cannot run in this session; no container or cluster was started. Sanitized output: `evidence/day7/mac-docker-20261119.json`.

Later on 2026-11-19, the installed Ollama 0.40.16 server was started on `127.0.0.1:11434` only. `/api/tags` reported `qwen2.5:1.5b` digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` and `qwen2.5:7b` digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`. The gateway doctor found both configured models installed. A bounded small-tier train smoke made one new request and reused 578 saved checkpoints. Sanitized run details: `evidence/day7/mac-local-eval-smoke-20261119.json`.

The evaluation command has task-level filtering for collecting non-code results while Docker-based code scoring is offline, and exact prompt-ID filtering for a bounded retry. Both are applied locally and do not require an additional package or service.

Docker Desktop 29.6.2 was later started from the installed app bundle. It reported an ARM64 daemon with an 8,321,372,160-byte memory limit. The cached `python:3.12.7-slim-bookworm` image was ARM64 with image ID `sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d`. Small-tier code scoring used ephemeral network-disabled containers; no evaluation containers remained after the run. The final Mac training coverage and exception counts are in `evidence/day7/small-train-full-audit-20261119.json`.

At 2026-11-19T23:24:45-05:00, the medium-tier evaluation command was active in the Codex-managed shell session, while native Ollama served `qwen2.5:7b` at `127.0.0.1:11434`. `ollama ps` showed the 4.8 GB model on GPU with a 4,096-token context; `memory_pressure` reported 28% system memory free. Docker Desktop was stopped during this non-code workload. While active, the process was visible in the command runner session and its prompt checkpoints were written under the ignored `runs/day2-checkpoints/`; it did not appear as a separate app window. See `evidence/day7/medium-train-runtime-snapshot-20261119T2324-0500.json` for the sanitized snapshot. These are point-in-time readings, not a memory trace or a completed model comparison.

At 23:38, the evaluation command exited 130 after the requested overnight pause, then the loopback Ollama server was stopped too. A final inventory confirmed 420 intact checkpoint files and 62% system memory free. Tomorrow's resume command starts Ollama explicitly on loopback and reuses those checkpoint files; see `evidence/day7/medium-train-stop-audit-20261119.json`.

On 2026-11-20, Ollama 0.40.16 was restarted with `OLLAMA_HOST=127.0.0.1:11434`. It loaded `qwen2.5:7b` at digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` on Apple Metal; `ollama ps` reported 4.8 GB, 4,096-token context, and 100% GPU. The resumed evaluation finished with 1,260 train math/choice rows, reusing 420 checkpoint records. At 11:10 local time, system memory free was 27%. Docker Desktop UI processes were present but `docker info` could not connect to its daemon socket; no Docker task was started for this non-code phase.

The medium validation math/choice run later completed 420 unique prompts under Ollama with no Docker dependency. At session close (11:51 local time), the evaluation process and Ollama server were stopped and system memory free was 76%. The Docker Desktop UI process remained, but its daemon was still unreachable; the attempted CLI restart timed out trying to stop stale helpers. No containers or clusters were started. See `evidence/day8/mac-docker-blocker-20261120.json` for the sanitized final state.

On the later resume, the stale Docker Desktop UI/helper processes were terminated and `docker desktop start --detach` restored the daemon. It reported engine 29.6.2, aarch64, with 8,321,372,160 bytes assigned. The cached ARM sandbox image had ID `sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d`. Medium train code completed through the configured isolated evaluator; `docker ps` showed no containers afterward. Ollama was restarted loopback-only for that run. At 17:40 local time, the model had unloaded after its keep-alive and system memory free was 72%; no validation code request had started yet.

By 17:54 local time, medium validation code had completed its initial 80-prompt run plus two bounded exact-ID recovery attempts for `mbpp:401`. All other rows completed scoring; the three attempts for that ID remained `blocked/environment_error`. A trivial call through the same sandbox function passed, but the prompt-specific error is undiagnosed. No evaluation process or Docker container remained active. The loopback Ollama server process was still up with no model resident, and system memory free was 68%.

At 18:07 local time, the restricted command runner could not access Docker's API socket; the Docker CLI reported permission denied. The local network-disabled scorer was run with the authorized elevated execution path against the saved validation response and emitted a Python `SyntaxError`, confirming the generated code was invalid rather than blocked by Docker. Docker Engine reported 29.6.2/aarch64 with 8,321,372,160 bytes assigned during that diagnostic. No model request was made, no paid API was called, and the ephemeral container exited. The response was reclassified as incorrect after the sandbox fix; see the rescore diagnostic and audit in `evidence/day8/`.

Later on 2026-11-20, native Ollama 0.40.16 served the installed `qwen2.5:1.5b` model for bounded prompted-router decisions. Both model tags were installed and the pre-run `memory_pressure` reading showed 75% free. The 500-decision validation batch was serial with 24 output tokens per request; follow-up train pilots were capped at 9 and 30 decisions. Local runs used no paid provider and made no generator-backend calls. The shell network sandbox denied direct loopback access, so the authorized local execution path was used. Command summaries and aggregate usage are in `evidence/day8/prompted-small-*.txt` and `prompted-small-audit-20261120.json`.

The existing Python 3.14.5 `.venv` ran `make verify` after the D4/D5 work: compileall succeeded and **162 tests passed**. One Starlette/httpx deprecation warning remains. No networked provider or model service is part of this offline suite; raw output is `evidence/testing/offline-suite-day8-20261120.txt`.

After prompted-router v4, `make verify` again completed compileall and **162 offline tests passed** in 0.77 seconds. The only warning remains the existing Starlette `TestClient`/httpx deprecation; no networked model/provider was contacted. Full output: `evidence/testing/offline-suite-day8-post-v4-20261120.txt`.

On 2026-11-20, the local Ollama prompted-small v4 router ran a 30-decision train pilot followed by 500 validation decisions. Each request was capped at 24 output tokens; no answer-generation or paid-provider request was made. The first validation invocation ran in the restricted shell and recorded 500 loopback `ConnectError`s. An elevated local inference invocation then hit an already-existing output path after inference completed, so it has no durable decisions. The captured retry used `runs/day8-prompted-small-validation-v4-rerun-20261120.jsonl` and selected on 500/500 rows. Both failure records remain in ignored `runs/` for provenance. See the v4 hash-backed audit for input hashes and usage totals.

On 2026-11-21, `tests/routing/test_evaluate.py` passed all four focused tests after the output-path reservation fix. The existing-path regression uses a patched router call counter and a preserved sentinel file; no model or provider was contacted. Output: `evidence/testing/evaluate-output-collision-20261121.txt`.

Also on 2026-11-21, the v4 audit helper's focused tests passed (2 tests) without model/provider access. Output: `evidence/testing/prompted-router-audit-focused-20261121.txt`.

On 2026-11-21, the full `make verify` after the evaluator output reservation and prompted-audit tests passed compileall plus 165 offline tests in 0.82 seconds. The only warning is the existing Starlette/httpx deprecation. No networked model or provider was used. Output: `evidence/testing/offline-suite-day9-20261121.txt`.

On 2026-11-21, the Day 6 Colab notebook structural tests passed (2 tests) on the Mac Python 3.14 venv. They do not establish Colab/GPU/vLLM compatibility; no runtime was provisioned. Evidence: `evidence/testing/day6-colab-notebook-focused-20261121.txt`.
