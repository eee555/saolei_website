from datetime import datetime, timezone
import logging
from pathlib import Path
import re
import sys
import time

import psutil

logger = logging.getLogger(__name__)
PROCESS_GROUPS = ('uwsgi', 'apscheduler', 'redis', 'mysql', 'db_worker', 'other')
COLLECTION_SECONDS = 5
MAX_PROCESSES = 5000


class CollectionError(Exception):
    def __init__(self, reason, unreadable_processes=0):
        super().__init__(reason, unreadable_processes)
        self.reason = reason
        self.unreadable_processes = unreadable_processes


def check_deadline(deadline):
    if time.monotonic() >= deadline:
        raise CollectionError('budget_exceeded')


def process_memory_metric():
    return 'pss' if sys.platform.startswith('linux') else 'rss'


def _is_containerized():
    if not sys.platform.startswith('linux'):
        return False
    if Path('/.dockerenv').exists() or Path('/run/.containerenv').exists():
        return True
    try:
        cgroup = Path('/proc/1/cgroup').read_text()
        return any(marker in cgroup for marker in ('docker', 'kubepods', 'lxc'))
    except OSError:
        return False


def _process_group(process, project_dir):
    info = process.info
    names = {Path(value).name.lower().removesuffix('.exe') for value in (info.get('name'), info.get('exe')) if value}
    if not names:
        raise psutil.AccessDenied(process.pid)
    if 'uwsgi' in names:
        return 'uwsgi'
    if 'redis-server' in names:
        return 'redis'
    if names & {'mysqld', 'mariadbd'}:
        return 'mysql'
    if not any(re.fullmatch(r'pythonw?(?:\d+(?:\.\d+)*)?', name) for name in names):
        return 'other'

    cmdline = info.get('cmdline')
    if cmdline is None:
        raise psutil.AccessDenied(process.pid)
    for index, arg in enumerate(cmdline[:-1]):
        if Path(arg).name != 'manage.py':
            continue
        manage_path = Path(arg)
        if not manage_path.is_absolute():
            manage_path = Path(process.cwd()) / manage_path
        if manage_path.resolve() != (Path(project_dir) / 'manage.py').resolve():
            return 'other'
        command = cmdline[index + 1]
        if command in {'runapscheduler', 'runapschedulermonitor', 'runapscheduleruserprofile', 'runapschedulervideomanager'}:
            return 'apscheduler'
        if command in {'db_worker', 'db_worker_robust'}:
            return 'db_worker'
    return 'other'


def collect_process_memory(project_dir, deadline):
    if _is_containerized():
        raise CollectionError('unsupported_scope')
    metric = process_memory_metric()
    groups = dict.fromkeys(PROCESS_GROUPS, 0)
    seen = set()
    unreadable = 0
    started = time.monotonic()
    host = psutil.virtual_memory()
    for process in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        check_deadline(deadline)
        if process.pid in seen:
            continue
        seen.add(process.pid)
        if len(seen) > MAX_PROCESSES:
            raise CollectionError('budget_exceeded')
        try:
            if metric == 'pss':
                memory = process.memory_full_info()
                if not hasattr(memory, 'pss'):
                    raise CollectionError('unsupported_metric')
                value = memory.pss
            else:
                value = process.memory_info().rss
            if value < 0:
                raise CollectionError('inconsistent_snapshot')
            if value:
                groups[_process_group(process, project_dir)] += value
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            unreadable += 1
    check_deadline(deadline)
    if unreadable:
        raise CollectionError('permission_denied', unreadable)
    logger.info('Process memory collected: metric=%s processes=%s elapsed=%.3fs', metric, len(seen), time.monotonic() - started)
    return {
        'status': 'ready', 'reason': None, 'sampled_at': datetime.now(timezone.utc),
        'metric': metric, 'total_bytes': sum(groups.values()), 'groups': groups,
        'host': {'total_bytes': host.total, 'available_bytes': host.available}, 'unreadable_processes': 0,
    }
