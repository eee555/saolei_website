from typing import Literal

from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError

from userprofile.decorators import staff_required
from userprofile.models import UserProfile
from .cache import TopRankingCache
from .services import rebuild_player_record
from .utils import record_field, TopLevel, TopStat

router = Router()


class TopRecordOut(Schema):
    player_id: int
    records: dict


class TopRankingOut(Schema):
    count: int
    players: list[TopRecordOut]


@router.get('/soft/rank', response=TopRankingOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_soft_ranking(request, ranking: Literal['lsf', 'std:b', 'std:i', 'std:e', 'std:sum', 'nf:b', 'nf:i', 'nf:e', 'nf:sum'] = 'lsf', start: int = 0, end: int = 20):
    """
    - ratelimit(key='ip', rate='5/s')

    九项派生排名只提供顺序，返回完整 top5；展示使用首次访问时取得的锚点。
    """
    start = max(0, start)
    end = min(max(start, end), start + 100)
    return TopRankingCache().get_range(ranking, start, end, soft=True)


@router.get('/rank', response=TopRankingOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_ranking(request, level: TopLevel, stat: TopStat, nf: bool = False, start: int = 0, end: int = 20):
    """
    - ratelimit(key='ip', rate='5/s')

    按指定小榜分页，返回各用户完整纪录；s 的成绩单位为 iqg。
    """
    start = max(0, start)
    end = min(max(start, end), start + 100)
    return TopRankingCache().get_range(record_field(nf, level, stat), start, end)


@router.get('/player/{player_id}', response=dict)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_player_records(request, player_id: int):
    """
    - ratelimit(key='ip', rate='5/s')

    一次读取用户完整纪录，保留 hash 中所有字段和录像明细。
    """
    return TopRankingCache().get_record(player_id)


@router.get('/anchors', response=dict)
@decorate_view(ratelimit(key='ip', rate='20/s'))
def get_anchors(request):
    """
    - ratelimit(key='ip', rate='20/s')

    即时读取十八个锚点缓存，不在请求中重新聚合。
    """
    return TopRankingCache().get_anchors()


@router.post('/admin/rebuild_record', response=TopRecordOut)
@decorate_view(staff_required)
def rebuild_record(request, player_id: Form[int], level: Form[TopLevel], stat: Form[TopStat], nf: Form[bool] = False):
    """
    - staff_required

    从录像库修复一个用户的小榜，并刷新对应锚点。
    """
    if not UserProfile.objects.filter(pk=player_id).exists():
        raise HttpError(404, 'User not found')
    return rebuild_player_record(player_id, level, stat, nf)
