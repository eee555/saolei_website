from captcha.models import CaptchaStore
from django.utils import timezone
from .models import EmailVerifyRecord

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
