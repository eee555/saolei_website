from django.db.models import F, Max, Min, Window
from django.db.models.functions import RowNumber
from django.utils import timezone

from config.customranking import CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel

from .cache import CUSTOM_PLUCK_CACHE_SIZE, PLuckRankingCache
from .models import CustomPluckRecord


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
    cache_size = len(ranking_cache)
    cache_end = min(end, cache_size)
    players = ranking_cache.get_rank_range(start, cache_end) if start < cache_end else []

    if end <= cache_end:
        return players

    db_start = min(cache_size, end)
    records = (
        CustomPluckRecord.objects
        .filter(level=level)
        .select_related('video')
        .order_by('pluck', 'timems', 'upload_time')[db_start:end]
    )
    records = list(records)

    cache_fill_count = max(min(end, CUSTOM_PLUCK_CACHE_SIZE) - cache_size, 0)
    if cache_fill_count:
        ranking_cache = PLuckRankingCache(level).open()
        ranking_cache.add_record_batch(records[:cache_fill_count])
        ranking_cache.close()

    result_start = max(start, db_start) - db_start
    players.extend(record_to_rank_dict(record) for record in records[result_start:])
    return players


def update_custom_pluck_top_cache(record: CustomPluckRecord | None, level: str, player_id: int):
    """在 Redis 缓存已存在时，更新或移除单个玩家的 pluck 排行缓存。"""

    ranking_cache = PLuckRankingCache(level)
    if len(ranking_cache) == 0:
        return

    if record is not None:
        if not ranking_cache.can_insert_record(record):
            return
        ranking_cache.update_record(record, player_id)
    else:
        ranking_cache.delete_record(player_id)
    ranking_cache.clamp(CUSTOM_PLUCK_CACHE_SIZE)


def refresh_custom_pluck_rank(player, level: str):
    """重新计算单个玩家在某个自定义级别下的最佳 pluck 纪录。"""
    video = (
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

    if video is None:
        CustomPluckRecord.objects.filter(player=player, level=level).delete()
        return None

    record, _ = CustomPluckRecord.objects.update_or_create(
        player_id=video.player_id,
        level=video.level,
        defaults={
            'video_id': video.id,
            'pluck': video.pluck,
            'timems': video.timems,
            'upload_time': video.upload_time,
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


def refresh_custom_pluck_rank_range(startid: int, endid: int):
    """逐条确认并刷新指定玩家 id 闭区间内的自定义 pluck 排行数据库纪录。"""
    refresh_started_at = timezone.now()

    best_videos = (
        VideoModel.objects
        .filter(
            player_id__gte=startid,
            player_id__lte=endid,
            level__in=CUSTOM_PLUCK_LEVELS,
            mode__in=CUSTOM_PLUCK_MODES,
            state=MS_TextChoices.State.OFFICIAL,
            ongoing_tournament=False,
            pluck__isnull=False,
        )
        .annotate(
            rn=Window(
                expression=RowNumber(),
                partition_by=[F('player_id'), F('level')],
                order_by=[F('pluck').asc(), F('timems').asc(), F('upload_time').asc()],
            ),
        )
        .filter(rn=1)
    )

    error_list = []
    success_count = 0
    for video in best_videos.iterator(chunk_size=1000):
        try:
            CustomPluckRecord.objects.update_or_create(
                player_id=video.player_id,
                level=video.level,
                defaults={
                    'video_id': video.id,
                    'pluck': video.pluck,
                    'timems': video.timems,
                    'upload_time': video.upload_time,
                },
            )
            success_count += 1
        except Exception:
            error_list.append(video.player_id)

    stale_records = CustomPluckRecord.objects.filter(
        player_id__gte=startid,
        player_id__lte=endid,
        updated_at__lt=refresh_started_at,
    )
    if error_list:
        stale_records = stale_records.exclude(player_id__in=error_list)
    stale_records.delete()

    return {
        'errorList': error_list,
        'successCount': success_count,
    }


def refresh_all_custom_pluck_ranks(player_batch_size: int = 1000):
    """按玩家 id 分段逐条确认并刷新全部自定义 pluck 排行数据库纪录。"""
    if player_batch_size <= 0:
        raise ValueError('player_batch_size must be positive')

    base_videos = (
        VideoModel.objects
        .filter(
            level__in=CUSTOM_PLUCK_LEVELS,
            mode__in=CUSTOM_PLUCK_MODES,
            state=MS_TextChoices.State.OFFICIAL,
            ongoing_tournament=False,
            pluck__isnull=False,
        )
    )
    player_bounds = base_videos.aggregate(
        min_player_id=Min('player_id'),
        max_player_id=Max('player_id'),
    )
    min_player_id = player_bounds['min_player_id']
    max_player_id = player_bounds['max_player_id']

    count = 0
    if min_player_id is not None and max_player_id is not None:
        player_id_start = min_player_id
        while player_id_start <= max_player_id:
            player_id_end = player_id_start + player_batch_size - 1
            result = refresh_custom_pluck_rank_range(player_id_start, player_id_end)
            count += result['successCount']
            player_id_start = player_id_end + 1

    return count
