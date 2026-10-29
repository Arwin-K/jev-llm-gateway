"""Decision-only local benchmark; no generator request or percentile addition."""
import argparse
import asyncio
import json
import platform
import resource
import statistics
import time
import uuid
from pathlib import Path

from jev_gateway.config import from_env
from .admission import request_for
from .baselines import FixedRouter, SeededRandomRouter


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered)-1, max(0, int((len(ordered)-1)*fraction)))]


async def measure(router, requests, *, warmup: int) -> dict:
    errors = []
    for request in requests[:warmup]:
        try: await router.decide(request)
        except Exception as exc: errors.append(type(exc).__name__)
    timings = []
    for request in requests[warmup:]:
        start = time.perf_counter()
        try:
            await router.decide(request)
            timings.append((time.perf_counter()-start)*1000)
        except Exception as exc:
            errors.append(type(exc).__name__)
    return {'policy':router.name, 'warmup':warmup, 'attempted':len(requests)-warmup,
            'successful':len(timings), 'errors':errors,
            'p50_ms':statistics.median(timings) if timings else None,
            'p95_ms':percentile(timings,.95) if timings else None,
            'duration_ms':timings}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples',type=int,default=100)
    parser.add_argument('--warmup',type=int,default=10)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    if args.samples < 1 or args.warmup < 0:
        parser.error('positive samples and nonnegative warmup required')
    settings=from_env()
    requests=[request_for(settings, ({'role':'user','content':'Explain 2+2 in one line.'},),
                          32, f'benchmark-{i}') for i in range(args.samples+args.warmup)]
    before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    policies=[FixedRouter('small'),FixedRouter('medium'),SeededRandomRouter(17)]
    results=asyncio.run(_run(policies,requests,args.warmup))
    after=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    run_id=uuid.uuid4().hex
    report={'run_id':run_id,'host':platform.platform(),'machine':platform.machine(),
            'python':platform.python_version(),'device':'cpu','model_state':'no decision model loaded',
            'workload':'identical short text, unique request IDs','concurrency':1,
            'measurement':'decision-only outer wall clock; no backend requests',
            'memory_maxrss_before':before,'memory_maxrss_after':after,
            'memory_units':'bytes on macOS, KiB on Linux', 'results':results}
    output=args.output or Path('runs')/f'day3-routing-benchmark-{run_id}.json'
    if not output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('benchmark output must be under runs/')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x") as stream:
        stream.write(json.dumps(report,indent=2))
    print(json.dumps({'run_id':run_id,'path':str(output),'summary':[
        {k:v for k,v in r.items() if k != 'duration_ms'} for r in results]}))


async def _run(policies,requests,warmup):
    return [await measure(policy,requests,warmup=warmup) for policy in policies]


if __name__=='__main__':
    main()
