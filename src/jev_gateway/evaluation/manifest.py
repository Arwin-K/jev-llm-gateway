"""Frozen grouped development split. Official source splits remain recorded separately."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .datasets import TEMPLATE_VERSION, gsm8k, mmlu, mbpp, read_jsonl
from .records import Prompt

SEED = 'jev-day2-2026-10-28-v1'
TARGETS = {'math': 1100, 'choice': 1000, 'code': 400}


def _rank(value):
    return hashlib.sha256((SEED + ':' + value).encode()).hexdigest()


def _group(prompt):
    # Exact normalized text groups superficial whitespace/case variants.
    text = re.sub(r'\s+', ' ', prompt.prompt).casefold().strip()
    return prompt.task + ':' + hashlib.sha256(text.encode()).hexdigest()


def _pools(source_dir: Path, version):
    return {
        'math': [gsm8k(row, row['source_index'], version=version) for row in read_jsonl(source_dir / 'gsm8k-train.jsonl')],
        'choice': [mmlu(row, row['source_index'], version=version) for row in read_jsonl(source_dir / 'mmlu-test.jsonl')],
        'code': [mbpp(row, version=version) for row in read_jsonl(source_dir / 'mbpp-sanitized.jsonl')],
    }


def build(source_dir: Path, version=TEMPLATE_VERSION):
    """Select and split on v1 text, then render the requested template.

    Deduplication, selection and split assignment always use the v1 rendering, so a template
    revision can change prompt wording but never which prompts are sampled or their split.
    Group IDs therefore keep their v1 values across template versions.
    """
    pools = _pools(source_dir, 'v1')
    rendered = {p.prompt_id: p for task in _pools(source_dir, version).values() for p in task} if version != 'v1' else None
    output = []
    for task, prompts in pools.items():
        groups = defaultdict(list)
        for prompt in prompts:
            groups[_group(prompt)].append(prompt)
        unique = [sorted(group, key=lambda p: p.prompt_id)[0] for group in groups.values()]
        if len(unique) < TARGETS[task]:
            raise ValueError(f'{task}: insufficient distinct source rows')
        selected = sorted(unique, key=lambda p: _rank(p.group_id))[:TARGETS[task]]
        for i, prompt in enumerate(selected):
            n = TARGETS[task]
            split = 'train' if i < n * 0.6 else 'validation' if i < n * 0.8 else 'test'
            chosen = rendered[prompt.prompt_id] if rendered else prompt
            output.append(chosen.model_copy(update={'split': split, 'group_id': _group(prompt)}))
    validate(output)
    return sorted(output, key=lambda p: p.prompt_id)


def validate(prompts):
    ids = [p.prompt_id for p in prompts]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate prompt ID')
    groups = defaultdict(set)
    for prompt in prompts:
        groups[prompt.group_id].add(prompt.split)
    if any(len(splits) != 1 for splits in groups.values()):
        raise ValueError('related prompts cross splits')
    counts = Counter((p.task, p.split) for p in prompts)
    for task, n in TARGETS.items():
        if sum(counts[task, split] for split in ('train', 'validation', 'test')) != n:
            raise ValueError(f'{task}: wrong count')
        if [counts[task, split] for split in ('train','validation','test')] != [int(.6*n), int(.2*n), int(.2*n)]:
            raise ValueError(f'{task}: wrong split ratio')


def save(prompts, path: Path):
    validate(prompts)
    path.parent.mkdir(parents=True, exist_ok=True)
    content=''.join(p.model_dump_json() + '\n' for p in prompts)
    if path.exists():
        if path.read_text()!=content: raise FileExistsError('frozen manifest differs')
        return
    path.write_text(content)


def same_assignment(previous, current):
    """Template revisions must not move any prompt between splits or change the selected IDs."""
    before = {p.prompt_id: p.split for p in previous}
    after = {p.prompt_id: p.split for p in current}
    if before != after:
        moved = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
        raise ValueError(f'split assignment changed for {len(moved)} prompts, e.g. {moved[:3]}')


def load_all(path: Path):
    """Every split, for integrity checks only; never use this to read test prompts for development."""
    return [Prompt.model_validate_json(line) for line in path.read_text().splitlines()]


def load(path: Path, split='validation', allow_test=False):
    if split == 'test' and not allow_test:
        raise PermissionError('held-out test is locked until final configuration freeze')
    if split not in ('train', 'validation', 'test'):
        raise ValueError('explicit split required')
    return [p for p in (Prompt.model_validate_json(line) for line in path.read_text().splitlines()) if p.split == split]
