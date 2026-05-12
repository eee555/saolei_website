
from datetime import datetime, timezone
import json
import logging
from typing import Literal
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django_redis import get_redis_connection
from config.global_settings import GameModes, RankingGameStats
from userprofile.models import EmailVerifyRecord, UserProfile
from userprofile.utils import count_new_avatar_chance, count_new_signature_chance
from utils import generate_code, verify_text
from utils.exceptions import ExceptionToResponse
from videomanager.models import VideoModel

cache = get_redis_connection('saolei_website')
logger = logging.getLogger('userprofile')


# 用户修改自己的名字后，同步修改redis缓存里的真实姓名，使得排行榜数据同步修改
# 开销较大
def update_cache_realname(user_id, user_realname):
    for index in RankingGameStats:
        for mode in GameModes:
            key = f'player_{index}_{mode}_{user_id}'
            if cache.exists(key):
                cache.hset(key, 'name', user_realname)
    # 遍历并修改最新录像
    for video_id, value in cache.hgetall('newest_queue').items():
        new_value = json.loads(value)
        if new_value['player_id'] == user_id:
            new_value['player'] = user_realname
            # 将修改后的值存回哈希表
            cache.hset('newest_queue', video_id, json.dumps(new_value))
    # 遍历并修改审查队列
    for video_id, value in cache.hgetall('review_queue').items():
        new_value = json.loads(value)
        if new_value['player_id'] == user_id:
            new_value['player'] = user_realname
            # 将修改后的值存回哈希表
            cache.hset('review_queue', video_id, json.dumps(new_value))


NAME_DEFAULT = {
    'realname': '匿名',
    'firstname': '',
    'lastname': '',
}


def try_update_user_name_fields(user: UserProfile, field_name: Literal['realname', 'firstname', 'lastname'], field_value: str, user_ip: str):
    old_value = getattr(user, field_name)
    if old_value == field_value:
        return

    if getattr(user, field_name) != NAME_DEFAULT[field_name]:
        raise ExceptionToResponse('name', 'exist')

    try:
        is_valid = verify_text(field_value, user.id, user_ip)
    except Exception:
        raise ExceptionToResponse('censorship', 'unknown')

    if not is_valid:
        raise ExceptionToResponse('censorship', 'illegal')

    setattr(user, field_name, field_value)
    try:
        user.save(update_fields=[field_name])
    except ValidationError:
        raise ExceptionToResponse('database', 'validation')

    logger.info(f'用户 {user.username}#{user.id} 设置 {field_name} 为 "{field_value}"')
    return


def try_update_user_signature(user: UserProfile, signature: str, user_ip: str):
    if user.signature == signature:
        return

    if user.userms.e_timems_std >= 200000:
        raise ExceptionToResponse('signature', 'expTime')

    refresh_signature_chance(user)
    if user.left_signature_n <= 0:
        raise ExceptionToResponse('signature', 'cooldown')

    try:
        is_valid = verify_text(signature, user.id, user_ip)
    except Exception:
        raise ExceptionToResponse('censorship', 'unknown')

    if not is_valid:
        raise ExceptionToResponse('censorship', 'illegal')

    user.signature = signature
    user.left_signature_n -= 1
    try:
        user.save(update_fields=['signature', 'left_signature_n'])
    except ValidationError:
        raise ExceptionToResponse('database', 'validation')

    return


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
    queryset = VideoModel.objects.filter(player=user)
    if client != user:
        queryset = queryset.filter(ongoing_tournament=False)
    videos = queryset.values('id', 'upload_time', 'level', 'mode', 'timems', 'bv', 'state', 'software', 'cl', 'ce', 'file_size', 'end_time', 'ongoing_tournament', 'path')
    return {
        'id': user.id,
        'username': user.username,
        'realname': user.realname,
        'signature': user.signature,
        'popularity': user.popularity,
        'identifiers': user.userms.identifiers,
        'is_banned': user.is_banned,
        'is_staff': user.is_staff,
        'country': user.country,
        'videos': list(videos),
    }


def refresh_avatar_chance(user: UserProfile):
    now = datetime.now(timezone.utc)
    new_avatar = count_new_avatar_chance(user.last_change_avatar, now)

    if new_avatar > 0:
        user.left_avatar_n += new_avatar
        user.last_change_avatar = now
        user.save(update_fields=['left_avatar_n', 'last_change_avatar'])

    return


def refresh_signature_chance(user: UserProfile):
    now = datetime.now(timezone.utc)
    new_signature = count_new_signature_chance(user.last_change_signature, now)

    if new_signature > 0:
        user.left_signature_n += new_signature
        user.last_change_signature = now
        user.save(update_fields=['left_signature_n', 'last_change_signature'])

    return
