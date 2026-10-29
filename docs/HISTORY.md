# Branch and commit history

The repository follows the cumulative milestone pattern used by the [CUDA Attention Softmax project](https://github.com/Arwin-K/CUDA-Attention-Softmax): `day-one` points to the completed gateway and engineering-notebook foundation, `day-two` adds evaluation infrastructure, and `main` points to the latest reviewed project state. The daily branches are snapshots in one ancestry, so `day-two` includes Day 1 commits as ancestors.

Commit subjects use plain verbs without `docs:`, `test:`, `feat:`, or work-day prefixes. Historical checkpoint IDs remain in commit bodies as `Checkpoint: D1-01` and `Checkpoint: D2-01` trailers. The dataset adapter commit covers `D2-02`, `D2-03`, and `D2-04` together, matching the requested 16 Day 2 commits.

Find a checkpoint without relying on a shortened hash:

```bash
git log day-two --format='%h %s%n%b' --grep='Checkpoint: D2-09'
```

The original 108-checkpoint plan in `docs/COMMIT_PLAN.md` is a plan, not a record of completed work. The project status and experiment ledger distinguish implemented behavior from real verification. A local `backup/pre-descriptive-commit-history` branch preserves the pre-reword snapshot. Raw experiment IDs and dataset revision hashes are source identities, not Git commit references to this repository.
