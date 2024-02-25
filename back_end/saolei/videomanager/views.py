# -*- coding: utf-8 -*-
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UploadVideoForm
from .models import VideoModel, ExpandVideoModel
from userprofile.models import UserProfile
from django.http import HttpResponse, JsonResponse, FileResponse
# from asgiref.sync import sync_to_async
import json
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
# get_redis_connection("saolei_website").flushall()
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.core.management.base import BaseCommand
# from django_apscheduler.models import DjangoJobExecution
# from django_apscheduler import util
from django.shortcuts import render, redirect
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events
# https://django-ratelimit.readthedocs.io/en/stable/rates.html
from django_ratelimit.decorators import ratelimit
from django.utils import timezone

logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@login_required(login_url='/')
def video_upload(request):
    if request.method == 'POST':
        if request.user.is_banned:
            return JsonResponse({"status": 101, "msg": "用户被封禁!"})
        if request.user.userms.video_num_total >= request.user.userms.video_num_limit:
            return JsonResponse({"status": 188, "msg": "用户录像仓库已满!"})
            
        # response = {'status': 100, 'msg': None}
        # request.POST['file'] = request.FILES
        video_form = UploadVideoForm(data=request.POST, files=request.FILES)
        # print(video_form)
        if video_form.is_valid():
            data = video_form.cleaned_data
            # 表中添加数据
            # print(data['review_code'])
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
                                      state=["c", "b", "a", "a"][data['review_code']], software=data["software"], level=data["level"],
                                      mode=data["mode"] if data["mode"]!="00" else ("12" if data["flag"]==0 else "00"), 
                                      rtime=data["rtime"],
                                      bv=data["bv"], bvs=data["bvs"])
            
            # cache.hget("review_queue", "filed")

            if data['review_code'] >= 2:
                # 往审查队列里添加录像
                cache.hset("review_queue", video.id, json.dumps({"time": video.upload_time,
                                                                "player": video.player.realname,
                                                                "player_id": video.player.id,
                                                                "level": video.level,
                                                                "mode": video.mode,
                                                                "rtime": video.rtime,
                                                                "bv": video.bv,
                                                                "bvs": video.bvs}, cls=ComplexEncoder))
            else:
                # 如果录像自动通过了审核，更新最新录像和纪录
                cache.hset("newest_queue", video.id, json.dumps({"time": video.upload_time,
                                                                "player": video.player.realname,
                                                                "player_id": video.player.id,
                                                                "level": video.level,
                                                                "mode": video.mode,
                                                                "rtime": video.rtime,
                                                                "bv": video.bv,
                                                                "bvs": video.bvs}, cls=ComplexEncoder))
                update_personal_record(video, e_video)
                update_video_num(request.user.userms, video)
                

            # review_video_ids = cache.hgetall("review_queue")
            # print(review_video_ids)

            # update_personal_record(request, data, e_video)
            return JsonResponse({"status": 100, "msg": None})
        else:
            # print(video_form.errors)
            return JsonResponse({"status": 666, "msg": "小型网站，请勿攻击！"})
    elif request.method == 'GET':
        return HttpResponse("别瞎玩")
    else:
        return HttpResponse("别瞎玩")

# 根据id向后台请求软件类型（适配flop播放器用）
def get_software(request):
    if request.method != 'GET':
        return HttpResponse("别瞎玩")
    try:
        video = VideoModel.objects.get(id=request.GET["id"])
        # print({"status": 100, "msg": video.software})
        return JsonResponse({"status": 100, "msg": video.software})
    except Exception:
        return JsonResponse({"status": 104, "msg": "file not exist!"})

# 给预览用的接口，区别是结尾是文件后缀
# 坑：如果做成必须登录才能下载，由于Django的某种特性，会重定向资源，
# 然而flop播放器不能处理此状态码，因此会请求到空文件，导致解码失败
@ratelimit(key='ip', rate='20/m')
def video_preview(request):
    if request.method != 'GET':
        return HttpResponse("别瞎玩")
    # 这里性能可能有问题
    try:
        video = VideoModel.objects.get(id=int(request.GET["id"][:-4]))
        response =FileResponse(open(video.file.path, 'rb'))
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']=f'attachment;filename="{video.file.name.split("/")[2]}"'
        return response
    except Exception:
        return JsonResponse({"status": 104, "msg": "file not exist!"})

# 给下载用的接口，区别是结尾没有文件后缀
# @login_required(login_url='/')
@ratelimit(key='ip', rate='20/m')
def video_download(request):
    if request.method != 'GET':
        return HttpResponse("别瞎玩")
    try:
        video = VideoModel.objects.get(id=request.GET["id"])
        response =FileResponse(open(video.file.path, 'rb'))
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']=f'attachment;filename="{video.file.name.split("/")[2]}"'
        return response
    except VideoModel.DoesNotExist:
        return JsonResponse({"status": 104, "msg": "录像不存在！"})
    # try:
    #     video = VideoModel.objects.get(id=request.GET["id"])
    #     response =FileResponse(open(video.file.path, 'rb'))
    #     response['Content-Type']='application/octet-stream'
    #     response['Content-Disposition']=f'attachment;filename="{video.file.name.split("/")[2]}"'
    #     return response
    # except Exception:
    #     return JsonResponse({"status": 104, "msg": "file not exist!"})
        


# 录像查询（无需登录）
# 按任何基础指标+难度+模式，排序，分页
@ratelimit(key='ip', rate='20/m')
def video_query(request):
    if request.method == 'GET':
        data = request.GET
        index = data["index"]
        if index[0] == '-':
            order_index = "-video__" + index[1:]
            values_index = "video__" + index[1:]
        else:
            order_index = values_index = "video__" + index

        if data["mode"] != "00":
            if index in {"id", "upload_time", "bv", "bvs", "-upload_time", "-bv", "-bvs"}:
                videos = VideoModel.objects.filter(level=data["level"], mode=data["mode"])\
                    .order_by(index, "rtime").\
                    values("id", "upload_time", "player__realname", "player__id", "bv", "bvs", "rtime")
            elif index == "rtime" or index == "-rtime":
                videos = VideoModel.objects.filter(level=data["level"], mode=data["mode"])\
                    .order_by(index).\
                    values("id", "upload_time", "player__realname", "player__id", "bv", "bvs", "rtime")
            else:
                videos = VideoModel.objects.filter(level=data["level"], mode=data["mode"])\
                    .order_by(order_index, "rtime").\
                    values("id", "upload_time", "player__realname", "player__id", "bv",
                        "bvs", "rtime", values_index)
        else:
            if index in {"id", "upload_time", "bv", "bvs", "-upload_time", "-bv", "-bvs"}:
                videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(level=data["level"])\
                    .order_by(index, "rtime").\
                    values("id", "upload_time", "player__realname", "player__id", "bv", "bvs", "rtime")
            elif index == "rtime" or index == "-rtime":
                videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(level=data["level"])\
                    .order_by(index).\
                    values("id", "upload_time", "player__realname", "player__id", "bv", "bvs", "rtime")
            else:
                videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(level=data["level"])\
                    .order_by(order_index, "rtime").\
                    values("id", "upload_time", "player__realname", "player__id", "bv",
                        "bvs", "rtime", values_index)

        # print(videos)
        paginator = Paginator(videos, 20)  # 每页20条数据
        page_number = data["page"]
        page_videos = paginator.get_page(page_number)
        response = {
            "total_page": paginator.num_pages,
            "videos": list(page_videos)
            }
        # t=json.dumps(response, cls=ComplexEncoder)
        # print(t)
        return JsonResponse(json.dumps(response, cls=ComplexEncoder), safe=False)

    elif request.method == 'POST':
        return HttpResponse("别瞎玩")
    else:
        return HttpResponse("别瞎玩")


# 按id查询这个用户的所有录像
def video_query_by_id(request):
    if request.method == 'GET':
        id_ = request.GET["id"]
        
        user = UserProfile.objects.get(id=id_)
        videos = VideoModel.objects.filter(player=user).values('id', 'upload_time', "level", "mode", "rtime", "bv", "bvs")
        # print(list(videos))

        return JsonResponse(json.dumps({"videos": list(videos)}, cls=ComplexEncoder), safe=False)
    else:
        return HttpResponse("别瞎玩")


# {
#     "1": "{\"time\": \"2023-12-16 14:52:40\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"b\", \"mode\": \"00\", \"rtime\": \"4.770\", \"bv\": 23, \"bvs\": 4.821802935010482}",
#     "3": "{\"time\": \"2023-12-16 14:52:52\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"i\", \"mode\": \"00\", \"rtime\": \"20.390\", \"bv\": 71, \"bvs\": 3.4330554193231975}",
#     "4": "{\"time\": \"2023-12-16 15:17:58\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"b\", \"mode\": \"12\", \"rtime\": \"1.530\", \"bv\": 4, \"bvs\": 2.6143790849673203}",
#     "8": "{\"time\": \"2023-12-16 15:26:22\", \"player\": \"www333\", \"level\": \"e\", \"mode\": \"00\", \"rtime\": \"51.940\", \"bv\": 149, \"bvs\": 2.849441663457836}",
#     "9": "{\"time\": \"2023-12-16 15:26:26\", \"player\": \"www333\", \"level\": \"b\", \"mode\": \"00\", \"rtime\": \"3.250\", \"bv\": 18, \"bvs\": 5.538461538461538}",
#     "10": "{\"time\": \"2023-12-16 15:26:30\", \"player\": \"www333\", \"level\": \"i\", \"mode\": \"00\", \"rtime\": \"20.110\", \"bv\": 69, \"bvs\": 3.431128791645947}",
#     "7": "{\"time\": \"2023-12-16 15:24:07\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"i\", \"mode\": \"00\", \"rtime\": \"15.280\", \"bv\": 31, \"bvs\": 2.0287958115183247}",
#     "6": "{\"time\": \"2023-12-16 15:24:02\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"e\", \"mode\": \"00\", \"rtime\": \"59.450\", \"bv\": 193, \"bvs\": 3.2127838519764507}",
#     "2": "{\"time\": \"2023-12-16 14:52:48\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"e\", \"mode\": \"00\", \"rtime\": \"61.710\", \"bv\": 193, \"bvs\": 3.0789175174201913}",
#     "5": "{\"time\": \"2023-12-16 15:23:59\", \"player\": \"\\u5b9e\\u540d\", \"level\": \"b\", \"mode\": \"12\", \"rtime\": \"1.580\", \"bv\": 6, \"bvs\": 3.7974683544303796}"
# }


