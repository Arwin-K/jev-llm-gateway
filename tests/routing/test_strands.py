import asyncio
import httpx
import pytest
from jev_gateway.config import from_env
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.strands import StrandsRouter


def test_local_typed_server_contract():
    def handler(request):
        assert request.url.path=='/v1/systemone'
        return httpx.Response(200,json={'model':'hobson-latest','answers':{'route':{
            'type':'choice','choice':'small','probabilities':{'small':.7,'medium':.3}}}})
    settings=from_env()
    router=StrandsRouter(settings,url='http://127.0.0.1:8099',model='hobson-latest',
                         checkpoint='pinned-local-folder',device='mps',transport=httpx.MockTransport(handler))
    decision=asyncio.run(router.decide(request_for(settings, ({'role':'user','content':'x'},), 32, 'p')))
    assert decision.tier=='small' and decision.decision_model=='pinned-local-folder@mps'


def test_public_server_rejected():
    with pytest.raises(ValueError):
        StrandsRouter(from_env(),url='https://example.com',model='x',checkpoint='x',device='cpu')
