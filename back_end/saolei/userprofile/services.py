from django.conf import settings
from django.core.mail import send_mail
from userprofile.models import EmailVerifyRecord, UserProfile
from utils import generate_code, verify_text


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