# 上传的录像进入数据库后，更新用户的录像数目
def update_video_num(userms, video):
    if video.mode == '00':
        userms.video_num_std += 1
    elif video.mode == '12':
        userms.video_num_nf += 1
    elif video.mode == '05':
        userms.video_num_ng += 1
    elif video.mode == '11':
        userms.video_num_dg += 1

    if video.level == "b":
        userms.video_num_beg += 1
    elif video.level == 'i':
        userms.video_num_int += 1
    elif video.level == 'e':
        userms.video_num_exp += 1

    # 给高玩自动扩容
    if video.mode == "00" and video.level == 'e':
        if video.rtime < 100 and userms.video_num_limit < 200:
            userms.video_num_limit = 200
        if video.rtime < 60 and userms.video_num_limit < 500:
            userms.video_num_limit = 500
        if video.rtime < 50 and userms.video_num_limit < 600:
            userms.video_num_limit = 600
        if video.rtime < 40 and userms.video_num_limit < 800:
            userms.video_num_limit = 800
        if video.rtime < 30 and userms.video_num_limit < 1000:
            userms.video_num_limit = 1000
    
    userms.save()


# 参数: 用户、拓展录像数据
def update_personal_record(video_i, e_video):
    # user = UserProfile.objects.get(id=user_id)
    user = UserProfile.objects.get(id=video_i.player_id)
    ms_user = UserMS.objects.get(id=user.userms_id)
    # print(e_video.flag)
    # print(type(video_i.rtime))

    if video_i.mode == "12":
        video_i.mode = "00"
    if video_i.mode == "00":
        if video_i.level == "b":
            if video_i.rtime < ms_user.b_time_std:
                ms_user.b_time_std = video_i.rtime
                ms_user.b_time_id_std = e_video.id
                if ms_user.b_time_std < 999.998 and ms_user.i_time_std < 999.998 and ms_user.e_time_std < 999.998:
                    key = f"player_time_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_std))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_std))
                    cache.hset(key, "i", float(ms_user.i_time_std))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_std))
                    cache.hset(key, "e", float(ms_user.e_time_std))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_std))
                    s = float(ms_user.b_time_std + ms_user.i_time_std + ms_user.e_time_std)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_std_ids", {ms_user.id: s}) 
                    # if not cache.lindex('player_time_std_ids', ms_user.id):
                    #     cache.lpush('player_time_std_ids', ms_user.id)
            if video_i.bvs > ms_user.b_bvs_std:
                ms_user.b_bvs_std = video_i.bvs
                ms_user.b_bvs_id_std = e_video.id
                if ms_user.b_bvs_std > 0.001 and ms_user.i_bvs_std > 0.001 and ms_user.e_bvs_std > 0.001:
                    key = f"player_bvs_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_std)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_std)
                    cache.hset(key, "i", ms_user.i_bvs_std)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_std)
                    cache.hset(key, "e", ms_user.e_bvs_std)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_std)
                    s = ms_user.b_bvs_std + ms_user.i_bvs_std + ms_user.e_bvs_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_std_ids", {ms_user.id: s})
                    # if not cache.lindex('player_bvs_std_ids', ms_user.id):
                    #     cache.lpush('player_bvs_std_ids', ms_user.id)
            if e_video.stnb > ms_user.b_stnb_std:
                ms_user.b_stnb_std = e_video.stnb
                ms_user.b_stnb_id_std = e_video.id
                if ms_user.b_stnb_std > 0.001 and ms_user.i_stnb_std > 0.001 and ms_user.e_stnb_std > 0.001:
                    key = f"player_stnb_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_std)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_std)
                    cache.hset(key, "i", ms_user.i_stnb_std)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_std)
                    cache.hset(key, "e", ms_user.e_stnb_std)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_std)
                    s = ms_user.b_stnb_std + ms_user.i_stnb_std + ms_user.e_stnb_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_std_ids", {ms_user.id: s})
                    # cache.hset(key, "sum", ms_user.b_stnb_std + ms_user.i_stnb_std + ms_user.e_stnb_std)
                    # if not cache.lindex('player_stnb_std_ids', ms_user.id):
                    #     cache.lpush('player_stnb_std_ids', ms_user.id)
            if e_video.ioe > ms_user.b_ioe_std:
                ms_user.b_ioe_std = e_video.ioe
                ms_user.b_ioe_id_std = e_video.id
                if ms_user.b_ioe_std > 0.001 and ms_user.i_ioe_std > 0.001 and ms_user.e_ioe_std > 0.001:
                    key = f"player_ioe_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_std)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_std)
                    cache.hset(key, "i", ms_user.i_ioe_std)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_std)
                    cache.hset(key, "e", ms_user.e_ioe_std)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_std)
                    # cache.hset(key, "sum", ms_user.b_ioe_std + ms_user.i_ioe_std + ms_user.e_ioe_std)
                    # if not cache.lindex('player_ioe_std_ids', ms_user.id):
                    #     cache.lpush('player_ioe_std_ids', ms_user.id)
                    s = ms_user.b_ioe_std + ms_user.i_ioe_std + ms_user.e_ioe_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_std_ids", {ms_user.id: s})
            if e_video.path < ms_user.b_path_std:
                ms_user.b_path_std = e_video.path
                ms_user.b_path_id_std = e_video.id
                if ms_user.b_path_std < 99999.8 and ms_user.i_path_std < 99999.8 and ms_user.e_path_std < 99999.8:
                    key = f"player_path_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_std)
                    cache.hset(key, "b_id", ms_user.b_path_id_std)
                    cache.hset(key, "i", ms_user.i_path_std)
                    cache.hset(key, "i_id", ms_user.i_path_id_std)
                    cache.hset(key, "e", ms_user.e_path_std)
                    cache.hset(key, "e_id", ms_user.e_path_id_std)
                    # cache.hset(key, "sum", ms_user.b_path_std + ms_user.i_path_std + ms_user.e_path_std)
                    # if not cache.lindex('player_path_std_ids', ms_user.id):
                    #     cache.lpush('player_path_std_ids', ms_user.id)
                    s = ms_user.b_path_std + ms_user.i_path_std + ms_user.e_path_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_std_ids", {ms_user.id: s})
        if video_i.level == "i":
            if video_i.rtime < ms_user.i_time_std:
                ms_user.i_time_std = video_i.rtime
                ms_user.i_time_id_std = e_video.id
                if ms_user.b_time_std < 999.998 and ms_user.i_time_std < 999.998 and ms_user.e_time_std < 999.998:
                    key = f"player_time_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_std))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_std))
                    cache.hset(key, "i", float(ms_user.i_time_std))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_std))
                    cache.hset(key, "e", float(ms_user.e_time_std))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_std))
                    # cache.hset(key, "sum", float(ms_user.b_time_std + ms_user.i_time_std + ms_user.e_time_std))
                    # if not cache.lindex('player_time_std_ids', ms_user.id):
                    #     cache.lpush('player_time_std_ids', ms_user.id)
                    s = float(ms_user.b_time_std + ms_user.i_time_std + ms_user.e_time_std)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_std_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.i_bvs_std:
                ms_user.i_bvs_std = video_i.bvs
                ms_user.i_bvs_id_std = e_video.id
                if ms_user.b_bvs_std > 0.001 and ms_user.i_bvs_std > 0.001 and ms_user.e_bvs_std > 0.001:
                    key = f"player_bvs_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_std)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_std)
                    cache.hset(key, "i", ms_user.i_bvs_std)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_std)
                    cache.hset(key, "e", ms_user.e_bvs_std)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_std)
                    # cache.hset(key, "sum", ms_user.b_bvs_std + ms_user.i_bvs_std + ms_user.e_bvs_std)
                    # if not cache.lindex('player_bvs_std_ids', ms_user.id):
                    #     cache.lpush('player_bvs_std_ids', ms_user.id)
                    s = ms_user.b_bvs_std + ms_user.i_bvs_std + ms_user.e_bvs_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_std_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.i_stnb_std:
                ms_user.i_stnb_std = e_video.stnb
                ms_user.i_stnb_id_std = e_video.id
                if ms_user.b_stnb_std > 0.001 and ms_user.i_stnb_std > 0.001 and ms_user.e_stnb_std > 0.001:
                    key = f"player_stnb_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_std)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_std)
                    cache.hset(key, "i", ms_user.i_stnb_std)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_std)
                    cache.hset(key, "e", ms_user.e_stnb_std)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_std)
                    # cache.hset(key, "sum", ms_user.b_stnb_std + ms_user.i_stnb_std + ms_user.e_stnb_std)
                    # if not cache.lindex('player_stnb_std_ids', ms_user.id):
                    #     cache.lpush('player_stnb_std_ids', ms_user.id)
                    s = ms_user.b_stnb_std + ms_user.i_stnb_std + ms_user.e_stnb_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_std_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.i_ioe_std:
                ms_user.i_ioe_std = e_video.ioe
                ms_user.i_ioe_id_std = e_video.id
                if ms_user.b_ioe_std > 0.001 and ms_user.i_ioe_std > 0.001 and ms_user.e_ioe_std > 0.001:
                    key = f"player_ioe_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_std)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_std)
                    cache.hset(key, "i", ms_user.i_ioe_std)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_std)
                    cache.hset(key, "e", ms_user.e_ioe_std)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_std)
                    # cache.hset(key, "sum", ms_user.b_ioe_std + ms_user.i_ioe_std + ms_user.e_ioe_std)
                    # if not cache.lindex('player_ioe_std_ids', ms_user.id):
                    #     cache.lpush('player_ioe_std_ids', ms_user.id)
                    s = ms_user.b_ioe_std + ms_user.i_ioe_std + ms_user.e_ioe_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_std_ids", {ms_user.id: s})
            if e_video.path < ms_user.i_path_std:
                ms_user.i_path_std = e_video.path
                ms_user.i_path_id_std = e_video.id
                if ms_user.b_path_std < 99999.8 and ms_user.i_path_std < 99999.8 and ms_user.e_path_std < 99999.8:
                    key = f"player_path_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_std)
                    cache.hset(key, "b_id", ms_user.b_path_id_std)
                    cache.hset(key, "i", ms_user.i_path_std)
                    cache.hset(key, "i_id", ms_user.i_path_id_std)
                    cache.hset(key, "e", ms_user.e_path_std)
                    cache.hset(key, "e_id", ms_user.e_path_id_std)
                    # cache.hset(key, "sum", ms_user.b_path_std + ms_user.i_path_std + ms_user.e_path_std)
                    # if not cache.lindex('player_path_std_ids', ms_user.id):
                    #     cache.lpush('player_path_std_ids', ms_user.id)
                    s = ms_user.b_path_std + ms_user.i_path_std + ms_user.e_path_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_std_ids", {ms_user.id: s})
        if video_i.level == "e":
            if video_i.rtime < ms_user.e_time_std:
                ms_user.e_time_std = video_i.rtime
                ms_user.e_time_id_std = e_video.id
                if ms_user.b_time_std < 999.998 and ms_user.i_time_std < 999.998 and ms_user.e_time_std < 999.998:
                    key = f"player_time_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_std))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_std))
                    cache.hset(key, "i", float(ms_user.i_time_std))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_std))
                    cache.hset(key, "e", float(ms_user.e_time_std))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_std))
                    # cache.hset(key, "sum", float(ms_user.b_time_std + ms_user.i_time_std + ms_user.e_time_std))
                    # if not cache.lindex('player_time_std_ids', ms_user.id):
                    #     cache.lpush('player_time_std_ids', ms_user.id)
                    s = float(ms_user.b_time_std + ms_user.i_time_std + ms_user.e_time_std)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_std_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.e_bvs_std:
                ms_user.e_bvs_std = video_i.bvs
                ms_user.e_bvs_id_std = e_video.id
                if ms_user.b_bvs_std > 0.001 and ms_user.i_bvs_std > 0.001 and ms_user.e_bvs_std > 0.001:
                    key = f"player_bvs_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_std)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_std)
                    cache.hset(key, "i", ms_user.i_bvs_std)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_std)
                    cache.hset(key, "e", ms_user.e_bvs_std)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_std)
                    # cache.hset(key, "sum", ms_user.b_bvs_std + ms_user.i_bvs_std + ms_user.e_bvs_std)
                    # if not cache.lindex('player_bvs_std_ids', ms_user.id):
                    #     cache.lpush('player_bvs_std_ids', ms_user.id)
                    s = ms_user.b_bvs_std + ms_user.i_bvs_std + ms_user.e_bvs_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_std_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.e_stnb_std:
                ms_user.e_stnb_std = e_video.stnb
                ms_user.e_stnb_id_std = e_video.id
                if ms_user.b_stnb_std > 0.001 and ms_user.i_stnb_std > 0.001 and ms_user.e_stnb_std > 0.001:
                    key = f"player_stnb_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_std)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_std)
                    cache.hset(key, "i", ms_user.i_stnb_std)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_std)
                    cache.hset(key, "e", ms_user.e_stnb_std)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_std)
                    # cache.hset(key, "sum", ms_user.b_stnb_std + ms_user.i_stnb_std + ms_user.e_stnb_std)
                    # if not cache.lindex('player_stnb_std_ids', ms_user.id):
                    #     cache.lpush('player_stnb_std_ids', ms_user.id)
                    s = ms_user.b_stnb_std + ms_user.i_stnb_std + ms_user.e_stnb_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_std_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.e_ioe_std:
                ms_user.e_ioe_std = e_video.ioe
                ms_user.e_ioe_id_std = e_video.id
                if ms_user.b_ioe_std > 0.001 and ms_user.i_ioe_std > 0.001 and ms_user.e_ioe_std > 0.001:
                    key = f"player_ioe_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_std)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_std)
                    cache.hset(key, "i", ms_user.i_ioe_std)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_std)
                    cache.hset(key, "e", ms_user.e_ioe_std)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_std)
                    # cache.hset(key, "sum", ms_user.b_ioe_std + ms_user.i_ioe_std + ms_user.e_ioe_std)
                    # if not cache.lindex('player_ioe_std_ids', ms_user.id):
                    #     cache.lpush('player_ioe_std_ids', ms_user.id)
                    s = ms_user.b_ioe_std + ms_user.i_ioe_std + ms_user.e_ioe_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_std_ids", {ms_user.id: s})
            if e_video.path < ms_user.e_path_std:
                ms_user.e_path_std = e_video.path
                ms_user.e_path_id_std = e_video.id
                if ms_user.b_path_std < 99999.8 and ms_user.i_path_std < 99999.8 and ms_user.e_path_std < 99999.8:
                    key = f"player_path_std_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_std)
                    cache.hset(key, "b_id", ms_user.b_path_id_std)
                    cache.hset(key, "i", ms_user.i_path_std)
                    cache.hset(key, "i_id", ms_user.i_path_id_std)
                    cache.hset(key, "e", ms_user.e_path_std)
                    cache.hset(key, "e_id", ms_user.e_path_id_std)
                    # cache.hset(key, "sum", ms_user.b_path_std + ms_user.i_path_std + ms_user.e_path_std)
                    # if not cache.lindex('player_path_std_ids', ms_user.id):
                    #     cache.lpush('player_path_std_ids', ms_user.id)
                    s = ms_user.b_path_std + ms_user.i_path_std + ms_user.e_path_std
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_std_ids", {ms_user.id: s})

    if video_i.mode == "00":
        if e_video.flag == 0:
            video_i.mode = "12"

    if video_i.mode == "12":
        if video_i.level == "b":
            if video_i.rtime < ms_user.b_time_nf:
                ms_user.b_time_nf = video_i.rtime
                ms_user.b_time_id_nf = e_video.id
                if ms_user.b_time_nf < 999.998 and ms_user.i_time_nf < 999.998 and ms_user.e_time_nf < 999.998:
                    key = f"player_time_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_nf))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_nf))
                    cache.hset(key, "i", float(ms_user.i_time_nf))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_nf))
                    cache.hset(key, "e", float(ms_user.e_time_nf))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_nf))
                    # cache.hset(key, "sum", float(ms_user.b_time_nf + ms_user.i_time_nf + ms_user.e_time_nf))
                    # if not cache.lindex('player_time_nf_ids', ms_user.id):
                    #     cache.lpush('player_time_nf_ids', ms_user.id)
                    s = float(ms_user.b_time_nf + ms_user.i_time_nf + ms_user.e_time_nf)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_nf_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.b_bvs_nf:
                ms_user.b_bvs_nf = video_i.bvs
                ms_user.b_bvs_id_nf = e_video.id
                if ms_user.b_bvs_nf > 0.001 and ms_user.i_bvs_nf > 0.001 and ms_user.e_bvs_nf > 0.001:
                    key = f"player_bvs_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_nf)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_nf)
                    cache.hset(key, "i", ms_user.i_bvs_nf)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_nf)
                    cache.hset(key, "e", ms_user.e_bvs_nf)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_nf)
                    # cache.hset(key, "sum", ms_user.b_bvs_nf + ms_user.i_bvs_nf + ms_user.e_bvs_nf)
                    # if not cache.lindex('player_bvs_nf_ids', ms_user.id):
                    #     cache.lpush('player_bvs_nf_ids', ms_user.id)
                    s = ms_user.b_bvs_nf + ms_user.i_bvs_nf + ms_user.e_bvs_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_nf_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.b_stnb_nf:
                ms_user.b_stnb_nf = e_video.stnb
                ms_user.b_stnb_id_nf = e_video.id
                if ms_user.b_stnb_nf > 0.001 and ms_user.i_stnb_nf > 0.001 and ms_user.e_stnb_nf > 0.001:
                    key = f"player_stnb_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_nf)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_nf)
                    cache.hset(key, "i", ms_user.i_stnb_nf)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_nf)
                    cache.hset(key, "e", ms_user.e_stnb_nf)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_nf)
                    # cache.hset(key, "sum", ms_user.b_stnb_nf + ms_user.i_stnb_nf + ms_user.e_stnb_nf)
                    # if not cache.lindex('player_stnb_nf_ids', ms_user.id):
                    #     cache.lpush('player_stnb_nf_ids', ms_user.id)
                    s = ms_user.b_stnb_nf + ms_user.i_stnb_nf + ms_user.e_stnb_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_nf_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.b_ioe_nf:
                ms_user.b_ioe_nf = e_video.ioe
                ms_user.b_ioe_id_nf = e_video.id
                if ms_user.b_ioe_nf > 0.001 and ms_user.i_ioe_nf > 0.001 and ms_user.e_ioe_nf > 0.001:
                    key = f"player_ioe_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_nf)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_nf)
                    cache.hset(key, "i", ms_user.i_ioe_nf)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_nf)
                    cache.hset(key, "e", ms_user.e_ioe_nf)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_nf)
                    # cache.hset(key, "sum", ms_user.b_ioe_nf + ms_user.i_ioe_nf + ms_user.e_ioe_nf)
                    # if not cache.lindex('player_ioe_nf_ids', ms_user.id):
                    #     cache.lpush('player_ioe_nf_ids', ms_user.id)
                    s = ms_user.b_ioe_nf + ms_user.i_ioe_nf + ms_user.e_ioe_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_nf_ids", {ms_user.id: s})
            if e_video.path < ms_user.b_path_nf:
                ms_user.b_path_nf = e_video.path
                ms_user.b_path_id_nf = e_video.id
                if ms_user.b_path_nf < 99999.8 and ms_user.i_path_nf < 99999.8 and ms_user.e_path_nf < 99999.8:
                    key = f"player_path_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_nf)
                    cache.hset(key, "b_id", ms_user.b_path_id_nf)
                    cache.hset(key, "i", ms_user.i_path_nf)
                    cache.hset(key, "i_id", ms_user.i_path_id_nf)
                    cache.hset(key, "e", ms_user.e_path_nf)
                    cache.hset(key, "e_id", ms_user.e_path_id_nf)
                    # cache.hset(key, "sum", ms_user.b_path_nf + ms_user.i_path_nf + ms_user.e_path_nf)
                    # if not cache.lindex('player_path_nf_ids', ms_user.id):
                    #     cache.lpush('player_path_nf_ids', ms_user.id)
                    s = ms_user.b_path_nf + ms_user.i_path_nf + ms_user.e_path_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_nf_ids", {ms_user.id: s})
        if video_i.level == "i":
            if video_i.rtime < ms_user.i_time_nf:
                ms_user.i_time_nf = video_i.rtime
                ms_user.i_time_id_nf = e_video.id
                if ms_user.b_time_nf < 999.998 and ms_user.i_time_nf < 999.998 and ms_user.e_time_nf < 999.998:
                    key = f"player_time_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_nf))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_nf))
                    cache.hset(key, "i", float(ms_user.i_time_nf))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_nf))
                    cache.hset(key, "e", float(ms_user.e_time_nf))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_nf))
                    # cache.hset(key, "sum", float(ms_user.b_time_nf + ms_user.i_time_nf + ms_user.e_time_nf))
                    # if not cache.lindex('player_time_nf_ids', ms_user.id):
                    #     cache.lpush('player_time_nf_ids', ms_user.id)
                    s = float(ms_user.b_time_nf + ms_user.i_time_nf + ms_user.e_time_nf)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_nf_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.i_bvs_nf:
                ms_user.i_bvs_nf = video_i.bvs
                ms_user.i_bvs_id_nf = e_video.id
                if ms_user.b_bvs_nf > 0.001 and ms_user.i_bvs_nf > 0.001 and ms_user.e_bvs_nf > 0.001:
                    key = f"player_bvs_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_nf)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_nf)
                    cache.hset(key, "i", ms_user.i_bvs_nf)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_nf)
                    cache.hset(key, "e", ms_user.e_bvs_nf)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_nf)
                    # cache.hset(key, "sum", ms_user.b_bvs_nf + ms_user.i_bvs_nf + ms_user.e_bvs_nf)
                    # if not cache.lindex('player_bvs_nf_ids', ms_user.id):
                    #     cache.lpush('player_bvs_nf_ids', ms_user.id)
                    s = ms_user.b_bvs_nf + ms_user.i_bvs_nf + ms_user.e_bvs_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_nf_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.i_stnb_nf:
                ms_user.i_stnb_nf = e_video.stnb
                ms_user.i_stnb_id_nf = e_video.id
                if ms_user.b_stnb_nf > 0.001 and ms_user.i_stnb_nf > 0.001 and ms_user.e_stnb_nf > 0.001:
                    key = f"player_stnb_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_nf)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_nf)
                    cache.hset(key, "i", ms_user.i_stnb_nf)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_nf)
                    cache.hset(key, "e", ms_user.e_stnb_nf)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_nf)
                    # cache.hset(key, "sum", ms_user.b_stnb_nf + ms_user.i_stnb_nf + ms_user.e_stnb_nf)
                    # if not cache.lindex('player_stnb_nf_ids', ms_user.id):
                    #     cache.lpush('player_stnb_nf_ids', ms_user.id)
                    s = ms_user.b_stnb_nf + ms_user.i_stnb_nf + ms_user.e_stnb_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_nf_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.i_ioe_nf:
                ms_user.i_ioe_nf = e_video.ioe
                ms_user.i_ioe_id_nf = e_video.id
                if ms_user.b_ioe_nf > 0.001 and ms_user.i_ioe_nf > 0.001 and ms_user.e_ioe_nf > 0.001:
                    key = f"player_ioe_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_nf)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_nf)
                    cache.hset(key, "i", ms_user.i_ioe_nf)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_nf)
                    cache.hset(key, "e", ms_user.e_ioe_nf)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_nf)
                    # cache.hset(key, "sum", ms_user.b_ioe_nf + ms_user.i_ioe_nf + ms_user.e_ioe_nf)
                    # if not cache.lindex('player_ioe_nf_ids', ms_user.id):
                    #     cache.lpush('player_ioe_nf_ids', ms_user.id)
                    s = ms_user.b_ioe_nf + ms_user.i_ioe_nf + ms_user.e_ioe_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_nf_ids", {ms_user.id: s})
            if e_video.path < ms_user.i_path_nf:
                ms_user.i_path_nf = e_video.path
                ms_user.i_path_id_nf = e_video.id
                if ms_user.b_path_nf < 99999.8 and ms_user.i_path_nf < 99999.8 and ms_user.e_path_nf < 99999.8:
                    key = f"player_path_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_nf)
                    cache.hset(key, "b_id", ms_user.b_path_id_nf)
                    cache.hset(key, "i", ms_user.i_path_nf)
                    cache.hset(key, "i_id", ms_user.i_path_id_nf)
                    cache.hset(key, "e", ms_user.e_path_nf)
                    cache.hset(key, "e_id", ms_user.e_path_id_nf)
                    # cache.hset(key, "sum", ms_user.b_path_nf + ms_user.i_path_nf + ms_user.e_path_nf)
                    # if not cache.lindex('player_path_nf_ids', ms_user.id):
                    #     cache.lpush('player_path_nf_ids', ms_user.id)
                    s = ms_user.b_path_nf + ms_user.i_path_nf + ms_user.e_path_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_nf_ids", {ms_user.id: s})
        if video_i.level == "e":
            if video_i.rtime < ms_user.e_time_nf:
                ms_user.e_time_nf = video_i.rtime
                ms_user.e_time_id_nf = e_video.id
                if ms_user.b_time_nf < 999.998 and ms_user.i_time_nf < 999.998 and ms_user.e_time_nf < 999.998:
                    key = f"player_time_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_nf))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_nf))
                    cache.hset(key, "i", float(ms_user.i_time_nf))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_nf))
                    cache.hset(key, "e", float(ms_user.e_time_nf))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_nf))
                    # cache.hset(key, "sum", float(ms_user.b_time_nf + ms_user.i_time_nf + ms_user.e_time_nf))
                    # if not cache.lindex('player_time_nf_ids', ms_user.id):
                    #     cache.lpush('player_time_nf_ids', ms_user.id)
                    s = float(ms_user.b_time_nf + ms_user.i_time_nf + ms_user.e_time_nf)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_nf_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.e_bvs_nf:
                ms_user.e_bvs_nf = video_i.bvs
                ms_user.e_bvs_id_nf = e_video.id
                if ms_user.b_bvs_nf > 0.001 and ms_user.i_bvs_nf > 0.001 and ms_user.e_bvs_nf > 0.001:
                    key = f"player_bvs_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_nf)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_nf)
                    cache.hset(key, "i", ms_user.i_bvs_nf)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_nf)
                    cache.hset(key, "e", ms_user.e_bvs_nf)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_nf)
                    # cache.hset(key, "sum", ms_user.b_bvs_nf + ms_user.i_bvs_nf + ms_user.e_bvs_nf)
                    # if not cache.lindex('player_bvs_nf_ids', ms_user.id):
                    #     cache.lpush('player_bvs_nf_ids', ms_user.id)
                    s = ms_user.b_bvs_nf + ms_user.i_bvs_nf + ms_user.e_bvs_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_nf_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.e_stnb_nf:
                ms_user.e_stnb_nf = e_video.stnb
                ms_user.e_stnb_id_nf = e_video.id
                if ms_user.b_stnb_nf > 0.001 and ms_user.i_stnb_nf > 0.001 and ms_user.e_stnb_nf > 0.001:
                    key = f"player_stnb_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_nf)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_nf)
                    cache.hset(key, "i", ms_user.i_stnb_nf)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_nf)
                    cache.hset(key, "e", ms_user.e_stnb_nf)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_nf)
                    # cache.hset(key, "sum", ms_user.b_stnb_nf + ms_user.i_stnb_nf + ms_user.e_stnb_nf)
                    # if not cache.lindex('player_stnb_nf_ids', ms_user.id):
                    #     cache.lpush('player_stnb_nf_ids', ms_user.id)
                    s = ms_user.b_stnb_nf + ms_user.i_stnb_nf + ms_user.e_stnb_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_nf_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.e_ioe_nf:
                ms_user.e_ioe_nf = e_video.ioe
                ms_user.e_ioe_id_nf = e_video.id
                if ms_user.b_ioe_nf > 0.001 and ms_user.i_ioe_nf > 0.001 and ms_user.e_ioe_nf > 0.001:
                    key = f"player_ioe_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_nf)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_nf)
                    cache.hset(key, "i", ms_user.i_ioe_nf)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_nf)
                    cache.hset(key, "e", ms_user.e_ioe_nf)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_nf)
                    # cache.hset(key, "sum", ms_user.b_ioe_nf + ms_user.i_ioe_nf + ms_user.e_ioe_nf)
                    # if not cache.lindex('player_ioe_nf_ids', ms_user.id):
                    #     cache.lpush('player_ioe_nf_ids', ms_user.id)
                    s = ms_user.b_ioe_nf + ms_user.i_ioe_nf + ms_user.e_ioe_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_nf_ids", {ms_user.id: s})
            if e_video.path < ms_user.e_path_nf:
                ms_user.e_path_nf = e_video.path
                ms_user.e_path_id_nf = e_video.id
                if ms_user.b_path_nf < 99999.8 and ms_user.i_path_nf < 99999.8 and ms_user.e_path_nf < 99999.8:
                    key = f"player_path_nf_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_nf)
                    cache.hset(key, "b_id", ms_user.b_path_id_nf)
                    cache.hset(key, "i", ms_user.i_path_nf)
                    cache.hset(key, "i_id", ms_user.i_path_id_nf)
                    cache.hset(key, "e", ms_user.e_path_nf)
                    cache.hset(key, "e_id", ms_user.e_path_id_nf)
                    # cache.hset(key, "sum", ms_user.b_path_nf + ms_user.i_path_nf + ms_user.e_path_nf)
                    # if not cache.lindex('player_path_nf_ids', ms_user.id):
                    #     cache.lpush('player_path_nf_ids', ms_user.id)
                    s = ms_user.b_path_nf + ms_user.i_path_nf + ms_user.e_path_nf
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_nf_ids", {ms_user.id: s})

    if video_i.mode == "05":
        if video_i.level == "b":
            if video_i.rtime < ms_user.b_time_ng:
                ms_user.b_time_ng = video_i.rtime
                ms_user.b_time_id_ng = e_video.id
                if ms_user.b_time_ng < 999.998 and ms_user.i_time_ng < 999.998 and ms_user.e_time_ng < 999.998:
                    key = f"player_time_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_ng))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_ng))
                    cache.hset(key, "i", float(ms_user.i_time_ng))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_ng))
                    cache.hset(key, "e", float(ms_user.e_time_ng))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_ng))
                    # cache.hset(key, "sum", float(ms_user.b_time_ng + ms_user.i_time_ng + ms_user.e_time_ng))
                    # if not cache.lindex('player_time_ng_ids', ms_user.id):
                    #     cache.lpush('player_time_ng_ids', ms_user.id)
                    s = float(ms_user.b_time_ng + ms_user.i_time_ng + ms_user.e_time_ng)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_ng_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.b_bvs_ng:
                ms_user.b_bvs_ng = video_i.bvs
                ms_user.b_bvs_id_ng = e_video.id
                if ms_user.b_bvs_ng > 0.001 and ms_user.i_bvs_ng > 0.001 and ms_user.e_bvs_ng > 0.001:
                    key = f"player_bvs_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_ng)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_ng)
                    cache.hset(key, "i", ms_user.i_bvs_ng)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_ng)
                    cache.hset(key, "e", ms_user.e_bvs_ng)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_ng)
                    # cache.hset(key, "sum", ms_user.b_bvs_ng + ms_user.i_bvs_ng + ms_user.e_bvs_ng)
                    # if not cache.lindex('player_bvs_ng_ids', ms_user.id):
                    #     cache.lpush('player_bvs_ng_ids', ms_user.id)
                    s = ms_user.b_bvs_ng + ms_user.i_bvs_ng + ms_user.e_bvs_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_ng_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.b_stnb_ng:
                ms_user.b_stnb_ng = e_video.stnb
                ms_user.b_stnb_id_ng = e_video.id
                if ms_user.b_stnb_ng > 0.001 and ms_user.i_stnb_ng > 0.001 and ms_user.e_stnb_ng > 0.001:
                    key = f"player_stnb_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_ng)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_ng)
                    cache.hset(key, "i", ms_user.i_stnb_ng)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_ng)
                    cache.hset(key, "e", ms_user.e_stnb_ng)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_ng)
                    # cache.hset(key, "sum", ms_user.b_stnb_ng + ms_user.i_stnb_ng + ms_user.e_stnb_ng)
                    # if not cache.lindex('player_stnb_ng_ids', ms_user.id):
                    #     cache.lpush('player_stnb_ng_ids', ms_user.id)
                    s = ms_user.b_stnb_ng + ms_user.i_stnb_ng + ms_user.e_stnb_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_ng_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.b_ioe_ng:
                ms_user.b_ioe_ng = e_video.ioe
                ms_user.b_ioe_id_ng = e_video.id
                if ms_user.b_ioe_ng > 0.001 and ms_user.i_ioe_ng > 0.001 and ms_user.e_ioe_ng > 0.001:
                    key = f"player_ioe_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_ng)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_ng)
                    cache.hset(key, "i", ms_user.i_ioe_ng)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_ng)
                    cache.hset(key, "e", ms_user.e_ioe_ng)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_ng)
                    # cache.hset(key, "sum", ms_user.b_ioe_ng + ms_user.i_ioe_ng + ms_user.e_ioe_ng)
                    # if not cache.lindex('player_ioe_ng_ids', ms_user.id):
                    #     cache.lpush('player_ioe_ng_ids', ms_user.id)
                    s = ms_user.b_ioe_ng + ms_user.i_ioe_ng + ms_user.e_ioe_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_ng_ids", {ms_user.id: s})
            if e_video.path < ms_user.b_path_ng:
                ms_user.b_path_ng = e_video.path
                ms_user.b_path_id_ng = e_video.id
                if ms_user.b_path_ng < 99999.8 and ms_user.i_path_ng < 99999.8 and ms_user.e_path_ng < 99999.8:
                    key = f"player_path_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_ng)
                    cache.hset(key, "b_id", ms_user.b_path_id_ng)
                    cache.hset(key, "i", ms_user.i_path_ng)
                    cache.hset(key, "i_id", ms_user.i_path_id_ng)
                    cache.hset(key, "e", ms_user.e_path_ng)
                    cache.hset(key, "e_id", ms_user.e_path_id_ng)
                    # cache.hset(key, "sum", ms_user.b_path_ng + ms_user.i_path_ng + ms_user.e_path_ng)
                    # if not cache.lindex('player_path_ng_ids', ms_user.id):
                    #     cache.lpush('player_path_ng_ids', ms_user.id)
                    s = ms_user.b_path_ng + ms_user.i_path_ng + ms_user.e_path_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_ng_ids", {ms_user.id: s})
        if video_i.level == "i":
            if video_i.rtime < ms_user.i_time_ng:
                ms_user.i_time_ng = video_i.rtime
                ms_user.i_time_id_ng = e_video.id
                if ms_user.b_time_ng < 999.998 and ms_user.i_time_ng < 999.998 and ms_user.e_time_ng < 999.998:
                    key = f"player_time_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_ng))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_ng))
                    cache.hset(key, "i", float(ms_user.i_time_ng))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_ng))
                    cache.hset(key, "e", float(ms_user.e_time_ng))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_ng))
                    # cache.hset(key, "sum", float(ms_user.b_time_ng + ms_user.i_time_ng + ms_user.e_time_ng))
                    # if not cache.lindex('player_time_ng_ids', ms_user.id):
                    #     cache.lpush('player_time_ng_ids', ms_user.id)
                    s = float(ms_user.b_time_ng + ms_user.i_time_ng + ms_user.e_time_ng)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_ng_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.i_bvs_ng:
                ms_user.i_bvs_ng = video_i.bvs
                ms_user.i_bvs_id_ng = e_video.id
                if ms_user.b_bvs_ng > 0.001 and ms_user.i_bvs_ng > 0.001 and ms_user.e_bvs_ng > 0.001:
                    key = f"player_bvs_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_ng)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_ng)
                    cache.hset(key, "i", ms_user.i_bvs_ng)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_ng)
                    cache.hset(key, "e", ms_user.e_bvs_ng)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_ng)
                    # cache.hset(key, "sum", ms_user.b_bvs_ng + ms_user.i_bvs_ng + ms_user.e_bvs_ng)
                    # if not cache.lindex('player_bvs_ng_ids', ms_user.id):
                    #     cache.lpush('player_bvs_ng_ids', ms_user.id)
                    s = ms_user.b_bvs_ng + ms_user.i_bvs_ng + ms_user.e_bvs_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_ng_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.i_stnb_ng:
                ms_user.i_stnb_ng = e_video.stnb
                ms_user.i_stnb_id_ng = e_video.id
                if ms_user.b_stnb_ng > 0.001 and ms_user.i_stnb_ng > 0.001 and ms_user.e_stnb_ng > 0.001:
                    key = f"player_stnb_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_ng)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_ng)
                    cache.hset(key, "i", ms_user.i_stnb_ng)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_ng)
                    cache.hset(key, "e", ms_user.e_stnb_ng)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_ng)
                    # cache.hset(key, "sum", ms_user.b_stnb_ng + ms_user.i_stnb_ng + ms_user.e_stnb_ng)
                    # if not cache.lindex('player_stnb_ng_ids', ms_user.id):
                    #     cache.lpush('player_stnb_ng_ids', ms_user.id)
                    s = ms_user.b_stnb_ng + ms_user.i_stnb_ng + ms_user.e_stnb_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_ng_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.i_ioe_ng:
                ms_user.i_ioe_ng = e_video.ioe
                ms_user.i_ioe_id_ng = e_video.id
                if ms_user.b_ioe_ng > 0.001 and ms_user.i_ioe_ng > 0.001 and ms_user.e_ioe_ng > 0.001:
                    key = f"player_ioe_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_ng)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_ng)
                    cache.hset(key, "i", ms_user.i_ioe_ng)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_ng)
                    cache.hset(key, "e", ms_user.e_ioe_ng)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_ng)
                    # cache.hset(key, "sum", ms_user.b_ioe_ng + ms_user.i_ioe_ng + ms_user.e_ioe_ng)
                    # if not cache.lindex('player_ioe_ng_ids', ms_user.id):
                    #     cache.lpush('player_ioe_ng_ids', ms_user.id)
                    s = ms_user.b_ioe_ng + ms_user.i_ioe_ng + ms_user.e_ioe_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_ng_ids", {ms_user.id: s})
            if e_video.path < ms_user.i_path_ng:
                ms_user.i_path_ng = e_video.path
                ms_user.i_path_id_ng = e_video.id
                if ms_user.b_path_ng < 99999.8 and ms_user.i_path_ng < 99999.8 and ms_user.e_path_ng < 99999.8:
                    key = f"player_path_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_ng)
                    cache.hset(key, "b_id", ms_user.b_path_id_ng)
                    cache.hset(key, "i", ms_user.i_path_ng)
                    cache.hset(key, "i_id", ms_user.i_path_id_ng)
                    cache.hset(key, "e", ms_user.e_path_ng)
                    cache.hset(key, "e_id", ms_user.e_path_id_ng)
                    # cache.hset(key, "sum", ms_user.b_path_ng + ms_user.i_path_ng + ms_user.e_path_ng)
                    # if not cache.lindex('player_path_ng_ids', ms_user.id):
                    #     cache.lpush('player_path_ng_ids', ms_user.id)
                    s = ms_user.b_path_ng + ms_user.i_path_ng + ms_user.e_path_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_ng_ids", {ms_user.id: s})
        if video_i.level == "e":
            if video_i.rtime < ms_user.e_time_ng:
                ms_user.e_time_ng = video_i.rtime
                ms_user.e_time_id_ng = e_video.id
                if ms_user.b_time_ng < 999.998 and ms_user.i_time_ng < 999.998 and ms_user.e_time_ng < 999.998:
                    key = f"player_time_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_ng))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_ng))
                    cache.hset(key, "i", float(ms_user.i_time_ng))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_ng))
                    cache.hset(key, "e", float(ms_user.e_time_ng))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_ng))
                    # cache.hset(key, "sum", float(ms_user.b_time_ng + ms_user.i_time_ng + ms_user.e_time_ng))
                    # if not cache.lindex('player_time_ng_ids', ms_user.id):
                    #     cache.lpush('player_time_ng_ids', ms_user.id)
                    s = float(ms_user.b_time_ng + ms_user.i_time_ng + ms_user.e_time_ng)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_ng_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.e_bvs_ng:
                ms_user.e_bvs_ng = video_i.bvs
                ms_user.e_bvs_id_ng = e_video.id
                if ms_user.b_bvs_ng > 0.001 and ms_user.i_bvs_ng > 0.001 and ms_user.e_bvs_ng > 0.001:
                    key = f"player_bvs_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_ng)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_ng)
                    cache.hset(key, "i", ms_user.i_bvs_ng)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_ng)
                    cache.hset(key, "e", ms_user.e_bvs_ng)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_ng)
                    # cache.hset(key, "sum", ms_user.b_bvs_ng + ms_user.i_bvs_ng + ms_user.e_bvs_ng)
                    # if not cache.lindex('player_bvs_ng_ids', ms_user.id):
                    #     cache.lpush('player_bvs_ng_ids', ms_user.id)
                    s = ms_user.b_bvs_ng + ms_user.i_bvs_ng + ms_user.e_bvs_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_ng_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.e_stnb_ng:
                ms_user.e_stnb_ng = e_video.stnb
                ms_user.e_stnb_id_ng = e_video.id
                if ms_user.b_stnb_ng > 0.001 and ms_user.i_stnb_ng > 0.001 and ms_user.e_stnb_ng > 0.001:
                    key = f"player_stnb_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_ng)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_ng)
                    cache.hset(key, "i", ms_user.i_stnb_ng)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_ng)
                    cache.hset(key, "e", ms_user.e_stnb_ng)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_ng)
                    # cache.hset(key, "sum", ms_user.b_stnb_ng + ms_user.i_stnb_ng + ms_user.e_stnb_ng)
                    # if not cache.lindex('player_stnb_ng_ids', ms_user.id):
                    #     cache.lpush('player_stnb_ng_ids', ms_user.id)
                    s = ms_user.b_stnb_ng + ms_user.i_stnb_ng + ms_user.e_stnb_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_ng_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.e_ioe_ng:
                ms_user.e_ioe_ng = e_video.ioe
                ms_user.e_ioe_id_ng = e_video.id
                if ms_user.b_ioe_ng > 0.001 and ms_user.i_ioe_ng > 0.001 and ms_user.e_ioe_ng > 0.001:
                    key = f"player_ioe_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_ng)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_ng)
                    cache.hset(key, "i", ms_user.i_ioe_ng)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_ng)
                    cache.hset(key, "e", ms_user.e_ioe_ng)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_ng)
                    # cache.hset(key, "sum", ms_user.b_ioe_ng + ms_user.i_ioe_ng + ms_user.e_ioe_ng)
                    # if not cache.lindex('player_ioe_ng_ids', ms_user.id):
                    #     cache.lpush('player_ioe_ng_ids', ms_user.id)
                    s = ms_user.b_ioe_ng + ms_user.i_ioe_ng + ms_user.e_ioe_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_ng_ids", {ms_user.id: s})
            if e_video.path < ms_user.e_path_ng:
                ms_user.e_path_ng = e_video.path
                ms_user.e_path_id_ng = e_video.id
                if ms_user.b_path_ng < 99999.8 and ms_user.i_path_ng < 99999.8 and ms_user.e_path_ng < 99999.8:
                    key = f"player_path_ng_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_ng)
                    cache.hset(key, "b_id", ms_user.b_path_id_ng)
                    cache.hset(key, "i", ms_user.i_path_ng)
                    cache.hset(key, "i_id", ms_user.i_path_id_ng)
                    cache.hset(key, "e", ms_user.e_path_ng)
                    cache.hset(key, "e_id", ms_user.e_path_id_ng)
                    # cache.hset(key, "sum", ms_user.b_path_ng + ms_user.i_path_ng + ms_user.e_path_ng)
                    # if not cache.lindex('player_path_ng_ids', ms_user.id):
                    #     cache.lpush('player_path_ng_ids', ms_user.id)
                    s = ms_user.b_path_ng + ms_user.i_path_ng + ms_user.e_path_ng
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_ng_ids", {ms_user.id: s})

    if video_i.mode == "11":
        if video_i.level == "b":
            if video_i.rtime < ms_user.b_time_dg:
                ms_user.b_time_dg = video_i.rtime
                ms_user.b_time_id_dg = e_video.id
                if ms_user.b_time_dg < 999.998 and ms_user.i_time_dg < 999.998 and ms_user.e_time_dg < 999.998:
                    key = f"player_time_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_dg))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_dg))
                    cache.hset(key, "i", float(ms_user.i_time_dg))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_dg))
                    cache.hset(key, "e", float(ms_user.e_time_dg))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_dg))
                    # cache.hset(key, "sum", float(ms_user.b_time_dg + ms_user.i_time_dg + ms_user.e_time_dg))
                    # if not cache.lindex('player_time_dg_ids', ms_user.id):
                    #     cache.lpush('player_time_dg_ids', ms_user.id)
                    s = float(ms_user.b_time_dg + ms_user.i_time_dg + ms_user.e_time_dg)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_dg_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.b_bvs_dg:
                ms_user.b_bvs_dg = video_i.bvs
                ms_user.b_bvs_id_dg = e_video.id
                if ms_user.b_bvs_dg > 0.001 and ms_user.i_bvs_dg > 0.001 and ms_user.e_bvs_dg > 0.001:
                    key = f"player_bvs_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_dg)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_dg)
                    cache.hset(key, "i", ms_user.i_bvs_dg)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_dg)
                    cache.hset(key, "e", ms_user.e_bvs_dg)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_dg)
                    # cache.hset(key, "sum", ms_user.b_bvs_dg + ms_user.i_bvs_dg + ms_user.e_bvs_dg)
                    # if not cache.lindex('player_bvs_dg_ids', ms_user.id):
                    #     cache.lpush('player_bvs_dg_ids', ms_user.id)
                    s = ms_user.b_bvs_dg + ms_user.i_bvs_dg + ms_user.e_bvs_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_dg_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.b_stnb_dg:
                ms_user.b_stnb_dg = e_video.stnb
                ms_user.b_stnb_id_dg = e_video.id
                if ms_user.b_stnb_dg > 0.001 and ms_user.i_stnb_dg > 0.001 and ms_user.e_stnb_dg > 0.001:
                    key = f"player_stnb_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_dg)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_dg)
                    cache.hset(key, "i", ms_user.i_stnb_dg)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_dg)
                    cache.hset(key, "e", ms_user.e_stnb_dg)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_dg)
                    # cache.hset(key, "sum", ms_user.b_stnb_dg + ms_user.i_stnb_dg + ms_user.e_stnb_dg)
                    # if not cache.lindex('player_stnb_dg_ids', ms_user.id):
                    #     cache.lpush('player_stnb_dg_ids', ms_user.id)
                    s = ms_user.b_stnb_dg + ms_user.i_stnb_dg + ms_user.e_stnb_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_dg_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.b_ioe_dg:
                ms_user.b_ioe_dg = e_video.ioe
                ms_user.b_ioe_id_dg = e_video.id
                if ms_user.b_ioe_dg > 0.001 and ms_user.i_ioe_dg > 0.001 and ms_user.e_ioe_dg > 0.001:
                    key = f"player_ioe_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_dg)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_dg)
                    cache.hset(key, "i", ms_user.i_ioe_dg)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_dg)
                    cache.hset(key, "e", ms_user.e_ioe_dg)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_dg)
                    # cache.hset(key, "sum", ms_user.b_ioe_dg + ms_user.i_ioe_dg + ms_user.e_ioe_dg)
                    # if not cache.lindex('player_ioe_dg_ids', ms_user.id):
                    #     cache.lpush('player_ioe_dg_ids', ms_user.id)
                    s = ms_user.b_ioe_dg + ms_user.i_ioe_dg + ms_user.e_ioe_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_dg_ids", {ms_user.id: s})
            if e_video.path < ms_user.b_path_dg:
                ms_user.b_path_dg = e_video.path
                ms_user.b_path_id_dg = e_video.id
                if ms_user.b_path_dg < 99999.8 and ms_user.i_path_dg < 99999.8 and ms_user.e_path_dg < 99999.8:
                    key = f"player_path_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_dg)
                    cache.hset(key, "b_id", ms_user.b_path_id_dg)
                    cache.hset(key, "i", ms_user.i_path_dg)
                    cache.hset(key, "i_id", ms_user.i_path_id_dg)
                    cache.hset(key, "e", ms_user.e_path_dg)
                    cache.hset(key, "e_id", ms_user.e_path_id_dg)
                    # cache.hset(key, "sum", ms_user.b_path_dg + ms_user.i_path_dg + ms_user.e_path_dg)
                    # if not cache.lindex('player_path_dg_ids', ms_user.id):
                    #     cache.lpush('player_path_dg_ids', ms_user.id)
                    s = ms_user.b_path_dg + ms_user.i_path_dg + ms_user.e_path_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_dg_ids", {ms_user.id: s})
        if video_i.level == "i":
            if video_i.rtime < ms_user.i_time_dg:
                ms_user.i_time_dg = video_i.rtime
                ms_user.i_time_id_dg = e_video.id
                if ms_user.b_time_dg < 999.998 and ms_user.i_time_dg < 999.998 and ms_user.e_time_dg < 999.998:
                    key = f"player_time_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_dg))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_dg))
                    cache.hset(key, "i", float(ms_user.i_time_dg))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_dg))
                    cache.hset(key, "e", float(ms_user.e_time_dg))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_dg))
                    # cache.hset(key, "sum", float(ms_user.b_time_dg + ms_user.i_time_dg + ms_user.e_time_dg))
                    # if not cache.lindex('player_time_dg_ids', ms_user.id):
                    #     cache.lpush('player_time_dg_ids', ms_user.id)
                    s = float(ms_user.b_time_dg + ms_user.i_time_dg + ms_user.e_time_dg)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_dg_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.i_bvs_dg:
                ms_user.i_bvs_dg = video_i.bvs
                ms_user.i_bvs_id_dg = e_video.id
                if ms_user.b_bvs_dg > 0.001 and ms_user.i_bvs_dg > 0.001 and ms_user.e_bvs_dg > 0.001:
                    key = f"player_bvs_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_dg)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_dg)
                    cache.hset(key, "i", ms_user.i_bvs_dg)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_dg)
                    cache.hset(key, "e", ms_user.e_bvs_dg)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_dg)
                    # cache.hset(key, "sum", ms_user.b_bvs_dg + ms_user.i_bvs_dg + ms_user.e_bvs_dg)
                    # if not cache.lindex('player_bvs_dg_ids', ms_user.id):
                    #     cache.lpush('player_bvs_dg_ids', ms_user.id)
                    s = ms_user.b_bvs_dg + ms_user.i_bvs_dg + ms_user.e_bvs_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_dg_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.i_stnb_dg:
                ms_user.i_stnb_dg = e_video.stnb
                ms_user.i_stnb_id_dg = e_video.id
                if ms_user.b_stnb_dg > 0.001 and ms_user.i_stnb_dg > 0.001 and ms_user.e_stnb_dg > 0.001:
                    key = f"player_stnb_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_dg)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_dg)
                    cache.hset(key, "i", ms_user.i_stnb_dg)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_dg)
                    cache.hset(key, "e", ms_user.e_stnb_dg)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_dg)
                    # cache.hset(key, "sum", ms_user.b_stnb_dg + ms_user.i_stnb_dg + ms_user.e_stnb_dg)
                    # if not cache.lindex('player_stnb_dg_ids', ms_user.id):
                    #     cache.lpush('player_stnb_dg_ids', ms_user.id)
                    s = ms_user.b_stnb_dg + ms_user.i_stnb_dg + ms_user.e_stnb_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_dg_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.i_ioe_dg:
                ms_user.i_ioe_dg = e_video.ioe
                ms_user.i_ioe_id_dg = e_video.id
                if ms_user.b_ioe_dg > 0.001 and ms_user.i_ioe_dg > 0.001 and ms_user.e_ioe_dg > 0.001:
                    key = f"player_ioe_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_dg)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_dg)
                    cache.hset(key, "i", ms_user.i_ioe_dg)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_dg)
                    cache.hset(key, "e", ms_user.e_ioe_dg)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_dg)
                    # cache.hset(key, "sum", ms_user.b_ioe_dg + ms_user.i_ioe_dg + ms_user.e_ioe_dg)
                    # if not cache.lindex('player_ioe_dg_ids', ms_user.id):
                    #     cache.lpush('player_ioe_dg_ids', ms_user.id)
                    s = ms_user.b_ioe_dg + ms_user.i_ioe_dg + ms_user.e_ioe_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_dg_ids", {ms_user.id: s})
            if e_video.path < ms_user.i_path_dg:
                ms_user.i_path_dg = e_video.path
                ms_user.i_path_id_dg = e_video.id
                if ms_user.b_path_dg < 99999.8 and ms_user.i_path_dg < 99999.8 and ms_user.e_path_dg < 99999.8:
                    key = f"player_path_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_dg)
                    cache.hset(key, "b_id", ms_user.b_path_id_dg)
                    cache.hset(key, "i", ms_user.i_path_dg)
                    cache.hset(key, "i_id", ms_user.i_path_id_dg)
                    cache.hset(key, "e", ms_user.e_path_dg)
                    cache.hset(key, "e_id", ms_user.e_path_id_dg)
                    # cache.hset(key, "sum", ms_user.b_path_dg + ms_user.i_path_dg + ms_user.e_path_dg)
                    # if not cache.lindex('player_path_dg_ids', ms_user.id):
                    #     cache.lpush('player_path_dg_ids', ms_user.id)
                    s = ms_user.b_path_dg + ms_user.i_path_dg + ms_user.e_path_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_dg_ids", {ms_user.id: s})
        if video_i.level == "e":
            if video_i.rtime < ms_user.e_time_dg:
                ms_user.e_time_dg = video_i.rtime
                ms_user.e_time_id_dg = e_video.id
                if ms_user.b_time_dg < 999.998 and ms_user.i_time_dg < 999.998 and ms_user.e_time_dg < 999.998:
                    key = f"player_time_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", float(ms_user.b_time_dg))
                    cache.hset(key, "b_id", float(ms_user.b_time_id_dg))
                    cache.hset(key, "i", float(ms_user.i_time_dg))
                    cache.hset(key, "i_id", float(ms_user.i_time_id_dg))
                    cache.hset(key, "e", float(ms_user.e_time_dg))
                    cache.hset(key, "e_id", float(ms_user.e_time_id_dg))
                    # cache.hset(key, "sum", float(ms_user.b_time_dg + ms_user.i_time_dg + ms_user.e_time_dg))
                    # if not cache.lindex('player_time_dg_ids', ms_user.id):
                    #     cache.lpush('player_time_dg_ids', ms_user.id)
                    s = float(ms_user.b_time_dg + ms_user.i_time_dg + ms_user.e_time_dg)
                    cache.hset(key, "sum", s)
                    cache.zadd("player_time_dg_ids", {ms_user.id: s})
            if video_i.bvs > ms_user.e_bvs_dg:
                ms_user.e_bvs_dg = video_i.bvs
                ms_user.e_bvs_id_dg = e_video.id
                if ms_user.b_bvs_dg > 0.001 and ms_user.i_bvs_dg > 0.001 and ms_user.e_bvs_dg > 0.001:
                    key = f"player_bvs_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_bvs_dg)
                    cache.hset(key, "b_id", ms_user.b_bvs_id_dg)
                    cache.hset(key, "i", ms_user.i_bvs_dg)
                    cache.hset(key, "i_id", ms_user.i_bvs_id_dg)
                    cache.hset(key, "e", ms_user.e_bvs_dg)
                    cache.hset(key, "e_id", ms_user.e_bvs_id_dg)
                    # cache.hset(key, "sum", ms_user.b_bvs_dg + ms_user.i_bvs_dg + ms_user.e_bvs_dg)
                    # if not cache.lindex('player_bvs_dg_ids', ms_user.id):
                    #     cache.lpush('player_bvs_dg_ids', ms_user.id)
                    s = ms_user.b_bvs_dg + ms_user.i_bvs_dg + ms_user.e_bvs_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_bvs_dg_ids", {ms_user.id: s})
            if e_video.stnb > ms_user.e_stnb_dg:
                ms_user.e_stnb_dg = e_video.stnb
                ms_user.e_stnb_id_dg = e_video.id
                if ms_user.b_stnb_dg > 0.001 and ms_user.i_stnb_dg > 0.001 and ms_user.e_stnb_dg > 0.001:
                    key = f"player_stnb_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_stnb_dg)
                    cache.hset(key, "b_id", ms_user.b_stnb_id_dg)
                    cache.hset(key, "i", ms_user.i_stnb_dg)
                    cache.hset(key, "i_id", ms_user.i_stnb_id_dg)
                    cache.hset(key, "e", ms_user.e_stnb_dg)
                    cache.hset(key, "e_id", ms_user.e_stnb_id_dg)
                    # cache.hset(key, "sum", ms_user.b_stnb_dg + ms_user.i_stnb_dg + ms_user.e_stnb_dg)
                    # if not cache.lindex('player_stnb_dg_ids', ms_user.id):
                    #     cache.lpush('player_stnb_dg_ids', ms_user.id)
                    s = ms_user.b_stnb_dg + ms_user.i_stnb_dg + ms_user.e_stnb_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_stnb_dg_ids", {ms_user.id: s})
            if e_video.ioe > ms_user.e_ioe_dg:
                ms_user.e_ioe_dg = e_video.ioe
                ms_user.e_ioe_id_dg = e_video.id
                if ms_user.b_ioe_dg > 0.001 and ms_user.i_ioe_dg > 0.001 and ms_user.e_ioe_dg > 0.001:
                    key = f"player_ioe_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_ioe_dg)
                    cache.hset(key, "b_id", ms_user.b_ioe_id_dg)
                    cache.hset(key, "i", ms_user.i_ioe_dg)
                    cache.hset(key, "i_id", ms_user.i_ioe_id_dg)
                    cache.hset(key, "e", ms_user.e_ioe_dg)
                    cache.hset(key, "e_id", ms_user.e_ioe_id_dg)
                    # cache.hset(key, "sum", ms_user.b_ioe_dg + ms_user.i_ioe_dg + ms_user.e_ioe_dg)
                    # if not cache.lindex('player_ioe_dg_ids', ms_user.id):
                    #     cache.lpush('player_ioe_dg_ids', ms_user.id)
                    s = ms_user.b_ioe_dg + ms_user.i_ioe_dg + ms_user.e_ioe_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_ioe_dg_ids", {ms_user.id: s})
            if e_video.path < ms_user.e_path_dg:
                ms_user.e_path_dg = e_video.path
                ms_user.e_path_id_dg = e_video.id
                if ms_user.b_path_dg < 99999.8 and ms_user.i_path_dg < 99999.8 and ms_user.e_path_dg < 99999.8:
                    key = f"player_path_dg_{ms_user.id}"
                    cache.hset(key, "name", user.realname)
                    cache.hset(key, "b", ms_user.b_path_dg)
                    cache.hset(key, "b_id", ms_user.b_path_id_dg)
                    cache.hset(key, "i", ms_user.i_path_dg)
                    cache.hset(key, "i_id", ms_user.i_path_id_dg)
                    cache.hset(key, "e", ms_user.e_path_dg)
                    cache.hset(key, "e_id", ms_user.e_path_id_dg)
                    # cache.hset(key, "sum", ms_user.b_path_dg + ms_user.i_path_dg + ms_user.e_path_dg)
                    # if not cache.lindex('player_path_dg_ids', ms_user.id):
                    #     cache.lpush('player_path_dg_ids', ms_user.id)
                    s = ms_user.b_path_dg + ms_user.i_path_dg + ms_user.e_path_dg
                    cache.hset(key, "sum", s)
                    cache.zadd("player_path_dg_ids", {ms_user.id: s})
    # 改完记录，存回数据库
    ms_user.save()


