# Branch and commit history

The repository uses cumulative day branches with explicit local merge commits on `main`:

```text
plan ── day-one merge ── day-two merge ── day-three merge ── day-four merge ── day-five merge  main
       ╱               ╱                 ╱                   ╱                  ╱
   gateway         evaluation         routing           verification        deployment
```

Each day branch starts from the preceding main merge and is merged without squashing. Day 5 covers observability, local deployment, bounded load tooling, and failure evidence. The merge commits make daily lanes visible in the graph while preserving each coherent change.

Commit subjects use descriptive plain language rather than the checkpoint headings. Checkpoint IDs appear in commit bodies. The dataset adapter commit covers `D2-02`, `D2-03`, and `D2-04` together, matching the original Day 2 history. The Day 5 branch contains all 18 checkpoint IDs plus genuine follow-up fixes to the locked image, paid-load guard, and raw Locust reporting.

Find a checkpoint without relying on a shortened hash:

```bash
git log day-five --format='%h %s%n%b' --grep='D5-09'
```

The original 108-checkpoint plan in `docs/COMMIT_PLAN.md` is a plan, not a record of completed work. The project status and experiment ledger distinguish implemented behavior from real verification. Local backup branches preserve the linear histories from before the merge-topology change. Raw experiment IDs and dataset revision hashes are source identities, not Git commit references to this repository.
