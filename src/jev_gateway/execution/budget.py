"""One cumulative request ledger across generation and decision stages."""
import asyncio
import json
import time
from dataclasses import dataclass

from jev_gateway.budget import FrontierBudget


class ExecutionLimit(RuntimeError):
    pass


@dataclass(frozen=True)
class StageReservation:
    stage: str
    tier: str | None
    tokens: int
    usd: float
    cost_status: str


class ExecutionBudget:
    def __init__(self, settings, *, deadline_at: float, max_requests: int,
                 max_tokens: int, max_usd: float, frontier_budget: FrontierBudget):
        if max_requests < 1 or max_tokens < 1 or max_usd < 0:
            raise ValueError('positive request/token caps and nonnegative USD cap required')
        self.settings=settings
        self.deadline_at=deadline_at
        self.max_requests=max_requests
        self.max_tokens=max_tokens
        self.max_usd=max_usd
        self.frontier_budget=frontier_budget
        self.lock=asyncio.Lock()
        self.requests=0
        self.tokens=0
        self.usd=0.
        self.observed_tokens=0
        self.stages=[]
        self.overrun=False

    def remaining(self):
        remaining=self.deadline_at-time.monotonic()
        if remaining <= 0:
            raise ExecutionLimit('whole-request deadline exhausted')
        return remaining

    async def reserve(self, stage: str, *, tier: str | None, content: object,
                      output_tokens: int = 0) -> StageReservation:
        self.remaining()
        input_units=4*len(json.dumps(content,ensure_ascii=False)) + 256
        tokens=input_units+output_tokens
        usd=0.
        status='self_hosted_capacity_unknown'
        if stage in {'router_jev','verification','cache_verification'}:
            if not self.settings.jev_enabled:
                raise ExecutionLimit('Jev disabled')
            usd=(input_units*self.settings.jev_input_usd_per_million +
                 output_tokens*self.settings.jev_output_usd_per_million)/1_000_000
            status='estimated_api_reservation'
        if tier=='frontier':
            if not self.settings.frontier_enabled:
                raise ExecutionLimit('frontier disabled')
            usd=(input_units*self.settings.frontier_input_usd_per_million +
                 output_tokens*self.settings.frontier_output_usd_per_million)/1_000_000
            status='estimated_api_reservation'
        async with self.lock:
            if (self.overrun or self.requests+1>self.max_requests or
                self.tokens+tokens>self.max_tokens or self.usd+usd>self.max_usd):
                raise ExecutionLimit('whole-request cumulative budget exceeded')
            if tier=='frontier':
                await self.frontier_budget.reserve(list(content['messages']), output_tokens)
            self.requests+=1
            self.tokens+=tokens
            self.usd+=usd
            reservation=StageReservation(stage,tier,tokens,usd,status)
            self.stages.append(reservation)
        return reservation

    async def observe(self, usage: dict):
        observed=usage.get('total_tokens')
        if observed is None:
            parts=(usage.get('prompt_tokens'),usage.get('completion_tokens'))
            if all(isinstance(x,int) for x in parts): observed=sum(parts)
        if observed is None:
            parts=(usage.get('input_tokens'),usage.get('output_tokens'))
            if all(isinstance(x,int) for x in parts): observed=sum(parts)
        if observed is not None:
            async with self.lock:
                self.observed_tokens+=observed
                if self.observed_tokens>self.max_tokens:
                    self.overrun=True


class GenerationAdapter:
    def __init__(self, settings, transport, budget: ExecutionBudget):
        self.settings=settings
        self.transport=transport
        self.budget=budget

    async def generate(self,tier,messages,max_output_tokens,temperature,deadline_seconds):
        backend=self.settings.backend(tier)
        await self.budget.reserve('generation',tier=tier,content={'messages':messages},
                                  output_tokens=max_output_tokens)
        payload={'model':backend.model,'messages':list(messages),'max_tokens':max_output_tokens,
                 'stream':False}
        if temperature is not None:
            payload['temperature']=temperature
        response=await asyncio.wait_for(self.transport.complete(backend,payload),
                                         timeout=min(deadline_seconds,self.budget.remaining()))
        await self.budget.observe(response.get('usage') or {})
        return response


class BudgetedVerifier:
    def __init__(self, verifier, budget: ExecutionBudget, *, stage='verification'):
        self.verifier=verifier
        self.budget=budget
        self.stage=stage

    async def judge(self, request, *, deadline_seconds=None):
        await self.budget.reserve(self.stage,tier=None,
                                  content={'messages':request.messages,'answer':request.answer},
                                  output_tokens=self.budget.settings.jev_decision_output_tokens)
        decision=await self.verifier.judge(request,deadline_seconds=self.budget.remaining())
        await self.budget.observe(decision.usage)
        return decision


class BudgetedRouter:
    def __init__(self, router, budget: ExecutionBudget):
        self.router=router
        self.name=router.name
        self.version=router.version
        self.budget=budget

    async def decide(self, request):
        if self.name.startswith('jev-'):
            await self.budget.reserve('router_jev',tier=None,
                                      content={'request':request.text,'eligible':request.eligible_tiers},
                                      output_tokens=self.budget.settings.jev_decision_output_tokens)
        elif self.name=='prompted-small':
            await self.budget.reserve('router_prompted',tier=None,
                                      content={'request':request.text},output_tokens=24)
        decision=await self.router.decide(request)
        await self.budget.observe(dict(decision.usage))
        return decision
