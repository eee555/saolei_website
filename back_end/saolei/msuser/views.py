import base64
import decimal
import json
import logging
import os
import urllib.parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from django_redis import get_redis_connection

from config.global_settings import GameModes, RankingGameStats
from userprofile.models import UserProfile
from userprofile.utils import user_metadata
from utils import ComplexEncoder
from .forms import UserUpdateAvatarForm, UserUpdateRealnameForm, UserUpdateSignatureForm

logger = logging.getLogger('userprofile')
cache = get_redis_connection("saolei_website")

# 根据id获取用户的基本资料、扫雷记录
# 无需登录就可获取


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


# 获取我的地盘里的头像、姓名、个性签名、过审标识
@ratelimit(key='ip', rate='20/m')
@require_GET
def get_info(request):
    if not (user_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()

    user.popularity += 1
    user.save(update_fields=["popularity"])

    return JsonResponse(user_metadata(user, request.user))


# 获取我的地盘里的姓名、全部纪录
@ratelimit(key='ip', rate='15/m')
@require_GET
def get_records(request):
    if not (user_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    ms_user = user.userms

    response = {"id": user_id, "realname": user.realname}
    for mode in GameModes:
        value = {}
        for stat in RankingGameStats:
            value[stat] = ms_user.getrecords_level(stat, mode)
            value[f"{stat}_id"] = ms_user.getrecordIDs_level(stat, mode)
        response[f"{mode}_record"] = json.dumps(value, cls=DecimalEncoder)
    return JsonResponse(response)


# 鼠标移到人名上时，展现头像、姓名、id、记录
@ratelimit(key='ip', rate='5/s')
@require_GET
def get_info_abstract(request):
    # 此处要防攻击
    if not (user_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
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
        "record_abstract": json.dumps(
            {
                "timems": ms_user.getrecords_level("timems", "std"),
                "bvs": ms_user.getrecords_level("bvs", "std"),
                "timems_id": ms_user.getrecordIDs_level("timems", "std"),
                "bvs_id": ms_user.getrecordIDs_level("bvs", "std"),
            },
            cls=DecimalEncoder,
        ),
    }

    return JsonResponse(response)


@require_GET
def get_identifiers(request):
    if not (userid := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound()
    return JsonResponse(user.userms.identifiers, safe=False)


# 上传或更新我的地盘里的头像、姓名、个性签名
# 应该写到用户的app里，而不是玩家
@login_required(login_url='/')
@require_POST
def update_realname(request):
    user_update_realname_form = UserUpdateRealnameForm(
        data=request.POST, request=request)
    if user_update_realname_form.is_valid():
        realname = user_update_realname_form.cleaned_data["realname"]
        user: UserProfile = request.user
        if user.is_banned:
            return JsonResponse({"status": 110, "msg": "用户已被封禁"})
        logger.info(f'用户 {user.username}#{user.id} 修改实名 从 "{user.realname}" 到 "{realname}"')
        user.realname = realname
        try:
            user.save(update_fields=["realname", "left_realname_n"])
        except Exception:
            return JsonResponse({"status": 107, "msg": "未知错误。可能原因：不支持此种字符"})
        update_cache_realname(user.id, realname)
        user.userms.save(update_fields=["identifiers"])
        return JsonResponse({"status": 100, "msg": {"n": user.left_realname_n}})
    else:
        ErrorDict = json.loads(user_update_realname_form.errors.as_json())
        Error = ErrorDict[next(iter(ErrorDict))][0]['message']
        return JsonResponse({"status": 101, "msg": Error})


# 上传或更新我的地盘里的头像
# 应该写到用户的app里，而不是玩家
@login_required(login_url='/')
@require_POST
def update_avatar(request):
    if request.user.userms.e_timems_std >= 200000:
        return JsonResponse({"status": 177, "msg": "只允许标准高级sub200的玩家修改头像和个性签名！"})
    user_update_form = UserUpdateAvatarForm(
        data=request.POST, files=request.FILES, request=request)
    if user_update_form.is_valid():
        data = user_update_form.cleaned_data
        user = request.user
        if user.is_banned:
            return JsonResponse({"status": 110, "msg": "用户已被封禁"})
        user.avatar = data["avatar"]
        user.save(update_fields=["avatar", "left_avatar_n"])
        logger.info(f'用户 {user.username}#{user.id} 修改头像')
        return JsonResponse({"status": 100, "msg": {"n": user.left_avatar_n}})

    else:
        ErrorDict = json.loads(user_update_form.errors.as_json())
        Error = ErrorDict[next(iter(ErrorDict))][0]['message']
        return JsonResponse({"status": 101, "msg": Error})


# 上传或更新我的地盘里的个性签名
# 应该写到用户的app里，而不是玩家
@login_required(login_url='/')
@require_POST
def update_signature(request):
    if request.user.userms.e_timems_std >= 200000:
        return JsonResponse({"status": 177, "msg": "只允许标准高级sub200的玩家修改头像和个性签名！"})
    user_update_form = UserUpdateSignatureForm(
        data=request.POST, request=request)
    if user_update_form.is_valid():
        signature = user_update_form.cleaned_data["signature"]
        user = request.user
        if user.is_banned:
            return JsonResponse({"status": 110, "msg": "用户已被封禁"})
        if signature:
            # 个性签名的修改次数每年增加一次
            user.signature = signature
        try:
            user.save(update_fields=["signature", "left_signature_n"])
            return JsonResponse({"status": 100, "msg": {"n": user.left_signature_n}})
        except Exception:
            return JsonResponse({"status": 107, "msg": "未知错误。可能原因：不支持此种字符"})
    else:
        ErrorDict = json.loads(user_update_form.errors.as_json())
        # print(ErrorDict)
        Error = ErrorDict[next(iter(ErrorDict))][0]['message']
        return JsonResponse({"status": 101, "msg": Error})


# 用户修改自己的名字后，同步修改redis缓存里的真实姓名，使得排行榜数据同步修改
# 开销较大，然而用户改名只有1次机会
def update_cache_realname(user_id, user_realname):
    for index in RankingGameStats:
        for mode in GameModes:
            key = f"player_{index}_{mode}_{user_id}"
            if cache.exists(key):
                cache.hset(key, "name", user_realname)
    # 遍历并修改最新录像
    for video_id, value in cache.hgetall("newest_queue").items():
        new_value = json.loads(value)
        if new_value["player_id"] == user_id:
            new_value["player"] = user_realname
            # 将修改后的值存回哈希表
            cache.hset("newest_queue", video_id, json.dumps(new_value))
    # 遍历并修改审查队列
    for video_id, value in cache.hgetall("review_queue").items():
        new_value = json.loads(value)
        if new_value["player_id"] == user_id:
            new_value["player"] = user_realname
            # 将修改后的值存回哈希表
            cache.hset("review_queue", video_id, json.dumps(new_value))


# 从redis获取用户排行榜
@require_GET
def player_rank(request):
    data = request.GET
    num_player = cache.zcard(data["ids"])
    start_idx = 20 * (int(data["page"]) - 1)
    if start_idx >= num_player:
        start_idx = num_player // 20 * 20
    if num_player % 20 == 0 and num_player > 0:
        start_idx -= 20
    desc_flag = True if data["reverse"] == "true" else False
    res = cache.sort(data["ids"], by=data["sort_by"], get=json.loads(data["indexes"]), desc=desc_flag, start=start_idx, num=20)
    response = {
        "total_page": num_player // 20 + 1,
        "players": res,
    }
    return JsonResponse(response, safe=False, encoder=ComplexEncoder)
