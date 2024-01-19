from django import forms
# from .models import Profile
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()
from captcha.fields import CaptchaField

# 登录表单，继承了 forms.Form 类
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


# 获取邮箱验证码时的表单，检查邮箱格式用
class EmailForm(forms.Form):
    email = forms.EmailField(max_length=100, required=True,error_messages = {
            'max_length': '最多不能超过100个字符！',
            'required': '邮箱是必填项！',
            'invalid': '邮箱格式错误！',
        })


# 注册表单
class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(min_length=1, max_length=20, required=True,error_messages = {
        'max_length': '最多不能超过20个字符！',
        'required': '用户名是必填项！',
        'invalid': "非法用户名！"
        })
    password = forms.CharField(max_length=20, min_length=6, required=True, error_messages={
        'max_length': '最多不能超过20个字符！',
        'min_length': '最少不能少于6个字符！'
        })
    email = forms.EmailField(min_length=4, max_length=100, required=True, error_messages={
        'max_length': '最多不能超过100个字符！',
        'required': '邮箱是必填项！',
        'invalid': '邮箱格式错误！',
        })
    def clean_username(self):
        # 删去前后空格，长度不能少于1
        username = self.cleaned_data.get('username')
        # 普通的空格，django自己会删，只有下面这个，既是合法的unicode字符，又是不可见字符，同时django不会自动删
        username = username.strip("ㅤ")
        # 检查剩余可见字符长度至少为1
        if len(username) < 1:
            raise forms.ValidationError("别瞎玩！", code='invalid_username')
        return username

    class Meta:
        model = User
        fields = ("username", "password", "email")


# 找回密码表单
class UserRetrieveForm(forms.ModelForm):
    password = forms.CharField(max_length=20, min_length=6, required=True)
    email = forms.EmailField(max_length=100, required=True)

    class Meta:
        # 自定义错误消息
        error_messages = {
            'email': {
                'max_length': '最多不能超过100个字符！',
                'required': '邮箱是必填项！',
                'invalid': '邮箱格式错误！',
            },
            'password': {
                'max_length': '最多不能超过20个字符！',
                'min_length': '最少不能少于6个字符！'
            },
        }


# class UserRegisterCaptchaForm(forms.ModelForm):
#     # 注册时验证码的表单
#     captcha = CaptchaField()

    


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('phone', 'avatar', 'bio')
