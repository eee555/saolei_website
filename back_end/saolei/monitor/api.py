from datetime import datetime
from typing import Literal

from django_ratelimit.decorators import ratelimit
from ninja import Router, Schema
from ninja.decorators import decorate_view
from pydantic import NonNegativeInt

from .cache import get_cached_statistic
from .services import get_disk_usage, get_memory_usage, get_task_summary, get_video_summary

router = Router()


class VideoSummaryOut(Schema):
    total: int
    software: dict[str, int]
    level: dict[str, int]
    mode: dict[str, int]
    state: dict[str, int]


class TaskSummaryOut(Schema):
    total: int
    status: dict[str, int]


class DiskUsageOut(Schema):
    total: int
    used: int
    free: int
    video: int | None
    db: int


class MemorySectionOut(Schema):
    status: Literal['ready', 'unavailable']
    sampled_at: datetime | None
    reason: Literal['permission_denied', 'unsupported_metric', 'unsupported_scope', 'budget_exceeded', 'metadata_unavailable', 'inconsistent_snapshot', 'redis_unavailable', 'database_unavailable', 'collection_failed'] | None
    total_bytes: NonNegativeInt | None


class ProcessGroupsOut(Schema):
    uwsgi: NonNegativeInt
    apscheduler: NonNegativeInt
    redis: NonNegativeInt
    mysql: NonNegativeInt
    db_worker: NonNegativeInt
    other: NonNegativeInt


class HostMemoryOut(Schema):
    total_bytes: NonNegativeInt
    available_bytes: NonNegativeInt


class ProcessMemoryOut(MemorySectionOut):
    metric: Literal['pss', 'rss']
    groups: ProcessGroupsOut | None
    host: HostMemoryOut | None
    unreadable_processes: NonNegativeInt


class RedisGroupsOut(Schema):
    pb_rankings: NonNegativeInt
    other_rankings: NonNegativeInt
    latest_videos: NonNegativeInt
    other: NonNegativeInt


class RedisMemoryOut(MemorySectionOut):
    metric: Literal['redis_allocated']
    groups: RedisGroupsOut | None
    estimated: Literal[True]
    samples: Literal[5]


class MemoryUsageOut(Schema):
    memory: ProcessMemoryOut
    redis: RedisMemoryOut


@router.get('/videosummary', response=VideoSummaryOut)
@decorate_view(ratelimit(key='ip', rate='30/m', block=True))
def video_summary(request):
    """
    - ratelimit(key='ip', rate='30/m', block=True)
    """
    return get_cached_statistic('videosummary', get_video_summary)


@router.get('/tasksummary', response=TaskSummaryOut)
@decorate_view(ratelimit(key='ip', rate='30/m', block=True))
def task_summary(request):
    """
    - ratelimit(key='ip', rate='30/m', block=True)
    """
    return get_cached_statistic('tasksummary', get_task_summary)


@router.get('/diskusage', response=DiskUsageOut)
@decorate_view(ratelimit(key='ip', rate='30/m', block=True))
def disk_usage(request):
    """
    - ratelimit(key='ip', rate='30/m', block=True)
    """
    return get_cached_statistic('diskusage', get_disk_usage)


@router.get('/memoryusage', response=MemoryUsageOut)
@decorate_view(ratelimit(key='ip', rate='30/m', block=True))
def memory_usage(request):
    """
    - ratelimit(key='ip', rate='30/m', block=True)

    Return process and Redis memory statistics cached together for 300 seconds.
    """
    return get_cached_statistic('memoryusage', get_memory_usage)
