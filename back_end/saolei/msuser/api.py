from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from ninja import Router
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.global_settings import GameLevels, GameModes, RankingGameStats
from .models import UserMS

router = Router()

RECORD_ABSTRACT_STATS = ('timems', 'bvs')

UserMSRecordsOut = create_schema(
    UserMS,
    fields=[
        field
        for mode in GameModes
        for stat in RankingGameStats
        for level in GameLevels
        for field in (
            f'{level}_{stat}_{mode}',
            f'{level}_{stat}_id_{mode}',
        )
    ],
)

UserMSRecordsAbstractOut = create_schema(
    UserMS,
    fields=[
        field
        for stat in RECORD_ABSTRACT_STATS
        for level in GameLevels
        for field in (
            f'{level}_{stat}_std',
            f'{level}_{stat}_id_std',
        )
    ],
)


@router.get('/records', response=UserMSRecordsOut)
@decorate_view(ratelimit(key='ip', rate='15/m'))
def get_records(request, user_id: int):
    """
    - ratelimit(key='ip', rate='15/m')
    """
    return get_object_or_404(UserMS, parent__id=user_id)


@router.get('/records_abstract', response=UserMSRecordsAbstractOut)
@decorate_view(ratelimit(key='ip', rate='5/s'))
def get_records_abstract(request, user_id: int):
    """
    - ratelimit(key='ip', rate='5/s')
    """
    return get_object_or_404(UserMS, parent__id=user_id)
