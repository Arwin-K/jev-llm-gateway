from datetime import datetime, timezone
from jev_gateway.evaluation.records import Prompt, Result
from jev_gateway.routing.training_data import prepare_training

NOW = datetime.now(timezone.utc)


def prompt(split='train'):
    return Prompt(prompt_id='p', task='math', split=split, dataset='x', dataset_revision='d',
                  source_split='train', source_id='1', source_revision='s', group_id='g',
                  template_fingerprint='t', prompt='What is 2+2?')


def result(tier, outcome='correct', split='train', charge=1):
    return Result(run_id='r', prompt_id='p', task='math', split=split, dataset_revision='d',
                  source_revision='s', template_fingerprint='t', settings_fingerprint='config',
                  tier=tier, backend=tier, model=tier+'-model', raw_response='4', score=1 if outcome=='correct' else None,
                  outcome=outcome, started_at=NOW, ended_at=NOW, charge_usd=charge)


def test_only_complete_real_training_rows_receive_labels():
    rows, report = prepare_training([prompt()], [result('small'), result('medium'), result('frontier')])
    assert rows[0].label == 'small'
    assert report['label_counts'] == {'small': 1}
    assert rows[0].backend_models['frontier'] == 'frontier-model'
    rows, report = prepare_training([prompt()], [result('small'), result('medium')])
    assert not rows and report['statuses']['incomplete'] == 1


def test_validation_cannot_enter_training():
    try:
        prepare_training([prompt('validation')], [result('small', split='validation')])
    except PermissionError:
        pass
    else:
        raise AssertionError('validation entered training')
