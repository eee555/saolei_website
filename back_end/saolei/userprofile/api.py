from datetime import datetime
import logging
import mimetypes
import os

from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from ninja import File, Router, Schema, UploadedFile
from ninja.decorators import decorate_view

from userprofile.decorators import banned_blocked, login_required_error
from userprofile.services import refresh_avatar_chance, try_update_user_name_fields, try_update_user_signature
from utils import verify_image
from utils.exceptions import ExceptionToResponse

from .models import UserProfile

router = Router()
logger = logging.getLogger('userprofile')


class UserInfoOut(Schema):
    id: int
    firstname: str
    lastname: str
    realname: str
    signature: str
    country: str
    is_banned: bool
    last_change_avatar: datetime
    last_change_signature: datetime


@router.get('/info', response=UserInfoOut)
def get_user_info(request, user_id: int):
    user = get_object_or_404(UserProfile, id=user_id)

    return {
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'realname': user.realname,
        'signature': user.signature,
        'country': user.country,
        'is_banned': user.is_banned,
        'last_change_avatar': user.last_change_avatar,
        'last_change_signature': user.last_change_signature,
    }


@router.get('/avatar/{user_id}')
def get_user_avatar(request, user_id: int):
    user = get_object_or_404(UserProfile, id=user_id)
    if not user.avatar or not os.path.exists(user.avatar.path):
        return HttpResponseNotFound()
    content_type, _ = mimetypes.guess_type(user.avatar.path)
    return FileResponse(open(user.avatar.path, 'rb'), content_type=content_type or 'image/jpeg')


class UpdateUserProfileIn(Schema):
    realname: str = None
    signature: str = None
    firstname: str = None
    lastname: str = None


@router.post('/update_profile')
@decorate_view(login_required_error, banned_blocked)
def update_user_profile(request: HttpRequest, data: UpdateUserProfileIn):
    """
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
        except ExceptionToResponse as e:
            data_out['signature'] = e.body

        data_out['signature'] = success_out

    return data_out


@router.post('/update_avatar')
@decorate_view(login_required_error, banned_blocked)
def update_user_avatar(request, avatar: File[UploadedFile]):
    """
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
