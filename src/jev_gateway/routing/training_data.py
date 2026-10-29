"""Build supervised labels only from complete, real training observations."""
from collections import Counter, defaultdict
from dataclasses import dataclass

from jev_gateway.evaluation.oracle import label as oracle_label
from jev_gateway.evaluation.records import Prompt, Result
from .contracts import TIERS


@dataclass(frozen=True)
class TrainingRow:
    prompt_id: str
    text: str
    label: str
    split: str
    source_revision: str
    dataset_revision: str
    template_fingerprint: str
    settings_fingerprint: str
    backend_models: dict[str, str]
    result_run_ids: dict[str, str]
    cost_basis: str


def prepare_training(prompts: list[Prompt], results: list[Result], split: str = 'train') -> tuple[list[TrainingRow], dict]:
    if split not in {'train', 'validation'}:
        raise PermissionError('held-out test is unavailable to training preparation')
    by_prompt = defaultdict(list)
    for result in results:
        if result.split == split and result.execution == 'real':
            by_prompt[result.prompt_id].append(result)
    rows = []
    states = Counter()
    for prompt in prompts:
        if prompt.split != split:
            raise PermissionError('prompt split does not match requested development split')
        observed = by_prompt[prompt.prompt_id]
        # Multiple versions of one tier are ambiguous rather than votes or extra samples.
        if len({r.tier for r in observed}) != len(observed):
            states['duplicate_tier'] += 1
            continue
        if any(r.source_revision != prompt.source_revision or
               r.dataset_revision != prompt.dataset_revision or
               r.template_fingerprint != prompt.template_fingerprint for r in observed):
            states['identity_mismatch'] += 1
            continue
        if len({r.settings_fingerprint for r in observed}) > 1:
            states['settings_mismatch'] += 1
            continue
        oracle = oracle_label(prompt, observed, allowed_split=split)
        states[oracle.status] += 1
        if oracle.status != 'labeled':
            continue
        selected = {r.tier: r for r in observed}
        rows.append(TrainingRow(prompt.prompt_id, prompt.prompt, oracle.tier, split,
                                prompt.source_revision, prompt.dataset_revision,
                                prompt.template_fingerprint, observed[0].settings_fingerprint,
                                {t: selected[t].model for t in TIERS},
                                {t: selected[t].run_id for t in TIERS}, oracle.cost_basis))
    return rows, {'expected_prompts': len(prompts), 'labeled': len(rows),
                  'label_counts': dict(Counter(row.label for row in rows)),
                  'statuses': dict(states), 'class_weighting': 'inverse_frequency_at_training'}


def public_summary(rows: list[TrainingRow], report: dict) -> dict:
    """Safe aggregate for documentation; row text stays in ignored runs/."""
    return report | {'settings_fingerprints': sorted({r.settings_fingerprint for r in rows}),
                     'backend_model_sets': sorted({tuple(sorted(r.backend_models.items())) for r in rows})}
