"""Generate an evidence-coverage SVG directly from immutable audit JSON."""

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from .common import digest, read_json


def coverage_svg(audit: Path) -> str:
    data = read_json(audit)
    if data.get('schema') != 'jev.day6.freeze_audit.v1':
        raise ValueError('expected freeze audit')
    observed = data['scored_observations']
    needed = data['required_scored_observations']
    rows = []
    for index, key in enumerate(sorted(needed)):
        y = 90 + index * 42
        count, total = observed[key], needed[key]
        if not 0 <= count <= total:
            raise ValueError('invalid coverage')
        width = 350 * count / total if total else 0
        rows.append(f'<text x="24" y="{y}" font-size="13">{escape(key)}</text>'
                    f'<rect x="170" y="{y-15}" width="350" height="19" fill="#e5e7eb"/>'
                    f'<rect x="170" y="{y-15}" width="{width:.1f}" height="19" fill="#2563eb"/>'
                    f'<text x="530" y="{y}" font-size="13">{count}/{total} scored</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="760" height="390" viewBox="0 0 760 390">'
            '<rect width="760" height="390" fill="white"/>'
            '<text x="24" y="33" font-size="18">Pre-freeze generation coverage</text>'
            '<text x="24" y="55" font-size="12">Unique scored prompts; real train/validation observations</text>'
            + ''.join(rows) + f'<text x="24" y="365" font-size="10">Input SHA-256: {digest(audit)}</text></svg>')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze-audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    with args.output.open('x') as stream:
        stream.write(coverage_svg(args.freeze_audit))


if __name__ == '__main__':
    main()
