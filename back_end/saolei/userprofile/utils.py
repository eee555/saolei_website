import base64
import os
import urllib.parse
import uuid

from captcha.models import CaptchaStore
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from utils import generate_code
from videomanager.models import VideoModel
from .models import EmailVerifyRecord, UserProfile


# 验证验证码
def judge_captcha(captchaStr: str, captchaHashkey):
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


# 发送邮件，根据send_type不同发送不同的邮件内容
def send_email(email, send_type='register'):
    email_record = EmailVerifyRecord()
    if settings.E2E_TEST:
        code = 'abcdef'
    else:
        code = generate_code(6)
    email_record.code = code
    # email_record.email = email
    hashkey = uuid.uuid4()
    email_record.hashkey = hashkey
    email_record.email = email
    # email_record.send_type = send_type
    email_record.save()

    # 验证码保存之后，我们就要把带有验证码的链接发送到注册时的邮箱！
    if settings.E2E_TEST:
        return hashkey
    if settings.EMAIL_SKIP:
        return code, hashkey
    if send_type == 'register':
        email_title = '开源扫雷网邮箱注册验证码'
        email_body = f'欢迎您注册开源扫雷网，您的邮箱验证码为：{code}（一小时内有效）。'
    elif send_type == 'retrieve':
        email_title = '开源扫雷网找回密码验证码'
        email_body = f'您正在找回密码。您的邮箱验证码为：{code}（一小时内有效）。请勿与任何人分享此代码，我们的管理员永远不会向您索要此代码。'
    else:
        return None
    send_status = send_mail(email_title, email_body, 'wangjianing@88.com', [email])
    if send_status:
        return hashkey
    else:
        return None


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


def user_metadata(user: UserProfile, client):
    if user.avatar:
        avatar_path = os.path.join(settings.MEDIA_ROOT, urllib.parse.unquote(user.avatar.url)[7:])
        image_data = open(avatar_path, "rb").read()
        image_data = base64.b64encode(image_data).decode()
    else:
        image_data = None

    queryset = VideoModel.objects.filter(player=user)
    if client != user:
        queryset = queryset.filter(ongoing_tournament=False)
    videos = queryset.values('id', 'upload_time', "level", "mode", "timems", "bv", "state", "software", "cl", "ce", "file_size", "end_time", "ongoing_tournament", 'path')
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
