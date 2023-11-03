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

# 根据id获取用户的基本资料、扫雷记录
# 无需登录就可获取


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


# 获取我的地盘里的头像、姓名、个性签名、记录
def get_info(request):
    if request.method == 'GET':
        # 此处要重点防攻击
        # print(request.GET)
        user_id = request.user.id
        user = UserProfile.objects.get(id=user_id)
        ms_user = UserMS.objects.get(id=request.user.userms_id)
        # print(user_id)
        # print(urllib.parse.unquote(user.avatar.url))

        if user.avatar:
            image_data = open(urllib.parse.unquote(
                user.avatar.url)[1:], "rb").read()
            image_data = base64.b64encode(image_data).decode()
        else:
            image_data = None
        response = {"id": user_id,
                    "realname": user.realname,
                    "avatar": image_data,
                    "signature": user.signature,
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
        # print(response["avatar"])
        # print(response["realname"])
        # print(JsonResponse(response))

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
            # print(data)
            user = request.user
            user.realname = data["realname"]
            user.signature = data["signature"]
            if data["avatar"]:
                user.avatar = data["avatar"]
            try:
                user.save()
                return JsonResponse({"status": 100, "msg": None})
            except Exception as e:
                return JsonResponse({"status": 107, "msg": "不支持此种字符"})
        else:
            ErrorDict = user_update_form.errors
            return JsonResponse({"status": 101, "msg": ErrorDict})
    else:
        return HttpResponse("别瞎玩")

def player_rank(request):
    if request.method == 'GET':
        # print(request.GET)
        data=request.GET
        num_player = cache.llen(data["ids"])
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



