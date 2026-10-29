import json
import pytest
from jev_gateway.routing.artifact import ArtifactError, inspect


def test_untrained_or_incomplete_artifact_rejected(tmp_path):
    with pytest.raises(ArtifactError):
        inspect(tmp_path)
    (tmp_path/'metadata.json').write_text(json.dumps({'artifact_kind': 'base_model'}))
    with pytest.raises(ArtifactError):
        inspect(tmp_path)
    (tmp_path/'metadata.json').write_text(json.dumps({
        'artifact_kind':'trained_distilbert', 'label2id':{'small':0,'medium':1,'frontier':2},
        'train_prompt_ids':['p'], 'validation_prompt_ids':['q'],
        'settings_fingerprint':'a', 'backend_models':{}}))
    with pytest.raises(ArtifactError):
        inspect(tmp_path, settings_fingerprint='b')
