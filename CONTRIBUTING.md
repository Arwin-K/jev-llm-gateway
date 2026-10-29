# Contributing

Keep implementation claims tied to code, tests, and saved evidence. Start with [the architecture](docs/ARCHITECTURE.md), [development guide](docs/DEVELOPMENT.md), and [feature status](docs/FEATURE_STATUS.md).

1. Make a focused change with a plain-language commit subject such as `add bounded retry accounting` or `clarify scorer denominators`. Put historical checkpoint IDs in the body when a change satisfies a planned checkpoint.
2. Run the affected offline tests, then the full offline suite when changing shared contracts: `uv sync --locked --extra test` and `uv run pytest -q`.
3. Keep paid calls, large downloads, and live model checks opt-in. Record exact environment, model identity, source revision, caps, commands, outputs, and limitations for real experiments.
4. Preserve raw results under ignored `runs/` and source snapshots under ignored `data/day2_sources/`. Commit only sanitized evidence and generated summaries that do not expose prompts, answers, tests, or secrets.
5. Never run generated code directly on the host. Preserve the Docker-only scoring path and explicit blocked status when isolation is unavailable.
6. Update documentation and the feature/evidence ledger when behavior or verification changes. Separate implemented code, mocked checks, real checks, and pending access.

The repository currently has no declared project license. Do not add or infer one from benchmark or dependency licenses without an explicit project decision.
