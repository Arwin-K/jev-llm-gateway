"""Private, human-readable scoring audit. Export is not human review."""
import csv
from collections import defaultdict
from pathlib import Path


def export(prompts, results, path: Path, per_task=40):
    if not 30 <= per_task <= 50:
        raise ValueError('audit sample size must be 30..50')
    by_prompt = {p.prompt_id:p for p in prompts if p.split in {'train','validation'}}
    rows = defaultdict(list)
    for result in results:
        prompt = by_prompt.get(result.prompt_id)
        if prompt:
            rows[prompt.task].append((prompt,result))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['review_status','task','prompt_id','tier','prompt','raw_answer','extracted_answer','reference','outcome','score','error_category'])
        for task in sorted(rows):
            for prompt,result in sorted(rows[task], key=lambda pair:(pair[0].prompt_id,pair[1].tier))[:per_task]:
                writer.writerow(['pending_human_review',task,prompt.prompt_id,result.tier,prompt.prompt,result.raw_response,result.parsed_answer,prompt.reference if prompt.reference is not None else '; '.join(prompt.tests),result.outcome,result.score,result.error_category])
    return {task:min(len(items),per_task) for task,items in rows.items()}
