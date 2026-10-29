from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from jev_gateway.evaluation.records import Result, Outcome


def test_immutable_record_preserves_unknowns():
    now = datetime.now(timezone.utc)
    fields = dict(run_id='r', prompt_id='p', task='math', split='train', dataset_revision='rev', source_revision='rev', template_fingerprint='t', settings_fingerprint='s', tier='small', backend='ollama', model='m', raw_response='bad', outcome=Outcome.PARSE_ERROR, started_at=now, ended_at=now)
    record = Result(**fields)
    assert record.score is None and record.prompt_tokens is None and record.charge_usd is None
    with pytest.raises(ValidationError):
        Result(**(fields | {'outcome': Outcome.CORRECT, 'score': 0}))
    with pytest.raises(ValidationError):
        record.score = 1
