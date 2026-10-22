# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_POST

from userprofile.decorators import staff_required
from .models import VideoModel
from .view_utils import refresh_video

logger = logging.getLogger('videomanager')


set_videoModel_fields = ['player', 'upload_time', 'state']  # 可修改的域列表


@require_POST
@staff_required
def set_videoModel(request):
    videoid = request.POST.get('id')
    video = VideoModel.objects.get(id=videoid)
    user = video.player
    if user.is_staff and user != request.user:
        return HttpResponseForbidden()  # 不能修改除自己以外管理员的信息
    field = request.POST.get('field')
    if field not in set_videoModel_fields:
        return HttpResponseForbidden()  # 只能修改特定的域
    value = request.POST.get('value')
    logger.info(
        f'管理员 {request.user.username}#{request.user.id} 修改录像#{videoid} 域 {field} 从 {getattr(video, field)} 到 {value}')
    setattr(video, field, value)
    video.save(update_fields=[field])
    return HttpResponse()


@require_POST
@staff_required
def update_videoModel(request):
    videoid = request.POST.get('id')
    if not (video := VideoModel.objects.filter(id=videoid).first()):
        return HttpResponseNotFound()
    refresh_video(video)
    return HttpResponse()


@require_POST
@staff_required
def batch_update_videoModel(request):
    startid = request.POST.get('startid')
    endid = request.POST.get('endid')
    logger.info(f'管理员#{request.user.id}批量刷新录像#{startid}-{endid} 开始')
    errorList = []
    successCount = 0
    for video in VideoModel.objects.filter(id__gte=startid, id__lte=endid):
        logger.info(f'刷新录像#{video.id} 开始')
        try:
            refresh_video(video)
            successCount += 1
        except Exception:
            logger.exception(f'刷新录像#{video.id} 失败')
            errorList.append(video.id)
        else:
            logger.info(f'刷新录像#{video.id} 成功')
    logger.info(f'批量刷新录像#{startid}-{endid} 完成{successCount}/{endid - startid + 1}')
    return JsonResponse({'errorList': errorList, 'successCount': successCount})
