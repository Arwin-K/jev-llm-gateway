"""Explicit evaluation CLI operations. Private outputs stay under runs/."""
import asyncio
import json
import uuid
from datetime import date
from pathlib import Path

from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport
from .audit import export
from .cost import ApiRate
from .checkpoint import Checkpoints
from .manifest import load
from .records import Result
from .report import quality_report
from .runner import RunLimits, evaluate_batch
from .serving import Workload, run as run_serving
from .latency import serving_report

MANIFEST=Path('runs/day2-manifest.jsonl')
CHECKPOINTS=Path('runs/day2-checkpoints')


def _saved(path):
    target=Path(path).resolve()
    if not target.is_relative_to(Path('runs').resolve()) or not target.name.startswith('day2-run-'):
        raise ValueError('run file must be an eval-run output under runs/')
    return [Result.model_validate_json(line) for line in target.read_text().splitlines()]


def execute(args):
    if args.command=='eval-prepare':
        from runpy import run_path
        run_path('scripts/prepare_day2.py',run_name='__main__')
        return 0
    if args.command=='eval-run':
        if args.max_prompts<1:
            raise ValueError('--max-prompts must be positive')
        prompts=load(MANIFEST,args.split)[:args.max_prompts]
        limits=RunLimits(args.max_requests,args.max_tokens,args.max_usd,args.concurrency,args.retries,args.output_tokens)
        settings=from_env()
        if args.paid_enabled and 'frontier' in args.tier and not args.rate_file:
            raise ValueError('paid evaluation requires a dated sourced --rate-file')
        rates={}
        if args.rate_file:
            for entry in json.loads(Path(args.rate_file).read_text()):
                rate=ApiRate(model=entry['model'],input_usd_per_million=entry['input_usd_per_million'],output_usd_per_million=entry['output_usd_per_million'],effective_date=date.fromisoformat(entry['effective_date']),source_url=entry['source_url'])
                rates[rate.model]=rate
        async def call():
            transport=BackendTransport(settings.timeout_seconds)
            try:
                return await evaluate_batch(prompts,args.tier,uuid.uuid4().hex,settings,transport,limits,args.paid_enabled,checkpoints=Checkpoints(CHECKPOINTS),rates=rates)
            finally:
                await transport.close()
        results=asyncio.run(call())
        out=Path('runs')/('day2-run-'+uuid.uuid4().hex+'.jsonl')
        with out.open('x') as stream:
            for result in results: stream.write(result.model_dump_json()+'\n')
        print(json.dumps({'results':len(results),'path':str(out),'outcomes':{x:sum(str(r.outcome)==x for r in results) for x in ('correct','incorrect','parse_error','backend_error','evaluator_error','blocked')}}))
        return 0
    if args.command=='eval-report':
        report=quality_report(load(MANIFEST,args.split),_saved(args.run))
        print(json.dumps(report,indent=2))
        return 0
    if args.command=='eval-audit':
        prompts=load(MANIFEST,args.split)
        path=Path('runs')/('day2-audit-'+args.split+'.csv')
        counts=export(prompts,_saved(args.run),path)
        print(json.dumps({'path':str(path),'rows':counts,'review_status':'pending_human_review'}))
        return 0
    if args.command=='eval-serving':
        workload=Workload(args.tier,args.prompt,args.requests,args.arrival_interval,args.concurrency,args.output_tokens,args.warmup,args.cache_state,args.placement,args.model_condition)
        settings=from_env()
        async def call():
            transport=BackendTransport(settings.timeout_seconds)
            try: return await run_serving(workload,settings,transport,args.paid_enabled,args.max_usd)
            finally: await transport.close()
        observed=asyncio.run(call())
        path=Path('runs')/('day2-serving-'+uuid.uuid4().hex+'.json')
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(observed,indent=2))
        print(json.dumps({'path':str(path),'report':serving_report(observed)},indent=2))
        return 0
    raise ValueError('unknown evaluation command')
