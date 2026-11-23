"""Typed System One decision client with local-Laya and hosted-Jev backends.

Contract: https://api.typesafe.ai/openapi.json (checked 2026-10-29).
"""
import asyncio
import json
import os
import time
from dataclasses import dataclass

import httpx

from jev_gateway.config import Settings
from .contracts import RoutingError
from .breaker import JevCircuitBreaker, JevUnavailable


@dataclass(frozen=True)
class JevReply:
    model: str
    answers: dict
    usage: dict[str, int]
    duration_ms: float


class JevClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.client = httpx.AsyncClient(base_url=settings.decision_url,
                                        timeout=settings.timeout_seconds, transport=transport)
        self.lock = asyncio.Lock()
        self.requests = 0
        self.tokens = 0
        self.usd = 0.0
        self.breaker = JevCircuitBreaker(settings.jev_breaker_failures,
                                         settings.jev_breaker_cooldown_seconds)

    async def close(self):
        await self.client.aclose()

    @staticmethod
    def _laya_questions(questions):
        normalized = {}
        for name, question in questions.items():
            item = dict(question)
            if item.get('type') == 'noul' and not item.get('criteria'):
                statement = item.get('instructions', 'the statement')
                item['criteria'] = {
                    'true': f'The following statement is true: {statement}',
                    'false': f'The following statement is false: {statement}',
                }
                item['labels'] = {'true': 'A', 'false': 'B'}
            normalized[name] = item
        return normalized

    async def decide(self, state: str | dict, questions: dict, *, deadline_seconds: float | None = None) -> JevReply:
        if not self.settings.decision_enabled:
            raise RoutingError('decision backend disabled: model, loopback service, and positive request/token caps required')
        if not questions or len(questions) > 3 or any(q.get('type') not in {'choice','noul','score'} for q in questions.values()):
            raise RoutingError('invalid or excessive Jev questions')
        timeout = min(self.settings.timeout_seconds, self.settings.timeout_seconds if deadline_seconds is None else deadline_seconds)
        if timeout <= 0:
            raise RoutingError('Jev decision deadline expired')
        if self.settings.decision_provider == 'laya':
            questions = self._laya_questions(questions)
        body = {'model': self.settings.jev_model, 'state': state, 'questions': questions}
        # Conservative pre-admission reservation. Actual billing may differ.
        input_units = 4*len(json.dumps(body, ensure_ascii=False))
        reserved_tokens = input_units + self.settings.jev_decision_output_tokens
        reserved_usd = 0.0
        if self.settings.decision_provider == 'jev':
            reserved_usd = (input_units*self.settings.jev_input_usd_per_million +
                            self.settings.jev_decision_output_tokens*self.settings.jev_output_usd_per_million)/1_000_000
        start = time.perf_counter()
        try:
            async def send():
                async with self.lock:
                    if (self.requests+1 > self.settings.jev_max_requests or
                        self.tokens+reserved_tokens > self.settings.jev_max_tokens or
                        (self.settings.decision_provider == 'jev' and
                         self.usd+reserved_usd > self.settings.jev_max_usd)):
                        raise RoutingError('decision backend exceeds configured process budget')
                    self.requests += 1
                    self.tokens += reserved_tokens
                    self.usd += reserved_usd
                headers = {}
                if self.settings.decision_provider == 'jev':
                    headers['authorization'] = f'Bearer {os.environ["TYPESAFE_API_KEY"]}'
                response = await self.client.post('/v1/systemone', json=body, timeout=timeout,
                                                  headers=headers)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data.get('answers'), dict) or set(data['answers']) != set(questions):
                    raise ValueError('answer keys do not match questions')
                return data

            data = await self.breaker.call(send)
            usage = data.get('usage') or {}
            return JevReply(str(data['model']), data['answers'],
                            {k:v for k,v in usage.items() if k in {'input_tokens','output_tokens'} and isinstance(v,int)},
                            (time.perf_counter()-start)*1000)
        except (httpx.HTTPError, ValueError, KeyError, TypeError, JevUnavailable) as exc:
            raise RoutingError('Jev decision request failed or returned invalid data') from exc
