# Day 2 observation schema

`Prompt` stores immutable source identity, frozen split, exact prompt, reference, and template fingerprint. `Result` stores one tier's observation, timing boundaries, raw response or reference, parsed answer, outcome, usage, cost status, execution origin, and reuse pointer. `Attempt` retains retry costs. Null means unknown; a parser failure, wrong answer, backend failure, and evaluator failure have separate outcomes. JSONL records are append-only. Raw responses may contain sensitive content and belong in private ignored run files, not public reports.

Math scoring accepts an explicit `Answer: <number>` line or a sole numeric line. Signed integers, decimals, comma thousands, and rational fractions compare exactly via `Fraction`. Units, multiple conflicting answers, and prose without a final marker remain parse errors. A bad reference is an evaluator error.

Multiple-choice scoring accepts a standalone A–D, `Answer: X`, or `The answer is X.` It rejects ordinary prose, conflicting labels, and known truncated completions. Parsing failure is separate from an incorrect selected option.

The audit CSV deliberately includes private prompts and references and belongs under ignored `runs/`. It samples up to 40 observed development rows per task by stable prompt/tier order. Every row is marked `pending_human_review`; creating an export does not constitute a human audit. No audit export is included in public aggregate reports.
