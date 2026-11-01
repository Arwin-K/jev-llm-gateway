"""Focused Nsight Systems collection around a separate diagnostic run."""

import argparse
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .common import digest, write_new


def collect(output_dir: Path, command: list[str], timeout: int) -> dict:
    if not command or timeout <= 0:
        raise ValueError('command and positive timeout required')
    if shutil.which('nsys') is None:
        raise RuntimeError('nsys unavailable; no profile artifact was collected')
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    stem = output_dir / f'nsys-{run_id}'
    invocation = ['nsys', 'profile', '--trace=cuda,nvtx', '--output', str(stem), '--force-overwrite=false', *command]
    completed = subprocess.run(invocation, capture_output=True, text=True, timeout=timeout)
    report = stem.with_suffix('.nsys-rep')
    return {'schema': 'jev.day6.profile.v1', 'run_id': run_id,
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
            'command': invocation, 'exit_code': completed.returncode,
            'stdout_tail': completed.stdout[-4000:], 'stderr_tail': completed.stderr[-4000:],
            'report_path': str(report) if report.exists() else None,
            'report_sha256': digest(report) if report.exists() else None,
            'diagnostic_only': True}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    result = collect(args.output_dir, command, args.timeout)
    write_new(args.output_dir / f"profile-{result['run_id']}.json", result)


if __name__ == '__main__':
    main()
