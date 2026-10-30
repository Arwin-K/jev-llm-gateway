from datetime import datetime, timedelta, timezone
from jev_gateway.cache.scope import CacheEntry, eligible, make_scope


def scope(messages=None, **kwargs):
    return make_scope(messages or ({'role':'system','content':'Be brief'},
        {'role':'user','content':'What is 2+2?'}),namespace=kwargs.get('namespace','local'),
        embedding_identity='minilm@rev',policy_identity='jev-choice@1',
        model_identity='small=a;medium=b',max_output_tokens=32,temperature=0)


def test_scope_excludes_query_but_includes_instructions_and_context():
    base=scope()
    paraphrase=scope(({'role':'system','content':'Be brief'},
                      {'role':'user','content':'Compute two plus two.'}))
    changed=scope(({'role':'system','content':'Use French'},
                   {'role':'user','content':'What is 2+2?'}))
    assert base.fingerprint==paraphrase.fingerprint
    assert base.fingerprint!=changed.fingerprint
    assert base.fingerprint!=scope(namespace='other').fingerprint


def test_entry_expiry_and_verified_status():
    base=scope(); now=datetime.now(timezone.utc)
    entry=CacheEntry('e',base.fingerprint,'2+2?','4',now.isoformat(),
                     (now+timedelta(hours=1)).isoformat(),'small','m','accepted',True,
                     base.embedding_identity)
    assert eligible(entry,base,now=now)
    assert not eligible(CacheEntry(**(entry.__dict__|{'verified':False})),base,now=now)
    assert not eligible(CacheEntry(**(entry.__dict__|{'expires_at':(now-timedelta(seconds=1)).isoformat()})),base,now=now)
