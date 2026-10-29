"""Portable trained DistilBERT fallback; never fabricates missing predictions."""
import asyncio
import time
from pathlib import Path

from .artifact import ArtifactError, inspect, reload_model
from .contracts import Decision, RoutingError, RoutingRequest, TIERS


class DistilBertRouter:
    name = 'distilbert'
    version = '1'

    def __init__(self, path: Path, settings, *, device: str = 'cpu'):
        if device not in {'cpu', 'mps'}:
            raise ValueError('supported Mac devices are cpu and mps')
        self.path = path
        self.device = device
        if not settings.router_training_fingerprint:
            raise ArtifactError('expected generation settings fingerprint is required')
        self.metadata = inspect(path, settings_fingerprint=settings.router_training_fingerprint,
                                backend_models={tier: settings.backend(tier).model for tier in TIERS})
        try:
            self.model, self.tokenizer = reload_model(path, device=device)
        except (OSError, RuntimeError, ImportError) as exc:
            raise ArtifactError('trained router could not be loaded on selected device') from exc

    def _predict(self, text: str) -> dict[str, float]:
        import torch
        encoded = self.tokenizer(text, truncation=True, padding='max_length',
                                 max_length=self.metadata['max_length'], return_tensors='pt').to(self.device)
        with torch.inference_mode():
            logits = self.model(**encoded).logits
            values = torch.softmax(logits, dim=-1)[0].cpu().tolist()
        return dict(zip(TIERS, values))

    async def decide(self, request: RoutingRequest) -> Decision:
        start = time.perf_counter()
        try:
            probabilities = await asyncio.to_thread(self._predict, request.text)
        except Exception as exc:
            raise RoutingError('trained router inference failed') from exc
        eligible = [tier for tier in TIERS if tier in request.eligible_tiers]
        if not eligible:
            raise RoutingError('no eligible tier for trained router')
        tier = max(eligible, key=lambda candidate: probabilities[candidate])
        return Decision(tier, self.name, self.version, (time.perf_counter()-start)*1000,
                        request_id=request.request_id, settings_fingerprint=request.settings_fingerprint,
                        probability_event='oracle-derived cheapest successful tier label',
                        probabilities=probabilities)
