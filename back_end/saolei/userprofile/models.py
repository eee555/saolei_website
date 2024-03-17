import os
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core import validators
from msuser.models import UserMS
from .fields import RestrictedImageField
from django_cleanup import cleanup
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
username_validator = UnicodeUsernameValidator()

# 自定义用户
# 头像修改后，自动删除服务器上原来的图片
@cleanup.select
class UserProfile(AbstractUser):
    userms = models.OneToOneField(
        UserMS, on_delete=models.CASCADE, related_name='+', null=True)
    
    username = models.CharField(
        _("username"),
        max_length=20,
        unique=True,
        help_text=_(
            "Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            'max_length': _('用户名的长度不超过20，支持各国语言！'),
            "unique": _("该用户名已存在！"),
        },
    )
    first_name = models.CharField(_("first name"), max_length=10, blank=True)
    last_name = models.CharField(_("last name"), max_length=10, blank=True)
    email = models.EmailField(_("email address"), 
                              max_length=100,
                              unique=True,
                              blank=False, 
                              null=False, 
                              error_messages={
                                  "blank": _("必须填写邮箱！"),
                                  "invalid": _("邮箱格式不正确！"),
                                  "unique": _("该邮箱已被注册！"),
                                  "max_length": _("邮箱的长度不能超过100！"),
                                  },)

    realname = models.CharField(
        max_length=10, unique=False, blank=True, default='请修改为实名', null=False)
    # 头像
    avatar = RestrictedImageField(upload_to='assets/avatar/%Y%m%d/', max_length=100,
                                  max_upload_size=1024*300, blank=True, null=True)
    # 签名
    signature = models.TextField(max_length=188, blank=True, null=True)  # 签名
    country = models.CharField(max_length=3, blank=True, null=True)
    # 封禁用户，禁止上传录像、头像、签名
    is_banned = models.BooleanField(default=False, blank=False)
    # 剩余修改真实姓名的次数，0~32767
    left_realname_n = models.PositiveSmallIntegerField(null=False, default=1)
    # 剩余修改头像次数，0~32767
    left_avatar_n = models.PositiveSmallIntegerField(null=False, default=2)
    # 最近修改头像时间
    last_change_avatar = models.DateTimeField(default=timezone.now)
    # 剩余修改签名次数，0~32767
    left_signature_n = models.PositiveSmallIntegerField(null=False, default=2)
    # 最近修改签名时间
    last_change_signature = models.DateTimeField(default=timezone.now)
    # 人气
    popularity = models.BigIntegerField(null=False, default=0)
    # vip，0为非vip，理论0~32767。类似于权限
    vip = models.PositiveSmallIntegerField(null=False, default=0)
    def delete(self, *args, **kwargs):
        # 删除关联的文件
        if self.avatar:
            # 使用os库删除文件
            if os.path.isfile(self.avatar.path):
                os.remove(self.avatar.path)
        
        # 调用父类的delete方法删除数据库记录
        super(UserProfile, self).delete(*args, **kwargs)



# 邮箱验证
class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=8, verbose_name="验证码")
    email = models.EmailField(max_length=100, verbose_name="邮箱")
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
