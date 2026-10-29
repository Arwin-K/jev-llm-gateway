"""Deterministic fixed-tier and request-identity seeded comparison policies."""
import hashlib
import time

from .contracts import Decision, RoutingError, RoutingRequest, TIERS


class FixedRouter:
    version = '1'

    def __init__(self, tier: str):
        if tier not in TIERS:
            raise ValueError('unknown fixed tier')
        self.tier = tier
        self.name = f'always-{tier}'

    async def decide(self, request: RoutingRequest) -> Decision:
        start = time.perf_counter()
        if self.tier not in request.eligible_tiers:
            raise RoutingError(f'{self.tier} is ineligible; fixed baseline excluded')
        return Decision(self.tier, self.name, self.version, (time.perf_counter()-start)*1000,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint)


class SeededRandomRouter:
    name = 'seeded-random'
    version = '1'

    def __init__(self, seed: int):
        self.seed = seed

    async def decide(self, request: RoutingRequest) -> Decision:
        start = time.perf_counter()
        if not request.eligible_tiers:
            raise RoutingError('no eligible tier for random baseline')
        digest = hashlib.sha256(f'{self.seed}:{request.request_id}'.encode()).digest()
        tier = request.eligible_tiers[int.from_bytes(digest[:8], 'big') % len(request.eligible_tiers)]
        return Decision(tier, self.name, self.version, (time.perf_counter()-start)*1000,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint)
