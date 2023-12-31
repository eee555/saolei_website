from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core import validators
from msuser.models import UserMS
from .fields import RestrictedImageField
from django_cleanup import cleanup
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
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
                              unique=True,
                              error_messages={
                                  "unique": _("该邮箱已被注册！"),
                                  },)

    realname = models.CharField(
        max_length=10, unique=False, blank=True, default='请修改为实名', null=False)
    # 头像
    avatar = RestrictedImageField(upload_to='assets/avatar/%Y%m%d/', max_length=100,
                                  max_upload_size=1024*300, blank=True, null=True)
    # 签名
    signature = models.TextField(max_length=188, blank=True, null=True)  # 签名
    country = models.CharField(max_length=3, blank=True, null=True)
    is_banned = models.BooleanField(default=False, blank=False)


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
