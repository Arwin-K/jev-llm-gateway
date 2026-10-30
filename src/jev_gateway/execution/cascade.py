"""Finite buffered generation → verification → escalation sequence."""
import asyncio
import time
from dataclasses import dataclass, field
from typing import Protocol

from jev_gateway.routing.contracts import TIERS
from .acceptance import AcceptancePolicy, Assessment
from .verifier import VerificationDecision, VerificationRequest


class Generator(Protocol):
    async def generate(self, tier: str, messages: tuple[dict[str, str], ...],
                       max_output_tokens: int, temperature: float | None,
                       deadline_seconds: float) -> dict: ...


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str
    messages: tuple[dict[str, str], ...]
    max_output_tokens: int
    temperature: float | None
    eligible_tiers: tuple[str, ...]
    deadline_at: float


@dataclass
class GenerationAttempt:
    tier: str
    model: str
    outcome: str
    duration_ms: float
    response: dict | None = None
    answer: str | None = None
    usage: dict = field(default_factory=dict)
    verification: VerificationDecision | None = None
    assessment: Assessment | None = None
    error_category: str | None = None


@dataclass
class CascadeResult:
    status: str
    accepted_tier: str | None
    response: dict | None
    attempts: list[GenerationAttempt]


class CascadeEngine:
    def __init__(self, generator: Generator, verifier, acceptance: AcceptancePolicy, models: dict[str, str]):
        self.generator = generator
        self.verifier = verifier
        self.acceptance = acceptance
        self.models = models

    async def run(self, request: ExecutionRequest, *, start_tier: str = 'small') -> CascadeResult:
        if start_tier not in TIERS:
            raise ValueError('unknown cascade start tier')
        attempts = []
        for tier in TIERS[TIERS.index(start_tier):]:
            if tier not in request.eligible_tiers:
                attempts.append(GenerationAttempt(tier,self.models[tier],'skipped',0.,error_category='ineligible'))
                continue
            remaining = request.deadline_at-time.monotonic()
            if remaining <= 0:
                return CascadeResult('deadline_exceeded',None,None,attempts)
            began = time.perf_counter()
            try:
                response = await asyncio.wait_for(
                    self.generator.generate(tier,request.messages,request.max_output_tokens,
                                            request.temperature,remaining),timeout=remaining)
                answer = response['choices'][0]['message']['content']
                if not isinstance(answer,str) or not answer.strip():
                    raise ValueError('empty or malformed generation')
                attempt = GenerationAttempt(tier,self.models[tier],'generated',
                                            (time.perf_counter()-began)*1000,response,answer,
                                            response.get('usage') or {})
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                attempts.append(GenerationAttempt(tier,self.models[tier],'generation_error',
                                                  (time.perf_counter()-began)*1000,
                                                  error_category=type(exc).__name__))
                # A backend error may warrant trying another eligible tier, within the same deadline.
                continue
            attempts.append(attempt)
            remaining = request.deadline_at-time.monotonic()
            if remaining <= 0:
                attempt.outcome='deadline_exceeded'
                return CascadeResult('deadline_exceeded',None,None,attempts)
            verification_request = VerificationRequest(request.request_id,request.messages,answer,
                                                        tier,self.models[tier])
            try:
                judgment = await asyncio.wait_for(self.verifier.judge(
                    verification_request,deadline_seconds=remaining),timeout=remaining)
                if judgment.answer_sha256 != verification_request.answer_sha256:
                    raise ValueError('verifier answer identity mismatch')
                attempt.verification = judgment
                assessment = self.acceptance.assess(judgment)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                assessment = self.acceptance.assess(None,error=type(exc).__name__)
            attempt.assessment = assessment
            if assessment.outcome in {'accepted_verified','unverified_allowed'}:
                attempt.outcome = assessment.outcome
                return CascadeResult(assessment.outcome,tier,response,attempts)
            if assessment.outcome == 'verification_failed':
                attempt.outcome='verification_failed'
                return CascadeResult('verification_failed',None,None,attempts)
            attempt.outcome='rejected'
        return CascadeResult('no_accepted_answer',None,None,attempts)
