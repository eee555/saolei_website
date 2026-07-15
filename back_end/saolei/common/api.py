

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from django.core.cache import cache
from django.db.models import Sum
from django.http import FileResponse, Http404, StreamingHttpResponse
from django.utils import timezone as django_timezone
from django_tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult
from ninja import Router, Schema
from ninja.decorators import decorate_view
from ninja.throttling import AnonRateThrottle
import psutil

from common.utils import get_db_size
from config.common import TASK_CLEANUP_CONFIGS
from config.text_choices import MS_TextChoices
from userprofile.decorators import staff_required
from utils.db import get_choice_counts_filtered
from videomanager.models import VideoModel

router = Router()

LOG_DIR = Path('logs')
DEFAULT_TAIL_BYTES = 64 * 1024
MAX_TAIL_BYTES = 1024 * 1024
LOG_STREAM_POLL_INTERVAL = 1


class LogFileOut(Schema):
    name: str
    size: int
    mtime: datetime


class LogTailOut(Schema):
    content: str
    offset: int
    size: int
    truncated: bool


def _get_log_path(filename: str) -> Path:
    if Path(filename).name != filename:
        raise Http404()

    log_dir = LOG_DIR.resolve()
    log_path = (log_dir / filename).resolve()
    if log_path.parent != log_dir or not log_path.is_file():
        raise Http404()
    return log_path


def _clamp_tail_bytes(tail_bytes: int) -> int:
    return min(max(tail_bytes, 1), MAX_TAIL_BYTES)


def _read_from_offset(log_path: Path, offset: int) -> tuple[str, int]:
    with log_path.open('rb') as f:
        f.seek(offset)
        content = f.read()
        next_offset = f.tell()
    return content.decode('utf-8', errors='replace'), next_offset


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
        count, _ = (
            DBTaskResult.objects
            .filter(
                task_path=config['task_path'],
                status=TaskResultStatus.SUCCESSFUL,
                finished_at__lt=deadline,
            )
            .delete()
        )
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
            'mtime': datetime.fromtimestamp(file_stat.st_ctime, tz=timezone.utc),
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


@router.get('/staff/logstream')
@decorate_view(staff_required)
def stream_log_tail(request, filename: str, offset: int = 0, tail_bytes: int = DEFAULT_TAIL_BYTES):
    """
    - staff_required

    Stream appended log content as Server-Sent Events from the given byte offset.
    """
    log_path = _get_log_path(filename)
    clamped_tail_bytes = _clamp_tail_bytes(tail_bytes)

    def event_stream():
        current_offset = max(offset, 0)
        while True:
            try:
                file_size = log_path.stat().st_size
                if file_size < current_offset:
                    current_offset = max(file_size - clamped_tail_bytes, 0)
                    yield 'event: reset\ndata: {}\n\n'
                if file_size > current_offset:
                    content, current_offset = _read_from_offset(log_path, current_offset)
                    yield f'data: {json.dumps({"content": content, "offset": current_offset})}\n\n'
                else:
                    yield ': keep-alive\n\n'
            except FileNotFoundError:
                yield 'event: deleted\ndata: {}\n\n'
                return
            time.sleep(LOG_STREAM_POLL_INTERVAL)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


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
