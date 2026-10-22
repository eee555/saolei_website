from datetime import datetime

from django_apscheduler import util

from .cache import newest_cache
from .models import VideoModel


def find_identical_video(file, **filters):
    candidates = VideoModel.objects.filter(file_size=file.size, **filters).order_by('pk')
    data = file.read()
    file.seek(0)
    for candidate in candidates:
        with candidate.file.open('rb') as existing:
            if existing.read() == data:
                return candidate
    return None


def set_import_upload_time(video: VideoModel, upload_time: datetime | None, *, created=False):
    """新录像覆盖 auto_now_add；重复录像只保留更早的时间，并触发保存信号。"""
    if upload_time is not None and (created or upload_time < video.upload_time):
        video.upload_time = upload_time
        video.save(update_fields=['upload_time'])


@util.close_old_connections
def delete_newest_queue():
    return newest_cache.trim()
