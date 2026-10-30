import asyncio
import pytest
from jev_gateway.cache.embedding import MiniLMEncoder, EmbeddingUnavailable


class FakeModel:
    max_seq_length=256
    def get_sentence_embedding_dimension(self): return 384
    def encode(self,text,**kwargs):
        assert kwargs['normalize_embeddings'] is True
        return [1.]+[0.]*383


def test_pinned_adapter_validates_normalized_shape():
    encoder=MiniLMEncoder(revision='abc123',model_factory=lambda *a,**k:FakeModel())
    embedding=asyncio.run(encoder.encode('a request'))
    assert len(embedding.vector)==384 and embedding.vector[0]==1
    assert embedding.normalization=='l2_unit'


def test_unpinned_or_missing_model_rejected():
    with pytest.raises(ValueError): MiniLMEncoder(revision='main')
    with pytest.raises(EmbeddingUnavailable):
        MiniLMEncoder(revision='abc123',model_factory=lambda *a,**k:(_ for _ in ()).throw(OSError()))
