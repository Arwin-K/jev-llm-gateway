"""Validation mode comparisons from recorded executions and independent scores."""
import argparse
import hashlib
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from jev_gateway.evaluation.manifest import load
from jev_gateway.evaluation.records import Result


@dataclass(frozen=True)
class StageCost:
    stage: str
    tier: str | None
    charge_usd: float | None
    cost_status: str


@dataclass(frozen=True)
class ExecutionObservation:
    prompt_id: str
    split: str
    mode: str
    status: str
    accepted_tier: str | None
    accepted_model: str | None
    answer_sha256: str | None
    settings_fingerprint: str
    stages: tuple[StageCost, ...]
    execution: str
    total_duration_ms: float | None = None


def compare(prompts, observations: list[ExecutionObservation], results: list[Result]) -> list[dict]:
    if not prompts or any(p.split!='validation' for p in prompts):
        raise PermissionError('validation mode comparison only')
    expected={p.prompt_id for p in prompts}
    scores={(r.prompt_id,r.tier,r.model,r.settings_fingerprint):r for r in results
            if r.split=='validation' and r.execution=='real'}
    reports=[]
    for mode in ('route_first','cascade','hybrid'):
        rows=[o for o in observations if o.mode==mode and o.prompt_id in expected]
        if any(o.split!='validation' or o.execution!='real' for o in rows):
            raise ValueError('real validation execution records required')
        if len({o.prompt_id for o in rows})!=len(rows):
            raise ValueError('duplicate mode execution for prompt')
        scored=correct=unmatched=0
        known_cost=0.
        cost_complete=True
        latencies=[]
        for row in rows:
            if row.total_duration_ms is not None:
                latencies.append(row.total_duration_ms)
            if not row.stages or any(stage.charge_usd is None for stage in row.stages):
                cost_complete=False
            else:
                known_cost+=sum(stage.charge_usd for stage in row.stages)
            if not row.accepted_tier or not row.answer_sha256:
                continue
            result=scores.get((row.prompt_id,row.accepted_tier,row.accepted_model,row.settings_fingerprint))
            if result is None or result.raw_response is None or \
               hashlib.sha256(result.raw_response.encode()).hexdigest()!=row.answer_sha256:
                unmatched+=1
                continue
            if result.outcome in {'correct','incorrect','parse_error'}:
                scored+=1
                correct+=result.outcome=='correct'
        reports.append({'mode':mode,'expected':len(prompts),'executed':len(rows),
                        'missing_execution':len(prompts)-len(rows), 'independently_scored':scored,
                        'correct':correct,'unmatched_answer_identity':unmatched,
                        'correct_completion_rate':correct/len(prompts),
                        'scored_accuracy':correct/scored if scored else None,
                        'total_charge_usd':known_cost if cost_complete and len(rows)==len(prompts) else None,
                        'end_to_end_p50_ms':statistics.median(latencies) if len(latencies)==len(rows) and rows else None,
                        'latency_count':len(latencies),'execution':'recorded_real_only'})
    return reports


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=Path('runs/day2-manifest.jsonl'))
    parser.add_argument('--executions',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('private mode report must stay under runs/')
    observations=[]
    for line in args.executions.read_text().splitlines():
        if line:
            value=json.loads(line)
            value['stages']=tuple(StageCost(**stage) for stage in value['stages'])
            observations.append(ExecutionObservation(**value))
    results=[Result.model_validate_json(line) for line in args.run.read_text().splitlines() if line]
    report=compare(load(args.manifest,'validation'),observations,results)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out:
        out.write(json.dumps(report,indent=2))
    print(json.dumps({'path':str(args.output),'reports':len(report),
                      'scored':sum(r['independently_scored'] for r in report)}))


if __name__=='__main__':
    main()
