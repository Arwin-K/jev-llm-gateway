"""Validation verifier errors against independently scored generated answers."""
import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from jev_gateway.evaluation.records import Result


@dataclass(frozen=True)
class VerificationRecord:
    prompt_id: str
    split: str
    tier: str
    generator_model: str
    settings_fingerprint: str
    answer_sha256: str
    probability: float | None
    error_category: str | None
    question_version: str
    verifier_model: str | None
    execution: str = 'real'


def measure(records: list[VerificationRecord], results: list[Result], *, threshold: float,
            config_id: str, expected: int | None = None) -> dict:
    if not config_id or not 0 <= threshold <= 1:
        raise ValueError('threshold and configuration identity required')
    if any(r.split!='validation' or r.execution!='real' for r in records):
        raise PermissionError('real validation verification records only')
    if expected is None: expected=len(records)
    if expected<len(records): raise ValueError('expected count below observed records')
    scored={(r.prompt_id,r.tier,r.model,r.settings_fingerprint):r for r in results
            if r.split=='validation' and r.execution=='real'}
    wrong=correct=wrong_accepted=correct_rejected=accepted_scored=judged=unmatched=failed=0
    for record in records:
        if record.error_category or record.probability is None:
            failed+=1
            continue
        if not 0 <= record.probability <= 1:
            failed+=1
            continue
        judged+=1
        result=scored.get((record.prompt_id,record.tier,record.generator_model,record.settings_fingerprint))
        if result is None or result.raw_response is None or \
           hashlib.sha256(result.raw_response.encode()).hexdigest()!=record.answer_sha256 or \
           result.outcome not in {'correct','incorrect','parse_error'}:
            unmatched+=1
            continue
        accepted=record.probability>=threshold
        if accepted: accepted_scored+=1
        if result.outcome=='correct':
            correct+=1
            correct_rejected+=not accepted
        else:
            wrong+=1
            wrong_accepted+=accepted
    return {'config_id':config_id,'threshold':threshold,'expected':expected,
            'records':len(records),'judged':judged,'execution_failures':failed,
            'unmatched_or_unscored':unmatched,'correct_evaluated':correct,
            'wrong_evaluated':wrong,'accepted_with_score':accepted_scored,
            'wrong_accepted':wrong_accepted,'correct_rejected':correct_rejected,
            'wrong_accept_rate_among_wrong':wrong_accepted/wrong if wrong else None,
            'correct_reject_rate_among_correct':correct_rejected/correct if correct else None,
            'wrong_fraction_among_accepted':wrong_accepted/accepted_scored if accepted_scored else None,
            'verification_coverage':judged/expected if expected else None,
            'execution':'validation_replay_of_real_judgments'}


def select_threshold(records, results, candidates, *, max_wrong_accept_rate: float,
                     min_coverage: float, config_prefix: str) -> dict:
    reports=[measure(records,results,threshold=value,
                     config_id=f'{config_prefix}:{value}') for value in candidates]
    feasible=[r for r in reports if r['wrong_accept_rate_among_wrong'] is not None and
              r['correct_reject_rate_among_correct'] is not None and
              r['wrong_accept_rate_among_wrong']<=max_wrong_accept_rate and
              (r['verification_coverage'] or 0)>=min_coverage]
    selected=min(feasible,key=lambda r:(r['correct_reject_rate_among_correct'],r['threshold'])) if feasible else None
    return {'candidates':reports,'selected':selected,
            'objective':{'max_wrong_accept_rate':max_wrong_accept_rate,
                         'min_coverage':min_coverage,'minimize':'correct_reject_rate_among_correct'}}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--judgments',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--threshold',type=float,required=True)
    parser.add_argument('--config-id',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('private report must stay under runs/')
    records=[VerificationRecord(**json.loads(line)) for line in args.judgments.read_text().splitlines() if line]
    results=[Result.model_validate_json(line) for line in args.run.read_text().splitlines() if line]
    report=measure(records,results,threshold=args.threshold,config_id=args.config_id)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out: out.write(json.dumps(report,indent=2))
    print(json.dumps({'path':str(args.output),'judged':report['judged'],'wrong_evaluated':report['wrong_evaluated']}))


if __name__=='__main__':
    main()
