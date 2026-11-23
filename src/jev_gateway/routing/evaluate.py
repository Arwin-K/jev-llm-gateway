"""Collect bounded validation routing decisions without generating answers."""
import argparse
import asyncio
import json
import uuid
from dataclasses import asdict, replace
from pathlib import Path

from jev_gateway.config import from_env
from jev_gateway.evaluation.manifest import load
from jev_gateway.transport import BackendTransport
from .admission import request_for
from .comparison import Selection
from .contracts import RoutingError, require_eligible
from .factory import build


async def collect(prompts, settings, *, max_decisions: int):
    transport = BackendTransport(settings.timeout_seconds)
    router, closers = build(settings, transport)
    records = []
    try:
        for prompt in prompts[:max_decisions]:
            request = request_for(settings, ({'role':'user','content':prompt.prompt},),
                                  settings.max_output_tokens, prompt.prompt_id)
            try:
                decision = require_eligible(await router.decide(request), request)
                # Decision call charges require observed usage and a sourced rate. No zero is invented.
                zero_overhead = decision.policy.startswith('always-') or decision.policy == 'seeded-random'
                selection = Selection(prompt.prompt_id, decision.policy, decision.tier,
                                      0.0 if zero_overhead else None, decision.duration_ms,
                                      'real_decision' if not zero_overhead else 'deterministic_local')
                records.append({'status':'selected', 'prompt_id':prompt.prompt_id,
                                'split':prompt.split, 'selection':asdict(selection),
                                'version':decision.version, 'decision_model':decision.decision_model,
                                'question_version':decision.question_version,
                                'probability_event':decision.probability_event,
                                'probabilities':dict(decision.probabilities),
                                'usage':dict(decision.usage)})
            except (RoutingError, ValueError, asyncio.TimeoutError) as exc:
                record = {'status':'error', 'prompt_id':prompt.prompt_id,
                          'split':prompt.split,
                          'policy':router.name, 'version':router.version,
                          'error_category':type(exc).__name__,
                          'cause_category':type(exc.__cause__).__name__ if exc.__cause__ else None}
                # JSONDecodeError.doc is the local model's malformed completion. Keep it only
                # in the private run record; aggregate reports must not print it.
                raw_output = getattr(exc.__cause__, 'doc', None)
                if isinstance(raw_output, str):
                    record['router_raw_response'] = raw_output
                records.append(record)
    finally:
        for closer in closers:
            await closer.close()
        await transport.close()
    return records


def select_prompts(prompts, max_prompts: int, prompt_ids: list[str] | None = None):
    if max_prompts < 1:
        raise ValueError('max_prompts must be positive')
    if not prompt_ids:
        return prompts[:max_prompts]
    if len(prompt_ids) != len(set(prompt_ids)):
        raise ValueError('prompt IDs must be unique')
    wanted = set(prompt_ids)
    selected = [prompt for prompt in prompts if prompt.prompt_id in wanted]
    if len(selected) != len(wanted):
        raise ValueError('one or more prompt IDs are absent from the selected split')
    return selected[:max_prompts]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', choices=('always-small','always-medium','always-frontier',
                        'seeded-random','distilbert','prompted-small','jev-choice',
                        'jev-threshold','laya-choice','laya-threshold','strands-decider'), required=True)
    parser.add_argument('--manifest', type=Path, default=Path('runs/day2-manifest.jsonl'))
    parser.add_argument('--split', choices=('train','validation'), default='validation')
    parser.add_argument('--max-prompts', type=int, required=True)
    parser.add_argument('--max-decisions', type=int, required=True)
    parser.add_argument('--prompt-id', action='append', default=[])
    parser.add_argument('--max-usd', type=float, default=0.)
    parser.add_argument('--paid-enabled', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if min(args.max_prompts,args.max_decisions) < 1:
        parser.error('positive prompt and decision caps required')
    settings = replace(from_env(), router_policy=args.policy)
    if args.policy.startswith('jev-'):
        if not args.paid_enabled or args.max_usd <= 0 or not settings.jev_enabled:
            parser.error('Jev run requires explicit --paid-enabled, positive --max-usd, key, model, sourced rates and caps')
        settings = replace(settings, jev_max_requests=min(settings.jev_max_requests,args.max_decisions),
                           jev_max_usd=min(settings.jev_max_usd,args.max_usd))
    elif args.policy.startswith('laya-'):
        if not settings.decision_enabled or settings.decision_provider != 'laya':
            parser.error('Laya run requires the local Laya provider, model, and positive request/token caps')
        settings = replace(settings, jev_max_requests=min(settings.jev_max_requests,args.max_decisions))
    prompts = select_prompts(load(args.manifest,args.split), args.max_prompts, args.prompt_id)
    output = args.output or Path('runs')/f'day3-decisions-{uuid.uuid4().hex}.jsonl'
    if not output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('private decisions must be saved under runs/')
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        stream = output.open('x')
    except FileExistsError:
        parser.error(f'output path already exists: {output}')
    try:
        with stream:
            records = asyncio.run(collect(prompts,settings,max_decisions=args.max_decisions))
            for record in records:
                stream.write(json.dumps(record,sort_keys=True)+'\n')
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    print(json.dumps({'path':str(output),'policy':args.policy,'attempted':len(records),
                      'selected':sum(r['status']=='selected' for r in records),
                      'errors':sum(r['status']=='error' for r in records)}))


if __name__=='__main__':
    main()
