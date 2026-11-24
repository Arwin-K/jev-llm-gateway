"""Optional pinned, normalized Mac embedding adapter."""
import asyncio
import math
import time
from dataclasses import dataclass

MODEL = 'sentence-transformers/all-MiniLM-L6-v2'


class EmbeddingUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class Embedding:
    vector: tuple[float, ...]
    model: str
    revision: str
    device: str
    normalization: str
    duration_ms: float


class MiniLMEncoder:
    def __init__(self, *, revision: str, device: str = 'cpu', local_files_only: bool = True,
                 model_factory=None):
        if not revision or revision in {'main','latest'}:
            raise ValueError('pin an immutable embedding model revision')
        if device not in {'cpu','mps'}:
            raise ValueError('Mac embedding device must be cpu or mps')
        self.revision=revision
        self.device=device
        self.semaphore=asyncio.Semaphore(1)
        started=time.perf_counter()
        try:
            if model_factory is None:
                from sentence_transformers import SentenceTransformer
                model_factory=SentenceTransformer
            self.model=model_factory(MODEL, revision=revision, device=device,
                                     local_files_only=local_files_only, trust_remote_code=False)
        except (ImportError,OSError,RuntimeError) as exc:
            raise EmbeddingUnavailable('pinned local embedding model unavailable') from exc
        self.initialization_ms=(time.perf_counter()-started)*1000
        self.dimension=self.model.get_sentence_embedding_dimension()
        self.max_seq_length=self.model.max_seq_length
        if self.dimension != 384 or not 1 <= self.max_seq_length <= 512:
            raise EmbeddingUnavailable('embedding model dimension or preprocessing incompatible')

    def _encode(self,text):
        started=time.perf_counter()
        vector=self.model.encode(text, normalize_embeddings=True,convert_to_numpy=True,
                                 precision='float32')
        values=tuple(float(x) for x in vector)
        norm=math.sqrt(sum(x*x for x in values))
        if len(values)!=384 or not all(math.isfinite(x) for x in values) or abs(norm-1)>1e-3:
            raise EmbeddingUnavailable('embedding output is not a finite unit vector')
        return Embedding(values,MODEL,self.revision,self.device,'l2_unit',
                         (time.perf_counter()-started)*1000)

    async def encode(self,text: str) -> Embedding:
        if not text.strip():
            raise ValueError('empty text cannot be embedded')
        async with self.semaphore:
            return await asyncio.to_thread(self._encode,text)
