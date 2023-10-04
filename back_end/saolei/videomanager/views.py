from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UploadVideoForm
from .models import VideoModel, ExpandVideoModel
from django.http import HttpResponse, JsonResponse
# from asgiref.sync import sync_to_async
import json
from utils import ComplexEncoder
from django.core.paginator import Paginator
from msuser.models import UserMS
from django.db.models import Q

# Create your views here.


@login_required(login_url='/')
def video_upload(request):
    if request.method == 'POST':
        # print(request.user)
        # print(request.FILES)
        # print(request.POST)
        # response = {'status': 100, 'msg': None}
        # request.POST['file'] = request.FILES
        video_form = UploadVideoForm(data=request.POST, files=request.FILES)
        # print(video_form)
        if video_form.is_valid():
            data = video_form.cleaned_data
            # 表中添加数据
            # print(data)
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
            VideoModel.objects.create(player=request.user, file=data["file"], video=e_video,
                                      software=data["software"], level=data["level"],
                                      mode=data["mode"] if data["mode"]!="00" else ("12" if data["flag"]==0 else "00"), 
                                      rtime=data["rtime"],
                                      bv=data["bv"], bvs=data["bvs"])
            update_personal_record(request, data, e_video)
            return JsonResponse({"status": 100, "msg": None})
        else:
            print(video_form.errors)
            return JsonResponse({"status": 666, "msg": "小型网站，请勿攻击！"})
    elif request.method == 'GET':
        return HttpResponse("别瞎玩")
    else:
        return HttpResponse("别瞎玩")


# 录像查询（无需登录）
def video_query(request):
    if request.method == 'GET':
        data = request.GET
        # print(data)
        index = data["index"]
        if index[0] == '-':
            order_index = "-video__" + index[1:]
            values_index = "video__" + index[1:]
        else:
            order_index = values_index = "video__" + index

        if data["mode"] != "00":
            if index in {"upload_time", "bv", "bvs", "-upload_time", "-bv", "-bvs"}:
                videos = VideoModel.objects.filter(level=data["level"], mode=data["mode"])\
                    .order_by(index, "rtime").\
                    values("upload_time", "player", "bv", "bvs", "rtime")
            elif index == "rtime" or index == "-rtime":
                videos = VideoModel.objects.filter(level=data["level"], mode=data["mode"])\
                    .order_by(index).\
                    values("upload_time", "player", "bv", "bvs", "rtime")
            else:
                videos = VideoModel.objects.filter(level=data["level"], mode=data["mode"])\
                    .order_by(order_index, "rtime").\
                    values("upload_time", "player", "bv",
                        "bvs", "rtime", values_index)
        else:
            if index in {"upload_time", "bv", "bvs", "-upload_time", "-bv", "-bvs"}:
                videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(level=data["level"])\
                    .order_by(index, "rtime").\
                    values("upload_time", "player", "bv", "bvs", "rtime")
            elif index == "rtime" or index == "-rtime":
                videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(level=data["level"])\
                    .order_by(index).\
                    values("upload_time", "player", "bv", "bvs", "rtime")
            else:
                videos = VideoModel.objects.filter(Q(mode="00")|Q(mode="12")).filter(level=data["level"])\
                    .order_by(order_index, "rtime").\
                    values("upload_time", "player", "bv",
                        "bvs", "rtime", values_index)



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


