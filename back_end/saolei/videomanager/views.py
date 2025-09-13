# -*- coding: utf-8 -*-
import datetime
import json
import logging
import urllib

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from django_redis import get_redis_connection

from accountlink.models import AccountSaolei
from config.text_choices import MS_TextChoices
from userprofile.decorators import banned_blocked, login_required_error, staff_required
from userprofile.models import UserProfile
from utils import ComplexEncoder
from utils.exceptions import ExceptionToResponse
from .forms import UploadVideoForm
from .models import ExpandVideoModel, VideoModel
from .view_utils import new_video_by_file, refresh_video, update_personal_record, update_personal_record_stock, update_state, update_video_num, video_all_fields, video_saolei_import_by_userid_helper

logger = logging.getLogger('videomanager')
cache = get_redis_connection("saolei_website")


@require_POST
@login_required_error
@banned_blocked
@ratelimit(key='ip', rate='5/s')
def video_upload(request):
    if request.user.userms.video_num_total >= request.user.userms.video_num_limit:
        return HttpResponse(status=402)  # 录像仓库已满
    video_form = UploadVideoForm(data=request.POST, files=request.FILES)
    if not video_form.is_valid():
        return HttpResponseBadRequest(video_form.errors)
    try:
        video = new_video_by_file(request.user, video_form.cleaned_data["file"])
    except ExceptionToResponse as e:
        return e.response()
    return JsonResponse({'type': 'success', 'object': 'videomodel', 'category': 'upload', 'data': {'id': video.id, 'state': video.state}})


@login_required_error
@ratelimit(key='ip', rate='5/s')
@require_POST
@banned_blocked
def video_saolei_import_by_userid_post(request) -> JsonResponse:
    user: AccountSaolei = request.user.account_saolei
    if user is None:
        return JsonResponse({'type': 'error', 'object': 'accountlink', 'category': 'notFound'})
    data = request.POST
    begin_time = data.get('begin_time')
    end_time = data.get('end_time')
    is_need_file_url = data.get('is_need_file_url')
    if is_need_file_url is None:
        is_need_file_url = False
    if begin_time is None or end_time is None:
        return JsonResponse({'type': 'error', 'object': 'videomodel', 'category': 'notFound'})
    video_saolei_import_by_userid_helper(
        userProfile=user.parent, accountSaolei=user, beginTime=datetime.datetime.fromisoformat(begin_time[:-1]), endTime=datetime.datetime.fromisoformat(end_time[:-1]), is_need_file_url=is_need_file_url)
    return JsonResponse({'type': 'success', 'object': 'videomodel', 'category': 'import'})


# 根据id向后台请求软件类型（适配flop播放器用）
@require_GET
def get_software(request):
    video = VideoModel.objects.get(id=request.GET["id"])
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
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/octet-stream'
    # response['Content-Disposition']=f'attachment;filename="{video.file.name.split("/")[2]}"'
    file_name = video.file.name.split("/")[2]
    file_name_uri = urllib.parse.quote(file_name)
    response['Content-Disposition'] = f'attachment; filename="{file_name_uri}"'
    response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response


