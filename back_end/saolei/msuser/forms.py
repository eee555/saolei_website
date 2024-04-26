# 引入表单类
from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
# 引入 User 模型
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from utils import verify_text, verify_image
from django.utils import timezone


# 更新我的地盘里的姓名
class UserUpdateRealnameForm(forms.ModelForm):
    realname = forms.CharField(max_length=10,  required=True)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = self.request.user
        super(UserUpdateRealnameForm, self).__init__(*args, **kwargs)
    def clean_realname(self):
        realname = self.cleaned_data.get('realname')
        
        if self.user.left_realname_n <= 0:
            raise forms.ValidationError("姓名剩余修改次数不足！", code='no_times')
        else:
            self.user.left_realname_n -= 1
        try:
            is_valid = verify_text(realname, self.request.user.id, self.request.get_host())
        except:
            raise forms.ValidationError("网站已欠费，该功能暂停使用！", code='no_money')
        if not is_valid:
            raise forms.ValidationError("姓名违规！", code='invalid_realname')
        return realname
    
    class Meta:
        model = User
        fields = ("realname",)


# 更新我的地盘里的头像
class UserUpdateAvatarForm(forms.ModelForm):
    # 头像
    avatar = forms.ImageField(required=True)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = self.request.user
        super(UserUpdateAvatarForm, self).__init__(*args, **kwargs)
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        delta_t = timezone.now() - self.user.last_change_avatar
        n_add = delta_t.days // 365
        self.user.left_avatar_n += n_add
        self.user.last_change_avatar += timezone.timedelta(days=n_add * 365)
        
        if self.user.left_avatar_n <= 0:
            raise forms.ValidationError("头像剩余修改次数不足！", code='no_times')
        else:
            self.user.left_avatar_n -= 1
        try:
            is_valid = verify_image(avatar.read(), self.request.user.id, self.request.get_host())
        except:
            raise forms.ValidationError("网站已欠费，该功能暂停使用！", code='no_money')
        if not is_valid:
            raise forms.ValidationError("头像违规！", code='invalid_avatar')
        return avatar
    class Meta:
        model = User
        fields = ("avatar",)


# 更新我的地盘里的头像、姓名、个性签名
class UserUpdateSignatureForm(forms.ModelForm):
    # 个性签名
    signature = forms.CharField(max_length=188,required=True, error_messages={
        'max_length': '最多不能超过188个字符！'
        })# 签名
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = self.request.user
        super(UserUpdateSignatureForm, self).__init__(*args, **kwargs)
    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        delta_t = timezone.now() - self.user.last_change_signature
        n_add = delta_t.days // 365
        self.user.left_signature_n += n_add
        self.user.last_change_signature += timezone.timedelta(days=n_add * 365)
        # print(self.user.left_signature_n)
        if self.user.left_signature_n <= 0:
            raise forms.ValidationError("个性签名剩余修改次数不足！", code='no_times')
        else:
            self.user.left_signature_n -= 1
        try:
            is_valid = verify_text(signature, self.request.user.id, self.request.get_host())
        except:
            raise forms.ValidationError("网站已欠费，该功能暂停使用！", code='no_money')
        if not is_valid:
            raise forms.ValidationError("个性签名违规！", code='invalid_signature')
        return signature
    class Meta:
        model = User
        fields = ("signature",)        


