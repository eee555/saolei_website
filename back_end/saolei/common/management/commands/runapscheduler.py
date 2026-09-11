import json
import os
from pathlib import Path
import time
from typing import Any

from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
import psutil

from common.apscheduler import logger, register_jobs

SCHEDULER_COMMANDS = {
    'runapscheduler',
    'runapschedulermonitor',
    'runapscheduleruserprofile',
    'runapschedulervideomanager',
}
PIDFILE_STARTED_TOLERANCE_SECONDS = 120


def _cmdline_runs_scheduler(cmdline: list[str]) -> bool:
    return any(Path(arg).name in SCHEDULER_COMMANDS for arg in cmdline)


def _process_matches_pidfile(pid: int, started_at: int) -> bool:
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False
    except psutil.Error:
        return True

    try:
        process_started_at = int(process.create_time())
    except psutil.Error:
        return True
    if abs(process_started_at - started_at) > PIDFILE_STARTED_TOLERANCE_SECONDS:
        return False

    try:
        return _cmdline_runs_scheduler(process.cmdline())
    except psutil.Error:
        return True


def _read_pidfile(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None


def acquire_pidfile(path: Path) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = int(time.time())
    content = json.dumps({
        'pid': os.getpid(),
        'started_at': now,
    })

    for _ in range(2):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            existing = _read_pidfile(path)
            if existing:
                try:
                    pid = int(existing.get('pid', 0))
                    started_at = int(existing.get('started_at', 0))
                except (TypeError, ValueError):
                    pid = 0
                    started_at = 0
                if _process_matches_pidfile(pid, started_at):
                    return False
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                return False
            continue

        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


def release_pidfile(path: Path):
    existing = _read_pidfile(path)
    if existing and existing.get('pid') != os.getpid():
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


class Command(BaseCommand):
    help = 'Runs all APScheduler jobs in one process.'
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--pidfile',
            default=None,
            help='Pidfile used to prevent duplicate APScheduler processes.',
        )

    def handle(self, *args, **options):
        pidfile = Path(options['pidfile']) if options['pidfile'] else settings.BASE_DIR / 'logs/apscheduler.pid'

        if not acquire_pidfile(pidfile):
            self.stdout.write(self.style.WARNING(
                f'Another APScheduler process appears to be running; pidfile={pidfile}.',
            ))
            return

        try:
            scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
            scheduler.add_jobstore(DjangoJobStore(), 'default')
            register_jobs(scheduler)

            try:
                logger.info('Starting scheduler...')
                scheduler.start()
            except KeyboardInterrupt:
                logger.info('Stopping scheduler...')
                scheduler.shutdown()
                logger.info('Scheduler shut down successfully!')
        finally:
            release_pidfile(pidfile)
