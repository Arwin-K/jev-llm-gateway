# Day 2 observation schema

`Prompt` stores immutable source identity, frozen split, exact prompt, reference, and template fingerprint. `Result` stores one tier's observation, timing boundaries, raw response or reference, parsed answer, outcome, usage, cost status, execution origin, and reuse pointer. `Attempt` retains retry costs. Null means unknown; a parser failure, wrong answer, backend failure, and evaluator failure have separate outcomes. JSONL records are append-only. Raw responses may contain sensitive content and belong in private ignored run files, not public reports.

Math scoring accepts an explicit `Answer: <number>` line or a sole numeric line. Signed integers, decimals, comma thousands, and rational fractions compare exactly via `Fraction`. Units, multiple conflicting answers, and prose without a final marker remain parse errors. A bad reference is an evaluator error.

Multiple-choice scoring accepts a standalone A–D, `Answer: X`, or `The answer is X.` It rejects ordinary prose, conflicting labels, and known truncated completions. Parsing failure is separate from an incorrect selected option.

The audit CSV deliberately includes private prompts and references and belongs under ignored `runs/`. It samples up to 40 observed development rows per task by stable prompt/tier order. Every row is marked `pending_human_review`; creating an export does not constitute a human audit. No audit export is included in public aggregate reports.

Oracle labels are offline hindsight references derived only for training prompts with all three tier results and comparable charges. Missing evaluations, failures, and unknown costs abstain; none-correct has its own status. Equal cheapest successful costs tie, with a deterministic tier order for the stored label. This is not a deployable perfect router.

Cost accounting sums every billable attempt, including retries. A provider charge is `known_charge`; token usage with a dated, sourced rate is `estimated_api`; absent usage/rate is `unknown`. Self-hosted capacity is a separate model based on all allocated hours, including idle hours. Router and verifier calls can use the same attempt ledger in later days. Application budgets are admission guards, not provider-enforced caps. No default price is fabricated.

Quality reports are regenerated from records plus the explicit expected manifest selection. Scored accuracy divides correct by correct+incorrect; correct-completion rate divides correct by all expected prompt/tier pairs. Missing, parsing, backend, and evaluator failures retain their own counts and rates. Overall numbers micro-weight tasks by selected prompt count, not equal task weight.
