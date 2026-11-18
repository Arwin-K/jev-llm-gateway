import subprocess
from jev_gateway.evaluation.sandbox import execute
from jev_gateway.evaluation import sandbox


def test_docker_command_is_bounded_and_no_host_fallback():
    calls = []
    def runner(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0, '', '')
    assert execute('def f(): return 2', ('assert f() == 2',), runner=runner)['status'] == 'passed'
    cmd, kwargs = calls[0]
    for flag in ['--network', 'none', '--read-only', '--cap-drop', 'ALL', '--user', '65534:65534', '--memory', '--pids-limit']:
        assert flag in cmd
    assert kwargs['timeout'] == 11


def test_unavailable_docker_is_environment_error():
    def missing(*args, **kwargs):
        raise FileNotFoundError('docker')
    assert execute('x=1', ('assert x == 1',), runner=missing)['status'] == 'environment_error'


def test_cleanup_timeout_does_not_replace_evaluation_timeout(monkeypatch):
    def cleanup(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])

    monkeypatch.setattr(sandbox.subprocess, 'run', cleanup)

    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])

    assert execute('x=1', ('assert x == 1',), runner=timed_out)['status'] == 'timeout'
