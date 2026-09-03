
from datetime import datetime, timezone
import os
from pathlib import Path
import socket
from uuid import UUID

from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.db.models import Sum
from django.http import FileResponse
from django.tasks import TaskResultStatus
from django.utils import timezone as django_timezone
from django_tasks_db.models import DBTaskResult
from ninja import Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.orm import create_schema
from ninja.throttling import AnonRateThrottle
import psutil

from accountlink.services import restart_accountlink_task
from common.utils import get_db_size
from config.common import TASK_CLEANUP_CONFIGS
from config.text_choices import MS_TextChoices
from tournament.gsc.services import restart_gsc_task
from userprofile.decorators import staff_required
from utils.db import get_choice_counts_filtered
from videomanager.models import VideoModel

router = Router()

LOG_DIR = Path('logs')
DEFAULT_TAIL_BYTES = 64 * 1024
MAX_TAIL_BYTES = 1024 * 1024
TASK_CLEANUP_BATCH_SIZE = 200
RUNNING_TASK_STALE_AFTER_SECONDS = 60 * 60
WORKER_STARTED_TOLERANCE_SECONDS = 120
WORKER_STATE_ALIVE = 'alive'
WORKER_STATE_DEAD = 'dead'
WORKER_STATE_UNKNOWN = 'unknown'
TASK_RESTART_SERVICES = [
    restart_accountlink_task,
    restart_gsc_task,
]


class LogFileOut(Schema):
    name: str
    size: int
    mtime: datetime


class LogTailOut(Schema):
    content: str
    offset: int
    size: int
    truncated: bool


class LogPollOut(Schema):
    content: str
    offset: int
    size: int
    status: str


def _get_log_path(filename: str) -> Path:
    if Path(filename).name != filename:
        raise HttpError(404, 'Log file not found.')

    log_dir = LOG_DIR.resolve()
    log_path = (log_dir / filename).resolve()
    if log_path.parent != log_dir or not log_path.is_file():
        raise HttpError(404, 'Log file not found.')
    return log_path


def _clamp_tail_bytes(tail_bytes: int) -> int:
    return min(max(tail_bytes, 1), MAX_TAIL_BYTES)


def _read_from_offset(log_path: Path, offset: int) -> tuple[str, int]:
    with log_path.open('rb') as f:
        f.seek(offset)
        content = f.read()
        next_offset = f.tell()
    return content.decode('utf-8', errors='replace'), next_offset


def _raise_task_not_found_or_locked(task_id: UUID):
    if DBTaskResult.objects.filter(id=task_id).exists():
        raise HttpError(409, 'Task is locked.')
    raise HttpError(404, 'Task not found.')


class VideoSummaryOut(Schema):
    total: int
    software: dict[str, int]
    level: dict[str, int]
    mode: dict[str, int]
    state: dict[str, int]


@router.get('/videosummary', response=VideoSummaryOut, throttle=[AnonRateThrottle('30/m')])
def video_summary(request):
    """
    - Throttle: AnonRateThrottle('30/m')
    """
    if (cached_data := cache.get('api:common/videosummary')) is not None:
        return cached_data

    total = VideoModel.objects.count()
    software = get_choice_counts_filtered(VideoModel, 'software', MS_TextChoices.Software)
    level = get_choice_counts_filtered(VideoModel, 'level', MS_TextChoices.Level)
    mode = get_choice_counts_filtered(VideoModel, 'mode', MS_TextChoices.Mode)
    state = get_choice_counts_filtered(VideoModel, 'state', MS_TextChoices.State)

    result = {'total': total, 'software': software, 'level': level, 'mode': mode, 'state': state}
    cache.set('api:common/videosummary', result, 300)

    return result


class TaskSummaryOut(Schema):
    total: int
    status: dict[str, int]


TaskDetailOut = create_schema(
    DBTaskResult,
    fields=[
        'id', 'status',
        'enqueued_at', 'started_at', 'finished_at',
        'args_kwargs', 'priority', 'task_path',
        'worker_ids', 'queue_name', 'backend_name', 'run_after',
        'return_value', 'exception_class_path', 'traceback',
    ],
)


class RunningTaskHealthOut(Schema):
    id: str
    task_path: str
    started_at: datetime | None
    age_seconds: int | None
    worker_id: str | None
    worker_state: str
    stale_by_age: bool
    probably_orphaned: bool


class TaskIdIn(Schema):
    task_id: UUID


def _local_hostname_aliases() -> set[str]:
    hostname = socket.gethostname()
    aliases = {hostname, hostname.split('.')[0]}
    fqdn = socket.getfqdn()
    aliases.add(fqdn)
    aliases.add(fqdn.split('.')[0])
    return {alias for alias in aliases if alias}


