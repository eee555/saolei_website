from datetime import datetime, timedelta, timezone
import json

from django_apscheduler import util
from django_redis import get_redis_connection

from .models import VideoModel

cache = get_redis_connection('saolei_website')


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


def n_days_ago(time_str: str, n=7) -> bool:
    t = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - t
    return delta > timedelta(days=n)


@util.close_old_connections
def delete_newest_queue():
    if cache.hlen('newest_queue') <= 100:
        return
    newest_queue_ids = cache.hgetall('newest_queue')
    for key in newest_queue_ids.keys():
        video_info = json.loads(newest_queue_ids[key])
        if n_days_ago(video_info['time']):
            cache.hdel('newest_queue', key)
