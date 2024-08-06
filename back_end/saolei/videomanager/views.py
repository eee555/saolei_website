# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('videomanager')
from django.contrib.auth.decorators import login_required
from .forms import UploadVideoForm
from .models import VideoModel, ExpandVideoModel
from .view_utils import update_personal_record, update_personal_record_stock, video_all_fields, update_video_num, update_state
from userprofile.models import UserProfile
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound
import json, urllib
from utils import ComplexEncoder
from django.core.paginator import Paginator
from msuser.models import UserMS
from django.db.models import Q
# import os
# import time
from datetime import datetime
# from django.core.cache import cache
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from django.shortcuts import render, redirect
# https://django-ratelimit.readthedocs.io/en/stable/rates.html
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
# import ms_toollib as ms
from django.utils.encoding import escape_uri_path
from django.conf import settings

from django.views.decorators.http import require_GET, require_POST

@login_required(login_url='/')
def video_upload(request):
    if request.method == 'POST':
        if request.user.is_banned:
            return HttpResponseForbidden() # 用户被封禁
        if request.user.userms.video_num_total >= request.user.userms.video_num_limit:
            return HttpResponse(status = 402) # 录像仓库已满
            
        # response = {'status': 100, 'msg': None}
        # request.POST['file'] = request.FILES
        video_form = UploadVideoForm(data=request.POST, files=request.FILES)
        # print(video_form)
        if video_form.is_valid():
            data = video_form.cleaned_data
            if data["designator"] not in request.user.userms.designators:
                # 如果标识是首次使用的，需要得到管理员的审核
                data['review_code'] = 2

            # 查重
            collisions = list(VideoModel.objects.filter(timems=data["timems"], bv=data["bv"]).filter(video__cl=data["cl"], video__op=data["op"], video__isl=data["isl"], video__designator=data["designator"]))
            if collisions:
                return HttpResponse(status = 409)
            
            # 表中添加数据
            e_video = ExpandVideoModel.objects.create(designator=data["designator"],
                                                      left=data["left"], right=data["right"],
                                                      double=data["double"], cl=data["cl"],
                                                      left_s=data["left_s"], right_s=data["right_s"],
                                                      double_s=data["double_s"], cl_s=data["cl_s"],
                                                      path=data["path"], flag=data["flag"],
                                                      flag_s=data["flag_s"], stnb=data["stnb"],
                                                      rqp=data["rqp"], ioe=data["ioe"],
                                                      thrp=data["thrp"], corr=data["corr"],
                                                      ce=data["ce"], ce_s=data["ce_s"],
                                                      op=data["op"], isl=data["isl"],
                                                      cell0=data["cell0"], cell1=data["cell1"],
                                                      cell2=data["cell2"], cell3=data["cell3"],
                                                      cell4=data["cell4"], cell5=data["cell5"],
                                                      cell6=data["cell6"], cell7=data["cell7"],
                                                      cell8=data["cell8"])
            # 会检查是否为盲扫，自动修改模式
            video = VideoModel.objects.create(player=request.user, file=data["file"], video=e_video,
                                      state=["c", "b", "d", "a"][data['review_code']], software=data["software"], level=data["level"],
                                      mode=data["mode"] if data["mode"]!="00" else ("12" if data["flag"]==0 else "00"), 
                                      timems=data["timems"],
                                      bv=data["bv"], bvs=data["bvs"])

    # 查重
    collisions = list(VideoModel.objects.filter(timems=data["timems"], bv=data["bv"]).filter(video__cl=data["cl"], video__op=data["op"], video__isl=data["isl"], video__designator=data["designator"]))
    if collisions:
        return JsonResponse({'type': 'error', 'object': 'videomodel', 'category': 'conflict'})  
    new_video(data, request.user) # 表中添加数据
    return JsonResponse({'type': 'success', 'object': 'videomodel', 'category': 'upload'})

# 根据id向后台请求软件类型（适配flop播放器用）
@require_GET
def get_software(request):
    video = VideoModel.objects.get(id=request.GET["id"])
    # print({"status": 100, "msg": video.software})
    return JsonResponse({"msg": video.software})

