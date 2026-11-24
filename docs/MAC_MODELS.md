# Native Mac Ollama models

The selected candidates are `qwen2.5:1.5b` (small) and `qwen2.5:7b` (medium). Ollama lists their downloads at approximately 986 MB and 4.7 GB respectively. Actual memory residency and load latency are unmeasured.

Install the native macOS Ollama app from https://docs.ollama.com/macos. After installing, use `ollama pull qwen2.5:1.5b`, then `ollama list` and `ollama ps`. With the server running locally, `make doctor-local` checks model tags, and `make chat PROMPT='Say hello' MODEL=small` sends one bounded request through the CLI. Do not equate a downloaded model with a successful inference.

The CLI targets Ollama's documented `http://127.0.0.1:11434/v1/chat/completions` compatibility surface: https://docs.ollama.com/api/openai-compatibility. The 2026-11-23 doctor check found Ollama unreachable, so the current native CLI migration has no generated chat result yet.

For medium, pull `qwen2.5:7b` only after checking free disk. Run one bounded `make chat PROMPT='Say hello' MODEL=medium`, then inspect `ollama ps` and Activity Monitor memory pressure. Record cold and warm load times, `size_vram`, and whether both tags remain loaded. An 18 GB unified-memory Mac may need sequential loading; sequential quality tests cannot establish simultaneous live routing. The current chat and memory measurements are pending because Ollama is unreachable in this environment.
