from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json

import httpx
from fastapi.testclient import TestClient

from jev_gateway.api import create_app
from jev_gateway.cache.check import CacheCheck
from jev_gateway.cache.embedding import Embedding
from jev_gateway.cache.retrieval import Candidate
from jev_gateway.cache.scope import CacheEntry
from jev_gateway.config import from_env
from jev_gateway.execution.verifier import EVENT, QUESTION_VERSION, VerificationDecision
from jev_gateway.routing.baselines import FixedRouter
from jev_gateway.transport import BackendTransport


class Verifier:
    def __init__(self, probability):
        self.probability=probability

    async def judge(self, request, *, deadline_seconds=None):
        return VerificationDecision(request.request_id,request.answer_sha256,self.probability,
                                    EVENT,QUESTION_VERSION,'fixture-jev',1.0,{})


def paid_settings(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY','offline-test-key')
    return replace(from_env(),jev_model='fixture-jev',jev_max_requests=10,jev_max_tokens=100000,
                   jev_max_usd=1,jev_input_usd_per_million=1,jev_output_usd_per_million=1,
                   jev_rate_source_url='https://example.invalid/offline-fixture',
                   jev_rate_effective_date='2026-10-30',execution_paid_enabled=True,
                   execution_max_requests=10,execution_max_tokens=100000,execution_max_usd=1,
                   verification_threshold=.8,verification_threshold_source='offline-test-threshold',
                   cache_verification_threshold=.8,
                   cache_verification_threshold_source='offline-test-threshold')


def post(client, **options):
    return client.post('/v1/chat/completions',json={'model':'auto',
        'messages':[{'role':'user','content':'What is two plus two?'}],**options})


def test_route_first_and_legacy_explicit_dispatch_keep_separate_headers():
    seen=[]
    def respond(request):
        seen.append(request.url)
        return httpx.Response(200,json={'choices':[{'message':{'content':'four'}}]})
    settings=from_env()
    with TestClient(create_app(settings,BackendTransport(2,httpx.MockTransport(respond)),
                               router=FixedRouter('medium'))) as client:
        routed=post(client,execution_mode='route_first')
        explicit=client.post('/v1/chat/completions',json={'model':'small',
            'messages':[{'role':'user','content':'x'}]})
        refused=post(client,execution_mode='route_first',stream=True)
    assert routed.status_code==200 and routed.headers['x-jev-tier']=='medium'
    assert routed.headers['x-jev-verification']=='unverified_route_first'
    assert explicit.status_code==200 and explicit.headers['x-jev-tier']=='small'
    assert refused.status_code==422 and len(seen)==2


def test_cascade_buffers_rejection_and_escalates(monkeypatch):
    settings=paid_settings(monkeypatch)
    models=[]
    def respond(request):
        model=json.loads(request.content)['model']
        models.append(model)
        return httpx.Response(200,json={'choices':[{'message':{'content':'answer '+model}}]})
    class Sequence(Verifier):
        def __init__(self): self.calls=0
        async def judge(self,request,*,deadline_seconds=None):
            self.calls+=1
            self.probability=.2 if self.calls==1 else .9
            return await super().judge(request,deadline_seconds=deadline_seconds)
    with TestClient(create_app(settings,BackendTransport(2,httpx.MockTransport(respond)),
                               router=FixedRouter('small'),answer_verifier=Sequence())) as client:
        result=post(client,execution_mode='cascade')
    assert result.status_code==200 and result.headers['x-jev-tier']=='medium'
    assert result.headers['x-jev-verification']=='accepted_verified'
    assert len(models)==2 and settings.small.model in models[0] and settings.medium.model in models[1]
    assert settings.small.model not in result.json()['choices'][0]['message']['content']


def test_verified_cache_hit_skips_generation(monkeypatch):
    settings=paid_settings(monkeypatch)
    class Index:
        embedding_identity='fixture@revision'
        def close(self): pass
    class Retriever:
        async def lookup(self,question,scope,**kwargs):
            now=datetime.now(timezone.utc)
            entry=CacheEntry('stored',scope.fingerprint,question,'stored answer',now.isoformat(),
                             (now+timedelta(hours=1)).isoformat(),'small',settings.small.model,
                             'accepted',True,scope.embedding_identity)
            return [Candidate(entry,.98,.9,'offline-test-threshold')]
    class Checker:
        async def check(self,candidate,messages,scope,**kwargs):
            return CacheCheck(candidate.entry.entry_id,'accepted','threshold_met',.95,.8,
                              'offline-test-threshold','applies','v1','fixture-jev',1.0,{})
    class Encoder: pass
    class Lifecycle: pass
    calls=[]
    transport=BackendTransport(2,httpx.MockTransport(lambda request:calls.append(request) or
                            httpx.Response(500)))
    with TestClient(create_app(settings,transport,router=FixedRouter('small'),
                               cache_runtime=(Encoder(),Index(),Retriever(),Lifecycle()),
                               cache_checker=Checker())) as client:
        result=post(client,execution_mode='cascade',cache_mode='verified')
    assert result.status_code==200 and result.headers['x-jev-cache']=='verified_hit'
    assert result.json()['choices'][0]['message']['content']=='stored answer' and not calls


def test_paid_and_experimental_gates_fail_before_backend():
    calls=[]
    transport=BackendTransport(2,httpx.MockTransport(lambda request:calls.append(request) or
                               httpx.Response(500)))
    with TestClient(create_app(from_env(),transport,router=FixedRouter('small'))) as client:
        assert post(client,execution_mode='cascade').status_code==503
        assert post(client,execution_mode='route_first',cache_mode='similarity_only').status_code==503
    assert not calls


def test_cache_check_miss_generates_and_inserts_only_verified_answer(monkeypatch):
    settings=paid_settings(monkeypatch)
    class Index:
        embedding_identity='fixture@revision'
        def close(self): pass
    class Retriever:
        async def lookup(self,question,scope,**kwargs):
            now=datetime.now(timezone.utc)
            entry=CacheEntry('old',scope.fingerprint,question,'wrong',now.isoformat(),
                             (now+timedelta(hours=1)).isoformat(),'small',settings.small.model,
                             'accepted',True,scope.embedding_identity)
            return [Candidate(entry,.99,.9,'offline-test-threshold')]
    class Checker:
        async def check(self,candidate,messages,scope,**kwargs):
            return CacheCheck('old','rejected','below_threshold',.1,.8,
                              'offline-test-threshold','applies','v1','fixture-jev',1.0,{})
    class Encoder:
        async def encode(self,text):
            return Embedding((1.,0.),'fixture','revision','cpu','l2_unit',1.)
    class Lifecycle:
        def __init__(self): self.saved=[]
        async def insert(self,entry,vector): self.saved.append((entry,vector))
    lifecycle=Lifecycle(); calls=[]
    def respond(request):
        calls.append(request)
        return httpx.Response(200,json={'choices':[{'message':{'content':'correct'}}]})
    with TestClient(create_app(settings,BackendTransport(2,httpx.MockTransport(respond)),
                               router=FixedRouter('small'),answer_verifier=Verifier(.9),
                               cache_runtime=(Encoder(),Index(),Retriever(),lifecycle),
                               cache_checker=Checker())) as client:
        result=post(client,execution_mode='cascade',cache_mode='verified')
    assert result.status_code==200 and result.headers['x-jev-cache']=='inserted'
    assert len(calls)==1 and len(lifecycle.saved)==1
    assert lifecycle.saved[0][0].answer=='correct' and lifecycle.saved[0][0].verified
