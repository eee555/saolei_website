import logging
import mimetypes
import os
from typing import List

from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control
from django_ratelimit.decorators import ratelimit
from ninja import File, Form, Router, Schema, UploadedFile
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.orm import create_schema

from utils import verify_image
from utils.exceptions import ExceptionToResponse
from videomanager.models import VideoModel
from .decorators import banned_blocked, login_required_error
from .models import UserProfile
from .services import refresh_avatar_chance, try_update_user_name_fields, try_update_user_signature

router = Router()
logger = logging.getLogger('userprofile')


UserInfoOut = create_schema(
    UserProfile,
    fields=[
        'id', 'username',
        'firstname', 'lastname', 'realname',
        'signature', 'country',
        'is_banned', 'is_staff',
        'last_change_avatar', 'last_change_signature',
        'left_avatar_n', 'left_signature_n',
    ],
)


@router.get('/info/{user_id}', response=UserInfoOut)
@decorate_view(cache_control(max_age=5))
def get_user_info(request, user_id: int):
    """
    - Rate limited by nginx
    - cache_control(max_age=5)
    """
    if user_id == 0:
        if request.user.is_authenticated:
            return request.user
        raise HttpError(401, 'Unauthorized')
    return get_object_or_404(UserProfile, id=user_id)


@router.get('/identifier', response=List[str])
@decorate_view(ratelimit(key='ip', rate='2/s'))
def get_user_identifier(request, user_id: int):
    """
    - ratelimit(key='ip', rate='2/s')
    """
    user = get_object_or_404(UserProfile, id=user_id)
    return user.userms.identifiers


@router.get('/avatar/{user_id}')
@decorate_view(cache_control(max_age=5))
def get_user_avatar(request, user_id: int):
    """
    - Rate limited by nginx
    - cache_control(max_age=5)
    """
    user = get_object_or_404(UserProfile, id=user_id)
    if not user.avatar or not os.path.exists(user.avatar.path):
        return HttpResponseNotFound()
    content_type, _ = mimetypes.guess_type(user.avatar.path)
    return FileResponse(open(user.avatar.path, 'rb'), content_type=content_type or 'image/jpeg')


UserVideoOut = create_schema(
    VideoModel,
    fields=[
        'id',
        'upload_time', 'level', 'mode', 'timems', 'bv',
        'state', 'software', 'cl', 'ce', 'file_size',
        'end_time', 'ongoing_tournament', 'path',
    ],
)


@router.get('/videolist', response=List[UserVideoOut])
@decorate_view(ratelimit(key='ip', rate='1/s'))
def get_user_videos(request, user_id: int):
    """
    - ratelimit(key='ip', rate='1/s')
    """
    user = get_object_or_404(UserProfile, id=user_id)
    queryset = VideoModel.objects.filter(player=user)
    if user != request.user:
        queryset = queryset.filter(ongoing_tournament=False)
    videos = queryset.values('id', 'upload_time', 'level', 'mode', 'timems', 'bv', 'state', 'software', 'cl', 'ce', 'file_size', 'end_time', 'ongoing_tournament', 'path')
    return list(videos)


class UpdateUserProfileIn(Schema):
    realname: str = None
    signature: str = None
    firstname: str = None
    lastname: str = None


@router.post('/update_profile')
@decorate_view(
    banned_blocked,
    login_required_error,
    ratelimit(key='ip', rate='1/m'),
)
def update_user_profile(request: HttpRequest, data: UpdateUserProfileIn = Form(...)):  # noqa: B008
    """
    - login_required_error
    - banned_blocked
    - ratelimit(key='ip', rate='1/m')

    ### Example response
    ```json
    {
        "realname": {"type": "success"},
        "signature": None,
        "firstname": {"type": "error", "object": "firstname", "category": "validation"},
        "lastname": {"type": "error", "object": "censorship", "category": "illegal"}
    }
    ```

    ### Reference
    Response is a `dict[str, None | dict]`. The keys are `realname`, `signature`, `firstname` and `lastname`. For the values,
    - If the field is not requested, the value is `None`.
    - If the field is successfully updated (including the case where the value doesn't change), the value is `{"type": "success"}`.
    - If the field is not successfully updated, the value is `{"type": "error", "object": str, "category": str}`. The cases for `object` and `category` are listed below.

    |object|category|Description|
    |---|---|---|
    |censorship|unknown|The censorship backend raises an unexpected exception.|
    |censorship|illegal|The realname is blocked by censorship.|
    |database|validation|The value doesn't pass the database's validation.|
    |name|exist|The name fields cannot be updated after they are set. The user must contact a moderator to request a change.|
    |signature|cooldown|The user doesn't have budget for this service.|
    |signature|expTime|The signature can only be updated by a sub200 player.|

    ### 403 Forbidden
    If the user doesn't have permission to update any of the fields:
    - The user is not logged in.
    - The user is banned.
    """
    user: UserProfile = request.user
    user_ip = request.get_host()

    data_out: dict[str, None | dict] = {
        'realname': None,
        'firstname': None,
        'lastname': None,
        'signature': None,
    }
    success_out = {'type': 'success'}

    for name_field in ['realname', 'firstname', 'lastname']:
        name_value = getattr(data, name_field)
        if name_value is None:
            continue
        try:
            try_update_user_name_fields(user, name_field, name_value, user_ip)
        except ExceptionToResponse as e:
            data_out[name_field] = e.body

        data_out[name_field] = success_out

    if (signature := data.signature) is not None:
        try:
            try_update_user_signature(user, signature, user_ip)
            data_out['signature'] = success_out
        except ExceptionToResponse as e:
            data_out['signature'] = e.body

    return data_out


@router.post('/update_avatar')
@decorate_view(
    login_required_error,
    banned_blocked,
    ratelimit(key='ip', rate='1/m'),
)
def update_user_avatar(request, avatar: File[UploadedFile]):
    """
    - login_required_error
    - banned_blocked
    - ratelimit(key='ip', rate='1/m')

    ### Success response
    ```json
    {"type": "success"}
    ```

    ### Error response
    ```json
    {"type": "error", "object": str, "category": str}
    ```
    |object|category|Description|
    |---|---|---|
    |avatar|validation|The file doesn't pass the database's validation.|
    |censorship|unknown|The censorship backend raises an unexpected exception.|
    |censorship|illegal|The realname is blocked by censorship.|

    ### 403 Forbidden
    The request should not have been sent from a normal frontend.
    - The user is not logged in.
    - The user is not a sub200 player.
    - The user doesn't have enough budget for the service.
    """
    user: UserProfile = request.user

    if user.userms.e_timems_std >= 200000:
        raise HttpResponseForbidden

    refresh_avatar_chance(user)
    if user.left_avatar_n <= 0:
        return HttpResponseForbidden()

    try:
        is_valid = verify_image(avatar.read(), user.id, request.get_host())
    except Exception:
        raise ExceptionToResponse('censorship', 'unknown')

    if not is_valid:
        raise ExceptionToResponse('censorship', 'illegal')

    user.avatar = avatar
    user.left_avatar_n -= 1
    logger.info(f'用户 {user.username}#{user.id} 修改头像')
    try:
        user.save(update_fields=['avatar', 'left_avatar_n'])
    except ValidationError:
        raise ExceptionToResponse('avatar', 'validation')

    return {'type': 'success'}
