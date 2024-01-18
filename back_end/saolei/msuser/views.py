# from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
# from .models import VideoModel, ExpandVideoModel
from django.http import HttpResponse, JsonResponse
# from asgiref.sync import sync_to_async
import json
from utils import ComplexEncoder
# from django.core.paginator import Paginator
from msuser.models import UserMS
from userprofile.models import UserProfile
import base64
import decimal
import urllib.parse
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from django.conf import settings
import os
from django.utils import timezone
from datetime import datetime, timedelta


# 根据id获取用户的基本资料、扫雷记录
# 无需登录就可获取


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


# 获取我的地盘里的头像、姓名、个性签名
def get_info(request):
    if request.method == 'GET':
        # 此处要重点防攻击
        # user_id = request.user.id
        user_id = request.GET["id"]
        user = UserProfile.objects.get(id=user_id)
        # ms_user = UserMS.objects.get(id=request.user.userms_id)
        # ms_user = user.userms
        
        if user.avatar:
            avatar_path = os.path.join(settings.MEDIA_ROOT, urllib.parse.unquote(user.avatar.url)[7:])
            image_data = open(avatar_path, "rb").read()
            image_data = base64.b64encode(image_data).decode()
        else:
            image_data = None
        response = {"id": user_id,
                    "username": user.username,
                    "realname": user.realname,
                    "avatar": image_data,
                    "signature": user.signature,
                    }
        return JsonResponse(response)
    else:
        return HttpResponse("别瞎玩")


# 获取我的地盘里的姓名、全部纪录
def get_records(request):
    if request.method == 'GET':
        # 此处要重点防攻击
        user_id = request.GET["id"]
        user = UserProfile.objects.get(id=user_id)
        ms_user = user.userms

        response = {"id": user_id,
                    "realname": user.realname,
                    "std_record": json.dumps({"time": [ms_user.b_time_std, ms_user.i_time_std, ms_user.e_time_std],
                                             "bvs": [ms_user.b_bvs_std, ms_user.i_bvs_std, ms_user.e_bvs_std],
                                              "stnb": [ms_user.b_stnb_std, ms_user.i_stnb_std, ms_user.e_stnb_std],
                                              "ioe": [ms_user.b_ioe_std, ms_user.i_ioe_std, ms_user.e_ioe_std],
                                              "path": [ms_user.b_path_std, ms_user.i_path_std, ms_user.e_path_std],
                                              "time_id": [ms_user.b_time_id_std, ms_user.i_time_id_std, ms_user.e_time_id_std],
                                              "bvs_id": [ms_user.b_bvs_id_std, ms_user.i_bvs_id_std, ms_user.e_bvs_id_std],
                                              "stnb_id": [ms_user.b_stnb_id_std, ms_user.i_stnb_id_std, ms_user.e_stnb_id_std],
                                              "ioe_id": [ms_user.b_ioe_id_std, ms_user.i_ioe_id_std, ms_user.e_ioe_id_std],
                                              "path_id": [ms_user.b_path_id_std, ms_user.i_path_id_std, ms_user.e_path_id_std]}, cls=DecimalEncoder),
                    "nf_record": json.dumps({"time": [ms_user.b_time_nf, ms_user.i_time_nf, ms_user.e_time_nf],
                                             "bvs": [ms_user.b_bvs_nf, ms_user.i_bvs_nf, ms_user.e_bvs_nf],
                                             "stnb": [ms_user.b_stnb_nf, ms_user.i_stnb_nf, ms_user.e_stnb_nf],
                                             "ioe": [ms_user.b_ioe_nf, ms_user.i_ioe_nf, ms_user.e_ioe_nf],
                                             "path": [ms_user.b_path_nf, ms_user.i_path_nf, ms_user.e_path_nf],
                                             "time_id": [ms_user.b_time_id_nf, ms_user.i_time_id_nf, ms_user.e_time_id_nf],
                                             "bvs_id": [ms_user.b_bvs_id_nf, ms_user.i_bvs_id_nf, ms_user.e_bvs_id_nf],
                                             "stnb_id": [ms_user.b_stnb_id_nf, ms_user.i_stnb_id_nf, ms_user.e_stnb_id_nf],
                                             "ioe_id": [ms_user.b_ioe_id_nf, ms_user.i_ioe_id_nf, ms_user.e_ioe_id_nf],
                                             "path_id": [ms_user.b_path_id_nf, ms_user.i_path_id_nf, ms_user.e_path_id_nf]}, cls=DecimalEncoder),
                    "ng_record": json.dumps({"time": [ms_user.b_time_ng, ms_user.i_time_ng, ms_user.e_time_ng],
                                             "bvs": [ms_user.b_bvs_ng, ms_user.i_bvs_ng, ms_user.e_bvs_ng],
                                             "stnb": [ms_user.b_stnb_ng, ms_user.i_stnb_ng, ms_user.e_stnb_ng],
                                             "ioe": [ms_user.b_ioe_ng, ms_user.i_ioe_ng, ms_user.e_ioe_ng],
                                             "path": [ms_user.b_path_ng, ms_user.i_path_ng, ms_user.e_path_ng],
                                             "time_id": [ms_user.b_time_id_ng, ms_user.i_time_id_ng, ms_user.e_time_id_ng],
                                             "bvs_id": [ms_user.b_bvs_id_ng, ms_user.i_bvs_id_ng, ms_user.e_bvs_id_ng],
                                             "stnb_id": [ms_user.b_stnb_id_ng, ms_user.i_stnb_id_ng, ms_user.e_stnb_id_ng],
                                             "ioe_id": [ms_user.b_ioe_id_ng, ms_user.i_ioe_id_ng, ms_user.e_ioe_id_ng],
                                             "path_id": [ms_user.b_path_id_ng, ms_user.i_path_id_ng, ms_user.e_path_id_ng]}, cls=DecimalEncoder),
                    "dg_record": json.dumps({"time": [ms_user.b_time_dg, ms_user.i_time_dg, ms_user.e_time_dg],
                                             "bvs": [ms_user.b_bvs_dg, ms_user.i_bvs_dg, ms_user.e_bvs_dg],
                                             "stnb": [ms_user.b_stnb_dg, ms_user.i_stnb_dg, ms_user.e_stnb_dg],
                                             "ioe": [ms_user.b_ioe_dg, ms_user.i_ioe_dg, ms_user.e_ioe_dg],
                                             "path": [ms_user.b_path_dg, ms_user.i_path_dg, ms_user.e_path_dg],
                                             "time_id": [ms_user.b_time_id_dg, ms_user.i_time_id_dg, ms_user.e_time_id_dg],
                                             "bvs_id": [ms_user.b_bvs_id_dg, ms_user.i_bvs_id_dg, ms_user.e_bvs_id_dg],
                                             "stnb_id": [ms_user.b_stnb_id_dg, ms_user.i_stnb_id_dg, ms_user.e_stnb_id_dg],
                                             "ioe_id": [ms_user.b_ioe_id_dg, ms_user.i_ioe_id_dg, ms_user.e_ioe_id_dg],
                                             "path_id": [ms_user.b_path_id_dg, ms_user.i_path_id_dg, ms_user.e_path_id_dg]}, cls=DecimalEncoder),
                    }
        
        return JsonResponse(response)
    else:
        return HttpResponse("别瞎玩")
    