# 获取审查队列里的录像
# http://127.0.0.1:8000/video/review_queue
def review_queue(request):
    if request.method == 'GET':
        review_video_ids = cache.hgetall("review_queue")
        for key in list(review_video_ids.keys()):
            review_video_ids.update({str(key, encoding="utf-8"): review_video_ids.pop(key)})
        return JsonResponse(review_video_ids, encoder=ComplexEncoder)
    else:
        return HttpResponse("别瞎玩")

# 获取最新录像
# http://127.0.0.1:8000/video/newest_queue
def newest_queue(request):
    if request.method == 'GET':
        newest_queue_ids = cache.hgetall("newest_queue")
        for key in list(newest_queue_ids.keys()):
            newest_queue_ids.update({str(key, encoding="utf-8"): newest_queue_ids.pop(key)})
        return JsonResponse(newest_queue_ids, encoder=ComplexEncoder)
    else:
        return HttpResponse("别瞎玩")
    
    

# 管理员审核通过队列里的录像，未审核或冻结状态的录像可以审核通过
# 返回"True","False"（已经是通过的状态）,"Null"（不存在该录像）
# http://127.0.0.1:8000/video/approve?ids=[18,19,999]
def approve(request):
    if request.user.is_staff and request.method == 'GET':
        ids = json.loads(request.GET["ids"])
        res = []
        for i in range(len(ids)):
            if not isinstance(ids[i], int):
                return HttpResponse("审核录像的id应为正整数。")
            video_i = VideoModel.objects.filter(id=ids[i])
            if not video_i:
                res.append("Null")
            else:
                e_video = ExpandVideoModel.objects.filter(id=ids[i])
                if video_i[0].state == "c":
                    res.append("False")
                else:
                    video_i[0].state = "c"
                    video_i[0].upload_time = timezone.now()
                    res.append("True")
                    video_i[0].save()
                    cache.hset("newest_queue", ids[i], cache.hget("review_queue", ids[i]))
                    update_personal_record(video_i[0], e_video[0])
                    update_video_num(request.user.userms, video_i[0])
                cache.hdel("review_queue", ids[i])
        logger.info(f'{request.user.id} approve {json.dumps(ids)} response {json.dumps(res)}')
        return JsonResponse(json.dumps(res), safe=False)
    else:
        return HttpResponse("别瞎玩")

