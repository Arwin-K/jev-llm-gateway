"""Record the actual execution host; missing GPU facts remain missing."""

import argparse
import importlib.metadata
import os
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .common import digest, write_new


def capture(source_archive: Path, model: str, model_revision: str, dtype: str, config: Path) -> dict:
    for path in (source_archive, config):
        if not path.is_file():
            raise FileNotFoundError(path)
    try:
        gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version,compute_cap',
                              '--format=csv,noheader'], capture_output=True, text=True, timeout=10)
        gpu_lines = gpu.stdout.strip().splitlines() if gpu.returncode == 0 else []
        gpu_error = gpu.stderr.strip() if gpu.returncode else None
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        gpu_lines, gpu_error = [], type(exc).__name__
    packages = {}
    for name in ('jev-gateway', 'vllm', 'torch', 'transformers'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        'schema': 'jev.day6.environment.v1', 'run_id': uuid.uuid4().hex,
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'host': platform.node(), 'platform': platform.platform(), 'python': sys.version,
        'gpu': gpu_lines, 'gpu_error': gpu_error, 'packages': packages,
        'source_archive_sha256': digest(source_archive), 'config_sha256': digest(config),
        'model': model, 'model_revision': model_revision, 'dtype': dtype,
        'cuda_visible_devices': os.getenv('CUDA_VISIBLE_DEVICES'),
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-archive', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--model', required=True)
    parser.add_argument('--model-revision', required=True)
    parser.add_argument('--dtype', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    write_new(args.output, capture(args.source_archive, args.model, args.model_revision, args.dtype, args.config))


if __name__ == '__main__':
    main()
