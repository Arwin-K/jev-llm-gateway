# Day 3 routing handoff — 2026-10-29, America/Toronto

The `day-three` branch adds `model=auto`. Its default policy is Jev choice, with a compatible trained DistilBERT artifact as the only production fallback. A routing failure without that artifact returns 503. Explicit tier requests retain their path. Every chosen tier is rechecked against configured context ceilings and the frontier admission guard before execution. Request traces retain policy, version, decision outcome, fallback reason, decision usage, selected tier, and actual backend. Streaming remains SSE. The configured context ceilings use a conservative byte-count admission estimate; they are not verified token counts or backend availability checks.

## Comparison methods and evidence state

| Method | Code | Offline check | Real decision / validation result |
| --- | --- | --- | --- |
| Always-small, always-medium, always-frontier | Implemented | Yes | Decision-only small/medium timing; generation unavailable |
| Seeded random | Implemented | Yes | Decision-only timing; no scored generation |
| Observed hindsight oracle | Implemented as replay | Yes | No complete three-tier validation observation |
| DistilBERT | Trainer, portable artifact and CPU/MPS adapter implemented | Missing/incompatible artifact checks | No labels, training run, artifact, or classifier timing |
| Prompted small LLM | Implemented | Yes | Ollama unavailable |
| Jev choice | Implemented against official System One schema | Yes | Key, model, rates, and positive caps absent |
| Jev generator-success thresholds | Implemented | Yes | No validation-selected thresholds or live Jev result |
| Self-hosted Strands Decider | Typed local server adapter implemented | Yes | No checkpoint/server or real host resource measurement |

The saved Day 2 run has two validation backend errors and no train result. Thus training coverage is **0/1,500**, there is no validation-selected operating point, and the held-out test remains unused. The Day 3 replay under ignored `runs/day3-validation-comparison-20261029.json` includes ten policy rows and plots zero cost-quality points. No quality, calibration, or live router overhead number is available. `config/day3-router.json` freezes identifiers and records null for unselected settings.

## Working commands

Run from the repository root. The current environment has `.venv/bin/python` and `.venv/bin/jev`; `uv` is not on PATH. `--help` works for each module command below without training dependencies or network access.

```bash
.venv/bin/pytest -q
.venv/bin/jev doctor
.venv/bin/jev serve
.venv/bin/jev smoke --tier auto
.venv/bin/python -m jev_gateway.routing.benchmark --samples 100 --warmup 10
.venv/bin/python -m jev_gateway.routing.comparison --run runs/day2-run-8debb816c7474f559ab5197df9c1fea6.jsonl
```

`jev smoke --tier auto` is a live request; it currently returns 503 with the default disabled Jev configuration. For an explicitly configured local baseline, export `JEV_ROUTER_POLICY=always-small`, start Ollama and the gateway, then run it again. No model installation or paid call is automatic.

After collecting complete real train and validation results with known comparable per-tier costs, export private labels separately:

```bash
.venv/bin/python -m jev_gateway.routing.prepare --split train --run runs/<train-run>.jsonl --output runs/day3-train-labels.jsonl
.venv/bin/python -m jev_gateway.routing.prepare --split validation --run runs/<validation-run>.jsonl --output runs/day3-validation-labels.jsonl
```

Run the optional training extra in a Colab GPU environment using `notebooks/day3_distilbert.ipynb`, a pinned DistilBERT revision, and the same committed repository source. Its equivalent module command is:

```bash
python -m jev_gateway.routing.train --train runs/day3-train-labels.jsonl --validation runs/day3-validation-labels.jsonl --output runs/day3-distilbert --revision <pinned-Hugging-Face-commit>
python -m jev_gateway.routing.artifact --path runs/day3-distilbert
python -m jev_gateway.routing.tuning --cases runs/<validation-cases>.jsonl --candidates runs/<candidate-thresholds>.json --min-quality 0.8 --min-coverage 1 --output runs/day3-validation-selection.json
```

The training command refuses empty labels and mismatched backend or generation identities. It saves weights, tokenizer, mapping, split IDs, source revisions, hyperparameters, metrics, and a save/reload prediction check under ignored `runs/`. The tuning command uses validation cases only and refuses a selection without complete coverage, known cost, and the requested quality. The numerical objective above is an example invocation, not an empirically chosen project threshold. There is no current input file for these last commands.

## Next prerequisites

Start and inspect native Ollama models, check disk/memory before a Strands download, collect bounded real answers across all three tiers, source current frontier and Jev rates and obtain a positive explicit paid budget, complete the pending human scoring audit, then create train/validation labels. Only after that can Colab training, artifact reload on Mac, Jev/Strands live comparison, validation threshold selection, calibration, and end-to-end timing be measured. The Day 4 verifier/cascade/cache work can consume this router contract; no Day 4 feature is claimed here.

Official integration references checked 2026-10-29: [TypeSafe OpenAPI schema](https://api.typesafe.ai/openapi.json), [TypeSafe Python SDK](https://github.com/typesafe-ai/typesafe-sdk-python/blob/main/README.md), and [Strands Decider inference guide](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md).

## Follow-up command paths

The decision collector writes private JSONL with selected tiers, probability semantics, usage, timing, or explicit error categories. It never generates answers. For a local fixed policy, this exact bounded command was run:

```bash
.venv/bin/python -m jev_gateway.routing.evaluate --policy always-small --max-prompts 1 --max-decisions 1
```

For a live Jev validation collection, configure an official HTTPS rate source and ISO effective date in addition to key, model, positive environment caps, and current rate values. Then use `--policy jev-choice` or `--policy jev-threshold` with `--paid-enabled --max-usd <positive-run-cap> --max-decisions <positive-request-cap>`. No such run has occurred. Pass the printed decision file to replay and calibration:

```bash
.venv/bin/python -m jev_gateway.routing.comparison --run runs/<validation-run>.jsonl --selections runs/<decision-run>.jsonl
.venv/bin/python -m jev_gateway.routing.calibration_report --event generator-success --decisions runs/<decision-run>.jsonl --run runs/<validation-run>.jsonl
```

The calibration CLI also accepts `selected-success` and `oracle-tier`. Its denominator covers selected decisions with the requested probability event; failed decisions remain in the decision file and are not assigned fabricated probabilities. It emits `insufficient_data` and no figure when independently scored coverage is absent; it does not treat a router's own probability as ground truth.