def _inspect_worker_id(worker_id: str | None) -> str:
    if not worker_id:
        return WORKER_STATE_UNKNOWN

    try:
        worker_host, worker_pid, worker_started = worker_id.rsplit('-', 2)
    except ValueError:
        return WORKER_STATE_UNKNOWN

    if not worker_pid.isdigit() or not worker_started.isdigit():
        return WORKER_STATE_UNKNOWN
    if worker_host not in _local_hostname_aliases():
        return WORKER_STATE_UNKNOWN

    pid = int(worker_pid)
    started_at = int(worker_started)
    try:
        process = psutil.Process(pid)
        process_started_at = int(process.create_time())
    except psutil.NoSuchProcess:
        return WORKER_STATE_DEAD
    except psutil.Error:
        return WORKER_STATE_UNKNOWN

    if abs(process_started_at - started_at) > WORKER_STARTED_TOLERANCE_SECONDS:
        return WORKER_STATE_DEAD

    try:
        cmdline = ' '.join(process.cmdline())
    except psutil.Error:
        return WORKER_STATE_ALIVE

    if 'db_worker' not in cmdline:
        return WORKER_STATE_DEAD
    return WORKER_STATE_ALIVE


@router.get('/tasksummary', throttle=[AnonRateThrottle('30/m')])
def task_summary(request):
    """
    - Throttle: AnonRateThrottle('30/m')
    """
    if (cached_data := cache.get('api:common/tasksummary')) is not None:
        return cached_data

    total = DBTaskResult.objects.count()
    status = get_choice_counts_filtered(DBTaskResult, 'status', TaskResultStatus)

    result = {'total': total, 'status': status}
    cache.set('api:common/tasksummary', result, 300)

    return result


@router.get('/tasks/detail', response=list[TaskDetailOut])
@decorate_view(staff_required)
def task_detail(request):
    """
    - staff_required
    """
    return DBTaskResult.objects.all()


@router.get('/tasks/running/health', response=list[RunningTaskHealthOut])
@decorate_view(staff_required)
def running_task_health(request, stale_after_seconds: int = RUNNING_TASK_STALE_AFTER_SECONDS):
    now = django_timezone.now()
    result = []

    for task in DBTaskResult.objects.filter(status=TaskResultStatus.RUNNING).order_by('started_at'):
        worker_id = (task.worker_ids or [None])[-1]
        worker_state = _inspect_worker_id(worker_id)
        age_seconds = int((now - task.started_at).total_seconds()) if task.started_at else None
        stale_by_age = age_seconds is not None and age_seconds >= stale_after_seconds
        result.append({
            'id': str(task.id),
            'task_path': task.task_path,
            'started_at': task.started_at,
            'age_seconds': age_seconds,
            'worker_id': worker_id,
            'worker_state': worker_state,
            'stale_by_age': stale_by_age,
            'probably_orphaned': worker_state == WORKER_STATE_DEAD or (
                worker_state == WORKER_STATE_UNKNOWN and stale_by_age
            ),
        })

    return result


@router.post('/tasks/delete')
@decorate_view(staff_required)
def delete_task(request, data: TaskIdIn):
    """
    - staff_required
    """
    with transaction.atomic():
        db_task = (
            DBTaskResult.objects
            .select_for_update(skip_locked=True)
            .filter(id=data.task_id)
            .first()
        )
        if not db_task:
            _raise_task_not_found_or_locked(data.task_id)
        if db_task.status == TaskResultStatus.RUNNING:
            raise HttpError(409, 'Running task cannot be deleted.')
        db_task.delete()

    cache.delete('api:common/tasksummary')
    return


@router.post('/tasks/restart', response=TaskDetailOut)
@decorate_view(staff_required)
def restart_task(request, data: TaskIdIn):
    """
    - staff_required
    """
    try:
        with transaction.atomic():
            db_task = (
                DBTaskResult.objects
                .select_for_update(skip_locked=True)
                .filter(id=data.task_id)
                .first()
            )
            if not db_task:
                _raise_task_not_found_or_locked(data.task_id)
            if db_task.status != TaskResultStatus.FAILED:
                raise HttpError(409, 'Only failed task can be restarted.')

            args_kwargs = db_task.args_kwargs
            if not isinstance(args_kwargs, dict):
                raise HttpError(400, 'Invalid task arguments.')
            args = args_kwargs.get('args', [])
            kwargs = args_kwargs.get('kwargs', {})
            if not isinstance(args, list) or not isinstance(kwargs, dict):
                raise HttpError(400, 'Invalid task arguments.')

            new_db_task = None
            for restart_service in TASK_RESTART_SERVICES:
                new_db_task = restart_service(db_task, args, kwargs)
                if new_db_task is not None:
                    break
            if new_db_task is None:
                new_db_task = db_task.task.enqueue(*args, **kwargs).db_result
    except (ImportError, SuspiciousOperation, TypeError, ValueError):
        raise HttpError(400, 'Invalid task restart request.')

    cache.delete('api:common/tasksummary')
    return new_db_task


