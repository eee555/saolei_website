from django.tasks import task

from .models import VideoModel
from .utils import calculate_pluck, is_custom_pluck_video, normalize_pluck


def helper_video_pluck(video: VideoModel):
    if video.pluck is not None:
        return

    if is_custom_pluck_video(video):
        task_video_pluck.enqueue(video.id)


@task(priority=-1)
def task_video_pluck(video_id: int):
    video = VideoModel.objects.get(id=video_id)
    pluck = normalize_pluck(calculate_pluck(video.file.path))
    video.pluck = pluck
    video.save(update_fields=['pluck'])
