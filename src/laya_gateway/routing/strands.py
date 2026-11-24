"""Local Strands Decider System One server comparison, never a chat endpoint."""
import time
from urllib.parse import urlparse

import httpx

from .contracts import Decision, RoutingError, RoutingRequest


class StrandsRouter:
    name = 'strands-decider'
    version = '1'
    question_version = 'routing-choice-v1'

    def __init__(self, settings, *, url: str, model: str, checkpoint: str,
                 device: str, transport: httpx.AsyncBaseTransport | None = None):
        parsed = urlparse(url)
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1','localhost'} or parsed.username or parsed.password:
            raise ValueError('Strands server must be a local loopback HTTP service')
        if not model or not checkpoint or device not in {'cpu','mps','mlx','cuda'}:
            raise ValueError('explicit Strands model, checkpoint and device required')
        self.settings = settings
        self.model = model
        self.checkpoint = checkpoint
        self.device = device
        self.client = httpx.AsyncClient(base_url=url, timeout=settings.timeout_seconds, transport=transport)

    async def close(self):
        await self.client.aclose()

    async def decide(self, request: RoutingRequest) -> Decision:
        if not request.eligible_tiers:
            raise RoutingError('no eligible generator for Strands choice')
        criteria = {tier: f'{tier}: {self.settings.backend(tier).model}' for tier in request.eligible_tiers}
        body = {'model':self.model, 'state':request.text,
                'questions':{'route':{'type':'choice',
                    'instructions':'Choose the least costly eligible generator likely to answer correctly.',
                    'criteria':criteria}}}
        start = time.perf_counter()
        try:
            response = await self.client.post('/v1/systemone', json=body)
            response.raise_for_status()
            data = response.json()
            answer = data['answers']['route']
            selected = answer['choice']
            probabilities = answer['probabilities']
            if (answer['type'] != 'choice' or selected not in request.eligible_tiers or
                set(probabilities) != set(request.eligible_tiers) or
                any(not isinstance(p,(int,float)) or not 0 <= p <= 1 for p in probabilities.values())):
                raise ValueError('invalid Strands choice')
            if data['model'] != self.model:
                raise ValueError('served Strands model differs from configured identity')
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise RoutingError('Strands decision unavailable or invalid') from exc
        usage = data.get('usage') or {}
        return Decision(selected, self.name, self.version, (time.perf_counter()-start)*1000,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint,
                        probability_event='Strands routing choice among eligible tiers',
                        probabilities=probabilities,
                        usage={k:v for k,v in usage.items() if k in {'input_tokens','output_tokens'} and isinstance(v,int)},
                        question_version=self.question_version,
                        decision_model=f'{self.checkpoint}@{self.device}', raw_value=selected)