# 给下载用的接口，区别是结尾没有文件后缀
# @login_required(login_url='/')
@ratelimit(key='ip', rate='20/m')
@require_GET
def video_download(request):
    try:
        video = VideoModel.objects.get(id=request.GET["id"])
        response = FileResponse(open(video.file.path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response[
            'Content-Disposition'] = f'attachment;filename="{video.file.name.split("/")[2]}"'
        return response
    except VideoModel.DoesNotExist:
        return HttpResponseNotFound()


# 录像查询（无需登录）
# 按任何基础指标+难度+模式，排序，分页
# 每项的定义参见 front_end/src/views/VideoView.vue 的 request_videos 函数
@ratelimit(key='ip', rate='60/m')
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
        video_filter = {"level": data["level"], "mode": data["mode"]}
        videos = VideoModel.objects.filter(**video_filter)
    else:
        video_filter = {"level": data["level"]}
        videos = VideoModel.objects.filter(
            Q(mode="00") | Q(mode="12")).filter(**video_filter)

    videos = videos.filter(bv__range=(data["bmin"], data["bmax"]))

    states = data.getlist("s[]")
    if states:
        videos = videos.filter(state__in=states)

    videos = videos.order_by(*orderby).values(*values)

    # print(videos)
    paginator = Paginator(videos, data["ps"])
    page_number = data["page"]
    page_videos = paginator.get_page(page_number)
    response = {
        "count": len(videos),
        "videos": list(page_videos),
    }
    # t=json.dumps(response, cls=ComplexEncoder)
    # print(t)
    return JsonResponse(json.dumps(response, cls=ComplexEncoder), safe=False)


# 按id查询这个用户的所有录像
@require_GET
def video_query_by_id(request):
    if not (userid := request.GET.get("id")):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound()
    videos = VideoModel.objects.filter(player=user).values('id', 'upload_time', "end_time", "level", "mode", "timems", "bv", "bvs", "state", "video__identifier",
                                                           "software", "flag", "cell0", "cell1", "cell2", "cell3", "cell4", "cell5", "cell6", "cell7", "cell8", "left", "right", "double", "op", "isl", "path")
    # print(list(videos))

    return JsonResponse(list(videos), safe=False)


# 获取审查队列里的录像
# http://127.0.0.1:8000/video/review_queue
@require_GET
def review_queue(request):
    review_video_ids = cache.hgetall("review_queue")
    for key in list(review_video_ids.keys()):
        review_video_ids.update({
            str(key, encoding="utf-8"): review_video_ids.pop(key)})
    return JsonResponse(review_video_ids, encoder=ComplexEncoder)


# 获取最新录像
# http://127.0.0.1:8000/video/newest_queue
@require_GET
def newest_queue(request):
    newest_queue_ids = cache.hgetall("newest_queue")
    for key in list(newest_queue_ids.keys()):
        newest_queue_ids.update({
            str(key, encoding="utf-8"): newest_queue_ids.pop(key)})
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
        freeze_queue_ids.update({
            str(key, encoding="utf-8"): freeze_queue_ids.pop(key)})
    return JsonResponse(freeze_queue_ids, encoder=ComplexEncoder)


# 审核通过单个录像
# check_identifier 为 true 则检查是否要修改玩家标识列表，并在修改后扫描所有待审录像的标识
def approve_single(videoid, check_identifier=True):
    if not (video := VideoModel.objects.filter(id=videoid)):
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
    identifier = video.video.identifier
    if check_identifier and identifier not in userms.identifiers:
        userms.identifiers.append(identifier)
        userms.save(update_fields=["identifiers"])
        logger.info(
            f'用户 {video.player.username}#{video.player.id} 新标识 "{identifier}"')
        approve_identifier(video.player.id, identifier)
    return True


# 审核通过所有特定用户特定标识的录像
def approve_identifier(userid, identifier):
    user_identifier_list = cache.hgetall("review_queue")
    for key in user_identifier_list:
        value = json.loads(user_identifier_list[key])
        if value["player_id"] == userid and value["identifier"] == identifier:
            logger.info(f'用户 #{userid} 录像#{key} 机审成功')
            approve_single(key, False)


# 【管理员】审核通过队列里的录像，未审核或冻结状态的录像可以审核通过
# 返回"True","False"（已经是通过的状态）,"Null"（不存在该录像）
# http://127.0.0.1:8000/video/approve?ids=[18,19,999]
@require_GET
@staff_required
def approve(request):
    ids = json.loads(request.GET["ids"])
    res = []
    for _id in ids:
        logger.info(
            f'管理员 {request.user.username}#{request.user.id} 过审录像#{_id}')
        res.append(approve_single(_id))
    return JsonResponse(res, safe=False)


# 【管理员】冻结队列里的录像，未审核或审核通过的录像可以冻结
# 两种用法，冻结指定的录像id，或冻结某用户的所有录像
# 冻结的录像七到14天后删除，用一个定时任务
# http://127.0.0.1:8000/video/freeze?ids=[18,19,20,21,102,273]
# http://127.0.0.1:8000/video/freeze?ids=12
# http://127.0.0.1:8000/video/freeze?user_id=20
@require_GET
@staff_required
def freeze(request):
    if video_ids := request.GET.get("ids"):
        res = []
        for video_id in video_ids:
            if not (v := VideoModel.objects.filter(id=video_id).first()):
                res.append("Null")
            else:
                update_state(v, MS_TextChoices.State.FROZEN)
                logger.info(
                    f'管理员 {request.user.username}#{request.user.id} 冻结录像#{id}')
        return JsonResponse(res)
    elif user_id := request.GET.get("user_id"):
        if not (user := UserProfile.objects.filter(id=user_id).first()):
            return HttpResponseNotFound()
        for v in VideoModel.objects.filter(player=user):
            update_state(v, MS_TextChoices.State.FROZEN, update_ranking=False)
        update_personal_record_stock(user)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


# 管理员使用的操作接口，调用方式见前端的StaffView.vue
get_videoModel_fields = ["player", "player__realname", "upload_time",
                         "state", "software", "level", "mode", "timems", "bv", "bvs"]  # 可获取的域列表
for name in [field.name for field in ExpandVideoModel._meta.get_fields()]:
    get_videoModel_fields.append("video__" + name)


@require_GET
@staff_required
def get_videoModel(request):
    if not (videolist := VideoModel.objects.filter(id=request.GET["id"])
            .values(*get_videoModel_fields)):
        return HttpResponseNotFound()
    return JsonResponse(videolist[0])


set_videoModel_fields = ["player", "upload_time", "state"]  # 可修改的域列表


@require_POST
@staff_required
def set_videoModel(request):
    videoid = request.POST.get("id")
    video = VideoModel.objects.get(id=videoid)
    user = video.player
    if user.is_staff and user != request.user:
        return HttpResponseForbidden()  # 不能修改除自己以外管理员的信息
    field = request.POST.get("field")
    if field not in set_videoModel_fields:
        return HttpResponseForbidden()  # 只能修改特定的域
    value = request.POST.get("value")
    logger.info(
        f'管理员 {request.user.username}#{request.user.id} 修改录像#{videoid} 域 {field} 从 {getattr(video, field)} 到 {value}')
    setattr(video, field, value)
    video.save()
    return HttpResponse()


@require_POST
@staff_required
def update_videoModel(request):
    videoid = request.POST.get("id")
    if not (video := VideoModel.objects.filter(id=videoid).first()):
        return HttpResponseNotFound()
    refresh_video(video)
    return HttpResponse()


@require_POST
@staff_required
def batch_update_videoModel(request):
    startid = request.POST.get("startid")
    endid = request.POST.get("endid")
    errorList = []
    successCount = 0
    for video in VideoModel.objects.filter(id__gte=startid, id__lte=endid):
        try:
            refresh_video(video)
            successCount += 1
        except:
            errorList.append(video.id)
    return JsonResponse({'errorList': errorList, 'successCount': successCount})
