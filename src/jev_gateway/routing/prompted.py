"""Bounded prompted small-model comparison router."""
import json
import time

from .contracts import Decision, RoutingError, RoutingRequest, TIERS


class PromptedRouter:
    name = 'prompted-small'
    version = '1'

    def __init__(self, settings, transport):
        self.settings = settings
        self.transport = transport

    async def decide(self, request: RoutingRequest) -> Decision:
        start = time.perf_counter()
        if not request.eligible_tiers:
            raise RoutingError('no eligible generation tier')
        descriptions = {tier: {'model': self.settings.backend(tier).model,
                               'context_limit': self.settings.backend(tier).max_context_tokens}
                        for tier in request.eligible_tiers}
        instruction = ('Choose one eligible generation tier for the user request. '
                       'Return only compact JSON with exactly one key, tier. '
                       'Use the least capable tier likely to answer correctly. '
                       f'Eligible backends: {json.dumps(descriptions, sort_keys=True)}')
        payload = {'model': self.settings.small.model, 'stream': False, 'temperature': 0,
                   'max_tokens': 24, 'messages': [
                       {'role':'system','content':instruction},
                       {'role':'user','content':request.text}]}
        response = None
        try:
            response = await self.transport.complete(self.settings.small, payload)
            content = response['choices'][0]['message']['content']
            parsed = json.loads(content)
            if not isinstance(parsed, dict) or set(parsed) != {'tier'} or parsed['tier'] not in request.eligible_tiers:
                raise ValueError('invalid tier selection')
        except Exception as exc:
            usage = (response.get('usage') or {}) if isinstance(response, dict) else {}
            raise RoutingError('prompted router returned no valid eligible tier',
                               duration_ms=(time.perf_counter()-start)*1000,
                               usage={k:v for k,v in usage.items() if k in {'prompt_tokens','completion_tokens','total_tokens'} and isinstance(v,int)}) from exc
        usage = response.get('usage') or {}
        return Decision(parsed['tier'], self.name, self.version,
                        (time.perf_counter()-start)*1000,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint,
                        usage={k:v for k,v in usage.items() if k in {'prompt_tokens','completion_tokens','total_tokens'} and isinstance(v,int)})
