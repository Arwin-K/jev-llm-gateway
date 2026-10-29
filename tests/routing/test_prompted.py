import asyncio
import httpx
import pytest
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.prompted import PromptedRouter
from jev_gateway.routing.contracts import RoutingError


def test_prompted_router_parses_only_eligible_json():
    seen=[]
    def handler(request):
        seen.append(request.content)
        return httpx.Response(200, json={'choices':[{'message':{'content':'{"tier":"medium"}'}}],
                                         'usage':{'prompt_tokens':10,'completion_tokens':4}})
    settings=from_env()
    transport=BackendTransport(2, httpx.MockTransport(handler))
    routing=request_for(settings, ({'role':'user','content':'Solve a hard problem'},), 32, 'id')
    decision=asyncio.run(PromptedRouter(settings, transport).decide(routing))
    assert decision.tier=='medium' and decision.usage['completion_tokens']==4
    assert b'"max_tokens":24' in seen[0]


def test_prompted_router_rejects_prose():
    def handler(request):
        return httpx.Response(200, json={'choices':[{'message':{'content':'I choose frontier'}}]})
    settings=from_env()
    transport=BackendTransport(2, httpx.MockTransport(handler))
    with pytest.raises(RoutingError):
        asyncio.run(PromptedRouter(settings, transport).decide(
            request_for(settings, ({'role':'user','content':'x'},), 32, 'id')))
