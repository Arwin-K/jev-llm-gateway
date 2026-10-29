import pytest
from jev_gateway.config import from_env
from jev_gateway.routing.artifact import ArtifactError
from jev_gateway.routing.distilbert import DistilBertRouter


def test_missing_trained_artifact_fails_closed(tmp_path):
    with pytest.raises(ArtifactError):
        DistilBertRouter(tmp_path, from_env())
