# Jev gateway

Day 1 provides a text-only OpenAI-style gateway. Jev routing and verification, trained DistilBERT fallback, evaluations, cache, deployment, and reporting remain required in the full [checkpoint plan](docs/COMMIT_PLAN.md).

## Mac quickstart

1. Install uv using its [official instructions](https://docs.astral.sh/uv/) and native Ollama using [Ollama's macOS instructions](https://docs.ollama.com/macos). Check disk space before model downloads.
2. From this directory run `uv sync --locked`, then `uv run jev --help`. The core environment does not install GPU serving or training packages.
3. Run `ollama pull qwen2.5:1.5b`; when disk and memory permit, run `ollama pull qwen2.5:7b`. Check `ollama list` and `ollama ps`.
4. Review `config/mac.env.example`. Export chosen values in your shell and keep secrets untracked. Run `uv run jev doctor`.
5. Run `uv run jev serve` in one terminal. In another run `uv run jev smoke --tier small` or `uv run jev smoke --tier medium`.

`POST http://127.0.0.1:8080/v1/chat/completions` accepts JSON with `model` set to `small`, `medium`, or `frontier`; a nonempty array of `{role, content}` text messages; optional `stream`, `max_tokens`, and `temperature`. Image, audio, tools, and `model=auto` are rejected. A nonstreaming response preserves the backend completion JSON. Streaming forwards SSE bytes and completion marker. Headers `x-request-id`, `x-jev-tier`, and `x-jev-backend-model` expose routing metadata without adding body fields. `/healthz`, `/readyz`, and `/v1/models` expose process and configured-model status; `/readyz` does not certify a backend is loaded. Run `jev doctor` for live availability.

```bash
curl -sS http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"small","messages":[{"role":"user","content":"Say hello."}],"max_tokens":16}'
```

The frontier transport reads its key only from `JEV_FRONTIER_API_KEY`. It stays disabled until a model, key, positive request/token/USD caps, and current token prices are configured. Budget counters are process local, reserve conservatively, and do not replace provider account spending controls. Use one gateway worker. Never commit `.env` or run paid requests without explicit caps.

For Colab, see [notebook instructions](notebooks/README.md). It serves on loopback within Colab and exports its results; it is not a permanent Mac backend. For evidence and blockers see [status](docs/STATUS.md), [environment](docs/ENVIRONMENT.md), and [experiments](docs/EXPERIMENTS.md).
