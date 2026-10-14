from datetime import datetime, timedelta, timezone
import json

from django_apscheduler import util
from django_redis import get_redis_connection


cache = get_redis_connection('saolei_website')


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
