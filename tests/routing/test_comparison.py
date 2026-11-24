from laya_gateway.routing.comparison import Selection, baselines, compare, write_frontier_svg
from laya_gateway.evaluation.records import Prompt


def prompt(split='validation'):
    return Prompt(prompt_id='p', task='math', split=split, dataset='x', dataset_revision='d',
                  source_split='train', source_id='1', source_revision='s', group_id='g',
                  template_fingerprint='t', prompt='What is 2+2?')


def test_offline_replay_preserves_missing_coverage(tmp_path):
    p=prompt('validation')
    selections=[Selection('p','always-small','small')]
    reports=compare([p],[],selections)
    assert reports[0]['missing_result']==1 and reports[0]['scored']==0
    assert reports[0]['total_charge_usd'] is None
    write_frontier_svg(reports,tmp_path/'plot.svg')
    assert 'Validation offline replay' in (tmp_path/'plot.svg').read_text()


def test_seeded_baseline_order_is_stable():
    p=prompt('validation')
    assert baselines([p],seed=8)==baselines([p],seed=8)


def test_saved_decision_replaces_generated_baseline_once():
    from laya_gateway.routing.comparison import merge_selections
    generated=[Selection('p','always-small','small',0.)]
    saved={'status':'selected','selection':{'prompt_id':'p','policy':'always-small','tier':'small',
           'decision_charge_usd':0.,'decision_duration_ms':.1,'execution':'deterministic_local'}}
    merged=merge_selections(generated,[saved])
    assert len(merged)==1 and merged[0].decision_duration_ms==.1


def test_parse_errors_reduce_completion_rate_but_not_binary_accuracy_denominator():
    from types import SimpleNamespace

    p = prompt('validation')
    result = SimpleNamespace(prompt_id='p', tier='small', split='validation',
                             execution='real', outcome='parse_error', charge_usd=None)
    report = compare([p], [result], [Selection('p', 'always-small', 'small')])[0]
    assert report['classified_result'] == 1
    assert report['scored'] == 0
    assert report['parse_errors'] == 1
    assert report['scored_accuracy'] is None
    assert report['correct_completion_rate'] == 0
