import json

from django_redis import get_redis_connection

from utils import ComplexEncoder

from .models import VideoModel

cache = get_redis_connection('saolei_website')


def serialize_video_to_queue(video: VideoModel):
    return {
        'state': video.state,
        'tournament': video.ongoing_tournament,
        'software': video.software,
        'time': video.upload_time,
        'player_id': video.player.id,
        'identifier': video.video.identifier,
        'level': video.level,
        'mode': video.mode,
        'timems': video.timems,
        'bv': video.bv,
        'cl': video.cl,
        'ce': video.ce,
    }


class VideoQueueCache:
    key: str

    def __init__(self, key: str):
        self.key = key

    def add(self, video: VideoModel):
        if video.ongoing_tournament:
            return
        cache.hset(self.key, video.id, json.dumps(serialize_video_to_queue(video), cls=ComplexEncoder))

    def remove(self, video: VideoModel):
        cache.hdel(self.key, video.id)


newest_cache = VideoQueueCache('newest_queue')
freeze_cache = VideoQueueCache('freeze_queue')
review_cache = VideoQueueCache('review_queue')