# 鼠标移到人名上时，展现头像、姓名、id、记录
def get_info_abstract(request):
    if request.method == 'GET':
        # 此处要防攻击
        user_id = request.GET["id"]
        user = UserProfile.objects.get(id=user_id)
        ms_user = user.userms
        if user.avatar:
            avatar_path = os.path.join(settings.MEDIA_ROOT, urllib.parse.unquote(user.avatar.url)[7:])
            image_data = open(avatar_path, "rb").read()
            image_data = base64.b64encode(image_data).decode()
        else:
            image_data = None

        response = {
            "id": user_id,
            "realname": user.realname,
            "avatar": image_data,
            "record_abstract": json.dumps({"time": [ms_user.b_time_std, ms_user.i_time_std, ms_user.e_time_std],
                                            "bvs": [ms_user.b_bvs_std, ms_user.i_bvs_std, ms_user.e_bvs_std],
                                            "time_id": [ms_user.b_time_id_std, ms_user.i_time_id_std, ms_user.e_time_id_std],
                                            "bvs_id": [ms_user.b_bvs_id_std, ms_user.i_bvs_id_std, ms_user.e_bvs_id_std]}, 
                                            cls=DecimalEncoder),
            }
        
        return JsonResponse(response)
    else:
        return HttpResponse("别瞎玩")
    

