import httpx
from fastapi.testclient import TestClient
from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.routing.baselines import FixedRouter
from jev_gateway.routing.contracts import RoutingError
from jev_gateway.transport import BackendTransport


class BrokenRouter:
    name='broken'
    version='1'
    async def decide(self, request):
        raise RoutingError('decision service unavailable')


def test_auto_dispatch_preserves_explicit_request_and_headers():
    seen=[]
    def handler(request):
        seen.append(request.content.decode())
        return httpx.Response(200,json={'choices':[{'message':{'content':'ok'}}]})
    settings=from_env()
    transport=BackendTransport(2,httpx.MockTransport(handler))
    with TestClient(create_app(settings,transport,router=FixedRouter('medium'))) as client:
        auto=client.post('/v1/chat/completions',json={'model':'auto','messages':[{'role':'user','content':'x'}]})
        explicit=client.post('/v1/chat/completions',json={'model':'small','messages':[{'role':'user','content':'x'}]})
    assert auto.status_code==200 and auto.headers['x-jev-tier']=='medium'
    assert auto.headers['x-jev-policy']=='always-medium'
    assert explicit.status_code==200 and explicit.headers['x-jev-tier']=='small'
    assert 'qwen2.5:7b' in seen[0] and 'qwen2.5:1.5b' in seen[1]


def test_auto_fallback_must_be_explicit_and_eligible():
    settings=from_env()
    transport=BackendTransport(2,httpx.MockTransport(lambda request:httpx.Response(200,json={'choices':[]})))
    with TestClient(create_app(settings,transport,router=BrokenRouter())) as client:
        failed=client.post('/v1/chat/completions',json={'model':'auto','messages':[{'role':'user','content':'x'}]})
    assert failed.status_code==503
    with TestClient(create_app(settings,transport,router=BrokenRouter(),fallback_router=FixedRouter('small'))) as client:
        recovered=client.post('/v1/chat/completions',json={'model':'auto','messages':[{'role':'user','content':'x'}]})
    assert recovered.status_code==200 and recovered.headers['x-jev-routing-outcome']=='fallback_selected'
    with TestClient(create_app(settings,transport,router=FixedRouter('frontier'))) as client:
        denied=client.post('/v1/chat/completions',json={'model':'auto','messages':[{'role':'user','content':'x'}]})
    assert denied.status_code==503


def test_auto_streaming_keeps_selected_tier_and_sse():
    class Stream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'data: {"choices":[]}\n\n'
            yield b'data: [DONE]\n\n'
    transport=BackendTransport(2,httpx.MockTransport(lambda request: httpx.Response(
        200,headers={'content-type':'text/event-stream'},stream=Stream())))
    with TestClient(create_app(from_env(),transport,router=FixedRouter('small'))) as client:
        with client.stream('POST','/v1/chat/completions',json={
            'model':'auto','messages':[{'role':'user','content':'x'}],'stream':True}) as response:
            body=b''.join(response.iter_raw())
            assert response.headers['x-jev-tier']=='small'
            assert response.headers['x-jev-policy']=='always-small'
    assert body.endswith(b'data: [DONE]\n\n')
