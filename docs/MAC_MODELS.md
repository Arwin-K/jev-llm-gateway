# Native Mac Ollama models

The selected candidates are `qwen2.5:1.5b` (small) and `qwen2.5:7b` (medium). Ollama lists their downloads at approximately 986 MB and 4.7 GB respectively. Actual memory residency and load latency are unmeasured.

Install the native macOS Ollama app from https://docs.ollama.com/macos. After installing, use `ollama pull qwen2.5:1.5b`, then `ollama list` and `ollama ps`. With the server running locally, `jev doctor` checks `/api/tags`, and `jev smoke --tier small` sends one bounded request. Do not equate a downloaded model with a successful inference.

The gateway targets Ollama's documented `http://localhost:11434/v1/chat/completions` compatibility surface: https://docs.ollama.com/api/openai-compatibility. The Mac preflight found Ollama absent from PATH on 2026-10-27, so no real small-model answer has yet been observed.

For medium, pull `qwen2.5:7b` only after checking free disk. Run one bounded `jev smoke --tier medium`, then inspect `ollama ps` and Activity Monitor memory pressure. Record cold and warm load times, `size_vram`, and whether both tags remain loaded. The adapter reads `/api/ps` for residency observations. An 18 GB unified-memory Mac may need sequential loading; sequential quality tests cannot establish simultaneous live routing. The medium answer and memory measurements are pending because Ollama is absent.
