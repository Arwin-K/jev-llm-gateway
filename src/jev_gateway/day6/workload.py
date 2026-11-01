"""Public synthetic prompts for serving experiments, never quality-test prompts."""

import argparse
import random
from pathlib import Path

from .common import write_new

LENGTHS = (32, 64, 128, 256)
WORDS = ('amber', 'river', 'stone', 'forest', 'orbit', 'copper', 'paper', 'garden')


def make(seed: int = 23, count: int = 32) -> dict:
    if count <= 0:
        raise ValueError('count must be positive')
    rng = random.Random(seed)
    prompts = []
    for index in range(count):
        target = LENGTHS[index % len(LENGTHS)]
        words = [rng.choice(WORDS) for _ in range(target)]
        prompts.append({'id': f'synthetic-{index:04d}', 'target_input_words': target,
                        'prompt': 'Summarize these arbitrary words in one sentence: ' + ' '.join(words)})
    return {'schema': 'jev.day6.workload.v1', 'origin': 'synthetic', 'seed': seed,
            'length_unit': 'whitespace_words', 'prompt_count': count,
            'prompts': prompts}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--count', type=int, default=32)
    parser.add_argument('--seed', type=int, default=23)
    args = parser.parse_args(argv)
    write_new(args.output, make(args.seed, args.count))


if __name__ == '__main__':
    main()
