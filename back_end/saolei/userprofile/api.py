import mimetypes
import os

from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from ninja import Router

from .models import UserProfile

router = Router()


@router.get('/avatar/{user_id}')
def get_user_avatar(request, user_id: int):
    user = get_object_or_404(UserProfile, id=user_id)
    if not user.avatar or not os.path.exists(user.avatar.path):
        return HttpResponseNotFound()
    content_type, _ = mimetypes.guess_type(user.avatar.path)
    return FileResponse(open(user.avatar.path, 'rb'), content_type=content_type or 'image/jpeg')
