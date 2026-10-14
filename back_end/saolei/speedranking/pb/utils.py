from datetime import datetime, timezone as datetime_timezone
from typing import Literal

from ..utils import upload_microseconds

PBLevel = Literal['b', 'i', 'e']
LEVELS = ('b', 'i', 'e')
SCORE_TIME_FACTOR = 2 ** 26


def encode_score(timems: int, upload_time: datetime) -> int:
    """毫秒用时与 Unix UTC 分钟数合成可精确还原用时的整数。"""
    upload = upload_microseconds(upload_time) // 60_000_000
    if not 0 <= upload < SCORE_TIME_FACTOR:
        raise ValueError('PB upload time exceeds the score range')
    return timems * SCORE_TIME_FACTOR + upload


def record_field(nf: bool, level: PBLevel, bv: int) -> str:
    return f'{"nf" if nf else "std"}:{level}:{bv}'


def parse_field(field: str) -> tuple[bool, PBLevel, int]:
    mode, level, bv = field.split(':')
    return mode == 'nf', level, int(bv)


def member(player_id: int, video_id: int) -> str:
    return f'{player_id}:{video_id}'


def parse_member(value: bytes | str) -> tuple[int, int]:
    if isinstance(value, bytes):
        value = value.decode()
    player_id, video_id = value.split(':')
    return int(player_id), int(video_id)


def record_from_score(video_id: int, score: float | int, rank: int | None = None):
    return {'timems': int(score) // SCORE_TIME_FACTOR, 'video_id': video_id, 'rank': rank}


def upload_time_from_score(score: float | int) -> datetime:
    return datetime.fromtimestamp((int(score) % SCORE_TIME_FACTOR) * 60, tz=datetime_timezone.utc)