# 给预览用的接口，区别是结尾是文件后缀
# 坑：如果做成必须登录才能下载，由于Django的某种特性，会重定向资源，
# 然而flop播放器不能处理此状态码，因此会请求到空文件，导致解码失败
@ratelimit(key='ip', rate='20/m')
@require_GET
def video_preview(request):
    # 这里性能可能有问题
    video = VideoModel.objects.get(id=int(request.GET["id"][:-4]))
    # video.file.name是相对路径(含upload_to)，video.file.path是绝对路径
    # print(settings.MEDIA_ROOT / "assets" / video.file.name)
    file_path = settings.MEDIA_ROOT / video.file.name
    response =FileResponse(open(file_path, 'rb'))
    response['Content-Type']='application/octet-stream'
    # response['Content-Disposition']=f'attachment;filename="{video.file.name.split("/")[2]}"'
    file_name = video.file.name.split("/")[2]
    file_name_uri = urllib.parse.quote(file_name)
    response['Content-Disposition'] = f'attachment; filename="{file_name_uri}"'
    response['Access-Control-Expose-Headers']='Content-Disposition'
    return response

# 给下载用的接口，区别是结尾没有文件后缀
# @login_required(login_url='/')
@ratelimit(key='ip', rate='20/m')
@require_GET
def video_download(request):
    try:
        video = VideoModel.objects.get(id=request.GET["id"])
        response =FileResponse(open(video.file.path, 'rb'))
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']=f'attachment;filename="{video.file.name.split("/")[2]}"'
        return response
    except VideoModel.DoesNotExist:
        return HttpResponseNotFound()

# 录像查询（无需登录）
# 按任何基础指标+难度+模式，排序，分页
# 每项的定义参见 front_end/src/views/VideoView.vue 的 request_videos 函数

@ratelimit(key='ip', rate='20/m')
@require_GET
def video_query(request):
    data = request.GET

    values = video_all_fields

    # 排序
    if data["r"] == "true":
        ob = "-" + data["o"]
    else:
        ob = data["o"]
    if data["o"] != "timems":
        orderby = (ob, "timems")
    else:
        orderby = (ob,)
            
    if data["mode"] != "00":
        filter = {"level": data["level"], "mode": data["mode"]}
        videos = VideoModel.objects.filter(**filter).order_by(*orderby).values(*values)
    else:
        filter = {"level": data["level"]}
        videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(**filter).order_by(*orderby).values(*values)

    # print(videos)
    paginator = Paginator(videos, data["ps"])
    page_number = data["page"]
    page_videos = paginator.get_page(page_number)
    response = {
        "count": len(videos),
        "videos": list(page_videos)
    }
    # t=json.dumps(response, cls=ComplexEncoder)
    # print(t)
    return JsonResponse(json.dumps(response, cls=ComplexEncoder), safe=False)


# 按id查询这个用户的所有录像
@require_GET
def video_query_by_id(request):
    id_ = request.GET["id"]
        
    user = UserProfile.objects.get(id=id_)
    videos = VideoModel.objects.filter(player=user).values('id', 'upload_time', "level", "mode", "timems", "bv", "bvs")
    # print(list(videos))

    return JsonResponse(json.dumps({"videos": list(videos)}, cls=ComplexEncoder), safe=False)



# 获取审查队列里的录像
# http://127.0.0.1:8000/video/review_queue
@require_GET
def review_queue(request):
    review_video_ids = cache.hgetall("review_queue")
    for key in list(review_video_ids.keys()):
        review_video_ids.update({str(key, encoding="utf-8"): review_video_ids.pop(key)})
    return JsonResponse(review_video_ids, encoder=ComplexEncoder)


# 获取最新录像
# http://127.0.0.1:8000/video/newest_queue
@require_GET
def newest_queue(request):
    newest_queue_ids = cache.hgetall("newest_queue")
    for key in list(newest_queue_ids.keys()):
        newest_queue_ids.update({str(key, encoding="utf-8"): newest_queue_ids.pop(key)})
    return JsonResponse(newest_queue_ids, encoder=ComplexEncoder)
    

# 获取谁破纪录的消息
# http://127.0.0.1:8000/video/news_queue
@require_GET
def news_queue(request):
    news_queue = cache.lrange("news_queue", 0, -1)
    return JsonResponse(news_queue, encoder=ComplexEncoder, safe=False)
    
    
# 获取全网被冻结的录像
# http://127.0.0.1:8000/video/freeze_queue
@require_GET
def freeze_queue(request):
    freeze_queue_ids = cache.hgetall("freeze_queue")
    for key in list(freeze_queue_ids.keys()):
        freeze_queue_ids.update({str(key, encoding="utf-8"): freeze_queue_ids.pop(key)})
    return JsonResponse(freeze_queue_ids, encoder=ComplexEncoder)
    