# 上传或更新我的地盘里的头像、姓名、个性签名
# 应该写到用户的app里，而不是玩家
@login_required(login_url='/')
def update(request):
    if request.method == 'POST':
        user_update_form = UserUpdateForm(
            data=request.POST, files=request.FILES)
        if user_update_form.is_valid():
            data = user_update_form.cleaned_data
            # print(data)
            user = request.user
            if user.is_banned:
                return JsonResponse({"status": 110, "msg": "用户已被封禁"})
            realname_flag = False
            signature_flag = False
            avatar_flag = False
            if data["realname"]:
                if user.left_realname_n > 0:
                    user.realname = data["realname"]
                    user.left_realname_n -= 1
                    realname_flag = True
                    update_cache_realname(user.id, data["realname"])
            if data["signature"]:
                # 个性签名的修改次数每年增加一次
                delta_t = timezone.now() - user.last_change_signature
                n_add = delta_t.days // 365
                user.left_signature_n += n_add
                user.last_change_signature += timezone.timedelta(days=n_add * 365)
                if user.left_signature_n > 0:
                    user.signature = data["signature"]
                    user.left_signature_n -= 1
                    signature_flag = True
            if data["avatar"]:
                # 头像的修改次数每年增加一次
                delta_t = timezone.now() - user.last_change_avatar
                n_add = delta_t.days // 365
                user.left_avatar_n += n_add
                user.last_change_avatar += timezone.timedelta(days=n_add * 365)
                if user.left_avatar_n > 0:
                    user.avatar = data["avatar"]
                    user.left_avatar_n -= 1
                    avatar_flag = True
            try:
                user.save()
                msg_dict = {
                    "id": user.id, "username": user.username, "realname": user.realname,
                     "realname_flag": realname_flag, "signature_flag": signature_flag,
                     "avatar_flag": avatar_flag, "left_realname_n": user.left_realname_n,
                     "left_signature_n": user.left_signature_n, "left_avatar_n": user.left_avatar_n,
                     "is_banned": user.is_banned}
                return JsonResponse({"status": 100, "msg": msg_dict})
            except Exception as e:
                return JsonResponse({"status": 107, "msg": "未知错误。可能原因：不支持此种字符"})
        else:
            ErrorDict = user_update_form.errors
            return JsonResponse({"status": 101, "msg": ErrorDict})
    else:
        return HttpResponse("别瞎玩")


# 用户修改自己的名字后，同步修改redis缓存里的真实姓名，使得排行榜数据同步修改
# 开销较大，然而用户改名只有1次机会
def update_cache_realname(user_id, user_realname):
    for index in ["time", "bvs", "path", "ioe", "stnb"]:
        for mode in ["std", "nf", "ng", "dg"]:
            key = f"player_{index}_{mode}_{user_id}"
            if cache.exists(key):
                cache.hset(key, "name", user_realname)


# 从redis获取用户排行榜
def player_rank(request):
    if request.method == 'GET':
        # print(request.GET)
        # print(cache.zcard("player_time_std_ids"))
        # print(cache.keys('*'))
        # [b'player_stnb_std_ids', b'player_path_std_2', b'player_time_std_1', b'player_bvs_std_2',
        #   b'player_bvs_std_1', b'newest_queue', b'player_path_std_ids', b'player_ioe_std_2',
        #     b'player_stnb_std_2', b'player_time_std_2', b'player_bvs_std_ids', b'player_ioe_std_ids',
        #       b'player_stnb_std_1', b'player_path_std_1', b'review_queue', b'player_ioe_std_1', 
        #       b':1:django.contrib.sessions.cachef7wlcpvziwulv829ah1r66afrc1xaae0', b'player_time_std_ids']
        # print(cache.zrange('player_time_std_ids', 0, -1))
        # print(cache.zrange('player_time_std_1', 0, -1))
        # print(cache.zrange('player_time_std_2', 0, -1))
        # print(cache.zrange('player_path_std_2', 0, -1))
        data=request.GET
        # num_player = cache.llen(data["ids"])
        num_player = cache.zcard(data["ids"])
        start_idx = 20 * int(data["page"])
        if start_idx >= num_player:
            start_idx = num_player // 20 * 20
        if num_player % 20 == 0 and num_player > 0:
            start_idx -= 20
        desc_flag = True if data["reverse"] == "true" else False
        res = cache.sort(data["ids"], by=data["sort_by"], get=json.loads(data["indexes"]), desc=desc_flag, start=start_idx, num=20)
        # print(res)
        # print(cache.get("player_time_std_ids"))
        # print(cache.hget("player_time_std_3", "b"))
        response = {
            "total_page": num_player // 20 + 1,
            "players": res
            }
        return JsonResponse(response, safe=False, encoder=ComplexEncoder)
    else:
        return HttpResponse("别瞎玩")



