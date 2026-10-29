# Branch and commit history

The repository uses the same cumulative milestone pattern as the [CUDA Attention Softmax project](https://github.com/Arwin-K/CUDA-Attention-Softmax), with explicit merge commits on `main`:

```text
project plan ── Merge day-one ── Merge day-two  main
             ╱                 ╱
    gateway and notebook     evaluation and root layout
          day-one                  day-two
```

`day-one` contains the gateway and engineering notebook work. It is merged into `main` without squashing. `day-two` starts from that merge, contains each evaluation commit, and is merged into `main` without squashing. The merge commits make the daily lanes visible in a Git graph while preserving individual work. The latest `main` tree matches the reviewed `day-two` tree.

Commit subjects use plain verbs without `docs:`, `test:`, `feat:`, or work-day prefixes. Historical checkpoint IDs remain in commit bodies as `Checkpoint: D1-01` and `Checkpoint: D2-01` trailers. The dataset adapter commit covers `D2-02`, `D2-03`, and `D2-04` together, matching the requested 16 original Day 2 commits.

Find a checkpoint without relying on a shortened hash:

```bash
git log day-two --format='%h %s%n%b' --grep='Checkpoint: D2-09'
```

The original 108-checkpoint plan in `docs/COMMIT_PLAN.md` is a plan, not a record of completed work. The project status and experiment ledger distinguish implemented behavior from real verification. Local backup branches preserve the linear histories from before the merge-topology change. Raw experiment IDs and dataset revision hashes are source identities, not Git commit references to this repository.