# 审核通过单个录像
# check_designator 为 true 则检查是否要修改玩家标识列表，并在修改后扫描所有待审录像的标识
def approve_single(videoid, check_designator=True):
    video = VideoModel.objects.filter(id=videoid)
    if not video:
        return None
    video = video[0]
    if video.state == "c":
        return False
    userms = video.player.userms
    video.state = "c"
    video.save()
    cache.hset("newest_queue", videoid, cache.hget("review_queue", videoid))
    update_personal_record(video)
    update_video_num(video)
    cache.hdel("review_queue", videoid)
    designator = video.video.designator
    if check_designator and designator not in userms.designators:
        userms.designators.append(designator)
        userms.save(update_fields=["designators"])
        logger.info(f'用户 {video.player.username}#{video.player.id} 新标识 "{designator}"')
        approve_designator(video.player.id, designator)
    return True

# 审核通过所有特定用户特定标识的录像
def approve_designator(userid, designator):
    user_designator_list = cache.hgetall("review_queue")
    for key in user_designator_list:
        value = json.loads(user_designator_list[key])
        if value["player_id"] == userid and value["designator"] == designator:
            logger.info(f'用户 #{userid} 录像#{key} 机审成功')
            approve_single(key, False)


# 【管理员】审核通过队列里的录像，未审核或冻结状态的录像可以审核通过
# 返回"True","False"（已经是通过的状态）,"Null"（不存在该录像）
# http://127.0.0.1:8000/video/approve?ids=[18,19,999]
@require_GET
def approve(request):
    if request.user.is_staff:
        ids = json.loads(request.GET["ids"])
        res = []
        for _id in ids:
            logger.info(f'管理员 {request.user.username}#{request.user.id} 过审录像#{_id}')
            res.append(approve_single(_id))
        return JsonResponse(res, safe=False)
    else:
        return HttpResponseNotAllowed()

# 【管理员】冻结队列里的录像，未审核或审核通过的录像可以冻结
# 两种用法，冻结指定的录像id，或冻结某用户的所有录像
# 冻结的录像七到14天后删除，用一个定时任务
# http://127.0.0.1:8000/video/freeze?ids=[18,19,20,21,102,273]
# http://127.0.0.1:8000/video/freeze?ids=12
# http://127.0.0.1:8000/video/freeze?user_id=20
@require_GET
def freeze(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    if ids := request.GET.get("ids"):
        res = [] 
        for id in ids:
            v = VideoModel.objects.filter(id=id).first()
            if not v:
                res.append("Null")
            else:
                update_state(v, VideoModel.State.FROZEN)
                logger.info(f'管理员 {request.user.username}#{request.user.id} 冻结录像#{id}')
        return JsonResponse(res)
    elif user_id := request.GET.get("user_id"): 
        user = UserProfile.objects.filter(id=user_id).first()
        if not user:
            return HttpResponseNotFound()
        videos = VideoModel.objects.filter(player=user)
        for v in videos:
            update_state(v, VideoModel.State.FROZEN, update_ranking=False)
        update_personal_record_stock(user)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# 管理员使用的操作接口，调用方式见前端的StaffView.vue
get_videoModel_fields = ["player", "player__realname", "upload_time", "state", "software", "level", "mode", "timems", "bv", "bvs"] # 可获取的域列表
for name in [field.name for field in ExpandVideoModel._meta.get_fields()]:
    get_videoModel_fields.append("video__" + name)

@require_GET
def get_videoModel(request):
    if request.user.is_staff:
        videolist = VideoModel.objects.filter(id=request.GET["id"]).values(*get_videoModel_fields)
        if not videolist:
            return HttpResponseNotFound()
        return JsonResponse(videolist[0])
    else:
        return HttpResponseForbidden()
    
set_videoModel_fields = ["player", "upload_time", "state"] # 可修改的域列表
@require_POST
def set_videoModel(request):
    if not request.user.is_staff:
        return HttpResponseForbidden() # 非管理员不能使用该api
    videoid = request.POST.get("id")
    video = VideoModel.objects.get(id=videoid)
    user = video.player
    if user.is_staff and user != request.user:
        return HttpResponseForbidden() # 不能修改除自己以外管理员的信息
    field = request.POST.get("field")
    if field not in set_videoModel_fields:
        return HttpResponseForbidden() # 只能修改特定的域
    value = request.POST.get("value")
    logger.info(f'管理员 {request.user.username}#{request.user.id} 修改录像#{videoid} 域 {field} 从 {getattr(video, field)} 到 {value}')
    setattr(video, field, value)
    video.save()
    return HttpResponse()



