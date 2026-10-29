"""Aggregate quality from saved records and explicit expected prompt set."""
from collections import Counter


def quality_report(prompts, results, tiers=('small','medium','frontier')):
    expected={p.prompt_id:p for p in prompts}
    observed={}
    for result in results:
        if result.prompt_id in expected:
            k=(result.prompt_id,result.tier)
            if k in observed:
                raise ValueError('duplicate result for prompt/tier')
            observed[k]=result
    groups={task:[p for p in prompts if task=='overall' or p.task==task] for task in sorted({p.task for p in prompts}|{'overall'})}
    rows=[]
    for task,subset in groups.items():
        for tier in tiers:
            found=[observed.get((p.prompt_id,tier)) for p in subset]
            actual=[r for r in found if r is not None]
            outcomes=Counter(str(r.outcome) for r in actual)
            costs=Counter(r.cost_status for r in actual)
            scored=outcomes['correct']+outcomes['incorrect']
            n=len(subset)
            rows.append({'task':task,'tier':tier,'expected':n,'observed':len(actual),'missing':n-len(actual),'scored':scored,'accuracy_scored':outcomes['correct']/scored if scored else None,'correct_completion_rate':outcomes['correct']/n if n else None,'outcomes':dict(outcomes),'completion_failure_rate':sum(outcomes[x] for x in ('backend_error','blocked'))/n if n else None,'parsing_failure_rate':outcomes['parse_error']/n if n else None,'evaluator_failure_rate':outcomes['evaluator_error']/n if n else None,'cost_statuses':dict(costs)})
    return {'weighting':'overall is prompt-weighted micro aggregation across selected tasks','rows':rows}
