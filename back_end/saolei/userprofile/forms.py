from django import forms
# from .models import Profile
from django.contrib.auth import get_user_model
from config.global_settings import MaxSizes, MinSizes
from config.messages import FormErrors
User = get_user_model()


# 登录表单，继承了 forms.Form 类
class UserLoginForm(forms.Form):
    username = forms.CharField(min_length=1, max_length=MaxSizes.username)
    password = forms.CharField(min_length=1, max_length=MaxSizes.password)
    captcha = forms.CharField(min_length=1, max_length=6)
    hashkey = forms.CharField(min_length=8, max_length=512)


# 获取邮箱验证码时的表单，检查邮箱格式用
class EmailForm(forms.Form):
    email = forms.EmailField(max_length=MaxSizes.email, required=True, error_messages=FormErrors.email)
    captcha = forms.CharField(required=True)
    hashkey = forms.CharField(required=True)


# 注册表单
class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(min_length=1, max_length=MaxSizes.username, required=True, error_messages=FormErrors.username)
    password = forms.CharField(max_length=MaxSizes.password, min_length=MinSizes.password, required=True, error_messages=FormErrors.password)
    email = forms.EmailField(min_length=4, max_length=MaxSizes.email, required=True, error_messages=FormErrors.email)

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
class UserRetrieveForm(forms.Form):
    password = forms.CharField(max_length=MaxSizes.password, min_length=MinSizes.password, required=True)
    email = forms.EmailField(max_length=MaxSizes.email, required=True)

    class Meta:
        # 自定义错误消息
        error_messages = {
            'email': FormErrors.email,
            'password': FormErrors.password
        }


# class UserRegisterCaptchaForm(forms.ModelForm):
#     # 注册时验证码的表单
#     captcha = CaptchaField()


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('phone', 'avatar', 'bio')
