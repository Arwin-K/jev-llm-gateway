"""Docker-only untrusted code executor. Containers reduce risk, not a security guarantee."""
import subprocess
import tempfile
import uuid
from pathlib import Path

IMAGE = 'python:3.12.7-slim-bookworm'


def _remove_container(name: str) -> None:
    """Best-effort cleanup after the foreground Docker client times out."""
    try:
        subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        # Preserve the evaluation timeout as the primary outcome. Docker may
        # have exited or become unavailable at the same time as the run.
        pass


def execute(code: str, tests: tuple[str, ...], imports: tuple[str, ...] = (), timeout: int = 8, runner=subprocess.run):
    if not 1 <= timeout <= 30:
        raise ValueError('timeout must be 1..30 seconds')
    name = 'jev-eval-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='jev-code-') as tmp:
        Path(tmp).chmod(0o755)  # nonroot container must traverse the temporary bind mount
        path = Path(tmp) / 'case.py'
        path.write_text(code + '\n' + '\n'.join(imports) + '\n' + '\n'.join(tests) + '\n')
        path.chmod(0o644)
        cmd = ['docker', 'run', '--rm', '--name', name, '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--memory', '256m', '--cpus', '1', '--pids-limit', '64', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m', '--mount', f'type=bind,src={tmp},dst=/work,readonly', '--workdir', '/work', IMAGE, 'python', '-B', 'case.py']
        try:
            result = runner(cmd, capture_output=True, text=True, timeout=timeout + 3)
        except subprocess.TimeoutExpired:
            _remove_container(name)
            return {'status': 'timeout', 'exit_code': None}
        except (OSError, subprocess.SubprocessError):
            return {'status': 'environment_error', 'exit_code': None}
    stderr = (result.stderr or '')[:1000]
    if result.returncode == 0:
        status = 'passed'
    elif 'AssertionError' in stderr:
        status = 'failed_tests'
    elif 'Traceback' in stderr or 'SyntaxError:' in stderr:
        status = 'crashed'
    else:
        status = 'environment_error'
    return {'status': status, 'exit_code': result.returncode}
