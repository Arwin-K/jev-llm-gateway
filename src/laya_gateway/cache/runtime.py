"""Construct the optional local cache only from explicit pinned configuration."""
from pathlib import Path

from .embedding import MODEL, MiniLMEncoder
from .index import FaissAnswerIndex
from .lifecycle import CacheLifecycle
from .retrieval import CacheRetriever


def build_cache(settings):
    if not settings.cache_path or not settings.cache_embedding_revision:
        return None
    if settings.cache_similarity_threshold is None:
        raise ValueError('cache similarity threshold and source required')
    encoder=MiniLMEncoder(revision=settings.cache_embedding_revision)
    identity=f'{MODEL}@{settings.cache_embedding_revision}'
    index=FaissAnswerIndex(Path(settings.cache_path),dimension=encoder.dimension,
                           embedding_identity=identity)
    retriever=CacheRetriever(index,encoder,threshold=settings.cache_similarity_threshold,
                             threshold_source=settings.cache_similarity_threshold_source)
    return encoder,index,retriever,CacheLifecycle(index)
