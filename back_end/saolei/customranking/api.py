from datetime import datetime

from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError

from config.customranking import CUSTOM_PLUCK_CONFIGS
from customranking.cache import get_player_pluck_records, PLuckRankingCache
from userprofile.decorators import staff_required
from .models import CustomPluckRecord
from .services import get_pluck_rank_range, refresh_custom_pluck_rank_range

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


class CustomPluckLevel(Schema):
    level: str


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
    count = CustomPluckRecord.objects.filter(level=level).count()

    players = get_pluck_rank_range(level, start, end)

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
    missing_levels = []
    for level in CUSTOM_PLUCK_CONFIGS:
        cached_record = cached_records.get(level)
        if cached_record is None:
            missing_levels.append(level)
            continue
        rows_by_level[level] = {
            'level': level,
            'video_id': cached_record['video_id'],
            'pluck': cached_record['pluck'],
        }

    if missing_levels:
        db_records = (
            CustomPluckRecord.objects
            .filter(player_id=player_id, level__in=missing_levels)
        )
        for record in db_records:
            rows_by_level[record.level] = {
                'level': record.level,
                'video_id': record.video_id,
                'pluck': record.pluck,
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


@router.post('pluck/cache/flush')
@decorate_view(staff_required)
def flush_pluck_cache(request, data: CustomPluckLevel = Form(...)):  # noqa: B008
    """
    - staff_required
    """
    PLuckRankingCache(data.level).flush()
