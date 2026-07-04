from datetime import datetime

from django_ratelimit.decorators import ratelimit
from ninja import Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError

from config.customranking import CUSTOM_PLUCK_CONFIGS
from userprofile.decorators import staff_required
from .models import CustomPluckRecord
from .services import get_custom_pluck_cache_range
from .tasks import task_refresh_all_custom_pluck_ranks
from .utils import CUSTOM_PLUCK_CACHE_SIZE

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


class RefreshCustomPluckRankOut(Schema):
    task_id: int


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

    players = get_custom_pluck_cache_range(level, start, end)

    return {
        'count': count,
        'players': players,
    }


@router.post('/pluck/refresh', response=RefreshCustomPluckRankOut)
@decorate_view(staff_required)
def refresh_pluck_rank(request):
    task_result = task_refresh_all_custom_pluck_ranks.enqueue().db_result
    return {'task_id': task_result.id}
