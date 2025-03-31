from captcha.models import CaptchaStore
from django.utils import timezone
from .models import EmailVerifyRecord
from .models import UserProfile
from videomanager.models import VideoModel
import os
from django.conf import settings
import urllib.parse
import base64


# 验证验证码
def judge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        get_captcha = CaptchaStore.objects.filter(
            hashkey=captchaHashkey).first()
        if get_captcha and get_captcha.response == captchaStr.lower():
            # 图形验证码15分钟有效，get_captcha.expiration是过期时间
            if (get_captcha.expiration - timezone.now()).seconds >= 0:
                CaptchaStore.objects.filter(hashkey=captchaHashkey).delete()
                return True
    CaptchaStore.objects.filter(hashkey=captchaHashkey).delete()
    return False


def judge_email_verification(email, email_captcha, emailHashkey):
    if not emailHashkey or not email or not email_captcha:
        return False
    get_email_captcha = EmailVerifyRecord.objects.filter(hashkey=emailHashkey).first()
    if not get_email_captcha:
        return False
    if (timezone.now() - get_email_captcha.send_time).seconds > 3600:
        EmailVerifyRecord.objects.filter(hashkey=emailHashkey).delete()
        return False
    return get_email_captcha.code == email_captcha and get_email_captcha.email == email


def user_metadata(user: UserProfile):
    if user.avatar:
        avatar_path = os.path.join(settings.MEDIA_ROOT, urllib.parse.unquote(user.avatar.url)[7:])
        image_data = open(avatar_path, "rb").read()
        image_data = base64.b64encode(image_data).decode()
    else:
        image_data = None

    videos = VideoModel.objects.filter(player=user).values('id', 'upload_time', "level", "mode", "timems", "bv", "state", "software", "cl", "ce", "file_size")
    return {
        "id": user.id,
        "username": user.username,
        "realname": user.realname,
        "avatar": image_data,
        "signature": user.signature,
        "popularity": user.popularity,
        "identifiers": user.userms.identifiers,
        "is_banned": user.is_banned,
        "is_staff": user.is_staff,
        "country": user.country,
        "videos": list(videos),
    }
