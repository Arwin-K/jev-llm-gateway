"""Offline hindsight labels from fully observed training outcomes."""
from dataclasses import dataclass

TIERS=('small','medium','frontier')


@dataclass(frozen=True)
class OracleLabel:
    prompt_id: str
    status: str
    tier: str | None
    tied_tiers: tuple[str,...] = ()
    cost_basis: str | None = None


def label(prompt, results, cost_basis='recorded_charge_usd'):
    if prompt.split != 'train':
        raise PermissionError('training labels use training split only')
    selected={r.tier:r for r in results if r.prompt_id==prompt.prompt_id}
    if set(selected)!=set(TIERS):
        return OracleLabel(prompt.prompt_id,'incomplete',None,cost_basis=cost_basis)
    if any(r.outcome in {'backend_error','blocked','evaluator_error'} for r in selected.values()):
        return OracleLabel(prompt.prompt_id,'failed_evaluation',None,cost_basis=cost_basis)
    correct=[selected[t] for t in TIERS if selected[t].outcome=='correct']
    if not correct:
        return OracleLabel(prompt.prompt_id,'none_correct',None,cost_basis=cost_basis)
    if any(r.charge_usd is None for r in selected.values()):
        return OracleLabel(prompt.prompt_id,'incomparable_cost',None,cost_basis=cost_basis)
    cheapest=min(r.charge_usd for r in correct)
    tied=tuple(t for t in TIERS if selected[t].outcome=='correct' and selected[t].charge_usd==cheapest)
    return OracleLabel(prompt.prompt_id,'labeled',tied[0],tied,cost_basis)
