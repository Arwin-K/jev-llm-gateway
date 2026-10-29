"""Controlled client workload; separate from answer-quality collection."""
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from time import monotonic

from .runner import RunBudget, RunLimits


@dataclass(frozen=True)
class Workload:
    tier: str
    prompt: str
    requests: int
    arrival_interval_s: float
    concurrency: int
    max_output_tokens: int
    warmup_requests: int
    cache_state: str
    backend_placement: str
    model_condition: str
    stopping_rule: str = 'max_output_tokens'

    def __post_init__(self):
        if self.requests<1 or self.concurrency<1 or self.max_output_tokens<1 or self.arrival_interval_s<0 or self.warmup_requests<0:
            raise ValueError('invalid workload bounds')
        if self.model_condition not in {'cold','warm','unverified'}:
            raise ValueError('model condition must be explicit')


async def run(workload, settings, transport, paid_enabled=False, max_usd=0):
    if workload.tier=='frontier' and (not paid_enabled or not settings.frontier_enabled or max_usd<=0):
        raise PermissionError('paid serving benchmark disabled')
    backend=settings.backend(workload.tier)
    total=workload.requests+workload.warmup_requests
    token_cap=total*(4*len(workload.prompt)+32+workload.max_output_tokens)
    limits=RunLimits(total,token_cap,max_usd,workload.concurrency,0,workload.max_output_tokens)
    budget=RunBudget(limits); sem=asyncio.Semaphore(workload.concurrency)
    origin=monotonic(); started_at=datetime.now(timezone.utc).isoformat()
    async def request(index,warmup):
        intended=origin+index*workload.arrival_interval_s
        await asyncio.sleep(max(0,intended-monotonic()))
        async with sem:
            if not await budget.reserve(workload.prompt,workload.tier,settings):
                return {'index':index,'warmup':warmup,'status':'budget_exhausted','intended_offset_s':index*workload.arrival_interval_s}
            start=monotonic(); first=None; output_tokens=None; status='ok'
            payload={'model':backend.model,'messages':[{'role':'user','content':workload.prompt}],'max_tokens':workload.max_output_tokens,'stream':True}
            try:
                async with transport.stream(backend,payload) as response:
                    async for line in response.aiter_lines():
                        if not line.startswith('data: '): continue
                        if line[6:].strip()=='[DONE]': break
                        event=json.loads(line[6:])
                        if any(c.get('delta',{}).get('content') for c in event.get('choices',[])) and first is None:
                            first=monotonic()
                        usage=event.get('usage') or {}
                        if usage.get('completion_tokens') is not None: output_tokens=usage['completion_tokens']
            except Exception:
                status='error'
            end=monotonic()
            return {'index':index,'warmup':warmup,'status':status,'intended_offset_s':index*workload.arrival_interval_s,'achieved_start_offset_s':start-origin,'latency_s':end-start,'first_visible_s':first-start if first is not None else None,'completion_tokens':output_tokens}
    all_rows=await asyncio.gather(*(request(i,i<workload.warmup_requests) for i in range(workload.requests+workload.warmup_requests)))
    return {'workload':workload.__dict__,'started_at':started_at,'elapsed_s':monotonic()-origin,'observations':all_rows}
