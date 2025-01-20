import logging
from .models import Identifier
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST
from utils.response import HttpResponseConflict
from videomanager.models import VideoModel
from videomanager.view_utils import update_state, update_personal_record_stock
from userprofile.decorators import login_required_error
from config.text_choices import MS_TextChoices
logger = logging.getLogger('userprofile')


# 请求修改自己的标识
@require_POST
@login_required_error
def add_identifier(request):
    user = request.user
    if not (identifier_text := request.POST.get('identifier')):
        return HttpResponseBadRequest()
    identifier = Identifier.objects.filter(identifier=identifier_text).first()
    if not identifier or not identifier.safe:
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'notFound'})
    if identifier.userms:
        identifier_user = identifier.userms.parent
        if identifier_user.id == user.id:
            return HttpResponseConflict()  # 本人已有该标识
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'conflict', 'value': identifier_user.id})  # 返回标识冲突的用户
    video_list = VideoModel.objects.filter(player=user, video__identifier=identifier_text)
    if not video_list:
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'notFound'})
    for video in video_list:
        if video.state == MS_TextChoices.State.IDENTIFIER:
            update_state(video, MS_TextChoices.State.OFFICIAL)
    identifier.userms = user.userms
    identifier.save()
    user.userms.identifiers.append(identifier_text)
    user.userms.save()
    logger.info(f'用户 {user.username}#{user.id} 绑定标识 "{identifier_text}"')
    return JsonResponse({'type': 'success', 'object': 'identifier', 'category': 'add', 'value': len(video_list)})


# 请求删除自己的标识
@require_POST
@login_required_error
def del_identifier(request):
    user = request.user
    if not (identifier_text := request.POST.get('identifier')):
        return HttpResponseBadRequest()
    if not (identifier := Identifier.objects.filter(identifier=identifier_text).first()):
        return HttpResponseNotFound()
    if identifier.userms.parent.id != user.id:
        return HttpResponseForbidden()
    identifier.userms = None
    identifier.save()
    user.userms.identifiers.remove(identifier_text)
    user.userms.save()
    logger.info(f'用户 {user.username}#{user.id} 解绑标识 "{identifier_text}"')
    video_list = VideoModel.objects.filter(player=user, video__identifier=identifier_text)
    for video in video_list:
        if video.state == MS_TextChoices.State.OFFICIAL:
            update_state(video, MS_TextChoices.State.IDENTIFIER, update_ranking=False)
    if video_list:
        update_personal_record_stock(user)
    return JsonResponse({'type': 'success', 'object': 'identifier', 'category': 'add', 'value': len(video_list)})


# 管理员添加标识
def staff_add_identifier(request):
    # TODO
    return HttpResponse()


# 管理员删除标识
def staff_del_identifier(request):
    # TODO
    return HttpResponse()
