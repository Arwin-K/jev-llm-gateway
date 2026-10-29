"""Explicit source download and frozen manifest preparation; never runs on normal tests."""
import json
from pathlib import Path
from jev_gateway.evaluation.datasets import fetch_hf, fetch_mbpp
from jev_gateway.evaluation.manifest import build, save

sources = Path('data/day2_sources')
print('gsm8k', fetch_hf('openai/gsm8k', '740312add88f781978c0658806c59bc2815b9866', 'main', 'train', sources/'gsm8k-train.jsonl'), flush=True)
print('mmlu', fetch_hf('cais/mmlu', 'c30699e8356da336a370243923dbaf21066bb9fe', 'all', 'test', sources/'mmlu-test.jsonl'), flush=True)
print('mbpp', fetch_mbpp(sources/'mbpp-sanitized.jsonl'), flush=True)
prompts = build(sources)
save(prompts, Path('runs/day2-manifest.jsonl'))
summary = [{'prompt_id':p.prompt_id,'task':p.task,'split':p.split,'group_id':p.group_id,'dataset_revision':p.dataset_revision,'template_fingerprint':p.template_fingerprint} for p in prompts]
Path('docs/day2-manifest-index.jsonl').write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in summary))
print('manifest', len(prompts), flush=True)
