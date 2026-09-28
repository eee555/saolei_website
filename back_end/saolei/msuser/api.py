import logging

from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from ninja import Form, Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.orm import create_schema

from config.global_settings import GameLevels, GameModes, RankingGameStats
from userprofile.decorators import staff_required
from userprofile.models import UserProfile
from .models import UserMS

router = Router()
logger = logging.getLogger('msuser')

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

AdminUserMSOut = create_schema(
    UserMS,
    fields=['identifiers', 'video_num_limit'],
)

AdminUserMSUpdateIn = create_schema(
    UserMS,
    fields=['video_num_limit'],
    optional_fields='__all__',
)


@router.patch('/admin/update/{userms_id}', response=AdminUserMSOut)
@decorate_view(staff_required)
def update_user_ms_admin(request, userms_id: int, data: AdminUserMSUpdateIn = Form(...)):  # noqa: B008
    """
    - staff_required
    """
    user: UserProfile = get_object_or_404(UserMS, id=userms_id).parent
    if user is not None and user.is_staff and user != request.user:
        raise HttpError(403, 'Cannot update another staff user.')

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user.userms, field, value)

    if userms_update_fields := list(updates.keys()):
        user.userms.save(update_fields=userms_update_fields)
        logger.warning(f'管理员 {request.user.username}#{request.user.id} 修改用户 #{user.id} UserMS {", ".join(userms_update_fields)}')

    return user.userms


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
