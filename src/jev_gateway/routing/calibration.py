"""Calibration for explicitly labeled binary events and oracle-tier distributions."""
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from xml.sax.saxutils import escape

from .contracts import TIERS


@dataclass(frozen=True)
class BinaryObservation:
    probability: float
    occurred: bool
    event: str


def binary_report(samples: list[BinaryObservation], *, bins: int = 10,
                  expected: int | None = None) -> dict:
    if bins < 1 or expected is not None and expected < len(samples):
        raise ValueError('invalid bin or coverage count')
    events = {sample.event for sample in samples}
    if len(events) != 1 or not samples:
        raise ValueError('a nonempty report must use one defined event')
    if any(not isfinite(s.probability) or not 0 <= s.probability <= 1 for s in samples):
        raise ValueError('probabilities must be finite and in [0,1]')
    buckets = [[] for _ in range(bins)]
    for sample in samples:
        buckets[min(bins-1, int(sample.probability*bins))].append(sample)
    count = len(samples)
    rows = []
    ece = 0.
    for index, bucket in enumerate(buckets):
        n = len(bucket)
        confidence = sum(s.probability for s in bucket)/n if n else None
        observed = sum(s.occurred for s in bucket)/n if n else None
        if n:
            ece += n/count*abs(confidence-observed)
        rows.append({'lower':index/bins, 'upper':(index+1)/bins, 'count':n,
                     'mean_probability':confidence, 'event_rate':observed})
    return {'event':events.pop(), 'count':count, 'expected':expected,
            'missing':None if expected is None else expected-count,
            'binning':'equal width, [lower,upper), final bin closed',
            'bins':rows, 'ece':ece,
            'brier':sum((s.probability-int(s.occurred))**2 for s in samples)/count}


def oracle_label_report(predictions: list[tuple[dict[str,float], str]], *, bins: int = 10,
                        expected: int | None = None) -> dict:
    binary = []
    squared = []
    for probabilities, label in predictions:
        if (label not in TIERS or set(probabilities) != set(TIERS) or
            any(not isfinite(p) or not 0 <= p <= 1 for p in probabilities.values()) or
            abs(sum(probabilities.values())-1) > .02):
            raise ValueError('invalid oracle-label distribution')
        chosen = max(TIERS, key=lambda tier: probabilities[tier])
        binary.append(BinaryObservation(probabilities[chosen], chosen == label,
                                        'predicted tier equals oracle-derived tier label'))
        squared.append(sum((probabilities[t]-int(t==label))**2 for t in TIERS))
    report = binary_report(binary, bins=bins, expected=expected)
    report['multiclass_brier'] = sum(squared)/len(squared)
    report['multiclass_brier_definition'] = 'mean sum over three tier classes; range 0..2'
    return report


def write_reliability_svg(report: dict, path: Path):
    """Standalone reliability figure generated solely from the stored report."""
    rows = report['bins']
    title = escape(report['event'])
    points = ' '.join(f'{40+320*row["mean_probability"]:.1f},{360-320*row["event_rate"]:.1f}'
                      for row in rows if row['count'])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="430" viewBox="0 0 440 430">'
           f'<rect width="440" height="430" fill="white"/><text x="40" y="20" font-size="12">{title}</text>'
           f'<line x1="40" y1="360" x2="360" y2="40" stroke="#aaa" stroke-dasharray="4 4"/>'
           f'<line x1="40" y1="360" x2="360" y2="360" stroke="black"/>'
           f'<line x1="40" y1="360" x2="40" y2="40" stroke="black"/>'
           f'<polyline points="{points}" fill="none" stroke="#185abc" stroke-width="2"/>'
           f'<text x="160" y="395" font-size="12">Predicted probability</text>'
           f'<text x="42" y="418" font-size="11">n={report["count"]}; ECE={report["ece"]:.3f}; Brier={report["brier"]:.3f}</text>'
           '</svg>')
    path.write_text(svg)
