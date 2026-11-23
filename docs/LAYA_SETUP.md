# Local Laya decision service

The gateway uses Laya as its default System One decision backend. It does not call Laya's hosted API. The repository's gateway process talks only to the loopback service URL; no API key or per-call billing is needed.

## Install and run on Apple Silicon

Install the pinned service into its own virtual environment. This keeps its model/runtime dependencies out of the gateway's portable core environment. From the repository root, `make setup-laya` performs this install; review the resulting package install before starting it. The first service startup downloads the pinned model checkpoint.

```bash
make setup-laya
make laya-serve
```

The default service target binds to `127.0.0.1:8000`, uses Apple MPS, preloads `typed-decisions`, and asks the pinned Laya release to use its reviewed checkpoint revision. Set `LAYA_DEVICE=cpu` in `.env` before `make laya-serve` to use CPU instead.

Laya downloads its model checkpoint the first time it is loaded. `LAYA_REVISION=reviewed` asks the pinned service release to use its reviewed Hub revisions. Keep this service bound to `127.0.0.1`; do not expose its port publicly. To use CPU instead, set `LAYA_DEVICE=cpu`. Model loading and inference consume local memory and power.

## Gateway configuration

`make mac-config` creates `.env` from the Mac example without overwriting an existing file. The profile selects the local provider and pins its request to the typed-decision checkpoint:

```dotenv
JEV_DECISION_PROVIDER=laya
JEV_DECISION_URL=http://127.0.0.1:8000
JEV_DECISION_MODEL=typed-decisions
JEV_DECISION_MAX_REQUESTS=100
JEV_DECISION_MAX_TOKENS=200000
JEV_ROUTER_POLICY=laya-choice
```

The positive request/token limits are process-local ceilings. The `JEV_DECISION_MAX_USD` and rate fields apply only when `JEV_DECISION_PROVIDER=jev`; keep those unset/zero for the local Laya path. The gateway rejects non-loopback URLs for Laya, and the Laya client sends no authorization token.

## Compatibility and evaluation limits

Laya's self-hosted server implements the Jev-compatible `POST /v1/systemone` wire format, but compatibility does not imply identical behavior. Laya caps choice fan-out at 100 options and has different confidence semantics from Jev. This project currently asks it to choose among at most three eligible tiers. Re-select and calibrate every probability threshold against this project's validation data. Do not use a Jev threshold with Laya without validation.

Laya upstream reports that its base typed-decision checkpoints need task-specific fine-tuning for strong performance and provides a fine-tuning path. No Laya inference, fine-tuning, or accuracy result has yet been measured on this project's routing prompts. The held-out split remains locked. Treat the integration as an unevaluated local backend until real train/validation evidence is collected.

## Personal-project safety notes

The upstream code is Apache-2.0. PyPI's provenance for pinned `laya==0.5.2` identifies the upstream GitHub Actions publisher and commit `e150aa92a0d4059ac621875b39b620847cf1b88a`; this is a useful supply-chain signal, not a complete security audit. Keep installation isolated in `.venv-laya`, keep model serving loopback-only, and do not pass secrets or sensitive prompts during evaluation. The upstream project is fast-moving, so review the package/model release and its dependencies before upgrading. The original code integration used fixtures only; a later local install and one-request gateway smoke succeeded on 2026-11-22. See `evidence/testing/local-laya-gateway-smoke-20261122.txt`. This smoke does not measure router quality.

The optional hosted Jev comparison remains available through `JEV_DECISION_PROVIDER=jev`; it requires its own credentials, sourced rates, and explicit positive paid caps. It is disabled by default.
