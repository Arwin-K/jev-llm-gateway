import asyncio
from dataclasses import replace
import json
import httpx
import pytest
from jev_gateway.config import from_env
from jev_gateway.routing.jev_client import JevClient
from jev_gateway.routing.contracts import RoutingError


def enabled(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY', 'test-only')
    return replace(from_env(), decision_provider='jev', decision_url='https://api.typesafe.ai',
                   jev_model='jev-latest', jev_max_requests=1,
                   jev_max_tokens=100000, jev_max_usd=1,
                   jev_input_usd_per_million=1, jev_output_usd_per_million=1, jev_rate_source_url='https://example.com/rates',
                   jev_rate_effective_date='2026-10-29')


def test_official_contract_and_budget(monkeypatch):
    settings=enabled(monkeypatch)
    seen=[]
    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={'model':'jev-1.13.0', 'answers':{'tier':{
            'type':'choice','choice':'small','confidence':.8,'probabilities':{'small':.8,'medium':.2}}},
            'usage':{'input_tokens':20,'output_tokens':4}})
    client=JevClient(settings, httpx.MockTransport(handler))
    q={'tier':{'type':'choice','instructions':'Choose', 'criteria':{'small':None,'medium':None}}}
    reply=asyncio.run(client.decide('hello',q))
    assert reply.answers['tier']['choice']=='small' and reply.usage['output_tokens']==4
    assert seen[0].url.path=='/v1/systemone'
    with pytest.raises(RoutingError):
        asyncio.run(client.decide('hello',q))


def test_disabled_has_no_network(monkeypatch):
    monkeypatch.delenv('TYPESAFE_API_KEY', raising=False)
    settings=from_env()
    assert settings.decision_provider=='laya' and settings.router_policy=='laya-choice'
    assert settings.jev_model=='typed-decisions' and not settings.decision_enabled
    client=JevClient(settings)
    with pytest.raises(RoutingError):
        asyncio.run(client.decide('x', {'x':{'type':'noul','instructions':'yes?'}}))


def test_laya_uses_loopback_without_api_key_or_usd_budget(monkeypatch):
    monkeypatch.delenv('TYPESAFE_API_KEY', raising=False)
    settings=replace(from_env(), decision_provider='laya', decision_url='http://127.0.0.1:8000',
                     jev_model='jev-1', jev_max_requests=1, jev_max_tokens=100000)
    seen=[]
    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={'model':'convaiinnovations/laya', 'answers':{'route':{
            'type':'choice','choice':'small','confidence':.8,'probabilities':{'small':.8,'medium':.2}}},
            'usage':{'input_tokens':20,'output_tokens':0}})
    client=JevClient(settings, httpx.MockTransport(handler))
    reply=asyncio.run(client.decide('hello', {'route':{'type':'choice','instructions':'Choose',
        'criteria':{'small':'small model','medium':'medium model'}}}))
    assert reply.model=='convaiinnovations/laya'
    assert seen[0].url.host=='127.0.0.1' and seen[0].url.path=='/v1/systemone'
    assert 'authorization' not in seen[0].headers
    assert client.usd==0


def test_laya_adds_descriptive_noul_options(monkeypatch):
    monkeypatch.delenv('TYPESAFE_API_KEY', raising=False)
    settings=replace(from_env(), jev_max_requests=1, jev_max_tokens=100000)
    seen=[]
    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={'model':'typed-decisions', 'answers':{'valid':{
            'type':'noul','noul':.9}}, 'usage':{'input_tokens':10,'output_tokens':0}})
    client=JevClient(settings, httpx.MockTransport(handler))
    asyncio.run(client.decide('answer text', {'valid':{'type':'noul','instructions':'Is it valid?'}}))
    question=json.loads(seen[0].content)['questions']['valid']
    assert set(question['criteria'])=={'true','false'}
    assert question['labels']=={'true':'A','false':'B'}


def test_laya_cannot_be_configured_off_loopback():
    with pytest.raises(ValueError, match='loopback'):
        replace(from_env(), decision_provider='laya', decision_url='https://example.com')


def test_expired_jev_deadline_does_not_spend(monkeypatch):
    settings=enabled(monkeypatch)
    client=JevClient(settings)
    with pytest.raises(RoutingError):
        asyncio.run(client.decide('x', {'x':{'type':'noul','instructions':'yes?'}}, deadline_seconds=0))
    assert client.requests==0
