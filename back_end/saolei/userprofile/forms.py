from django import forms
# from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()
from captcha.fields import CaptchaField

# 登录表单，继承了 forms.Form 类


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class UserRegisterForm(forms.ModelForm):
    # 复写 User 的密码
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=30)
    # usertoken = forms.CharField(max_length=32, min_length=32)
    usertoken = forms.CharField(max_length=2000, min_length=2)
    date_joined = forms.CharField(required=False)
    # password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', "password", "groups", "user_permissions",
                  "is_staff", "is_active", "last_login", "date_joined")
        # 自定义错误消息
        error_messages = {
            'username': {
                'max_length': '最多不能超过20个字符！',
            },
            'usertoken': {
                'max_length': '最多不能超过20个字符！',
                'min_length': '最少不能少于20个字符！'
            },
        }
        
        # 对两次输入的密码是否一致进行检查
    # def clean_password2(self):
    #     data = self.cleaned_data
    #     if data.get('password') == data.get('password2'):
    #         return data.get('password')
    #     else:
    #         raise forms.ValidationError("密码输入不一致,请重试。")

class UserRegisterCaptchaForm(forms.ModelForm):
    # 注册时验证码的表单
    captcha = CaptchaField()

    


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('phone', 'avatar', 'bio')
