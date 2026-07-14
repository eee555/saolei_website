import json

from django.db.models import QuerySet
from django_redis import get_redis_connection

from config.text_choices import MS_TextChoices
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

    def add_bulk(self, videos):
        mapping = {
            video.id: json.dumps(serialize_video_to_queue(video), cls=ComplexEncoder)
            for video in videos
            if not video.ongoing_tournament
        }
        if mapping:
            cache.hset(self.key, mapping=mapping)

    def update_bulk(self, videos):
        videos = [video for video in videos if not video.ongoing_tournament]
        video_ids = [video.id for video in videos]
        if not video_ids:
            return

        cached_values = cache.hmget(self.key, video_ids)
        mapping = {
            video.id: json.dumps(serialize_video_to_queue(video), cls=ComplexEncoder)
            for video, cached_value in zip(videos, cached_values)
            if cached_value is not None
        }
        if mapping:
            cache.hset(self.key, mapping=mapping)

    def remove(self, video: VideoModel):
        cache.hdel(self.key, video.id)

    def remove_bulk(self, videos):
        video_ids = [video.id for video in videos]
        if video_ids:
            cache.hdel(self.key, *video_ids)


newest_cache = VideoQueueCache('newest_queue')
freeze_cache = VideoQueueCache('freeze_queue')
review_cache = VideoQueueCache('review_queue')


def add_videos_to_state_queues_bulk(videos: QuerySet[VideoModel]):
    """按录像状态批量恢复普通队列。"""
    newest_cache.add_bulk(videos.filter(state__in=[MS_TextChoices.State.OFFICIAL, MS_TextChoices.State.IDENTIFIER]))
    freeze_cache.add_bulk(videos.filter(state=MS_TextChoices.State.FROZEN))
    review_cache.add_bulk(videos.filter(state=MS_TextChoices.State.PLAIN))
