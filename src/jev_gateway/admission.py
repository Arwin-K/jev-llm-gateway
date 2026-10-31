"""Bounded process-local HTTP admission with cancellable queue waits."""
import asyncio
import time


class AdmissionRejected(RuntimeError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


class AdmissionGate:
    def __init__(self, max_active: int, max_queued: int, metrics):
        if max_active < 1 or max_queued < 0:
            raise ValueError("admission limits are invalid")
        self.semaphore = asyncio.Semaphore(max_active)
        self.max_active = max_active
        self.max_queued = max_queued
        self.lock = asyncio.Lock()
        self.active = 0
        self.queued = 0
        self.metrics = metrics

    async def acquire(self, deadline):
        began = time.monotonic()
        async with self.lock:
            if self.active >= self.max_active and self.queued >= self.max_queued:
                raise AdmissionRejected("queue_full")
            self.queued += 1
            self.metrics.queued = self.queued
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise asyncio.TimeoutError
            await asyncio.wait_for(self.semaphore.acquire(), remaining)
        except BaseException as exc:
            async with self.lock:
                self.queued -= 1
                self.metrics.queued = self.queued
            if isinstance(exc, asyncio.TimeoutError):
                raise AdmissionRejected("queue_deadline") from exc
            raise
        async with self.lock:
            self.queued -= 1
            self.active += 1
            self.metrics.queued = self.queued
            self.metrics.active = self.active
        self.metrics.observe("jev_queue_duration_seconds", time.monotonic() - began)

    async def release(self):
        async with self.lock:
            self.active -= 1
            self.metrics.active = self.active
            self.semaphore.release()
