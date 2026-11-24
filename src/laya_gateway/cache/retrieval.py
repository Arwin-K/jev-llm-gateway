"""Scope-filtered cosine candidates; retrieval never accepts an answer."""
import asyncio
from dataclasses import dataclass
from datetime import datetime

from .scope import CacheEntry, CacheScope, eligible


@dataclass(frozen=True)
class Candidate:
    entry: CacheEntry
    cosine_similarity: float
    threshold: float
    threshold_source: str
    metric: str = 'cosine_via_normalized_inner_product'


class CacheRetriever:
    def __init__(self,index,encoder,*,threshold:float,threshold_source:str,max_candidates:int=5):
        if not -1 <= threshold <= 1 or not threshold_source or max_candidates<1:
            raise ValueError('cosine threshold, source, and positive candidate cap required')
        self.index=index
        self.encoder=encoder
        self.threshold=threshold
        self.threshold_source=threshold_source
        self.max_candidates=max_candidates

    async def lookup(self,question:str,scope:CacheScope,*,now:datetime|None=None,
                     allow_unverified:bool=False) -> list[Candidate]:
        if not self.index.entries:
            return []
        scoped=[CacheEntry(**raw) for raw in self.index.entries
                if eligible(CacheEntry(**raw),scope,now=now,allow_unverified=allow_unverified)]
        if not scoped:
            return []
        allowed={entry.entry_id for entry in scoped}
        embedding=await self.encoder.encode(question)
        if f'{embedding.model}@{embedding.revision}' != scope.embedding_identity:
            raise ValueError('query embedding identity differs from cache scope')
        matches=await asyncio.to_thread(self.index.search,embedding.vector,k=len(self.index.entries))
        candidates=[]
        for raw,similarity in matches:
            if raw['entry_id'] in allowed and similarity>=self.threshold:
                candidates.append(Candidate(CacheEntry(**raw),similarity,self.threshold,
                                            self.threshold_source))
                if len(candidates)>=self.max_candidates: break
        return candidates
