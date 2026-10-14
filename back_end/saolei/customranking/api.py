from datetime import datetime

from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError

from config.customranking import CUSTOM_PLUCK_CONFIGS
from customranking.cache import get_player_pluck_records, PLuckRankingCache
from userprofile.decorators import staff_required
from .services import refresh_custom_pluck_rank_range

router = Router()


class CustomPluckPlayerOut(Schema):
    player_id: int
    video_id: int
    mode: str
    pluck: float
    timems: int
    bv: int
    upload_time: datetime


class CustomPluckRankOut(Schema):
    count: int
    players: list[CustomPluckPlayerOut]


class CustomPluckRecordOut(Schema):
    level: str
    video_id: int
    pluck: float


class RefreshCustomPluckRankIn(Schema):
    startid: int
    endid: int


class RefreshCustomPluckRankOut(Schema):
    errorList: list[int]
    successCount: int


@router.get('/pluck', response=CustomPluckRankOut)
@decorate_view(ratelimit(key='ip', rate='1/s'))
def pluck_rank(request, level: str, start: int = 0, end: int = 20):
    """
    - ratelimit(key='ip', rate='1/s')
    """
    if level not in CUSTOM_PLUCK_CONFIGS:
        raise HttpError(400, 'Invalid custom pluck ranking level')

    start = max(start, 0)
    end = min(max(end, start), start + 100)
    ranking_cache = PLuckRankingCache(level)
    count = len(ranking_cache)
    players = ranking_cache.get_rank_range(start, end)

    return {
        'count': count,
        'players': players,
    }


@router.get('/pluck/player', response=list[CustomPluckRecordOut])
@decorate_view(ratelimit(key='ip', rate='1/s'))
def player_pluck_records(request, player_id: int):
    """
    - ratelimit(key='ip', rate='1/s')
    """
    rows_by_level = {}
    cached_records = get_player_pluck_records(
        player_id,
        CUSTOM_PLUCK_CONFIGS,
    )
    for level in CUSTOM_PLUCK_CONFIGS:
        cached_record = cached_records.get(level)
        if cached_record is None:
            continue
        rows_by_level[level] = {
            'level': level,
            'video_id': cached_record['video_id'],
            'pluck': cached_record['pluck'],
        }

    return [
        rows_by_level[level]
        for level in CUSTOM_PLUCK_CONFIGS
        if level in rows_by_level
    ]


@router.post('/pluck/refresh', response=RefreshCustomPluckRankOut)
@decorate_view(staff_required)
def refresh_pluck_rank(request, data: RefreshCustomPluckRankIn = Form(...)):  # noqa: B008
    """
    - staff_required
    """
    startid = min(data.startid, data.endid)
    endid = max(data.startid, data.endid)
    return refresh_custom_pluck_rank_range(startid, endid)
