import asyncio
from dataclasses import replace

import httpx
import pytest

from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.baselines import FixedRouter, SeededRandomRouter
from jev_gateway.routing.contracts import Decision, RoutingError, require_eligible
from jev_gateway.routing.jev_client import JevClient
from jev_gateway.routing.prompted import PromptedRouter
from jev_gateway.routing.strands import StrandsRouter


def run(coroutine):
    return asyncio.run(coroutine)


def test_unsupported_selection_and_disabled_frontier_cannot_upgrade():
    settings=from_env()
    request=request_for(settings, ({'role':'user','content':'x'},), 32, 'p')
    assert 'frontier' not in request.eligible_tiers
    with pytest.raises(ValueError):
        Decision('unknown', 'bad', '1', 0)
    with pytest.raises(RoutingError):
        run(FixedRouter('frontier').decide(request))
    for seed in range(20):
        assert run(SeededRandomRouter(seed).decide(request)).tier != 'frontier'
    with pytest.raises(RoutingError):
        require_eligible(Decision('frontier','bad','1',0),request)


def test_context_incompatibility_excludes_all_backends():
    request=request_for(from_env(), ({'role':'user','content':'a'*5000},), 32, 'p')
    with pytest.raises(RoutingError):
        run(FixedRouter('small').decide(request))


def test_prompted_timeout_and_invalid_choice_are_errors():
    settings=from_env()
    request=request_for(settings, ({'role':'user','content':'x'},), 32, 'p')
    def timeout(req): raise httpx.ReadTimeout('timeout')
    router=PromptedRouter(settings, BackendTransport(1,httpx.MockTransport(timeout)))
    with pytest.raises(RoutingError):
        run(router.decide(request))
    def invalid(req):
        return httpx.Response(200,json={'choices':[{'message':{'content':'{"tier":"frontier"}'}}]})
    router=PromptedRouter(settings, BackendTransport(1,httpx.MockTransport(invalid)))
    with pytest.raises(RoutingError):
        run(router.decide(request))


def test_jev_budget_and_timeout_fail_closed(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY','test-only')
    settings=replace(from_env(),jev_model='jev-latest',jev_max_requests=1,
                     jev_max_tokens=1,jev_max_usd=1,jev_input_usd_per_million=1,
                     jev_output_usd_per_million=1)
    seen=[]
    client=JevClient(settings,httpx.MockTransport(lambda req: seen.append(req) or httpx.Response(200)))
    with pytest.raises(RoutingError):
        run(client.decide('x',{'x':{'type':'noul','instructions':'yes?'}}))
    assert not seen
    settings=replace(settings,jev_max_tokens=100000)
    client=JevClient(settings,httpx.MockTransport(lambda req: (_ for _ in ()).throw(httpx.ReadTimeout('timeout'))))
    with pytest.raises(RoutingError):
        run(client.decide('x',{'x':{'type':'noul','instructions':'yes?'}}))


def test_strands_model_mismatch_fails():
    settings=from_env()
    def mismatch(req):
        return httpx.Response(200,json={'model':'other','answers':{'route':{
            'type':'choice','choice':'small','probabilities':{'small':.5,'medium':.5}}}})
    router=StrandsRouter(settings,url='http://127.0.0.1:8099',model='configured',
                         checkpoint='pinned',device='cpu',transport=httpx.MockTransport(mismatch))
    with pytest.raises(RoutingError):
        run(router.decide(request_for(settings, ({'role':'user','content':'x'},), 32, 'p')))
