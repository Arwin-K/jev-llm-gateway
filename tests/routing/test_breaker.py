import asyncio
import httpx
import pytest

from jev_gateway.routing.breaker import JevCircuitBreaker, JevUnavailable


@pytest.mark.anyio
async def test_breaker_opens_blocks_and_recovers_with_single_probe():
    now = [0.]
    breaker = JevCircuitBreaker(threshold=2, cooldown_seconds=10, clock=lambda: now[0])
    calls = [0]

    async def fail():
        calls[0] += 1
        raise httpx.ConnectError("offline")

    for _ in range(2):
        with pytest.raises(httpx.ConnectError):
            await breaker.call(fail)
    assert breaker.state == "open"
    with pytest.raises(JevUnavailable):
        await breaker.call(fail)
    assert calls[0] == 2
    now[0] = 11
    began = asyncio.Event()
    release = asyncio.Event()

    async def recover():
        began.set()
        await release.wait()
        return "ok"

    probe = asyncio.create_task(breaker.call(recover))
    await began.wait()
    assert breaker.state == "half_open"
    with pytest.raises(JevUnavailable):
        await breaker.call(recover)
    release.set()
    assert await probe == "ok"
    assert breaker.state == "closed"
    assert breaker.failures == 0


@pytest.mark.anyio
async def test_nonretryable_status_does_not_open_breaker():
    breaker = JevCircuitBreaker(threshold=1)
    request = httpx.Request("POST", "https://example.test")
    response = httpx.Response(400, request=request)
    async def bad_request():
        response.raise_for_status()
    with pytest.raises(httpx.HTTPStatusError):
        await breaker.call(bad_request)
    assert breaker.state == "closed"
