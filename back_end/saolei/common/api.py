

from django_tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult
from ninja import NinjaAPI, Schema
from ninja.throttling import AnonRateThrottle

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
    total = VideoModel.objects.count()

    software = get_choice_counts_filtered(VideoModel, 'software', MS_TextChoices.Software)

    level = get_choice_counts_filtered(VideoModel, 'level', MS_TextChoices.Level)

    mode = get_choice_counts_filtered(VideoModel, 'mode', MS_TextChoices.Mode)

    state = get_choice_counts_filtered(VideoModel, 'state', MS_TextChoices.State)

    return {'total': total, 'software': software, 'level': level, 'mode': mode, 'state': state}


class TaskSummaryOut(Schema):
    total: int
    status: dict[str, int]


@api.get('/tasksummary', throttle=[AnonRateThrottle('10/m')])
def api_task_summary(request):
    total = DBTaskResult.objects.count()

    status = get_choice_counts_filtered(DBTaskResult, 'status', TaskResultStatus)

    return {'total': total, 'status': status}
