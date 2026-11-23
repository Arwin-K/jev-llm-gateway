"""Configured automatic policy and explicit trained fallback construction."""
import json
from pathlib import Path

from .artifact import ArtifactError
from .baselines import FixedRouter, SeededRandomRouter
from .distilbert import DistilBertRouter
from .jev_choice import JevChoiceRouter, LayaChoiceRouter
from .jev_client import JevClient
from .jev_threshold import JevThresholdRouter, LayaThresholdRouter
from .prompted import PromptedRouter
from .strands import StrandsRouter


def build(settings, transport):
    policy = settings.router_policy
    if policy in {'always-small','always-medium','always-frontier'}:
        return FixedRouter(policy.removeprefix('always-')), []
    if policy == 'seeded-random':
        return SeededRandomRouter(settings.router_seed), []
    if policy == 'prompted-small':
        return PromptedRouter(settings, transport), []
    if policy == 'distilbert':
        return DistilBertRouter(Path(settings.router_artifact), settings), []
    if policy in {'jev-choice','jev-threshold','laya-choice','laya-threshold'}:
        if policy.startswith('laya-') and settings.decision_provider != 'laya':
            raise ValueError('Laya routing policy requires JEV_DECISION_PROVIDER=laya')
        if policy.startswith('jev-') and settings.decision_provider != 'jev':
            raise ValueError('hosted Jev routing policy requires JEV_DECISION_PROVIDER=jev')
        client = JevClient(settings)
        if policy == 'jev-choice':
            return JevChoiceRouter(settings, client), [client]
        if policy == 'laya-choice':
            return LayaChoiceRouter(settings, client), [client]
        if not settings.router_thresholds:
            raise ArtifactError('validation threshold selection file required')
        selection = json.loads(Path(settings.router_thresholds).read_text())
        if (not selection.get('selected') or not selection.get('objective') or
            selection['selected'].get('execution') != 'offline_replay'):
            raise ArtifactError('no documented validation operating point')
        threshold_router = LayaThresholdRouter if policy == 'laya-threshold' else JevThresholdRouter
        return threshold_router(settings, client, selection['selected']['thresholds'],
                                  selection_id=str(settings.router_thresholds)), [client]
    if policy == 'strands-decider':
        router = StrandsRouter(settings, url=settings.strands_url, model=settings.strands_model,
                               checkpoint=settings.strands_checkpoint, device=settings.strands_device)
        return router, [router]
    raise ValueError('unknown automatic routing policy')


def fallback(settings):
    if not settings.router_artifact:
        return None
    try:
        return DistilBertRouter(Path(settings.router_artifact), settings)
    except ArtifactError:
        return None
