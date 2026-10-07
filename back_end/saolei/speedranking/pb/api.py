from datetime import datetime
from typing import Annotated

from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from pydantic import Field

from userprofile.decorators import staff_required
from userprofile.models import UserProfile
from .cache import PBRankingCache
from .services import rebuild_player_record
from .utils import PBLevel

router = Router()
PositiveInt = Annotated[int, Field(gt=0)]


class PBRecordOut(Schema):
    video_id: int
    timems: int
    rank: int | None


class PBPlayerRecordOut(PBRecordOut):
    level: PBLevel
    bv: int
    nf: bool


class PBRankingRowOut(PBRecordOut):
    player_id: int
    upload_time: datetime


class PBRankingOut(Schema):
    count: int
    players: list[PBRankingRowOut]


@router.get('/counts', response=dict[str, int])
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_counts(request):
    """
    - ratelimit(key='ip', rate='5/s')

    一次读取所有普通/NF PB 小榜人数。
    """
    return PBRankingCache().get_counts()


@router.get('/rank', response=PBRankingOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_ranking(request, level: PBLevel, bv: PositiveInt, nf: bool = False, start: int = 0, end: int = 20):
    """
    - ratelimit(key='ip', rate='5/s')
    """
    start = max(0, start)
    end = min(max(start, end), start + 100)
    return PBRankingCache().get_range(nf, level, bv, start, end)


@router.get('/player/{player_id}', response=list[PBPlayerRecordOut])
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_player_records(request, player_id: int):
    """
    - ratelimit(key='ip', rate='5/s')

    一次读取用户 rank hash，不逐榜查询排名。
    """
    return PBRankingCache().get_player_records(player_id)


@router.post('/admin/rebuild_record', response=PBPlayerRecordOut | None)
@decorate_view(staff_required)
def rebuild_record(request, player_id: Form[int], level: Form[PBLevel], bv: Form[PositiveInt], nf: Form[bool] = False):
    """
    - staff_required

    从数据库重建用户的 PB 小榜纪录，并刷新该小榜 rank hash。
    """
    if not UserProfile.objects.filter(pk=player_id).exists():
        raise HttpError(404, 'User not found')
    return rebuild_player_record(player_id, level, bv, nf)
