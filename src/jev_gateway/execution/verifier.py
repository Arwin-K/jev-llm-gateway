"""Typed Jev judgment of one generated answer; not an accuracy label."""
import hashlib
from dataclasses import dataclass
from typing import Protocol

QUESTION_VERSION = 'answer-satisfies-request-v1'
EVENT = 'generated answer satisfies the request and applicable instructions'


class VerificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerificationRequest:
    request_id: str
    messages: tuple[dict[str, str], ...]
    answer: str
    tier: str
    generator_model: str

    @property
    def answer_sha256(self):
        return hashlib.sha256(self.answer.encode()).hexdigest()


@dataclass(frozen=True)
class VerificationDecision:
    request_id: str
    answer_sha256: str
    probability: float
    event: str
    question_version: str
    verifier_model: str
    duration_ms: float
    usage: dict[str, int]
    outcome: str = 'judged'


class Verifier(Protocol):
    async def judge(self, request: VerificationRequest, *, deadline_seconds: float | None = None) -> VerificationDecision: ...


class JevAnswerVerifier:
    question_version = QUESTION_VERSION

    def __init__(self, client):
        self.client = client

    async def judge(self, request: VerificationRequest, *, deadline_seconds: float | None = None) -> VerificationDecision:
        state = {'messages': request.messages, 'generated_answer': request.answer,
                 'generator_tier': request.tier, 'generator_model': request.generator_model,
                 'question_version': self.question_version}
        question = {'valid': {'type': 'noul',
                             'instructions': 'Does this particular generated answer satisfy the user request and all '
                                             'applicable system/developer instructions? Judge only the supplied answer. '
                                             'Do not assume it is correct because a model produced it.'}}
        try:
            reply = await self.client.decide(state, question, deadline_seconds=deadline_seconds)
            answer = reply.answers['valid']
            probability = answer['noul']
            if answer['type'] != 'noul' or not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
                raise ValueError('invalid Noul answer')
        except (KeyError, TypeError, ValueError, RuntimeError) as exc:
            raise VerificationError('answer verification unavailable or malformed') from exc
        return VerificationDecision(request.request_id, request.answer_sha256, float(probability),
                                    EVENT, self.question_version, reply.model,
                                    reply.duration_ms, reply.usage)
