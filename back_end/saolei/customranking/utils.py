from datetime import datetime, timezone

CUSTOM_PLUCK_CACHE_SIZE = 100


def get_custom_pluck_rank_key(level: str) -> str:
    return f'customranking:pluck:{level}:rank'


def get_custom_pluck_detail_key(level: str) -> str:
    return f'customranking:pluck:{level}:detail'


def get_custom_pluck_player_key(level: str) -> str:
    return f'customranking:pluck:{level}:player'


def get_custom_pluck_cache_ready_key(level: str) -> str:
    return f'customranking:pluck:{level}:ready'


def get_custom_pluck_member(video) -> str:
    upload_time = video.upload_time
    if upload_time.tzinfo is None:
        upload_time = upload_time.replace(tzinfo=timezone.utc)
    delta = upload_time - datetime(1970, 1, 1, tzinfo=timezone.utc)
    upload_time_ms = (delta.days * 86400 + delta.seconds) * 1000 + delta.microseconds // 1000
    return f'{video.timems:07d}:{upload_time_ms:013d}:{video.id}'


def parse_custom_pluck_member(member: str):
    timems, upload_time_ms, video_id = member.split(':', 2)
    return int(timems), int(upload_time_ms), int(video_id)
