import base64
import os
import urllib.parse
import uuid

# from captcha.models import CaptchaStore  # replaced by mine-sweeper captcha
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_redis import get_redis_connection

from utils import generate_code
from videomanager.models import VideoModel
from .mine_captcha_puzzles import PUZZLES
from .models import EmailVerifyRecord, UserProfile


_MINE_CAPTCHA_REDIS_PREFIX = 'mine_captcha:'
_MINE_CAPTCHA_BOTTOM_WIDTH = 5


def judge_captcha(captchaStr: str, captchaHashkey: str) -> bool:
    """
    Validate a mine-sweeper captcha submission.

    captchaStr: comma-separated 0-based indices of cells the user OPENED
                (i.e. believed to be safe / non-mines), e.g. "1,3".
                Order does not matter.
    captchaHashkey: the hashkey returned by refresh_captcha.

    Returns True iff the opened set exactly equals the puzzle's non-mine set
    (every safe cell opened, no mine cell opened). Deletes the redis key in
    all cases (one-shot, error-once-rotate-puzzle).
    """
    if not captchaStr or not captchaHashkey:
        return False

    conn = get_redis_connection('saolei_website')
    redis_key = f'{_MINE_CAPTCHA_REDIS_PREFIX}{captchaHashkey}'
    raw = conn.get(redis_key)
    if raw is None:
        return False
    conn.delete(redis_key)  # one-shot regardless of outcome

    try:
        puzzle_idx = int(raw)
        opened = {int(s) for s in captchaStr.split(',') if s.strip() != ''}
    except (ValueError, TypeError):
        return False

    if not opened:
        return False
    if any(i < 0 or i >= _MINE_CAPTCHA_BOTTOM_WIDTH for i in opened):
        return False
    if puzzle_idx < 0 or puzzle_idx >= len(PUZZLES):
        return False

    _, mine_positions = PUZZLES[puzzle_idx]
    safe_positions = set(range(_MINE_CAPTCHA_BOTTOM_WIDTH)) - set(mine_positions)
    return opened == safe_positions


# 发送邮件，根据send_type不同发送不同的邮件内容
def send_email(email: str, send_type='register'):
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
        image_data = open(avatar_path, 'rb').read()
        image_data = base64.b64encode(image_data).decode()
    else:
        image_data = None

    queryset = VideoModel.objects.filter(player=user)
    if client != user:
        queryset = queryset.filter(ongoing_tournament=False)
    videos = queryset.values('id', 'upload_time', 'level', 'mode', 'timems', 'bv', 'state', 'software', 'cl', 'ce', 'file_size', 'end_time', 'ongoing_tournament', 'path')
    return {
        'id': user.id,
        'username': user.username,
        'realname': user.realname,
        'avatar': image_data,
        'signature': user.signature,
        'popularity': user.popularity,
        'identifiers': user.userms.identifiers,
        'is_banned': user.is_banned,
        'is_staff': user.is_staff,
        'country': user.country,
        'videos': list(videos),
    }
