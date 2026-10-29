"""Bounded explicit-tier quality collection; no implicit mocks or held-out test."""
import asyncio
import hashlib
import json
from datetime import datetime, timezone

from .records import Attempt, Result, Outcome
from .scoring import score_math, score_choice, score_code


class RunLimits:
    def __init__(self, max_requests, max_tokens, max_usd, concurrency=1, retries=0, output_tokens=128, temperature=0):
        if min(max_requests,max_tokens,output_tokens,concurrency) <= 0 or max_usd < 0 or not 0 <= retries <= 3:
            raise ValueError('positive request/token/concurrency limits and bounded retries required')
        self.max_requests=max_requests; self.max_tokens=max_tokens; self.max_usd=max_usd
        self.concurrency=concurrency; self.retries=retries; self.output_tokens=output_tokens; self.temperature=temperature


class RunBudget:
    def __init__(self, limits):
        self.limits=limits; self.lock=asyncio.Lock(); self.requests=0; self.tokens=0; self.usd=0.0; self.frontier_requests=0; self.frontier_tokens=0; self.frontier_usd=0.0

    async def reserve(self, prompt, tier, settings):
        input_units=4*len(prompt)+32
        tokens=input_units+self.limits.output_tokens
        dollars=0.0
        if tier=='frontier':
            dollars=(input_units*settings.frontier_input_usd_per_million+self.limits.output_tokens*settings.frontier_output_usd_per_million)/1e6
        async with self.lock:
            if (self.requests+1>self.limits.max_requests or self.tokens+tokens>self.limits.max_tokens or self.usd+dollars>self.limits.max_usd or
                tier=="frontier" and (self.frontier_requests+1>settings.frontier_max_requests or self.frontier_tokens+tokens>settings.frontier_max_tokens or self.frontier_usd+dollars>settings.frontier_max_usd)):
                return False
            self.requests+=1; self.tokens+=tokens; self.usd+=dollars
            if tier=="frontier":
                self.frontier_requests+=1; self.frontier_tokens+=tokens; self.frontier_usd+=dollars
            return True


async def evaluate_one(prompt, tier, run_id, settings, transport, budget, limits, paid_enabled=False, executor=None):
    if prompt.split == 'test':
        raise PermissionError('test split locked')
    if tier=='frontier' and (not paid_enabled or not settings.frontier_enabled or limits.max_usd <= 0):
        raise PermissionError('paid frontier requires explicit enablement, credentials, rates and positive caps')
    backend=settings.backend(tier)
    payload={'model':backend.model,'messages':[{'role':'user','content':prompt.prompt}],'max_tokens':limits.output_tokens,'temperature':limits.temperature,'stream':False}
    settings_fp=hashlib.sha256(json.dumps({'output_tokens':limits.output_tokens,'temperature':limits.temperature},sort_keys=True).encode()).hexdigest()
    began=datetime.now(timezone.utc); attempts=[]; raw=None; score=None; parsed=None; error=None; model=backend.model; usage={}
    outcome=Outcome.BLOCKED
    for _ in range(limits.retries+1):
        if not await budget.reserve(prompt.prompt,tier,settings):
            error='run_budget_exhausted'; break
        start=datetime.now(timezone.utc)
        try:
            reply=await asyncio.wait_for(transport.complete(backend,payload),timeout=settings.timeout_seconds)
            end=datetime.now(timezone.utc)
            model=reply.get('model') or backend.model
            raw=reply['choices'][0]['message']['content']
            usage=reply.get('usage') or {}
        except Exception as exc:
            end=datetime.now(timezone.utc)
            error='timeout' if isinstance(exc,asyncio.TimeoutError) else 'backend_error'
            outcome=Outcome.BACKEND_ERROR
            attempts.append(Attempt(started_at=start,ended_at=end,outcome=error))
            continue
        try:
            if prompt.task=='math': scored=score_math(raw,prompt.reference)
            elif prompt.task=='choice': scored=score_choice(raw,prompt.reference,reply['choices'][0].get('finish_reason')=='length')
            elif prompt.task=='code': scored=score_code(raw,prompt.tests,prompt.test_imports,executor=executor) if executor else score_code(raw,prompt.tests,prompt.test_imports)
            else: raise ValueError('unsupported task')
            outcome=Outcome(scored['outcome']); parsed=scored['parsed_answer']; score=scored['score']; error=scored.get('error_category')
        except Exception:
            outcome=Outcome.EVALUATOR_ERROR; error='scorer_exception'
        attempts.append(Attempt(started_at=start,ended_at=end,outcome=outcome,prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens')))
        break
    ended=datetime.now(timezone.utc)
    return Result(run_id=run_id,prompt_id=prompt.prompt_id,task=prompt.task,split=prompt.split,dataset_revision=prompt.dataset_revision,source_revision=prompt.source_revision,template_fingerprint=prompt.template_fingerprint,settings_fingerprint=settings_fp,tier=tier,backend=backend.base_url,model=model,raw_response=raw,parsed_answer=parsed,score=score,outcome=outcome,error_category=error,started_at=began,ended_at=ended,prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),execution='real',attempts=tuple(attempts))


async def evaluate_batch(prompts, tiers, run_id, settings, transport, limits, paid_enabled=False, executor=None):
    if not prompts or not tiers or any(p.split=='test' for p in prompts):
        raise ValueError('nonempty development prompts and tiers required')
    sem=asyncio.Semaphore(limits.concurrency); budget=RunBudget(limits)
    async def one(prompt,tier):
        async with sem:
            return await evaluate_one(prompt,tier,run_id,settings,transport,budget,limits,paid_enabled,executor)
    return await asyncio.gather(*(one(prompt,tier) for prompt in prompts for tier in tiers))
