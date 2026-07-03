from django.core.cache import cache
from django.db.models import Min

from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel

from .config import CUSTOM_PLUCK_CACHE_SIZE, CUSTOM_PLUCK_CONFIGS, CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from .models import CustomPluckRecord
from .utils import get_custom_pluck_cache_key


def is_custom_pluck_video(video: VideoModel) -> bool:
    return (
        video.level in CUSTOM_PLUCK_LEVELS
        and video.mode in CUSTOM_PLUCK_MODES
        and video.state == MS_TextChoices.State.OFFICIAL
        and not video.ongoing_tournament
    )


def serialize_custom_pluck_record(record: CustomPluckRecord):
    return {
        'player_id': record.player_id,
        'video_id': record.video_id,
        'mode': record.mode,
        'pluck': record.pluck,
        'timems': record.video.timems,
        'bv': record.video.bv,
        'upload_time': record.video.upload_time,
    }


def build_custom_pluck_top_cache(level: str):
    records = (
        CustomPluckRecord.objects
        .filter(level=level)
        .select_related('video')
        .order_by('pluck', 'video__timems', 'video__id')[:CUSTOM_PLUCK_CACHE_SIZE]
    )
    players = [
        serialize_custom_pluck_record(record)
        for record in records
    ]
    cache.set(get_custom_pluck_cache_key(level), players, None)
    return players


def get_custom_pluck_top_cache(level: str):
    key = get_custom_pluck_cache_key(level)
    players = cache.get(key)
    if players is None:
        players = build_custom_pluck_top_cache(level)
    return players


def update_custom_pluck_top_cache(record: CustomPluckRecord | None, level: str, player_id: int):
    key = get_custom_pluck_cache_key(level)
    players = cache.get(key)
    if players is None:
        return

    players = [player for player in players if player['player_id'] != player_id]
    if record is not None:
        player = serialize_custom_pluck_record(record)
        player_key = (player['pluck'], player['timems'], player['video_id'])
        last_key = (players[-1]['pluck'], players[-1]['timems'], players[-1]['video_id']) if players else None
        if len(players) < CUSTOM_PLUCK_CACHE_SIZE or player_key < last_key:
            players.append(player)

    players.sort(key=lambda player: (player['pluck'], player['timems'], player['video_id']))
    players = players[:CUSTOM_PLUCK_CACHE_SIZE]
    cache.set(key, players, None)


def refresh_custom_pluck_rank(player, level: str):
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
        .order_by('pluck', 'timems', 'id')
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


def update_custom_pluck_rank_for_video(video: VideoModel):
    if not is_custom_pluck_video(video) or video.pluck is None:
        return refresh_custom_pluck_rank_for_video(video)

    record = CustomPluckRecord.objects.filter(player=video.player, level=video.level).first()
    if record is not None and (
        record.pluck < video.pluck
        or (record.pluck == video.pluck and record.video.timems <= video.timems)
    ):
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


def refresh_custom_pluck_rank_for_video(video: VideoModel):
    if video.level not in CUSTOM_PLUCK_LEVELS:
        return None
    return refresh_custom_pluck_rank(video.player, video.level)


def refresh_all_custom_pluck_ranks():
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
            .order_by('timems', 'id')
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
        build_custom_pluck_top_cache(level)
    return len(records)
