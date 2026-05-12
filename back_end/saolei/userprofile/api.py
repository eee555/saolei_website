import mimetypes
import os

from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja import File, Router, Schema, UploadedFile

from .models import UserProfile

router = Router()


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
