import asyncio
import pytest
from jev_gateway.config import from_env
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.baselines import FixedRouter, SeededRandomRouter
from jev_gateway.routing.contracts import RoutingError


def test_fixed_and_random_respect_eligibility():
    settings = from_env()
    request = request_for(settings, ({'role': 'user', 'content': 'x'},), 16, 'prompt-1')
    assert request.eligible_tiers == ('small', 'medium')
    assert asyncio.run(FixedRouter('small').decide(request)).tier == 'small'
    with pytest.raises(RoutingError):
        asyncio.run(FixedRouter('frontier').decide(request))
    policy = SeededRandomRouter(42)
    assert asyncio.run(policy.decide(request)).tier == asyncio.run(policy.decide(request)).tier


def test_context_excludes_tiers_without_silent_upgrade():
    request = request_for(from_env(), ({'role': 'user', 'content': 'x' * 4090},), 32, 'long')
    assert request.eligible_tiers == ()
    with pytest.raises(RoutingError):
        asyncio.run(SeededRandomRouter(42).decide(request))
