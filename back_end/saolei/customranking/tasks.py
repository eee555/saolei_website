from django.tasks import task
from timeout_decorator import timeout

from utils.parser import create_video_from_data
from videomanager.models import VideoModel

from .services import is_custom_pluck_video, refresh_custom_pluck_rank_for_video, update_custom_pluck_rank_for_video
from .utils import normalize_pluck

PLUCK_TIMEOUT_SECONDS = 60


def helper_custom_pluck(video: VideoModel):
    if is_custom_pluck_video(video):
        task_custom_pluck.enqueue(video.id)
    else:
        refresh_custom_pluck_rank_for_video(video)


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
def task_custom_pluck(video_id: int):
    video = VideoModel.objects.get(id=video_id)
    if not is_custom_pluck_video(video):
        refresh_custom_pluck_rank_for_video(video)
        return

    pluck = normalize_pluck(calculate_pluck(video.file.path))
    video.pluck = pluck
    video.save(update_fields=['pluck'])
    update_custom_pluck_rank_for_video(video)
