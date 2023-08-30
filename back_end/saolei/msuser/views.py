from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
# from .models import VideoModel, ExpandVideoModel
from django.http import HttpResponse, JsonResponse
# from asgiref.sync import sync_to_async
import json
from utils import ComplexEncoder
from django.core.paginator import Paginator
from msuser.models import UserMS

# 根据id获取用户的基本资料、扫雷记录
# 无需登录就可获取

# 获取我的地盘里的头像、姓名、个性签名、记录


def get_info(request):
    if request.method == 'GET':
        # print(request.GET)
        user_id = request.GET["id"]
        user = UserMS.objects.get(id=user_id)
        response = {"realname": user.realname,
                    "avatar": request.build_absolute_uri(user.avatar.url),
                    "signature": user.signature, }
        # print(response["avatar"])
        # print(response["realname"])
        # print(response["signature"])
        return JsonResponse(response)
    else:
        return HttpResponse("别瞎玩")

# 上传我的地盘里的头像、姓名、个性签名


@login_required(login_url='/')
def update(request):
    if request.method == 'POST':
        user_update_form = UserUpdateForm(
            data=request.POST, files=request.FILES)
        if user_update_form.is_valid():
            data = user_update_form.cleaned_data
            print(data)
            user = request.user
            user.realname = data["realname"]
            user.signature = data["signature"]
            user.avatar = data["avatar"]
            user.save()
            return JsonResponse({"status": 100, "msg": None})
        else:
            ErrorDict = user_update_form.errors
            return JsonResponse({"status": 101, "msg": ErrorDict})
    else:
        return HttpResponse("别瞎玩")
