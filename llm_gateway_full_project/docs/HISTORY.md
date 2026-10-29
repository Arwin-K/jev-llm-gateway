# Commit history and checkpoint IDs

Commit subjects describe the actual change instead of beginning with a work-day number. Historical Day 1 and Day 2 checkpoint IDs remain in commit bodies as `Checkpoint: D1-01` and `Checkpoint: D2-01` trailers. The dataset-adapter commit covers `D2-02`, `D2-03`, and `D2-04` in one commit, matching the requested 16 Day 2 commits.

Find a checkpoint without relying on a shortened hash:

```bash
git log --all --format='%h %s%n%b' --grep='Checkpoint: D2-09'
```

The original 108-checkpoint plan remains in `COMMIT_PLAN.md`; its subject column describes planned changes and is not the current Git log. Rewording history changes commit hashes and makes local `main` diverge from the previous `origin/main`. The old remote history is not rewritten by a local reword, and no push is part of this documentation change. Preserve raw experiment IDs and dataset revision hashes; they are source identities, not Git commit references to this repository.
