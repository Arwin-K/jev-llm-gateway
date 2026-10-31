"""Explicit route-first, cascade-only, and route-then-verify modes."""
import asyncio
import time
from dataclasses import dataclass, replace

from jev_gateway.routing.contracts import Decision, RoutingRequest, require_eligible
from .cascade import CascadeEngine, CascadeResult, ExecutionRequest, GenerationAttempt


@dataclass
class ModeResult:
    mode: str
    decision: Decision | None
    execution: CascadeResult


class ModeExecutor:
    def __init__(self, router, cascade: CascadeEngine, fallback_router=None):
        self.router = router
        self.cascade = cascade
        self.fallback_router = fallback_router

    async def run(self, mode: str, request: ExecutionRequest, routing: RoutingRequest | None = None) -> ModeResult:
        if mode not in {'route_first','cascade','hybrid'}:
            raise ValueError('unknown execution mode')
        if mode == 'cascade':
            return ModeResult(mode,None,await self.cascade.run(request))
        if routing is None:
            raise ValueError('routing request required')
        remaining=request.deadline_at-time.monotonic()
        if remaining <= 0:
            return ModeResult(mode,None,CascadeResult('deadline_exceeded',None,None,[]))
        try:
            if self.router is None:
                raise ValueError('primary router unavailable')
            decision=require_eligible(await asyncio.wait_for(self.router.decide(routing),remaining),routing)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if self.fallback_router is None:
                return ModeResult(mode,None,CascadeResult('routing_failed',None,None,[]))
            remaining=request.deadline_at-time.monotonic()
            if remaining <= 0:
                return ModeResult(mode,None,CascadeResult('deadline_exceeded',None,None,[]))
            try:
                decision=require_eligible(await asyncio.wait_for(
                    self.fallback_router.decide(routing),remaining),routing)
                decision=replace(decision,outcome='fallback_selected',fallback_reason=type(exc).__name__)
            except asyncio.CancelledError:
                raise
            except Exception:
                return ModeResult(mode,None,CascadeResult('routing_failed',None,None,[]))
        if mode == 'hybrid':
            return ModeResult(mode,decision,await self.cascade.run(request,start_tier=decision.tier))
        remaining=request.deadline_at-time.monotonic()
        if remaining <= 0:
            return ModeResult(mode,decision,CascadeResult('deadline_exceeded',None,None,[]))
        started=time.perf_counter()
        try:
            response=await asyncio.wait_for(self.cascade.generator.generate(
                decision.tier,request.messages,request.max_output_tokens,request.temperature,remaining),remaining)
            answer=response['choices'][0]['message']['content']
            if not isinstance(answer,str) or not answer.strip():
                raise ValueError('malformed generated answer')
            attempt=GenerationAttempt(decision.tier,self.cascade.models[decision.tier],
                                      'unverified_route_first',(time.perf_counter()-started)*1000,
                                      response,answer,response.get('usage') or {})
            execution=CascadeResult('unverified_route_first',decision.tier,response,[attempt])
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            attempt=GenerationAttempt(decision.tier,self.cascade.models[decision.tier],
                                      'generation_error',(time.perf_counter()-started)*1000,
                                      error_category=type(exc).__name__)
            execution=CascadeResult('generation_error',None,None,[attempt])
        return ModeResult(mode,decision,execution)
