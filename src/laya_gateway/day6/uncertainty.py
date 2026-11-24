"""Group-paired bootstrap for future policy differences on the same prompts."""

import random
import statistics


def paired_difference(left: dict[str, float], right: dict[str, float], *,
                      groups: dict[str, str], repetitions: int = 2000, seed: int = 23) -> dict:
    if set(left) != set(right) or set(left) != set(groups) or not left or repetitions < 100:
        raise ValueError('complete matched outcomes and groups required')
    by_group = {}
    for prompt_id in left:
        by_group.setdefault(groups[prompt_id], []).append(right[prompt_id]-left[prompt_id])
    if len(by_group) < 2:
        raise ValueError('at least two independent groups required')
    group_ids = sorted(by_group)
    rng = random.Random(seed)
    draws = []
    for _ in range(repetitions):
        selected = [rng.choice(group_ids) for _ in group_ids]
        values = [value for group_id in selected for value in by_group[group_id]]
        draws.append(statistics.mean(values))
    draws.sort()
    return {'method': 'paired group bootstrap', 'seed': seed, 'repetitions': repetitions,
            'prompt_count': len(left), 'group_count': len(by_group),
            'mean_right_minus_left': statistics.mean(right[key]-left[key] for key in left),
            'ci95': [draws[int(.025*repetitions)], draws[int(.975*repetitions)-1]]}
