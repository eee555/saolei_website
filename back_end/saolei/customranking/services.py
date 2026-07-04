import json
from datetime import datetime, timezone

from django.db.models import Min
from django_redis import get_redis_connection

from config.customranking import CUSTOM_PLUCK_CONFIGS, CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel

from .models import CustomPluckRecord
from .utils import (
    get_custom_pluck_cache_ready_key,
    get_custom_pluck_detail_key,
    get_custom_pluck_member,
    get_custom_pluck_player_key,
    get_custom_pluck_rank_key,
    parse_custom_pluck_member,
)

cache = get_redis_connection('saolei_website')


def serialize_custom_pluck_cache_detail(record: CustomPluckRecord):
    """将数据库纪录转换为 Redis detail hash 中保存的展示信息。"""
    return {
        'player_id': record.player_id,
        'mode': record.mode,
        'bv': record.video.bv,
    }


def serialize_custom_pluck_cache_player(member: str, score: float, detail: dict):
    """将 Redis zset member、score 和 detail 还原为 API 返回的玩家纪录。"""
    timems, upload_time_ms, video_id = parse_custom_pluck_member(member)
    return {
        **detail,
        'video_id': video_id,
        'pluck': score,
        'timems': timems,
        'upload_time': datetime.fromtimestamp(upload_time_ms / 1000, tz=timezone.utc),
    }


def build_custom_pluck_cache(level: str):
    """从数据库重建某个自定义级别的 pluck 排行 Redis 缓存。"""
    records = (
        CustomPluckRecord.objects
        .filter(level=level)
        .select_related('video')
        .order_by('pluck', 'video__timems', 'video__upload_time')
    )

    rank_key = get_custom_pluck_rank_key(level)
    detail_key = get_custom_pluck_detail_key(level)
    player_key = get_custom_pluck_player_key(level)
    ready_key = get_custom_pluck_cache_ready_key(level)
    pipeline = cache.pipeline()
    pipeline.delete(rank_key, detail_key, player_key, ready_key)
    for record in records:
        member = get_custom_pluck_member(record.video)
        pipeline.zadd(rank_key, {member: record.pluck})
        pipeline.hset(detail_key, member, json.dumps(serialize_custom_pluck_cache_detail(record)))
        pipeline.hset(player_key, record.player_id, member)
    pipeline.set(ready_key, '1')
    pipeline.execute()


def get_custom_pluck_cache_range(level: str, start: int, end: int):
    """读取某个自定义级别在指定排名区间内的 pluck 排行缓存。"""
    if not cache.exists(get_custom_pluck_cache_ready_key(level)):
        build_custom_pluck_cache(level)

    rank_key = get_custom_pluck_rank_key(level)
    detail_key = get_custom_pluck_detail_key(level)
    members_with_scores = cache.zrange(rank_key, start, end - 1, withscores=True)
    if not members_with_scores:
        return []

    members = [
        member.decode() if isinstance(member, bytes) else member
        for member, _ in members_with_scores
    ]
    details = cache.hmget(detail_key, members)
    players = []
    for member, (_, score), detail in zip(members, members_with_scores, details):
        if detail is None:
            continue
        if isinstance(detail, bytes):
            detail = detail.decode()
        players.append(serialize_custom_pluck_cache_player(member, score, json.loads(detail)))
    return players


def update_custom_pluck_top_cache(record: CustomPluckRecord | None, level: str, player_id: int):
    """在 Redis 缓存已存在时，更新或移除单个玩家的 pluck 排行缓存。"""
    if not cache.exists(get_custom_pluck_cache_ready_key(level)):
        return

    rank_key = get_custom_pluck_rank_key(level)
    detail_key = get_custom_pluck_detail_key(level)
    player_key = get_custom_pluck_player_key(level)
    old_member = cache.hget(player_key, player_id)
    if old_member is not None:
        if isinstance(old_member, bytes):
            old_member = old_member.decode()
        cache.zrem(rank_key, old_member)
        cache.hdel(detail_key, old_member)

    if record is not None:
        member = get_custom_pluck_member(record.video)
        cache.zadd(rank_key, {member: record.pluck})
        cache.hset(detail_key, member, json.dumps(serialize_custom_pluck_cache_detail(record)))
        cache.hset(player_key, player_id, member)
    else:
        cache.hdel(player_key, player_id)


def refresh_custom_pluck_rank(player, level: str):
    """重新计算单个玩家在某个自定义级别下的最佳 pluck 纪录。"""
    best_video = (
        VideoModel.objects
        .filter(
            player=player,
            level=level,
            mode__in=CUSTOM_PLUCK_MODES,
            state=MS_TextChoices.State.OFFICIAL,
            ongoing_tournament=False,
            pluck__isnull=False,
        )
        .order_by('pluck', 'timems', 'upload_time')
        .first()
    )

    if best_video is None:
        CustomPluckRecord.objects.filter(player=player, level=level).delete()
        update_custom_pluck_top_cache(None, level, player.id)
        return None

    record, _ = CustomPluckRecord.objects.update_or_create(
        player=player,
        level=level,
        defaults={
            'video': best_video,
            'mode': best_video.mode,
            'pluck': best_video.pluck,
        },
    )
    update_custom_pluck_top_cache(record, level, player.id)
    return record


def add_to_custom_pluck_rank(video: VideoModel):
    """尝试将一条录像加入 pluck 排行，并在优于原纪录时刷新玩家纪录。"""
    record = CustomPluckRecord.objects.filter(player=video.player, level=video.level).first()
    if record is not None:
        record_key = (record.pluck, record.video.timems, record.video.upload_time)
        video_key = (video.pluck, video.timems, video.upload_time)
        if record_key <= video_key:
            return record

    record, _ = CustomPluckRecord.objects.update_or_create(
        player=video.player,
        level=video.level,
        defaults={
            'video': video,
            'mode': video.mode,
            'pluck': video.pluck,
        },
    )
    update_custom_pluck_top_cache(record, video.level, video.player_id)
    return record


def remove_from_custom_pluck_rank(video: VideoModel):
    """从 pluck 排行中移除录像影响，并用该玩家剩余录像重新计算纪录。"""
    if video.level not in CUSTOM_PLUCK_LEVELS:
        return None
    return refresh_custom_pluck_rank(video.player, video.level)


def refresh_all_custom_pluck_ranks():
    """清空并重新生成全部自定义 pluck 排行数据库纪录和 Redis 缓存。"""
    CustomPluckRecord.objects.all().delete()
    groups = (
        VideoModel.objects
        .filter(
            level__in=CUSTOM_PLUCK_LEVELS,
            mode__in=CUSTOM_PLUCK_MODES,
            state=MS_TextChoices.State.OFFICIAL,
            ongoing_tournament=False,
            pluck__isnull=False,
        )
        .values('player_id', 'level')
        .annotate(best_pluck=Min('pluck'))
    )
    records = []
    for group in groups:
        video = (
            VideoModel.objects
            .filter(
                player_id=group['player_id'],
                level=group['level'],
                mode__in=CUSTOM_PLUCK_MODES,
                state=MS_TextChoices.State.OFFICIAL,
                ongoing_tournament=False,
                pluck=group['best_pluck'],
            )
            .order_by('timems', 'upload_time')
            .first()
        )
        if video is None:
            continue
        records.append(CustomPluckRecord(
            player=video.player,
            video=video,
            level=video.level,
            mode=video.mode,
            pluck=video.pluck,
        ))
    CustomPluckRecord.objects.bulk_create(records)
    for level in CUSTOM_PLUCK_CONFIGS:
        build_custom_pluck_cache(level)
    return len(records)
