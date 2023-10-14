from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core import validators
from msuser.models import UserMS
from .fields import RestrictedImageField

# 自定义用户


class UserProfile(AbstractUser):
    userms = models.OneToOneField(
        UserMS, on_delete=models.CASCADE, related_name='+', null=True)
    realname = models.CharField(
        max_length=10, unique=False, blank=True, default='无名氏', null=False)
    # 头像
    avatar = RestrictedImageField(upload_to='assets/avatar/%Y%m%d/', max_length=100,
                                  max_upload_size=1024*1024, blank=True, null=True)
    # 签名
    signature = models.TextField(max_length=188, blank=True, null=True)  # 签名
    country = models.CharField(max_length=3, blank=True, null=True)

    # 邮箱验证


class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=8, verbose_name="验证码")
    # email = models.EmailField(max_length=50, verbose_name="邮箱")
    # 包含注册验证和找回验证
    # send_type = models.CharField(verbose_name="验证码类型", max_length=10,
    #                              choices=(("register", "注册"), ("forget", "找回密码")))
    send_time = models.DateTimeField(verbose_name="发送时间", auto_now_add=True)
    hashkey = models.CharField(max_length=40, unique=True, default='???')

    class Meta:
        verbose_name = u"2. 邮箱验证码"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0}({1})'.format(self.code, self.email)
