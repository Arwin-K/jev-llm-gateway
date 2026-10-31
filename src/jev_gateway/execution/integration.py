"""Bounded HTTP execution path for optional verification and semantic reuse."""
import time
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from jev_gateway.cache.scope import CacheEntry, make_scope
from jev_gateway.routing.admission import request_for
from .acceptance import AcceptancePolicy
from .budget import BudgetedRouter, BudgetedVerifier, ExecutionBudget, GenerationAdapter
from .cascade import CascadeEngine, ExecutionRequest
from .modes import ModeExecutor


def _paid_ready(settings):
    return (settings.execution_paid_enabled and settings.jev_enabled and
            settings.execution_max_requests > 0 and settings.execution_max_tokens > 0 and
            settings.execution_max_usd > 0)


async def execute(app, request, trace, *, max_tokens: int, deadline: float):
    settings=app.state.settings
    mode=request.execution_mode
    cache_mode=request.cache_mode
    if request.stream:
        raise HTTPException(422,'streaming is unavailable for buffered execution modes')
    if mode in {'route_first','hybrid'} and request.model!='auto':
        raise HTTPException(422,'route-first and hybrid execution require model=auto')
    if mode=='cascade' and request.model not in {'auto','small'}:
        raise HTTPException(422,'cascade execution starts at small; use model=auto or small')
    if cache_mode!='off' and mode=='standard':
        raise HTTPException(422,'cache execution requires route_first, cascade, or hybrid mode')
    if cache_mode=='similarity_only' and not settings.cache_similarity_only_enabled:
        raise HTTPException(503,'experimental similarity-only reuse is disabled')
    paid=(mode in {'cascade','hybrid'} or cache_mode=='verified' or
          mode=='route_first' and getattr(app.state.router,'name','').startswith('jev-'))
    if paid and not _paid_ready(settings):
        raise HTTPException(503,'paid execution requires explicit enablement, Jev configuration, and positive run caps')
    if mode in {'cascade','hybrid'} and settings.verification_threshold is None:
        raise HTTPException(503,'answer verification threshold and source are unconfigured')
    if cache_mode=='verified' and settings.cache_verification_threshold is None:
        raise HTTPException(503,'cache applicability threshold and source are unconfigured')
    messages=tuple(message.model_dump() for message in request.messages)
    routing=request_for(settings,messages,max_tokens,trace.request_id)
    if not routing.eligible_tiers:
        raise HTTPException(422,'request exceeds configured backend context limits')
    budget=ExecutionBudget(settings,deadline_at=deadline,
                           max_requests=settings.execution_max_requests if paid else max(4,settings.execution_max_requests),
                           max_tokens=settings.execution_max_tokens if paid else max(50000,settings.execution_max_tokens),
                           max_usd=settings.execution_max_usd,frontier_budget=app.state.budget)
    scope=None
    cache_state='off'
    cache=app.state.cache_runtime
    if cache_mode!='off':
        cache_state='unavailable' if cache is None else 'miss'
        if cache is not None and messages[-1]['role']=='user':
            encoder,index,retriever,lifecycle=cache
            scope=make_scope(messages,namespace=settings.cache_namespace,
                             embedding_identity=index.embedding_identity,
                             policy_identity=f'{mode}:{settings.verification_threshold_source}:{settings.cache_verification_threshold_source}',
                             model_identity=':'.join(settings.backend(t).model for t in ('small','medium','frontier')),
                             max_output_tokens=max_tokens,temperature=request.temperature)
            try:
                candidates=await retriever.lookup(messages[-1]['content'],scope,
                                                   allow_unverified=cache_mode=='similarity_only')
                for candidate in candidates:
                    if (candidate.entry.origin_tier not in routing.eligible_tiers or
                        candidate.entry.origin_model!=settings.backend(candidate.entry.origin_tier).model):
                        cache_state='candidate_ineligible'
                        continue
                    if cache_mode=='verified':
                        await budget.reserve('cache_verification',tier=None,
                                             content={'messages':messages,'answer':candidate.entry.answer},
                                             output_tokens=settings.jev_decision_output_tokens)
                        check=await app.state.cache_checker.check(candidate,messages,scope,
                                                                   deadline_seconds=budget.remaining())
                        await budget.observe(check.usage)
                        if check.outcome!='accepted':
                            cache_state=f'candidate_{check.outcome}'
                            continue
                    entry=candidate.entry
                    trace.tier=entry.origin_tier
                    trace.backend_model=entry.origin_model
                    trace.execution={'mode':mode,'cache':'verified_hit' if cache_mode=='verified' else 'similarity_only_hit',
                                     'entry_id':entry.entry_id,'stage_count':budget.requests,
                                     'stages':[s.__dict__ for s in budget.stages]}
                    trace.finish('cache_hit',cost_status='estimated_api_reservation' if budget.usd else 'unpriced')
                    return {'id':f'chatcmpl-{uuid.uuid4().hex}','object':'chat.completion',
                            'created':int(time.time()),'model':entry.origin_model,
                            'choices':[{'index':0,'message':{'role':'assistant','content':entry.answer},'finish_reason':'stop'}],
                            'usage':None}, {'x-jev-cache':trace.execution['cache'],'x-jev-tier':entry.origin_tier,
                                             'x-jev-backend-model':entry.origin_model,'x-jev-verification':'cached_verified' if cache_mode=='verified' else 'experimental_unverified'}
            except Exception as exc:
                cache_state=f'error_{type(exc).__name__}'
    generator=GenerationAdapter(settings,app.state.transport,budget)
    verifier=BudgetedVerifier(app.state.answer_verifier,budget) if mode in {'cascade','hybrid'} else None
    threshold=settings.verification_threshold if settings.verification_threshold is not None else 1.0
    acceptance=AcceptancePolicy(threshold,settings.verification_threshold_source or 'unconfigured')
    cascade=CascadeEngine(generator,verifier,acceptance,
                          {tier:settings.backend(tier).model for tier in ('small','medium','frontier')})
    router=BudgetedRouter(app.state.router,budget) if app.state.router is not None else None
    execution=ExecutionRequest(trace.request_id,messages,max_tokens,request.temperature,
                               routing.eligible_tiers,deadline)
    result=await ModeExecutor(router,cascade).run(mode,execution,routing if mode!='cascade' else None)
    outcome=result.execution
    trace.execution={'mode':mode,'cache':cache_state,'status':outcome.status,
                     'attempts':[{'tier':a.tier,'outcome':a.outcome,'error_category':a.error_category,
                                  'duration_ms':a.duration_ms,
                                  'verification_probability':a.verification.probability if a.verification else None}
                                 for a in outcome.attempts],
                     'stage_count':budget.requests,'reserved_tokens':budget.tokens,
                     'reserved_usd':budget.usd,'observed_tokens':budget.observed_tokens,
                     'stages':[s.__dict__ for s in budget.stages]}
    if result.decision:
        trace.routing={'policy':result.decision.policy,'version':result.decision.version,
                       'outcome':result.decision.outcome,'duration_ms':result.decision.duration_ms,
                       'usage':dict(result.decision.usage)}
    if outcome.response is None or outcome.accepted_tier is None:
        trace.finish(outcome.status)
        raise HTTPException(504 if outcome.status=='deadline_exceeded' else 503,
                            f'execution ended without an accepted answer: {outcome.status}')
    trace.tier=outcome.accepted_tier
    trace.backend_model=settings.backend(outcome.accepted_tier).model
    if (scope is not None and cache is not None and outcome.status=='accepted_verified' and
        messages[-1]['role']=='user'):
        try:
            embedding=await cache[0].encode(messages[-1]['content'])
            now=datetime.now(timezone.utc)
            answer=outcome.response['choices'][0]['message']['content']
            entry=CacheEntry(uuid.uuid4().hex,scope.fingerprint,messages[-1]['content'],answer,
                             now.isoformat(),(now+timedelta(seconds=settings.cache_ttl_seconds)).isoformat(),
                             outcome.accepted_tier,trace.backend_model,'accepted',True,
                             scope.embedding_identity)
            await cache[3].insert(entry,embedding.vector)
            trace.execution['cache']='inserted'
        except Exception as exc:
            trace.execution['cache']=f'insertion_error_{type(exc).__name__}'
    trace.finish(outcome.status,outcome.response.get('usage'),
                 'estimated_api_reservation' if budget.usd else 'unpriced')
    headers={'x-jev-cache':trace.execution['cache'],'x-jev-tier':outcome.accepted_tier,
             'x-jev-backend-model':trace.backend_model,'x-jev-verification':outcome.status}
    if result.decision:
        headers['x-jev-policy']=result.decision.policy
        headers['x-jev-routing-outcome']=result.decision.outcome
    return outcome.response,headers
