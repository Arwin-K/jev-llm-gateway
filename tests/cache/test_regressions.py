import asyncio
import json
from datetime import datetime,timedelta,timezone
import pytest
from jev_gateway.cache.check import JevCacheChecker
from jev_gateway.cache.index import FaissAnswerIndex, IndexUnavailable
from jev_gateway.cache.retrieval import Candidate
from jev_gateway.cache.scope import CacheEntry, make_scope
from test_index import FakeFaiss


def scope(messages,model='m',embedding='e@r'):
    return make_scope(messages,namespace='local',embedding_identity=embedding,
        policy_identity='p',model_identity=model,max_output_tokens=16,temperature=0)


def test_context_model_and_embedding_changes_isolate_candidates():
    original=scope(({'role':'user','content':'Earlier: Paris'},
                    {'role':'assistant','content':'Noted'},
                    {'role':'user','content':'What is its capital?'}))
    changed=scope(({'role':'user','content':'Earlier: Berlin'},
                   {'role':'assistant','content':'Noted'},
                   {'role':'user','content':'What is its capital?'}))
    assert original.fingerprint!=changed.fingerprint
    assert original.fingerprint!=scope(({'role':'user','content':'What is its capital?'},),model='new').fingerprint
    assert original.fingerprint!=scope(({'role':'user','content':'What is its capital?'},),embedding='e@new').fingerprint


def test_corrupt_persistence_fails_closed_and_releases_lock(tmp_path):
    with FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='e@r',faiss_module=FakeFaiss()) as index:
        index.save([{'entry_id':'one'}],[[1.,0.]])
    pointer=json.loads((tmp_path/'current.json').read_text())
    metadata=tmp_path/'versions'/pointer['generation']/'metadata.json'
    metadata.write_text(metadata.read_text()+'corrupt')
    with pytest.raises(IndexUnavailable):
        FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='e@r',faiss_module=FakeFaiss())
    # A failed load must not leave a process lock held.
    with pytest.raises(IndexUnavailable):
        FaissAnswerIndex(tmp_path,dimension=2,embedding_identity='e@r',faiss_module=FakeFaiss())


def test_verifier_failure_is_miss_not_reuse():
    now=datetime.now(timezone.utc); current=scope(({'role':'user','content':'2+2?'},))
    entry=CacheEntry('e',current.fingerprint,'2+2?','4',now.isoformat(),
        (now+timedelta(hours=1)).isoformat(),'small','m','accepted',True,'e@r')
    class Broken:
        async def decide(self,*args,**kwargs): raise TimeoutError()
    check=asyncio.run(JevCacheChecker(Broken(),threshold=.8,threshold_source='v').check(
        Candidate(entry,.95,.9,'v'),({'role':'user','content':'two plus two?'},),current))
    assert check.outcome=='miss' and check.probability is None
