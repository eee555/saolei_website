from datetime import datetime

from django_ratelimit.decorators import ratelimit
from ninja import Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError

from userprofile.decorators import staff_required
from .config import CUSTOM_PLUCK_CONFIGS
from .models import CustomPluckRecord
from .services import (
    CUSTOM_PLUCK_CACHE_SIZE,
    get_custom_pluck_top_cache,
    refresh_all_custom_pluck_ranks,
    serialize_custom_pluck_record,
)

router = Router()


class CustomPluckConfigOut(Schema):
    row: int
    column: int
    mine: int


class CustomPluckPlayerOut(Schema):
    rank: int
    player_id: int
    player_name: str
    video_id: int
    mode: str
    pluck: float
    timems: int
    bv: int
    upload_time: datetime


class CustomPluckRankOut(Schema):
    count: int
    configs: dict[str, CustomPluckConfigOut]
    players: list[CustomPluckPlayerOut]


class RefreshCustomPluckRankOut(Schema):
    records: int


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

    if end <= CUSTOM_PLUCK_CACHE_SIZE:
        players = get_custom_pluck_top_cache(level)[start:end]
    else:
        records = (
            CustomPluckRecord.objects
            .filter(level=level)
            .select_related('player', 'video')
            .order_by('pluck', 'video__timems', 'video__id')[start:end]
        )
        players = [
            serialize_custom_pluck_record(record, rank)
            for rank, record in enumerate(records, start=start + 1)
        ]

    return {
        'count': count,
        'configs': {
            level_value: {
                'row': config[0],
                'column': config[1],
                'mine': config[2],
            }
            for level_value, config in CUSTOM_PLUCK_CONFIGS.items()
        },
        'players': players,
    }


@router.post('/pluck/refresh', response=RefreshCustomPluckRankOut)
@decorate_view(staff_required)
def refresh_pluck_rank(request):
    return {'records': refresh_all_custom_pluck_ranks()}
