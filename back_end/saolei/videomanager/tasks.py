import math

from django.tasks import task
from timeout_decorator import timeout

from utils.parser import create_video_from_data
from .models import VideoModel

PLUCK_TIMEOUT_SECONDS = 60


def normalize_pluck(value) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        return None
    return value


def helper_video_pluck(video: VideoModel):
    from customranking.services import is_custom_pluck_video

    if is_custom_pluck_video(video) and video.pluck is None:
        task_video_pluck.enqueue(video.id)


@timeout(PLUCK_TIMEOUT_SECONDS, use_signals=False, timeout_exception=TimeoutError)
def calculate_pluck(file_path: str):
    with open(file_path, 'rb') as file:
        data = file.read()

    parsed_video, _ = create_video_from_data(file_path, data)
    parsed_video.parse()
    parsed_video.analyse()
    parsed_video.analyse_for_features(['pluck'])
    parsed_video.current_time = 1e8
    return parsed_video.pluck


@task(priority=-1)
def task_video_pluck(video_id: int):
    from customranking.services import is_custom_pluck_video

    video = VideoModel.objects.get(id=video_id)
    if not is_custom_pluck_video(video):
        return

    pluck = normalize_pluck(calculate_pluck(video.file.path))
    video.pluck = pluck
    video.save(update_fields=['pluck'])
