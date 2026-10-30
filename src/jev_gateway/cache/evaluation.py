"""Cache-mode validation reports from saved observations, with explicit coverage."""
import argparse
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from .benchmark_data import CacheCase, load


@dataclass(frozen=True)
class CacheObservation:
    case_id: str
    mode: str
    execution: str
    config_id: str
    seed_revision: str
    embedding_identity: str
    order_index: int
    warmup: bool
    candidate_retrieved: bool
    reused: bool
    candidate_check: str | None
    generation_fallback: bool
    returned_answer: str | None
    duration_ms: float | None
    stage_charges_usd: tuple[float | None, ...]
    stage_usage_tokens: tuple[int | None, ...]


def _answer(value):
    return ' '.join(value.strip().casefold().split()) if value is not None else None


def report(cases:list[CacheCase],observations:list[CacheObservation]) -> list[dict]:
    if not cases or any(case.split!='validation' for case in cases):
        raise PermissionError('cache report uses development cases only')
    expected={c.case_id:c for c in cases}
    output=[]
    for origin in ('real','fixture'):
        origin_rows=[o for o in observations if o.execution==origin]
        for mode in ('disabled','similarity_only','verified'):
            rows=[o for o in origin_rows if o.mode==mode]
            if any(o.case_id not in expected for o in rows):
                raise ValueError('unknown cache benchmark case')
            if len({o.case_id for o in rows})!=len(rows):
                raise ValueError('duplicate cache case within mode')
            if any(mode=='disabled' and (o.candidate_retrieved or o.reused) or
                   mode=='verified' and o.reused and o.candidate_check!='accepted' for o in rows):
                raise ValueError('cache mode observation contradicts reuse policy')
            scored=[o for o in rows if o.returned_answer is not None and not o.warmup]
            correct=sum(_answer(o.returned_answer)==_answer(expected[o.case_id].query_answer) for o in scored)
            reused=[o for o in rows if o.reused and not o.warmup]
            harmful=sum(_answer(o.returned_answer)!=_answer(expected[o.case_id].query_answer) for o in reused)
            measured=[o.duration_ms for o in rows if o.duration_ms is not None and origin=='real' and not o.warmup]
            charges=[charge for o in rows for charge in o.stage_charges_usd]
            usage=[value for o in rows for value in o.stage_usage_tokens]
            output.append({'mode':mode,'execution':origin,'expected':len(cases),'observed':len(rows),
                'missing':len(cases)-len(rows), 'retrieved':sum(o.candidate_retrieved for o in rows),
                'retrieval_coverage':sum(o.candidate_retrieved for o in rows)/len(cases),
                'accepted_reuse':len(reused),'accepted_reuse_rate':len(reused)/len(cases),
                'harmful_reuse':harmful,'harmful_per_all_queries':harmful/len(cases),
                'harmful_among_reused':harmful/len(reused) if reused else None,
                'scored':len(scored),'correct':correct,
                'correct_completion_rate':correct/len(cases),
                'candidate_check_failures':sum(o.candidate_check=='error' for o in rows),
                'generation_fallbacks':sum(o.generation_fallback for o in rows),
                'total_charge_usd':sum(charges) if len(rows)==len(cases) and charges and all(
                    charge is not None for o in rows for charge in o.stage_charges_usd) else None,
                'observed_usage_tokens':sum(usage) if usage and all(v is not None for v in usage) else None,
                'end_to_end_p50_ms':statistics.median(measured) if origin=='real' and len(measured)==len(rows) and rows else None,
                'latency_count':len(measured),
                'config_ids':sorted({o.config_id for o in rows}),
                'seed_revisions':sorted({o.seed_revision for o in rows}),
                'embedding_identities':sorted({o.embedding_identity for o in rows}),
                'warmup_rows':sum(o.warmup for o in rows)})
    for origin in ('real','fixture'):
        rows=[r for r in output if r['execution']==origin]
        comparable=(all(r['observed']==len(cases) for r in rows) and
                    len({tuple(r['config_ids']) for r in rows})==1 and
                    len({tuple(r['seed_revisions']) for r in rows})==1 and
                    len({tuple(r['embedding_identities']) for r in rows})==1 and
                    all(r['warmup_rows']==0 for r in rows))
        for row in rows: row['comparison_compatible']=comparable
    return output


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',type=Path,default=Path('data/cache_benchmark_v1.jsonl'))
    parser.add_argument('--observations',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('private report must stay under runs/')
    observations=[]
    for line in args.observations.read_text().splitlines():
        if line:
            row=json.loads(line)
            row['stage_charges_usd']=tuple(row['stage_charges_usd'])
            row['stage_usage_tokens']=tuple(row['stage_usage_tokens'])
            observations.append(CacheObservation(**row))
    result=report(load(args.cases),observations)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out: out.write(json.dumps(result,indent=2))
    print(json.dumps({'path':str(args.output),'reports':len(result),'real_observed':sum(
        r['observed'] for r in result if r['execution']=='real')}))


if __name__=='__main__':
    main()
