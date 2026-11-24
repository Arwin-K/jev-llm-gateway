"""Accepted-answer-only cache insertion, expiry, eviction, and reset."""
import asyncio
from datetime import datetime, timezone
from .scope import CacheEntry


class CacheLifecycle:
    def __init__(self,index,*,max_entries:int=1000,allow_unverified_storage:bool=False):
        if max_entries<1: raise ValueError('positive cache size required')
        self.index=index
        self.max_entries=max_entries
        self.allow_unverified_storage=allow_unverified_storage
        self.lock=asyncio.Lock()

    def _pairs(self):
        pairs=[]
        for i,raw in enumerate(self.index.entries):
            vector=self.index.index.reconstruct(i)
            pairs.append((CacheEntry(**raw),vector.tolist() if hasattr(vector,'tolist') else list(vector)))
        return pairs

    async def insert(self,entry:CacheEntry,vector):
        try:
            expiry=datetime.fromisoformat(entry.expires_at)
        except ValueError as exc:
            raise ValueError('invalid entry expiry') from exc
        if (entry.acceptance!='accepted' or not entry.answer or
            entry.embedding_identity!=self.index.embedding_identity or expiry.tzinfo is None or
            expiry<=datetime.now(timezone.utc) or
            (not entry.verified and not self.allow_unverified_storage)):
            raise ValueError('only accepted eligible answers can be stored')
        async with self.lock:
            pairs=await asyncio.to_thread(self._pairs)
            pairs=[pair for pair in pairs if pair[0].entry_id!=entry.entry_id]
            pairs.append((entry,vector))
            pairs.sort(key=lambda pair:pair[0].created_at)
            pairs=pairs[-self.max_entries:]
            return await asyncio.to_thread(self.index.save,[e.__dict__ for e,_ in pairs],
                                           [v for _,v in pairs])

    async def invalidate(self,*,now:datetime|None=None,scope_fingerprint:str|None=None):
        current=now or datetime.now(timezone.utc)
        async with self.lock:
            pairs=await asyncio.to_thread(self._pairs)
            retained=[]
            for entry,vector in pairs:
                try: expiry=datetime.fromisoformat(entry.expires_at)
                except ValueError: expiry=current
                if expiry.tzinfo is None or expiry<=current or \
                   scope_fingerprint and entry.scope_fingerprint==scope_fingerprint:
                    continue
                retained.append((entry,vector))
            if len(retained)==len(pairs): return None
            return await asyncio.to_thread(self.index.save,[e.__dict__ for e,_ in retained],
                                           [v for _,v in retained])

    async def reset(self):
        async with self.lock:
            return await asyncio.to_thread(self.index.save,[],[])
