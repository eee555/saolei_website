from functools import partial
import uuid

from django.db import transaction
from django.db.models import F, QuerySet, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel
from .cache import SpeedRankingCache
from .utils import is_better, public_record, RANKING_NAMES, RankingName, RankStat, RULES, set_stat, TOTAL_PARTS, upload_microseconds

VIDEO_FIELDS = ('id', 'player_id', 'level', 'mode', 'state', 'ongoing_tournament', 'bv', 'timems', 'bvs', 'right_ce', 'upload_time')


def eligible_videos(videos: QuerySet, ranking_name: str, stat: str):
    level, minimum_bv, _ = RULES[stat]
    videos = videos.filter(level=level, bv__gte=minimum_bv, mode=MS_TextChoices.Mode.STD, state=MS_TextChoices.State.OFFICIAL, ongoing_tournament=False)
    if ranking_name == 'saolei_nf':
        videos = videos.filter(right_ce=0)
    return videos


def candidate_for_video(video: dict | None, ranking_name: str, stat: str):
    if video is None:
        return None
    level, minimum_bv, field = RULES[stat]
    if video['level'] != level or video['bv'] is None or video['bv'] < minimum_bv:
        return None
    if video['mode'] != MS_TextChoices.Mode.STD or video['state'] != MS_TextChoices.State.OFFICIAL or video['ongoing_tournament']:
        return None
    if ranking_name == 'saolei_nf' and video['right_ce'] != 0:
        return None
    return {'id': video['id'], 'value': video[field], 'upload': upload_microseconds(video['upload_time'])}


def best_candidate(player_id: int, ranking_name: str, stat: str):
    """仅对需要补位的单项查询最佳录像，upload_time 是唯一成绩 tie-breaker。"""
    field = RULES[stat][2]
    order = field if field == 'timems' else f'-{field}'
    video = eligible_videos(VideoModel.objects.filter(player_id=player_id), ranking_name, stat).order_by(order, 'upload_time', 'id').values(*VIDEO_FIELDS).first()
    return candidate_for_video(video, ranking_name, stat)


def rebuild_player_record(player_id: int, ranking_name: RankingName, stat: RankStat):
    """单项从数据库重建，总项只由缓存中的组成项重算，同时修复排序索引。"""
    ranking = SpeedRankingCache(ranking_name)

    def transform(record):
        if stat not in TOTAL_PARTS:
            set_stat(record, stat, best_candidate(player_id, ranking_name, stat))

    ranking.update(player_id, transform, force=True)
    return public_record(player_id, ranking.get_record(player_id))


def _sync_video(video_id: int, previous_player_id: int):
    video = VideoModel.objects.filter(pk=video_id).values(*VIDEO_FIELDS).first()
    players = {previous_player_id}
    if video:
        players.add(video['player_id'])
    for player_id in players:
        for ranking_name in RANKING_NAMES:
            def transform(record, ranking_name=ranking_name, player_id=player_id):
                current_video = VideoModel.objects.filter(pk=video_id, player_id=player_id).values(*VIDEO_FIELDS).first()
                for stat in RULES:
                    candidate = candidate_for_video(current_video, ranking_name, stat)
                    if record[f'{stat}_id'] == video_id:
                        if candidate is None or (not is_better(stat, candidate, record) and (candidate['value'] != record[stat] or candidate['upload'] != record['_uploads'][stat])):
                            set_stat(record, stat, best_candidate(player_id, ranking_name, stat))
                        else:
                            set_stat(record, stat, candidate)
                    elif candidate and is_better(stat, candidate, record):
                        set_stat(record, stat, candidate)
            SpeedRankingCache(ranking_name).update(player_id, transform)


def sync_video(video_id: int, previous_player_id: int):
    """提交成功后刷新录像的新旧玩家纪录，避免事务回滚污染 Redis。"""
    transaction.on_commit(partial(_sync_video, video_id, previous_player_id))


def player_batches(videos: QuerySet, batch_size: int):
    last_player = 0
    while players := list(videos.filter(player_id__gt=last_player).order_by('player_id').values_list('player_id', flat=True).distinct()[:batch_size]):
        yield players
        last_player = players[-1]


def _add_videos(videos: QuerySet, ranking_names=RANKING_NAMES, batch_size: int = 1000, namespace: str = 'speedranking'):
    """按玩家分段，在数据库分桶选最佳录像，再合并到 Redis。"""
    for players in player_batches(videos, batch_size):
        subset = videos.filter(player_id__in=players)
        for ranking_name in ranking_names:
            grouped = {}
            for stat, (_, _, field) in RULES.items():
                order = F(field).asc() if field == 'timems' else F(field).desc()
                best = eligible_videos(subset, ranking_name, stat).annotate(
                    rn=Window(RowNumber(), partition_by=[F('player_id')], order_by=[order, F('upload_time').asc(), F('id').asc()]),
                ).filter(rn=1).values(*VIDEO_FIELDS)
                for video in best:
                    grouped.setdefault(video['player_id'], {})[stat] = candidate_for_video(video, ranking_name, stat)
            ranking = SpeedRankingCache(ranking_name, namespace=namespace)
            for player_id, candidates in grouped.items():
                def transform(record, candidates=candidates):
                    for stat, candidate in candidates.items():
                        if is_better(stat, candidate, record):
                            set_stat(record, stat, candidate)
                ranking.update(player_id, transform)


def add_videos_to_speed_ranks(videos: QuerySet):
    """批量吸收已公开或已审核的录像，事务提交后执行。"""
    transaction.on_commit(partial(_add_videos, videos.all()))


def _remove_videos(videos: QuerySet):
    for players in player_batches(videos, 1000):
        ids_by_player = {}
        for player_id, video_id in videos.filter(player_id__in=players).values_list('player_id', 'id'):
            ids_by_player.setdefault(player_id, set()).add(video_id)
        for ranking_name in RANKING_NAMES:
            ranking = SpeedRankingCache(ranking_name)
            for player_id, video_ids in ids_by_player.items():
                def transform(record, video_ids=video_ids, player_id=player_id, ranking_name=ranking_name):
                    for stat in RULES:
                        if record[f'{stat}_id'] in video_ids:
                            set_stat(record, stat, best_candidate(player_id, ranking_name, stat))
                ranking.update(player_id, transform)


def remove_videos_from_speed_ranks(videos: QuerySet):
    """批量失效后仅补位这些录像保持的纪录；传入按 id 固定的 queryset。"""
    transaction.on_commit(partial(_remove_videos, videos.all()))


def rebuild_speed_ranks(ranking_names=RANKING_NAMES, batch_size: int = 1000):
    """从录像库重建临时榜，完成后原子发布；执行期间应暂停录像写入。"""
    if batch_size <= 0:
        raise ValueError('batch_size must be positive')
    counts = {}
    for ranking_name in ranking_names:
        namespace = f'speedranking:rebuild:{uuid.uuid4().hex}'
        temporary = SpeedRankingCache(ranking_name, namespace=namespace)
        try:
            _add_videos(VideoModel.objects.all(), ranking_names=(ranking_name,), batch_size=batch_size, namespace=namespace)
            counts[ranking_name] = temporary.get_range('sumt', 0, 0)['count']
            temporary.publish_to(SpeedRankingCache(ranking_name))
        finally:
            temporary.flush()
    return counts
