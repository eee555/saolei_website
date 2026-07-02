from django.tasks import task

from .models import VideoModel
from .utils import calculate_pluck, normalize_pluck


def helper_video_pluck(video: VideoModel):
    from customranking.services import is_custom_pluck_video

    if is_custom_pluck_video(video) and video.pluck is None:
        task_video_pluck.enqueue(video.id)


@task(priority=-1)
def task_video_pluck(video_id: int):
    from customranking.services import is_custom_pluck_video

    video = VideoModel.objects.get(id=video_id)
    if not is_custom_pluck_video(video):
        return

    pluck = normalize_pluck(calculate_pluck(video.file.path))
    video.pluck = pluck
    video.save(update_fields=['pluck'])
