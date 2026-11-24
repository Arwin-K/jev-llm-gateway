import pytest
from laya_gateway.config import from_env
from laya_gateway.routing.artifact import ArtifactError
from laya_gateway.routing.distilbert import DistilBertRouter


def test_missing_trained_artifact_fails_closed(tmp_path):
    with pytest.raises(ArtifactError):
        DistilBertRouter(tmp_path, from_env())
