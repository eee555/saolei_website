from copy import deepcopy
import uuid

from django.db.models import F, Q, Window
from django.db.models.functions import RowNumber

from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel
from .cache import TopRankingCache
from .utils import insert_video, merge_videos, MINIMUM_BV, parse_field, RANK_FIELDS, record_field, score, STAT_COLUMNS, stat_record, TOP_SIZE
from ..cache import pipeline
from ..utils import log_update_errors, player_batches


def eligible_videos(videos, nf=False):
    levels = Q()
    for level, minimum in MINIMUM_BV.items():
        levels |= Q(level=level, bv__gte=minimum)
    videos = videos.filter(levels, mode=MS_TextChoices.Mode.STD, state=MS_TextChoices.State.OFFICIAL, ongoing_tournament=False)
    return videos.filter(right_ce=0) if nf else videos


def candidates_for_video(video):
    if video is None or video['level'] not in MINIMUM_BV:
        return {}
    if video['bv'] is None or video['bv'] < MINIMUM_BV[video['level']]:
        return {}
    if video['mode'] != MS_TextChoices.Mode.STD or video['state'] != MS_TextChoices.State.OFFICIAL or video['ongoing_tournament']:
        return {}
    return {
        record_field(nf, video['level'], stat): {'video_id': video['id'], 'value': video[column]}
        for nf in ((False, True) if video['right_ce'] == 0 else (False,))
        for stat, column in STAT_COLUMNS.items() if video[column] is not None
    }


def best_videos(player_id: int, field: str):
    """仅对失效或变差的项查询真实前五，Stnb 全程使用 iqg。"""
    nf, level, stat = parse_field(field)
    column = STAT_COLUMNS[stat]
    videos = eligible_videos(VideoModel.objects.filter(player_id=player_id, level=level), nf).filter(**{f'{column}__isnull': False})
    order = column if stat == 't' else f'-{column}'
    return [{'video_id': video['id'], 'value': video[column]} for video in videos.order_by(order).values('id', column)[:TOP_SIZE]]


def set_videos(record: dict, field: str, videos: list[dict]):
    if videos:
        record[field] = stat_record(parse_field(field)[2], videos)
    else:
        record.pop(field, None)


def prepare_video_update(video, video_id: int, previous):
    """新增与改善有序插入；已入选录像变差或离榜时查库补位。"""
    records = deepcopy(previous)
    candidates = candidates_for_video(video)
    for player_id, record in records.items():
        current = candidates if video and video['player_id'] == player_id else {}
        for field in set(record) | set(current):
            stat = parse_field(field)[2]
            videos = record.get(field, {}).get('videos', [])
            old = next((item for item in videos if item['video_id'] == video_id), None)
            candidate = current.get(field)
            if old and (candidate is None or score(stat, candidate['value']) > score(stat, old['value'])):
                set_videos(record, field, best_videos(player_id, field))
            elif candidate:
                set_videos(record, field, insert_video(stat, videos, candidate))
    return records


def prepare_add_videos(videos, previous):
    """数据库按用户与等级分桶取本批前五，再合并缓存前五。"""
    records = deepcopy(previous)
    for nf in (False, True):
        for stat, column in STAT_COLUMNS.items():
            order = F(column).asc() if stat == 't' else F(column).desc()
            candidates = eligible_videos(videos, nf).filter(**{f'{column}__isnull': False}).annotate(
                rn=Window(RowNumber(), partition_by=[F('player_id'), F('level')], order_by=[order]),
            ).filter(rn__lte=TOP_SIZE).values('id', 'player_id', 'level', column)
            grouped = {}
            for video in candidates.iterator(chunk_size=1000):
                key = video['player_id'], record_field(nf, video['level'], stat)
                grouped.setdefault(key, []).append({'video_id': video['id'], 'value': video[column]})
            for (player_id, field), items in grouped.items():
                record = records[player_id]
                set_videos(record, field, merge_videos(stat, record.get(field, {}).get('videos', []), items))
    return records


def prepare_remove_videos(ids_by_player, previous):
    """仅补位被移除录像占据的用户小榜。"""
    records = deepcopy(previous)
    for player_id, record in records.items():
        removed = ids_by_player.get(player_id, set())
        for field, value in list(record.items()):
            if any(video['video_id'] in removed for video in value['videos']):
                set_videos(record, field, best_videos(player_id, field))
    return records


def write_records(pipe, previous, records, ranking=None, force_fields=None):
    """写入变更明细与均值索引，返回需要重算锚点的小榜。"""
    ranking = ranking or TopRankingCache()
    force_fields = force_fields or {}
    affected = set()
    for player_id, record in records.items():
        old = previous[player_id]
        if old != record or player_id in force_fields:
            ranking.write_record(pipe, player_id, record)
        for field in set(old) | set(record) | force_fields.get(player_id, set()):
            before, after = old.get(field), record.get(field)
            if before is not None and after is not None and before['mean'] == after['mean'] and field not in force_fields.get(player_id, set()):
                continue
            if before is None and after is None and field not in force_fields.get(player_id, set()):
                continue
            ranking.write_score(pipe, player_id, field, score(parse_field(field)[2], after['mean']) if after else None)
            affected.add(field)
    return affected


def rebuild_player_record(player_id: int, level: str, stat: str, nf: bool):
    """强制重建指定用户的小榜明细、排序索引和锚点。"""
    ranking = TopRankingCache()
    field = record_field(nf, level, stat)
    with log_update_errors('top.rebuild_record', player_id=player_id, field=field):
        previous = {player_id: ranking.get_record(player_id)}
        records = deepcopy(previous)
        set_videos(records[player_id], field, best_videos(player_id, field))
        with pipeline() as pipe:
            affected = write_records(pipe, previous, records, ranking, {player_id: {field}})
            pipe.execute()
        ranking.refresh_anchors(affected)
        return {'player_id': player_id, 'records': records[player_id]}


def rebuild_top_ranks(batch_size: int = 100, progress=None):
    """按玩家分段构建临时榜，生成全部锚点后原子发布。"""
    if batch_size <= 0:
        raise ValueError('batch_size must be positive')
    ranking = TopRankingCache(namespace=f'speedranking:rebuild:{uuid.uuid4().hex}')
    count = 0
    with log_update_errors('top.rebuild', batch_size=batch_size):
        try:
            videos = eligible_videos(VideoModel.objects.all())
            for players in player_batches(videos, batch_size):
                previous = {player_id: {} for player_id in players}
                records = prepare_add_videos(videos.filter(player_id__in=players), previous)
                with pipeline() as pipe:
                    write_records(pipe, previous, records, ranking)
                    pipe.execute()
                count += len(players)
                if progress:
                    progress(count, players[-1])
            ranking.refresh_anchors(set(RANK_FIELDS))
            ranking.publish_to(TopRankingCache())
        finally:
            ranking.flush()
    return count
