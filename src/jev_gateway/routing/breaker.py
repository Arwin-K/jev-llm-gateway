"""Single-probe async circuit breaker for the Jev dependency."""
import asyncio
import time

import httpx

from .contracts import RoutingError


class JevUnavailable(RoutingError):
    pass


class JevCircuitBreaker:
    def __init__(self, threshold=3, cooldown_seconds=30., clock=time.monotonic, on_transition=None):
        if threshold < 1 or cooldown_seconds <= 0:
            raise ValueError("breaker threshold and cooldown must be positive")
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.clock = clock
        self.on_transition = on_transition
        self.state = "closed"
        self.failures = 0
        self.opened_at = None
        self.probe_active = False
        self.lock = asyncio.Lock()

    def _transition(self, state):
        self.state = state
        if self.on_transition:
            self.on_transition(state)

    async def call(self, operation):
        async with self.lock:
            if self.state == "open":
                if self.clock() - self.opened_at < self.cooldown_seconds:
                    raise JevUnavailable("Jev circuit open")
                self._transition("half_open")
            if self.state == "half_open":
                if self.probe_active:
                    raise JevUnavailable("Jev recovery probe already in progress")
                self.probe_active = True
        try:
            result = await operation()
        except asyncio.CancelledError:
            async with self.lock:
                self.probe_active = False
            raise
        except Exception as exc:
            qualifies = (isinstance(exc, (httpx.RequestError, ValueError, KeyError, TypeError)) or
                         isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500)
            async with self.lock:
                self.probe_active = False
                if qualifies:
                    self.failures += 1
                    if self.state == "half_open" or self.failures >= self.threshold:
                        self.opened_at = self.clock()
                        self._transition("open")
                elif self.state == "half_open":
                    self.opened_at = self.clock()
                    self._transition("open")
            raise
        async with self.lock:
            self.probe_active = False
            self.failures = 0
            if self.state != "closed":
                self._transition("closed")
        return result
