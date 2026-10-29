from datetime import datetime, timezone
import pytest
from jev_gateway.evaluation.checkpoint import Checkpoints, key
from jev_gateway.evaluation.datasets import gsm8k
from jev_gateway.evaluation.records import Result
from jev_gateway.config import from_env


def test_checkpoint_identity_and_partial_resume(tmp_path):
    p=gsm8k({'question':'1+1?','answer':'#### 2'},0).model_copy(update={'split':'train'})
    backend=from_env().small; k=key(p,'small',backend,'settings')
    now=datetime.now(timezone.utc)
    r=Result(run_id='original',prompt_id=p.prompt_id,task='math',split='train',dataset_revision=p.dataset_revision,source_revision=p.source_revision,template_fingerprint=p.template_fingerprint,settings_fingerprint='settings',tier='small',backend=backend.base_url,model=backend.model,raw_response='Answer: 2',parsed_answer='2',score=1,outcome='correct',started_at=now,ended_at=now)
    store=Checkpoints(tmp_path); (tmp_path/'.partial-dead').write_text('partial')
    assert store.get(k,backend.model) is None
    store.put(k,r)
    reused=store.get(k,backend.model)
    assert reused.run_id=='original' and reused.started_at==now and reused.reuse_of=='original'
    assert store.get(k,'different') is None
    assert key(p.model_copy(update={'prompt':'changed'}),'small',backend,'settings')!=k
    with pytest.raises(FileExistsError): store.put(k,r.model_copy(update={'score':0}))
