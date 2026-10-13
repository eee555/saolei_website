import json

from config.customranking import CUSTOM_PLUCK_LEVELS
from customranking.cache import PLuckRankingCache
from speedranking.pb.cache import PBRankingCache
from speedranking.pb.utils import member, record_field
from speedranking.saolei.cache import SpeedRankingCache
from speedranking.saolei.utils import RANKING_NAMES, RULES
from videomanager.models import VideoModel


def get_video_rankings(video: VideoModel):
    """只读现有 Redis 排行榜；玩家缓存的纪录必须属于当前录像。"""
    rankings = []
    with SpeedRankingCache.pipeline() as pipe:
        for ranking_name in RANKING_NAMES:
            ranking = SpeedRankingCache(ranking_name)
            pipe.hget(ranking.detail_key, video.player_id)
            for stat in RULES:
                ranking.read_rank(pipe, video.player_id, stat)
        speed_results = iter(pipe.execute())
    for ranking_name in RANKING_NAMES:
        raw = next(speed_results)
        record = json.loads(raw) if raw else {}
        for stat in RULES:
            rank = next(speed_results)
            if record.get(f'{stat}_id') == video.id and rank is not None:
                rankings.append({'ranking': 'saolei', 'stat': stat, 'nf': ranking_name == 'saolei_nf', 'rank': rank + 1})

    if video.level in ('b', 'i', 'e') and video.bv is not None:
        pb = PBRankingCache()
        with SpeedRankingCache.pipeline() as pipe:
            for nf in (False, True):
                pipe.zrank(pb.rank_key(record_field(nf, video.level, video.bv)), member(video.player_id, video.id))
            pb_ranks = pipe.execute()
        for nf, rank in zip((False, True), pb_ranks):
            if rank is not None:
                rankings.append({'ranking': 'pb', 'stat': 'time', 'nf': nf, 'rank': rank + 1})

    if video.level in CUSTOM_PLUCK_LEVELS:
        pluck = PLuckRankingCache(video.level)
        with pluck.client.pipeline() as pipe:
            pipe.zrank(pluck.rank_key, video.player_id)
            pipe.hget(pluck.detail_key, video.player_id)
            rank, raw = pipe.execute()
        if rank is not None and raw and json.loads(raw).get('video_id') == video.id:
            rankings.append({'ranking': 'pluck', 'stat': 'pluck', 'nf': False, 'rank': rank + 1})
    return rankings
