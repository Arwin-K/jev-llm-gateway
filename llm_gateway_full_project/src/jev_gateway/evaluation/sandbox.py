"""Docker-only untrusted code executor. Containers reduce risk, not a security guarantee."""
import subprocess
import tempfile
import uuid
from pathlib import Path

IMAGE = 'python:3.12.7-slim-bookworm'


def execute(code: str, tests: tuple[str, ...], imports: tuple[str, ...] = (), timeout: int = 8, runner=subprocess.run):
    if not 1 <= timeout <= 30:
        raise ValueError('timeout must be 1..30 seconds')
    name = 'jev-eval-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='jev-code-') as tmp:
        path = Path(tmp) / 'case.py'
        path.write_text(code + '\n' + '\n'.join(imports) + '\n' + '\n'.join(tests) + '\n')
        cmd = ['docker', 'run', '--rm', '--name', name, '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--memory', '256m', '--cpus', '1', '--pids-limit', '64', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m', '--mount', f'type=bind,src={tmp},dst=/work,readonly', '--workdir', '/work', IMAGE, 'python', '-B', 'case.py']
        try:
            result = runner(cmd, capture_output=True, text=True, timeout=timeout + 3)
        except subprocess.TimeoutExpired:
            subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=5)
            return {'status': 'timeout', 'exit_code': None}
        except (OSError, subprocess.SubprocessError):
            return {'status': 'environment_error', 'exit_code': None}
    stderr = (result.stderr or '')[:1000]
    if result.returncode == 0:
        status = 'passed'
    elif 'AssertionError' in stderr:
        status = 'failed_tests'
    elif 'Traceback' in stderr:
        status = 'crashed'
    else:
        status = 'environment_error'
    return {'status': status, 'exit_code': result.returncode}
