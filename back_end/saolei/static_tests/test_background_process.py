import os
from pathlib import Path
import shutil
import subprocess

import pytest


LAUNCHER = Path(__file__).resolve().parents[1] / 'run_background.sh'
SHELL_SHIMS = Path(__file__).resolve().parent / 'fixtures/background_process.sh'


@pytest.fixture
def bash_path():
    if os.name == 'nt':
        git = shutil.which('git')
        bash = Path(git).resolve().parents[1] / 'bin/bash.exe' if git else None
        if bash and bash.is_file():
            return str(bash)
        pytest.skip('Git Bash is required for shell launcher tests on Windows.')
    bash = shutil.which('bash')
    if not bash:
        pytest.skip('Bash is required for shell launcher tests.')
    return bash


def run_launcher(bash_path, mode, service='apscheduler'):
    env = os.environ.copy()
    env['BACKGROUND_TEST_MODE'] = mode
    return subprocess.run(
        [bash_path, SHELL_SHIMS.as_posix(), LAUNCHER.as_posix(), service],
        env=env, capture_output=True, text=True, timeout=10,
    )


@pytest.mark.parametrize('service,command', [
    ('apscheduler', 'runapscheduler'),
    ('db-worker', 'db_worker_robust'),
])
def test_background_service_normal_exit(bash_path, service, command):
    result = run_launcher(bash_path, 'success', service)
    assert result.returncode == 0, result.stderr
    assert f'<-u> <-X> <faulthandler> <manage.py> <{command}>' in result.stdout
    assert 'exit_status=0 signal=none' in result.stdout
    assert 'launcher_pid=' in result.stdout
    assert ' started' in result.stdout
    if service == 'db-worker':
        assert '<--interval> <2.5>' in result.stdout


def test_background_service_records_nonzero_exit(bash_path):
    result = run_launcher(bash_path, 'failure')
    assert result.returncode == 7
    assert 'exit_status=7 signal=none' in result.stdout


def test_background_service_records_killed_child(bash_path):
    result = run_launcher(bash_path, 'killed')
    assert result.returncode == 137
    assert 'exit_status=137 signal=KILL' in result.stdout


def test_background_service_survives_hangup(bash_path):
    result = run_launcher(bash_path, 'hangup')
    assert result.returncode == 0, result.stderr
    assert 'survived_hangup' in result.stdout
    assert 'exit_status=0 signal=none' in result.stdout
