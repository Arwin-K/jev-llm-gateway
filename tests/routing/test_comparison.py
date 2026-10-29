from jev_gateway.routing.comparison import Selection, baselines, compare, write_frontier_svg
from jev_gateway.evaluation.records import Prompt


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
