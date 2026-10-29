import asyncio
from dataclasses import replace
import httpx
import pytest
from jev_gateway.config import from_env
from jev_gateway.routing.jev_client import JevClient
from jev_gateway.routing.contracts import RoutingError


def enabled(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY', 'test-only')
    return replace(from_env(), jev_model='jev-latest', jev_max_requests=1,
                   jev_max_tokens=100000, jev_max_usd=1,
                   jev_input_usd_per_million=1, jev_output_usd_per_million=1)


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
    client=JevClient(from_env())
    with pytest.raises(RoutingError):
        asyncio.run(client.decide('x', {'x':{'type':'noul','instructions':'yes?'}}))


def test_expired_jev_deadline_does_not_spend(monkeypatch):
    settings=enabled(monkeypatch)
    client=JevClient(settings)
    with pytest.raises(RoutingError):
        asyncio.run(client.decide('x', {'x':{'type':'noul','instructions':'yes?'}}, deadline_seconds=0))
    assert client.requests==0