def update_personal_record(request, data, video):
    user_id = request.user.id
    # user = UserProfile.objects.get(id=user_id)
    ms_user = UserMS.objects.get(id=user_id)
    # print(data["flag"])
    # print(type(data["rtime"]))
    if data["mode"] == "00":
        if data["level"] == "b":
            if data["rtime"] < ms_user.b_time_std:
                ms_user.b_time_std = data["rtime"]
                ms_user.b_time_id_std = video.id
            if data["bvs"] > ms_user.b_bvs_std:
                ms_user.b_bvs_std = data["bvs"]
                ms_user.b_bvs_id_std = video.id
            if data["stnb"] > ms_user.b_stnb_std:
                ms_user.b_stnb_std = data["stnb"]
                ms_user.b_stnb_id_std = video.id
            if data["ioe"] > ms_user.b_ioe_std:
                ms_user.b_ioe_std = data["ioe"]
                ms_user.b_ioe_id_std = video.id
            if data["path"] < ms_user.b_path_std:
                ms_user.b_path_std = data["path"]
                ms_user.b_path_id_std = video.id
        if data["level"] == "i":
            if data["rtime"] < ms_user.i_time_std:
                ms_user.i_time_std = data["rtime"]
                ms_user.i_time_id_std = video.id
            if data["bvs"] > ms_user.i_bvs_std:
                ms_user.i_bvs_std = data["bvs"]
                ms_user.i_bvs_id_std = video.id
            if data["stnb"] > ms_user.i_stnb_std:
                ms_user.i_stnb_std = data["stnb"]
                ms_user.i_stnb_id_std = video.id
            if data["ioe"] > ms_user.i_ioe_std:
                ms_user.i_ioe_std = data["ioe"]
                ms_user.i_ioe_id_std = video.id
            if data["path"] < ms_user.i_path_std:
                ms_user.i_path_std = data["path"]
                ms_user.i_path_id_std = video.id
        if data["level"] == "e":
            if data["rtime"] < ms_user.e_time_std:
                ms_user.e_time_std = data["rtime"]
                ms_user.e_time_id_std = video.id
            if data["bvs"] > ms_user.e_bvs_std:
                ms_user.e_bvs_std = data["bvs"]
                ms_user.e_bvs_id_std = video.id
            if data["stnb"] > ms_user.e_stnb_std:
                ms_user.e_stnb_std = data["stnb"]
                ms_user.e_stnb_id_std = video.id
            if data["ioe"] > ms_user.e_ioe_std:
                ms_user.e_ioe_std = data["ioe"]
                ms_user.e_ioe_id_std = video.id
            if data["path"] < ms_user.e_path_std:
                ms_user.e_path_std = data["path"]
                ms_user.e_path_id_std = video.id

    if data["mode"] == "00":
        if data["flag"] == 0:
            data["mode"] = "12"

    if data["mode"] == "12":
        if data["level"] == "b":
            if data["rtime"] < ms_user.b_time_nf:
                ms_user.b_time_nf = data["rtime"]
                ms_user.b_time_id_nf = video.id
            if data["bvs"] > ms_user.b_bvs_nf:
                ms_user.b_bvs_nf = data["bvs"]
                ms_user.b_bvs_id_nf = video.id
            if data["stnb"] > ms_user.b_stnb_nf:
                ms_user.b_stnb_nf = data["stnb"]
                ms_user.b_stnb_id_nf = video.id
            if data["ioe"] > ms_user.b_ioe_nf:
                ms_user.b_ioe_nf = data["ioe"]
                ms_user.b_ioe_id_nf = video.id
            if data["path"] < ms_user.b_path_nf:
                ms_user.b_path_nf = data["path"]
                ms_user.b_path_id_nf = video.id
        if data["level"] == "i":
            if data["rtime"] < ms_user.i_time_nf:
                ms_user.i_time_nf = data["rtime"]
                ms_user.i_time_id_nf = video.id
            if data["bvs"] > ms_user.i_bvs_nf:
                ms_user.i_bvs_nf = data["bvs"]
                ms_user.i_bvs_id_nf = video.id
            if data["stnb"] > ms_user.i_stnb_nf:
                ms_user.i_stnb_nf = data["stnb"]
                ms_user.i_stnb_id_nf = video.id
            if data["ioe"] > ms_user.i_ioe_nf:
                ms_user.i_ioe_nf = data["ioe"]
                ms_user.i_ioe_id_nf = video.id
            if data["path"] < ms_user.i_path_nf:
                ms_user.i_path_nf = data["path"]
                ms_user.i_path_id_nf = video.id
        if data["level"] == "e":
            if data["rtime"] < ms_user.e_time_nf:
                ms_user.e_time_nf = data["rtime"]
                ms_user.e_time_id_nf = video.id
            if data["bvs"] > ms_user.e_bvs_nf:
                ms_user.e_bvs_nf = data["bvs"]
                ms_user.e_bvs_id_nf = video.id
            if data["stnb"] > ms_user.e_stnb_nf:
                ms_user.e_stnb_nf = data["stnb"]
                ms_user.e_stnb_id_nf = video.id
            if data["ioe"] > ms_user.e_ioe_nf:
                ms_user.e_ioe_nf = data["ioe"]
                ms_user.e_ioe_id_nf = video.id
            if data["path"] < ms_user.e_path_nf:
                ms_user.e_path_nf = data["path"]
                ms_user.e_path_id_nf = video.id

    if data["mode"] == "05":
        if data["level"] == "b":
            if data["rtime"] < ms_user.b_time_ng:
                ms_user.b_time_ng = data["rtime"]
                ms_user.b_time_id_ng = video.id
            if data["bvs"] > ms_user.b_bvs_ng:
                ms_user.b_bvs_ng = data["bvs"]
                ms_user.b_bvs_id_ng = video.id
            if data["stnb"] > ms_user.b_stnb_ng:
                ms_user.b_stnb_ng = data["stnb"]
                ms_user.b_stnb_id_ng = video.id
            if data["ioe"] > ms_user.b_ioe_ng:
                ms_user.b_ioe_ng = data["ioe"]
                ms_user.b_ioe_id_ng = video.id
            if data["path"] < ms_user.b_path_ng:
                ms_user.b_path_ng = data["path"]
                ms_user.b_path_id_ng = video.id
        if data["level"] == "i":
            if data["rtime"] < ms_user.i_time_ng:
                ms_user.i_time_ng = data["rtime"]
                ms_user.i_time_id_ng = video.id
            if data["bvs"] > ms_user.i_bvs_ng:
                ms_user.i_bvs_ng = data["bvs"]
                ms_user.i_bvs_id_ng = video.id
            if data["stnb"] > ms_user.i_stnb_ng:
                ms_user.i_stnb_ng = data["stnb"]
                ms_user.i_stnb_id_ng = video.id
            if data["ioe"] > ms_user.i_ioe_ng:
                ms_user.i_ioe_ng = data["ioe"]
                ms_user.i_ioe_id_ng = video.id
            if data["path"] < ms_user.i_path_ng:
                ms_user.i_path_ng = data["path"]
                ms_user.i_path_id_ng = video.id
        if data["level"] == "e":
            if data["rtime"] < ms_user.e_time_ng:
                ms_user.e_time_ng = data["rtime"]
                ms_user.e_time_id_ng = video.id
            if data["bvs"] > ms_user.e_bvs_ng:
                ms_user.e_bvs_ng = data["bvs"]
                ms_user.e_bvs_id_ng = video.id
            if data["stnb"] > ms_user.e_stnb_ng:
                ms_user.e_stnb_ng = data["stnb"]
                ms_user.e_stnb_id_ng = video.id
            if data["ioe"] > ms_user.e_ioe_ng:
                ms_user.e_ioe_ng = data["ioe"]
                ms_user.e_ioe_id_ng = video.id
            if data["path"] < ms_user.e_path_ng:
                ms_user.e_path_ng = data["path"]
                ms_user.e_path_id_ng = video.id

    if data["mode"] == "11":
        if data["level"] == "b":
            if data["rtime"] < ms_user.b_time_dg:
                ms_user.b_time_dg = data["rtime"]
                ms_user.b_time_id_dg = video.id
            if data["bvs"] > ms_user.b_bvs_dg:
                ms_user.b_bvs_dg = data["bvs"]
                ms_user.b_bvs_id_dg = video.id
            if data["stnb"] > ms_user.b_stnb_dg:
                ms_user.b_stnb_dg = data["stnb"]
                ms_user.b_stnb_id_dg = video.id
            if data["ioe"] > ms_user.b_ioe_dg:
                ms_user.b_ioe_dg = data["ioe"]
                ms_user.b_ioe_id_dg = video.id
            if data["path"] < ms_user.b_path_dg:
                ms_user.b_path_dg = data["path"]
                ms_user.b_path_id_dg = video.id
        if data["level"] == "i":
            if data["rtime"] < ms_user.i_time_dg:
                ms_user.i_time_dg = data["rtime"]
                ms_user.i_time_id_dg = video.id
            if data["bvs"] > ms_user.i_bvs_dg:
                ms_user.i_bvs_dg = data["bvs"]
                ms_user.i_bvs_id_dg = video.id
            if data["stnb"] > ms_user.i_stnb_dg:
                ms_user.i_stnb_dg = data["stnb"]
                ms_user.i_stnb_id_dg = video.id
            if data["ioe"] > ms_user.i_ioe_dg:
                ms_user.i_ioe_dg = data["ioe"]
                ms_user.i_ioe_id_dg = video.id
            if data["path"] < ms_user.i_path_dg:
                ms_user.i_path_dg = data["path"]
                ms_user.i_path_id_dg = video.id
        if data["level"] == "e":
            if data["rtime"] < ms_user.e_time_dg:
                ms_user.e_time_dg = data["rtime"]
                ms_user.e_time_id_dg = video.id
            if data["bvs"] > ms_user.e_bvs_dg:
                ms_user.e_bvs_dg = data["bvs"]
                ms_user.e_bvs_id_dg = video.id
            if data["stnb"] > ms_user.e_stnb_dg:
                ms_user.e_stnb_dg = data["stnb"]
                ms_user.e_stnb_id_dg = video.id
            if data["ioe"] > ms_user.e_ioe_dg:
                ms_user.e_ioe_dg = data["ioe"]
                ms_user.e_ioe_id_dg = video.id
            if data["path"] < ms_user.e_path_dg:
                ms_user.e_path_dg = data["path"]
                ms_user.e_path_id_dg = video.id
    # 改完记录，存回数据库
    ms_user.save()




