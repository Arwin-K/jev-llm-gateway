import asyncio
from datetime import datetime, timedelta, timezone
from jev_gateway.cache.check import JevCacheChecker
from jev_gateway.cache.retrieval import Candidate
from jev_gateway.cache.scope import CacheEntry, make_scope
from jev_gateway.routing.jev_client import JevReply


class Client:
    def __init__(self): self.calls=0
    async def decide(self,state,questions,*,deadline_seconds=None):
        self.calls+=1
        assert state['candidate_answer']=='4'
        return JevReply('jev-1.13.0',{'applies':{'type':'noul','noul':.95}},
                        {'input_tokens':10,'output_tokens':2},3.)


def test_scope_checked_before_private_candidate_sent_to_jev():
    now=datetime.now(timezone.utc)
    scope=make_scope(({'role':'user','content':'two plus two?'},),namespace='local',
                     embedding_identity='e@r',policy_identity='p',model_identity='m',
                     max_output_tokens=16,temperature=0)
    entry=CacheEntry('e',scope.fingerprint,'2+2?','4',now.isoformat(),
                     (now+timedelta(hours=1)).isoformat(),'small','m','accepted',True,'e@r')
    candidate=Candidate(entry,.94,.9,'validation-a')
    client=Client(); checker=JevCacheChecker(client,threshold=.9,threshold_source='validation-a')
    accepted=asyncio.run(checker.check(candidate,({'role':'user','content':'two plus two?'},),scope))
    assert accepted.outcome=='accepted' and client.calls==1
    other=make_scope(({'role':'user','content':'two plus two?'},),namespace='other',
                     embedding_identity='e@r',policy_identity='p',model_identity='m',
                     max_output_tokens=16,temperature=0)
    rejected=asyncio.run(checker.check(candidate,({'role':'user','content':'two plus two?'},),other))
    assert rejected.outcome=='rejected' and client.calls==1
