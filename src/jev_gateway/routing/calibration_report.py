"""Validation calibration from saved real decisions and independently scored results."""
import argparse
import json
import uuid
from pathlib import Path

from jev_gateway.evaluation.manifest import load
from jev_gateway.evaluation.oracle import label as oracle_label
from jev_gateway.evaluation.records import Result
from .calibration import BinaryObservation, binary_report, oracle_label_report, write_reliability_svg

SUCCESS_EVENT = 'specified generator answer externally scores correct'
ORACLE_EVENT = 'oracle-derived cheapest successful tier label'


def report(event: str, decisions: list[dict], results: list[Result], prompts=None, *, bins=10) -> dict:
    if event not in {'generator-success','selected-success','oracle-tier'}:
        raise ValueError('unknown calibration event')
    observed = {(r.prompt_id,r.tier):r for r in results if r.split=='validation' and r.execution=='real'}
    by_prompt = {}
    for result in results:
        if result.split=='validation' and result.execution=='real':
            by_prompt.setdefault(result.prompt_id,[]).append(result)
    prompt_map = {p.prompt_id:p for p in prompts or []}
    samples = []
    multiclass = []
    expected = 0
    for record in decisions:
        if record.get('status') != 'selected':
            continue
        selection = record['selection']
        prompt_id = selection['prompt_id']
        probabilities = record.get('probabilities') or {}
        if event == 'oracle-tier':
            if record.get('probability_event') != ORACLE_EVENT:
                continue
            expected += 1
            prompt = prompt_map.get(prompt_id)
            if prompt is None:
                continue
            oracle = oracle_label(prompt,by_prompt.get(prompt_id,[]),allowed_split='validation')
            if oracle.status=='labeled':
                multiclass.append((probabilities,oracle.tier))
            continue
        if record.get('probability_event') != SUCCESS_EVENT:
            continue
        tiers = [selection['tier']] if event=='selected-success' else list(probabilities)
        expected += len(tiers)
        for tier in tiers:
            result = observed.get((prompt_id,tier))
            if result is None or result.outcome not in {'correct','incorrect','parse_error'}:
                continue
            samples.append(BinaryObservation(probabilities[tier],result.outcome=='correct',SUCCESS_EVENT))
    if not samples and not multiclass:
        return {'event':event,'status':'insufficient_data','expected':expected,'count':0,
                'missing':expected,'bins':bins,'execution':'validation_replay'}
    metrics = oracle_label_report(multiclass,bins=bins,expected=expected) if event=='oracle-tier' else \
              binary_report(samples,bins=bins,expected=expected)
    return metrics | {'status':'measured','execution':'validation_replay'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event',choices=('generator-success','selected-success','oracle-tier'),required=True)
    parser.add_argument('--decisions',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,default=Path('runs/day2-manifest.jsonl'))
    parser.add_argument('--bins',type=int,default=10)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    decisions=[json.loads(line) for line in args.decisions.read_text().splitlines() if line]
    results=[Result.model_validate_json(line) for line in args.run.read_text().splitlines() if line]
    prompts=load(args.manifest,'validation') if args.event=='oracle-tier' else None
    metrics=report(args.event,decisions,results,prompts,bins=args.bins)
    output=args.output or Path('runs')/f'day3-calibration-{uuid.uuid4().hex}.json'
    if not output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('calibration report must be under runs/')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream:
        stream.write(json.dumps(metrics,indent=2))
    figure=None
    if metrics['status']=='measured':
        figure=output.with_suffix('.svg')
        write_reliability_svg(metrics,figure)
    print(json.dumps({'report':str(output),'figure':str(figure) if figure else None,
                      'status':metrics['status'],'count':metrics['count']}))


if __name__=='__main__':
    main()
