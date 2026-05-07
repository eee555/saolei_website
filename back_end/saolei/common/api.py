

from django.core.cache import cache
from django.db.models import Sum
from django_tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult
from ninja import NinjaAPI, Schema
from ninja.throttling import AnonRateThrottle
import psutil

from common.utils import get_db_size
from config.text_choices import MS_TextChoices
from utils.db import get_choice_counts_filtered
from videomanager.models import VideoModel


api = NinjaAPI()


class VideoSummaryOut(Schema):
    total: int
    software: dict[str, int]
    level: dict[str, int]
    mode: dict[str, int]
    state: dict[str, int]


@api.get('/videosummary', response=VideoSummaryOut, throttle=[AnonRateThrottle('10/m')])
def api_video_summary(request):
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


@api.get('/tasksummary', throttle=[AnonRateThrottle('10/m')])
def api_task_summary(request):
    if (cached_data := cache.get('api:common/tasksummary')) is not None:
        return cached_data

    total = DBTaskResult.objects.count()
    status = get_choice_counts_filtered(DBTaskResult, 'status', TaskResultStatus)

    result = {'total': total, 'status': status}
    cache.set('api:common/tasksummary', result, 300)

    return result


@api.get('/diskusage', throttle=[AnonRateThrottle('10/m')])
def api_disk_usage(request):
    if (cached_data := cache.get('api:common/diskusage')) is not None:
        return cached_data

    disk = psutil.disk_usage('.')

    video_size: int = VideoModel.objects.aggregate(s=Sum('file_size'))['s']
    db_size = get_db_size()

    result = {'total': disk.total, 'used': disk.used, 'free': disk.free, 'video': video_size, 'db': db_size}
    cache.set('api:common/diskusage', result, 300)

    return result
