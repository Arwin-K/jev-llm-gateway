"""Validated, immutable observations. Null means unknown, never zero."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Outcome(StrEnum):
    CORRECT = 'correct'
    INCORRECT = 'incorrect'
    PARSE_ERROR = 'parse_error'
    BACKEND_ERROR = 'backend_error'
    EVALUATOR_ERROR = 'evaluator_error'
    BLOCKED = 'blocked'


class Prompt(BaseModel):
    model_config = ConfigDict(frozen=True)
    prompt_id: str
    task: str
    split: str
    dataset: str
    dataset_revision: str
    source_split: str
    source_id: str
    source_revision: str
    group_id: str
    template_fingerprint: str
    prompt: str
    reference: Any = None
    tests: tuple[str, ...] = ()
    test_imports: tuple[str, ...] = ()
    answer_provenance: str | None = None


class Attempt(BaseModel):
    model_config = ConfigDict(frozen=True)
    started_at: datetime
    ended_at: datetime
    outcome: str
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    charge_usd: float | None = Field(default=None, ge=0)
    cost_status: str = 'unknown'

    @model_validator(mode='after')
    def ordered(self):
        if self.ended_at < self.started_at:
            raise ValueError('attempt ends before it starts')
        return self


class Result(BaseModel):
    model_config = ConfigDict(frozen=True)
    run_id: str
    prompt_id: str
    task: str
    split: str
    dataset_revision: str
    source_revision: str
    template_fingerprint: str
    settings_fingerprint: str
    tier: str
    backend: str
    model: str
    model_revision: str | None = None
    raw_response: str | None = None
    raw_reference: str | None = None
    parsed_answer: str | None = None
    score: float | None = Field(default=None, ge=0, le=1)
    outcome: Outcome
    error_category: str | None = None
    started_at: datetime
    ended_at: datetime
    first_visible_at: datetime | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    cost_status: str = 'unknown'
    charge_usd: float | None = Field(default=None, ge=0)
    execution: str = 'real'
    reuse_of: str | None = None
    attempts: tuple[Attempt, ...] = ()

    @model_validator(mode='after')
    def consistent(self):
        if not self.run_id or not self.prompt_id or not self.model:
            raise ValueError('run, prompt and model IDs are required')
        if self.ended_at < self.started_at or (self.first_visible_at and not self.started_at <= self.first_visible_at <= self.ended_at):
            raise ValueError('invalid timing boundaries')
        if self.raw_response is None and self.raw_reference is None and self.outcome not in {Outcome.BACKEND_ERROR, Outcome.BLOCKED}:
            raise ValueError('response or reference required')
        if self.execution not in {'real', 'mocked'}:
            raise ValueError('execution must be real or mocked')
        if self.outcome == Outcome.CORRECT and self.score != 1 or self.outcome == Outcome.INCORRECT and self.score != 0:
            raise ValueError('scored outcomes require exact score')
        return self
