from django.db.models import Min

from config.customranking import CUSTOM_PLUCK_CONFIGS, CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel

from .cache import CUSTOM_PLUCK_CACHE_SIZE, PLuckRankingCache
from .models import CustomPluckRecord


def build_custom_pluck_cache(level: str):
    """从数据库重建某个自定义级别的 pluck 排行 Redis 缓存。"""
    records = (
        CustomPluckRecord.objects
        .filter(level=level)
        .select_related('video')
        .order_by('pluck', 'timems', 'upload_time')
    )

    ranking_cache = PLuckRankingCache(level).open()
    ranking_cache.flush()
    ranking_cache.add_record_batch(records)
    ranking_cache.close()

    ranking_cache = PLuckRankingCache(level)
    ranking_cache.clamp(CUSTOM_PLUCK_CACHE_SIZE)


def record_to_rank_dict(record: CustomPluckRecord):
    """将数据库纪录转换为 API 返回的玩家排行字典。"""
    return {
        'player_id': record.player_id,
        'video_id': record.video_id,
        'mode': record.video.mode,
        'pluck': record.pluck,
        'timems': record.timems,
        'bv': record.video.bv,
        'upload_time': record.upload_time,
    }


def get_pluck_rank_range(level: str, start: int, end: int):
    """读取某个自定义级别在指定排名区间内的 pluck 排行，缓存外部分回源数据库。"""
    ranking_cache = PLuckRankingCache(level)
    cache_end = min(end, len(ranking_cache))
    players = ranking_cache.get_rank_range(start, cache_end) if start < cache_end else []

    if end <= cache_end:
        return players

    db_start = max(start, cache_end)
    records = (
        CustomPluckRecord.objects
        .filter(level=level)
        .select_related('video')
        .order_by('pluck', 'timems', 'upload_time')[db_start:end]
    )
    players.extend(record_to_rank_dict(record) for record in records)
    return players


def update_custom_pluck_top_cache(record: CustomPluckRecord | None, level: str, player_id: int):
    """在 Redis 缓存已存在时，更新或移除单个玩家的 pluck 排行缓存。"""

    ranking_cache = PLuckRankingCache(level)
    if record is not None:
        ranking_cache.update_record(record, player_id)
    else:
        ranking_cache.delete_record(player_id)
    ranking_cache.clamp(CUSTOM_PLUCK_CACHE_SIZE)


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
        return None

    record, _ = CustomPluckRecord.objects.update_or_create(
        player=player,
        level=level,
        defaults={
            'video': best_video,
            'pluck': best_video.pluck,
            'timems': best_video.timems,
            'upload_time': best_video.upload_time,
        },
    )
    return record


def add_to_custom_pluck_rank(video: VideoModel):
    """尝试将一条录像加入 pluck 排行，并在优于原纪录时刷新玩家纪录。"""
    record, created = CustomPluckRecord.objects.get_or_create(
        player=video.player,
        level=video.level,
        defaults={
            'video': video,
            'pluck': video.pluck,
            'timems': video.timems,
            'upload_time': video.upload_time,
        },
    )
    if not created:
        record.add_video(video)
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
            pluck=video.pluck,
            timems=video.timems,
            upload_time=video.upload_time,
        ))
    CustomPluckRecord.objects.bulk_create(records)
    for level in CUSTOM_PLUCK_CONFIGS:
        build_custom_pluck_cache(level)
    return len(records)
