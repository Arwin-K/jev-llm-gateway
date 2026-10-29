"""Adapters for source rows. Acquisition is explicit and revision checked."""
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

from .records import Prompt

GSM_REV = '740312add88f781978c0658806c59bc2815b9866'
MMLU_REV = 'c30699e8356da336a370243923dbaf21066bb9fe'
MBPP_REV = '1ae1fded5c616deb6b4652818588577e8fca0f06'
TEMPLATES = {'math': 'gsm8k-zero-shot-v1', 'choice': 'mmlu-zero-shot-v1', 'code': 'mbpp-zero-shot-no-tests-v1'}


def fingerprint(s):
    return hashlib.sha256(s.encode()).hexdigest()


def gsm8k(row, index, source_split='train'):
    answer = row['answer'].rsplit('####', 1)
    if len(answer) != 2 or not answer[1].strip():
        raise ValueError('GSM8K final answer marker missing')
    question = row['question'].strip()
    return Prompt(prompt_id=f'gsm8k:{source_split}:{index}', task='math', split='unassigned', dataset='openai/gsm8k/main', dataset_revision=GSM_REV, source_revision=GSM_REV, source_split=source_split, source_id=str(index), group_id='gsm8k:'+fingerprint(question.casefold()), template_fingerprint=fingerprint(TEMPLATES['math']), prompt=f'Solve the problem. End with Answer: <number>.\n\n{question}', reference=answer[1].strip(), answer_provenance='answer field after final #### marker')


def mmlu(row, index, source_split='test'):
    choices = row['choices']
    answer = row['answer']
    if len(choices) != 4 or not isinstance(answer, int) or not 0 <= answer < 4:
        raise ValueError('MMLU requires four ordered choices and answer index 0..3')
    question = row['question'].strip()
    subject = row['subject']
    options = '\n'.join(f'{letter}. {choice}' for letter, choice in zip('ABCD', choices))
    prompt = f'Choose the best answer. Reply with Answer: A, B, C, or D.\nSubject: {subject}\nQuestion: {question}\n{options}'
    return Prompt(prompt_id=f'mmlu:{source_split}:{subject}:{index}', task='choice', split='unassigned', dataset='cais/mmlu/all', dataset_revision=MMLU_REV, source_revision=MMLU_REV, source_split=source_split, source_id=str(index), group_id='mmlu:'+fingerprint(question.casefold()), template_fingerprint=fingerprint(TEMPLATES['choice']), prompt=prompt, reference='ABCD'[answer], answer_provenance='zero-based answer index mapped to unchanged A-D choice order')


def mbpp(row):
    task_id = int(row['task_id'])
    description = row['prompt'].strip()
    tests = tuple(row['test_list'])
    if not tests:
        raise ValueError('MBPP task has no tests')
    return Prompt(prompt_id=f'mbpp:{task_id}', task='code', split='unassigned', dataset='google-research/mbpp/sanitized', dataset_revision=MBPP_REV, source_revision=MBPP_REV, source_split='sanitized', source_id=str(task_id), group_id='mbpp:'+str(task_id), template_fingerprint=fingerprint(TEMPLATES['code']), prompt=f'Write Python code for this task. Return code only.\n\n{description}', reference=None, tests=tests, test_imports=tuple(row.get('test_imports', ())), answer_provenance='sanitized-mbpp.json test_list; reference solution excluded')


def _json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'jev-gateway-evaluation/0.1'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def fetch_hf(dataset, revision, config, split, output: Path):
    """Download a source snapshot; refuse HEAD drift and incomplete pages."""
    head = _json('https://huggingface.co/api/datasets/' + dataset)['sha']
    if head != revision:
        raise RuntimeError(f'{dataset} HEAD moved; update and review pinned adapter revision')
    rows = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(dict(dataset=dataset, config=config, split=split, offset=offset, length=100))
        page = _json('https://datasets-server.huggingface.co/rows?' + query)
        if page.get('partial') or not page['rows'] and offset < page['num_rows_total']:
            raise RuntimeError('incomplete dataset page')
        rows.extend({'source_index': item['row_idx'], **item['row']} for item in page['rows'])
        offset = len(rows)
        if offset >= page['num_rows_total']:
            break
    if _json('https://huggingface.co/api/datasets/' + dataset)['sha'] != revision:
        raise RuntimeError('source revision moved during fetch')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    return len(rows)


def fetch_mbpp(output: Path):
    url = f'https://raw.githubusercontent.com/google-research/google-research/{MBPP_REV}/mbpp/sanitized-mbpp.json'
    rows = _json(url)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    return len(rows)


def read_jsonl(path):
    with open(path) as stream:
        for line in stream:
            yield json.loads(line)