@router.post('/tasks/cleanup', response=int)
@decorate_view(staff_required)
def cleanup_tasks(request):
    """
    - staff_required
    """
    deleted_count = 0
    now = django_timezone.now()

    for config in TASK_CLEANUP_CONFIGS:
        deadline = now - config['expires']
        queryset = DBTaskResult.objects.filter(
            task_path=config['task_path'],
            status=TaskResultStatus.SUCCESSFUL,
            finished_at__lt=deadline,
        )

        with transaction.atomic():
            task_ids = list(
                queryset
                .select_for_update(skip_locked=True)
                .values_list('id', flat=True)[:TASK_CLEANUP_BATCH_SIZE],
            )
            count, _ = DBTaskResult.objects.filter(id__in=task_ids).delete()

        deleted_count += count

    return deleted_count


@router.get('/staff/logs', response=list[LogFileOut])
@decorate_view(staff_required)
def list_logs(request):
    """
    - staff_required
    """
    file_stats = []
    for file in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file)
        file_stat = os.stat(file_path)
        file_stats.append({
            'name': file,
            'size': file_stat.st_size,
            'mtime': datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc),
        })
    return file_stats


@router.get('/staff/logview')
@decorate_view(staff_required)
def download_log(request, filename: str):
    """
    - staff_required

    Download the full log file.
    """
    return FileResponse(_get_log_path(filename).open('rb'), content_type='text/plain')


@router.get('/staff/logtail', response=LogTailOut)
@decorate_view(staff_required)
def get_log_tail(request, filename: str, tail_bytes: int = DEFAULT_TAIL_BYTES):
    """
    - staff_required

    Return only the tail of the log file instead of loading the full file.
    """
    log_path = _get_log_path(filename)
    clamped_tail_bytes = _clamp_tail_bytes(tail_bytes)
    file_size = log_path.stat().st_size
    offset = max(file_size - clamped_tail_bytes, 0)
    content, next_offset = _read_from_offset(log_path, offset)
    return {
        'content': content,
        'offset': next_offset,
        'size': file_size,
        'truncated': offset > 0,
    }


@router.get('/staff/logpoll', response=LogPollOut)
@decorate_view(staff_required)
def poll_log_tail(request, filename: str, offset: int = 0, tail_bytes: int = DEFAULT_TAIL_BYTES):
    """
    - staff_required

    Return appended log content from the given byte offset without holding a long-lived connection.
    """
    if Path(filename).name != filename:
        raise HttpError(404, 'Log file not found.')

    log_dir = LOG_DIR.resolve()
    log_path = (log_dir / filename).resolve()
    if log_path.parent != log_dir:
        raise HttpError(404, 'Log file not found.')

    clamped_tail_bytes = _clamp_tail_bytes(tail_bytes)
    current_offset = max(offset, 0)
    try:
        file_size = log_path.stat().st_size
        if file_size < current_offset:
            current_offset = max(file_size - clamped_tail_bytes, 0)
            content, current_offset = _read_from_offset(log_path, current_offset)
            return {
                'content': content,
                'offset': current_offset,
                'size': file_size,
                'status': 'reset',
            }
        if file_size > current_offset:
            content, current_offset = _read_from_offset(log_path, current_offset)
            return {
                'content': content,
                'offset': current_offset,
                'size': file_size,
                'status': 'ok',
            }
        return {
            'content': '',
            'offset': current_offset,
            'size': file_size,
            'status': 'ok',
        }
    except FileNotFoundError:
        return {
            'content': '',
            'offset': 0,
            'size': 0,
            'status': 'deleted',
        }


@router.get('/diskusage', throttle=[AnonRateThrottle('30/m')])
def disk_usage(request):
    """
    - Throttle: AnonRateThrottle('30/m')
    """
    if (cached_data := cache.get('api:common/diskusage')) is not None:
        return cached_data

    disk = psutil.disk_usage('.')

    video_size: int = VideoModel.objects.aggregate(s=Sum('file_size'))['s']
    db_size = get_db_size()

    result = {'total': disk.total, 'used': disk.used, 'free': disk.free, 'video': video_size, 'db': db_size}
    cache.set('api:common/diskusage', result, 300)

    return result
