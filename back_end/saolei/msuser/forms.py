# 引入表单类
from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
# 引入 User 模型
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


# 更新我的地盘里的头像、姓名、个性签名
class UserUpdateForm(forms.ModelForm):
    realname = forms.CharField(max_length=10,  required=False)
    # 头像
    avatar = forms.ImageField(required=False)
    # 个性签名
    signature = forms.CharField(max_length=188,required=False)# 签名
    class Meta:
        model = User
        fields = ("realname", "avatar", "signature")





