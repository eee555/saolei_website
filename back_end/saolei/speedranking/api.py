from django_ratelimit.decorators import ratelimit
from ninja import Router, Schema
from ninja.decorators import decorate_view

from .cache import get_player_records, SpeedRankingCache
from .utils import RankingName, RankStat

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


class PlayerRecordOut(RecordOut):
    ranks: dict[RankStat, int | None]


class RankingOut(Schema):
    count: int
    players: list[RecordOut]


@router.get('/rank', response=RankingOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_ranking(request, ranking_name: RankingName = 'saolei', stat: RankStat = 'sumt', start: int = 0, end: int = 20):
    """
    - ratelimit(key='ip', rate='5/s')
    """
    start = max(0, start)
    end = min(max(start, end), start + 100)
    return SpeedRankingCache(ranking_name).get_range(stat, start, end)


@router.get('/player/{player_id}', response=dict[RankingName, PlayerRecordOut])
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_player_record(request, player_id: int):
    """
    - ratelimit(key='ip', rate='5/s')
    """
    return get_player_records(player_id)
