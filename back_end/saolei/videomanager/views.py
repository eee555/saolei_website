from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UploadVideoForm
from .models import VideoModel, ExpandVideoModel
from django.http import HttpResponse, JsonResponse
# from asgiref.sync import sync_to_async
import json
from utils import ComplexEncoder
from django.core.paginator import Paginator

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
            VideoModel.objects.create(player=request.user, file=data["file"], video=e_video,
                                      software=data["software"], level=data["level"],
                                      mode=data["mode"], rtime=data["rtime"],
                                      bv=data["bv"], bvs=data["bvs"])
            return JsonResponse({"status": 100, "msg": None})
        else:
            print(video_form.errors)
            return JsonResponse({"status": 666, "msg": "小型网站，请勿攻击！"})
    elif request.method == 'GET':
        return HttpResponse("别瞎玩")
    else:
        return HttpResponse("别瞎玩")


def video_query(request):
    if request.method == 'GET':
        # print(request.GET)
        index = request.GET["index"]
        if index[0] == '-':
            order_index = "-video__" + index[1:]
            values_index = "video__" + index[1:]
        else:
            order_index = values_index = "video__" + index

        if index in {"upload_time", "bv", "bvs", "-upload_time", "-bv", "-bvs"}:
            videos = VideoModel.objects.filter(level=request.GET["level"], mode=request.GET["mode"])\
                .order_by(index, "rtime").\
                values("upload_time", "player", "bv", "bvs", "rtime")
        elif index == "rtime" or index == "-rtime":
            videos = VideoModel.objects.filter(level=request.GET["level"], mode=request.GET["mode"])\
                .order_by(index).\
                values("upload_time", "player", "bv", "bvs", "rtime")
        else:
            videos = VideoModel.objects.filter(level=request.GET["level"], mode=request.GET["mode"])\
                .order_by(order_index, "rtime").\
                values("upload_time", "player", "bv",
                       "bvs", "rtime", values_index)

        paginator = Paginator(videos, 20)  # 每页20条数据
        page_number = request.GET.get("page")
        page_videos = paginator.get_page(page_number)
        response = {"total_page": paginator.num_pages,
                    "videos": list(page_videos)}
        # t=json.dumps(response, cls=ComplexEncoder)
        # print(t)
        return JsonResponse(json.dumps(response, cls=ComplexEncoder), safe=False)

    elif request.method == 'POST':
        return HttpResponse("别瞎玩")
    else:
        return HttpResponse("别瞎玩")
