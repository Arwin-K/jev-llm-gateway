import asyncio
import time

import pytest

from jev_gateway.admission import AdmissionGate, AdmissionRejected
from jev_gateway.observability import Metrics


@pytest.mark.anyio
async def test_queue_is_bounded_and_cancellation_cleans_up():
    metrics = Metrics()
    gate = AdmissionGate(1, 1, metrics)
    await gate.acquire(time.monotonic() + 2)
    waiting = asyncio.create_task(gate.acquire(time.monotonic() + 2))
    await asyncio.sleep(0)
    assert gate.queued == 1
    with pytest.raises(AdmissionRejected, match="queue_full"):
        await gate.acquire(time.monotonic() + 2)
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting
    assert gate.queued == 0 and gate.active == 1
    await gate.release()
    assert metrics.active == 0
    await gate.acquire(time.monotonic() + 2)
    await gate.release()


@pytest.mark.anyio
async def test_queue_deadline_does_not_leak_slot():
    gate = AdmissionGate(1, 1, Metrics())
    await gate.acquire(time.monotonic() + 2)
    with pytest.raises(AdmissionRejected, match="queue_deadline"):
        await gate.acquire(time.monotonic() + .001)
    assert gate.active == 1 and gate.queued == 0
    await gate.release()
