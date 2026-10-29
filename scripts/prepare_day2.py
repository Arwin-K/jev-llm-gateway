"""Explicit pinned source download and frozen manifest preparation."""
import json
from pathlib import Path
from jev_gateway.evaluation.datasets import fetch_parquet, fetch_mbpp, GSM_REV, MMLU_REV
from jev_gateway.evaluation.manifest import build, save

sources = Path('data/day2_sources')
print('gsm8k', fetch_parquet('openai/gsm8k', GSM_REV, 'main/train-00000-of-00001.parquet', sources/'gsm8k-train.jsonl'), flush=True)
print('mmlu', fetch_parquet('cais/mmlu', MMLU_REV, 'all/test-00000-of-00001.parquet', sources/'mmlu-test.jsonl'), flush=True)
print('mbpp', fetch_mbpp(sources/'mbpp-sanitized.jsonl'), flush=True)
prompts = build(sources)
save(prompts, Path('runs/day2-manifest.jsonl'))
summary = [{'prompt_id':p.prompt_id,'task':p.task,'split':p.split,'group_id':p.group_id,'dataset_revision':p.dataset_revision,'template_fingerprint':p.template_fingerprint} for p in prompts]
Path('docs/day2-manifest-index.jsonl').write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in summary))
print('manifest', len(prompts), flush=True)