# 管理员冻结队列里的录像，未审核或审核通过的录像可以冻结
# 冻结的录像七到14天后删除，用一个定时任务
# http://127.0.0.1:8000/video/freeze?ids=[18,19]
def freeze(request):
    if request.user.is_staff and request.method == 'GET':
        ids = json.loads(request.GET["ids"])
        res = []
        for _id in ids:
            if not isinstance(_id, int) or _id < 1:
                return HttpResponse("冻结录像的id应为正整数。")
            video_i = VideoModel.objects.filter(id=_id)
            if not video_i:
                res.append("Null")
            else:
                if video_i[0].state == "b":
                    res.append("False")
                else:
                    video_i[0].state = "b"
                    video_i[0].upload_time = timezone.now()
                    res.append("True")
                    video_i[0].save()
                cache.hdel("review_queue", _id)
                cache.hdel("newest_queue", _id)
        logger.info(f'{request.user.id} freeze {json.dumps(ids)} response {json.dumps(res)}')
        return JsonResponse(json.dumps(res), safe=False)
    else:
        return HttpResponse("别瞎玩")


scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(DjangoJobStore(), "default")


# 定时清除最新录像，直至剩下最近7天的或剩下不到100条
# 可能有时区问题
def delete_newest_queue(name):
    if cache.hlen("newest_queue") <= 100:
        return
    newest_queue_ids = cache.hgetall("newest_queue")
    for key in newest_queue_ids.keys():
        a = json.loads(newest_queue_ids[key]['time'])
        d = datetime.strptime(a, "%Y-%m-%d %H:%M:%S")
        if (timezone.now() - d).days > 7:
            cache.hdel("newest_queue", key)


# 定时清除7天以前冻结的录像
def delete_freezed_video(name):
    ddl = timezone.now() - timezone.timedelta(days=7)
    VideoModel.objects.filter(upload_time__lt=ddl, state="b").delete()


# scheduler.add_job(job1, "interval", seconds=10, args=['22'], id="job2", replace_existing=True)
scheduler.add_job(delete_newest_queue, 'cron', hour='3', minute='11', second = '23',
                   args=['666'], id='delete_newest_queue', replace_existing=True)
scheduler.add_job(delete_freezed_video, 'cron', hour='4', minute='1', second = '5', 
                  args=['666'], id='delete_freezed_video', replace_existing=True)
# 监控任务
register_events(scheduler)
# 调度器开始运行
try:
    scheduler.start()
except:
    print("定时任务启动失败！")


