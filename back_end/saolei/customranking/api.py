from datetime import datetime

from ninja import Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.throttling import AnonRateThrottle

from userprofile.decorators import staff_required
from .config import CUSTOM_PLUCK_CONFIGS, CUSTOM_PLUCK_MODES
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
    pluck: float
    timems: int
    bv: int
    upload_time: datetime


class CustomPluckRankOut(Schema):
    count: int
    total_page: int
    page: int
    configs: dict[str, CustomPluckConfigOut]
    players: list[CustomPluckPlayerOut]


class RefreshCustomPluckRankOut(Schema):
    records: int


@router.get('/pluck', response=CustomPluckRankOut, throttle=[AnonRateThrottle('60/m')])
def pluck_rank(request, level: str, mode: str, page: int = 1, page_size: int = 20):
    """
    - Throttle: AnonRateThrottle('60/m')
    """
    if level not in CUSTOM_PLUCK_CONFIGS or mode not in CUSTOM_PLUCK_MODES:
        raise HttpError(400, 'Invalid custom pluck ranking level or mode')

    page_size = min(max(page_size, 1), 100)
    count = CustomPluckRecord.objects.filter(level=level, mode=mode).count()
    total_page = (count + page_size - 1) // page_size
    page = min(max(page, 1), max(total_page, 1))
    start_rank = (page - 1) * page_size
    end_rank = start_rank + page_size

    if end_rank <= CUSTOM_PLUCK_CACHE_SIZE:
        players = get_custom_pluck_top_cache(level, mode)[start_rank:end_rank]
    else:
        records = (
            CustomPluckRecord.objects
            .filter(level=level, mode=mode)
            .select_related('player', 'video')
            .order_by('pluck', 'video__timems', 'video__id')[start_rank:end_rank]
        )
        players = [
            serialize_custom_pluck_record(record, rank)
            for rank, record in enumerate(records, start=start_rank + 1)
        ]

    return {
        'count': count,
        'total_page': total_page,
        'page': page,
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
