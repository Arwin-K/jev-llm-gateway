import asyncio
from datetime import datetime,timedelta,timezone
from jev_gateway.cache.index import FaissAnswerIndex
from jev_gateway.cache.lifecycle import CacheLifecycle
from jev_gateway.cache.scope import CacheEntry
from test_index import FakeFaiss


def test_insert_expire_and_reset(tmp_path):
    now=datetime.now(timezone.utc)
    with FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='e@r',faiss_module=FakeFaiss()) as index:
        manager=CacheLifecycle(index,max_entries=1)
        entry=CacheEntry('e','scope','question','answer',now.isoformat(),
                         (now+timedelta(hours=1)).isoformat(),'small','m','accepted',True,'e@r')
        asyncio.run(manager.insert(entry,[1.,0.]))
        assert len(index.entries)==1
        asyncio.run(manager.invalidate(now=now+timedelta(hours=2)))
        assert index.entries==[]
        asyncio.run(manager.insert(entry,[1.,0.]))
        asyncio.run(manager.reset())
        assert index.entries==[]


def test_rejected_answer_cannot_be_inserted(tmp_path):
    now=datetime.now(timezone.utc)
    with FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='e@r',faiss_module=FakeFaiss()) as index:
        manager=CacheLifecycle(index)
        entry=CacheEntry('e','scope','q','bad',now.isoformat(),
                         (now+timedelta(hours=1)).isoformat(),'small','m','rejected',False,'e@r')
        try: asyncio.run(manager.insert(entry,[1.,0.]))
        except ValueError: pass
        else: raise AssertionError('rejected answer stored')
