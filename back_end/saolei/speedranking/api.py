from django_ratelimit.decorators import ratelimit
from ninja import Router, Schema
from ninja.decorators import decorate_view

from .cache import SpeedRankingCache
from .utils import Board, public_record, RankStat

router = Router()


class RecordOut(Schema):
    player_id: int
    bt: int | None
    bb: float | None
    it: int | None
    ib: float | None
    et: int | None
    eb: float | None
    sumt: int
    sumb: float
    bt_id: int | None
    bb_id: int | None
    it_id: int | None
    ib_id: int | None
    et_id: int | None
    eb_id: int | None


class RankingOut(Schema):
    count: int
    players: list[RecordOut]


@router.get('/rank', response=RankingOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_ranking(request, board: Board = 'saolei', stat: RankStat = 'sumt', start: int = 0, end: int = 20):
    """
    - ratelimit(key='ip', rate='5/s')
    """
    start = max(0, start)
    end = min(max(start, end), start + 100)
    return SpeedRankingCache(board).get_range(stat, start, end)


@router.get('/player/{player_id}', response=RecordOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_player_record(request, player_id: int, board: Board = 'saolei'):
    """
    - ratelimit(key='ip', rate='5/s')
    """
    return public_record(player_id, SpeedRankingCache(board).get_record(player_id))
