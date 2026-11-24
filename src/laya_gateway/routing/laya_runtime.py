"""In-process Laya decision runtime; no decision HTTP service is used."""
from __future__ import annotations

import asyncio
import json
import threading
import time
from dataclasses import dataclass

from .contracts import RoutingError


@dataclass(frozen=True)
class DecisionReply:
    model: str
    answers: dict
    usage: dict[str, int]
    duration_ms: float


class LayaRuntime:
    """Own one lazily initialized Laya Router and run predictions off the event loop."""

    def __init__(self, settings, router=None):
        self.settings = settings
        self._router = router
        self._init_lock = threading.Lock()
        self._budget_lock = asyncio.Lock()
        self.requests = 0
        self.input_units = 0

    @staticmethod
    def _laya_questions(questions):
        normalized = {}
        for name, question in questions.items():
            item = dict(question)
            if item.get("type") == "noul" and not item.get("criteria"):
                statement = item.get("instructions", "the statement")
                item["criteria"] = {
                    "true": f"The following statement is true: {statement}",
                    "false": f"The following statement is false: {statement}",
                }
                item["labels"] = {"true": "A", "false": "B"}
            normalized[name] = item
        return normalized

    def _get_router(self):
        if self._router is not None:
            return self._router
        with self._init_lock:
            if self._router is None:
                try:
                    from laya import PINNED_REVISIONS, Router
                except ImportError as exc:
                    raise RoutingError("Laya is not installed; install the native Laya extra") from exc
                model = self.settings.laya_model
                revision = self.settings.laya_revision
                if revision == "reviewed":
                    revision = PINNED_REVISIONS["convaiinnovations/laya"]
                router = Router(
                    models={model: ("convaiinnovations/laya", "typed-decisions")},
                    device=self.settings.laya_device,
                    revisions={model: revision},
                    default=model,
                    max_loaded=1,
                    preload=False,
                    vega=False,
                )
                # Router's default registry also contains English and multilingual models.
                # Load only the explicitly selected checkpoint so native startup does not
                # download and hold three model families unnecessarily.
                router.load(model)
                self._router = router
        return self._router

    async def initialize(self):
        """Download/load the pinned checkpoint before an interactive request begins."""
        await asyncio.to_thread(self._get_router)

    async def decide(self, state: str | dict, questions: dict, *, deadline_seconds: float | None = None) -> DecisionReply:
        if not self.settings.decision_enabled:
            raise RoutingError("native Laya decision runtime is disabled or its request/token caps are missing")
        if (not questions or len(questions) > 3 or
                any(q.get("type") not in {"choice", "noul", "score"} for q in questions.values())):
            raise RoutingError("invalid or excessive Laya questions")
        timeout = self.settings.timeout_seconds if deadline_seconds is None else min(
            self.settings.timeout_seconds, deadline_seconds)
        if timeout <= 0:
            raise RoutingError("Laya decision deadline expired")

        normalized = self._laya_questions(questions)
        input_units = len(json.dumps({"state": state, "questions": normalized}, ensure_ascii=False))
        async with self._budget_lock:
            if (self.requests + 1 > self.settings.laya_max_requests or
                    self.input_units + input_units > self.settings.laya_max_input_units):
                raise RoutingError("native Laya exceeds configured process request/input cap")
            self.requests += 1
            self.input_units += input_units

        started = time.perf_counter()
        try:
            # Model initialization can include a first checkpoint download. It is deliberately
            # kept outside the per-decision deadline and belongs to CLI startup, not request work.
            router = await asyncio.to_thread(self._get_router)
            result = await asyncio.wait_for(
                asyncio.to_thread(router.predict, state, normalized, model=self.settings.laya_model),
                timeout=max(0.001, timeout - (time.perf_counter() - started)),
            )
            answers = result.get("answers")
            if not isinstance(answers, dict) or set(answers) != set(questions):
                raise ValueError("Laya answer keys do not match questions")
            usage = result.get("usage") or {}
            selected_model = (result.get("routing") or {}).get("model", self.settings.laya_model)
            return DecisionReply(
                str(selected_model), answers,
                {key: value for key, value in usage.items()
                 if key in {"input_tokens", "output_tokens"} and isinstance(value, int)},
                (time.perf_counter() - started) * 1000,
            )
        except asyncio.TimeoutError as exc:
            raise RoutingError("native Laya decision timed out") from exc
        except RoutingError:
            raise
        except (ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:
            raise RoutingError("native Laya decision failed or returned invalid data") from exc

    def close(self):
        """Release any loaded checkpoint owned by the runtime."""
        router, self._router = self._router, None
        if router is None:
            return
        for name in tuple(getattr(router, "loaded", ())):
            router.unload(name)
