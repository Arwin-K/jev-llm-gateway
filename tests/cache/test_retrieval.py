import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from jev_gateway.cache.retrieval import CacheRetriever
from jev_gateway.cache.scope import CacheEntry, make_scope


class Index:
    def __init__(self,entries): self.entries=entries
    def search(self,vector,*,k): return [(self.entries[0],.93)]


class Encoder:
    async def encode(self,text):
        return SimpleNamespace(model='minilm',revision='rev',vector=(1.,0.))


def test_retrieval_is_candidate_only_and_scope_filtered():
    scope=make_scope(({'role':'user','content':'2+2?'},),namespace='local',
                     embedding_identity='minilm@rev',policy_identity='p',model_identity='m',
                     max_output_tokens=16,temperature=0)
    now=datetime.now(timezone.utc)
    entry=CacheEntry('one',scope.fingerprint,'2+2?','4',now.isoformat(),
                     (now+timedelta(hours=1)).isoformat(),'small','m','accepted',True,'minilm@rev')
    retriever=CacheRetriever(Index([entry.__dict__]),Encoder(),threshold=.9,threshold_source='validation-a')
    candidate=asyncio.run(retriever.lookup('two plus two?',scope))
    assert len(candidate)==1 and candidate[0].cosine_similarity==.93
    other=make_scope(({'role':'user','content':'2+2?'},),namespace='other',
                     embedding_identity='minilm@rev',policy_identity='p',model_identity='m',
                     max_output_tokens=16,temperature=0)
    assert asyncio.run(retriever.lookup('two plus two?',other))==[]
