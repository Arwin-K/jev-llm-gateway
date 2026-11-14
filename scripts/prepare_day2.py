"""Explicit pinned source download and frozen manifest preparation."""
import argparse
import json
from pathlib import Path
from jev_gateway.evaluation.datasets import fetch_parquet, fetch_mbpp, read_jsonl, GSM_REV, MMLU_REV
from jev_gateway.evaluation.manifest import build, load_all, same_assignment, save

# Row counts observed when the pinned snapshots were first downloaded (docs/DAY2_DATASETS.md).
EXPECTED_ROWS = {'gsm8k-train.jsonl': 7473, 'mmlu-test.jsonl': 14042, 'mbpp-sanitized.jsonl': 427}

parser = argparse.ArgumentParser()
parser.add_argument('--offline', action='store_true', help='rebuild from existing snapshots without downloading')
parser.add_argument('--previous', help='earlier manifest whose prompt IDs and splits must be unchanged')
args = parser.parse_args()

sources = Path('data/day2_sources')
if args.offline:
    for name, expected in EXPECTED_ROWS.items():
        found = sum(1 for _ in read_jsonl(sources/name))
        if found != expected:
            raise SystemExit(f'{name}: {found} rows, expected {expected}; download again without --offline')
        print(name, found, flush=True)
else:
    print('gsm8k', fetch_parquet('openai/gsm8k', GSM_REV, 'main/train-00000-of-00001.parquet', sources/'gsm8k-train.jsonl'), flush=True)
    print('mmlu', fetch_parquet('cais/mmlu', MMLU_REV, 'all/test-00000-of-00001.parquet', sources/'mmlu-test.jsonl'), flush=True)
    print('mbpp', fetch_mbpp(sources/'mbpp-sanitized.jsonl'), flush=True)
prompts = build(sources)
if args.previous:
    same_assignment(load_all(Path(args.previous)), prompts)
    print('split assignment unchanged from', args.previous, flush=True)
save(prompts, Path('runs/day2-manifest.jsonl'))
summary = [{'prompt_id':p.prompt_id,'task':p.task,'split':p.split,'group_id':p.group_id,'dataset_revision':p.dataset_revision,'template_fingerprint':p.template_fingerprint} for p in prompts]
Path('docs/day2-manifest-index.jsonl').write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in summary))
print('manifest', len(prompts), flush=True)
