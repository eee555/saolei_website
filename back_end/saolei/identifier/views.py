import logging

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from config.text_choices import MS_TextChoices
from userprofile.decorators import login_required_error, staff_required
from utils.response import HttpResponseConflict
from videomanager.models import VideoModel
from videomanager.view_utils import update_personal_record_stock, update_state
from .models import Identifier
from userprofile.models import UserProfile

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


@require_POST
@login_required_error
def refresh_identifier(request: HttpRequest):
    identifiers_new = list(Identifier.objects.filter(userms=request.user.userms, safe=True).values_list('identifier', flat=True))
    identifiers_old = request.user.userms.identifiers
    for identifier in identifiers_old:
        if identifier not in identifiers_new:
            for video in VideoModel.objects.filter(player=request.user, video__identifier=identifier):
                if video.state == MS_TextChoices.State.OFFICIAL:
                    update_state(video, MS_TextChoices.State.IDENTIFIER)
    for identifier in identifiers_new:
        if identifier not in identifiers_old:
            for video in VideoModel.objects.filter(player=request.user, video__identifier=identifier):
                if video.state == MS_TextChoices.State.IDENTIFIER:
                    update_state(video, MS_TextChoices.State.OFFICIAL)
    request.user.userms.identifiers = identifiers_new
    request.user.userms.save()
    return JsonResponse(identifiers_new, safe=False)


# 管理员添加标识
@require_POST
@staff_required
def staff_add_identifier(request: HttpRequest):
    if not (identifier_text := request.POST.get('identifier')):
        return HttpResponseBadRequest('identifier')
    if not (userid := request.POST.get('userid')):
        return HttpResponseBadRequest('userid')
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound('user')
    if not (identifier := Identifier.objects.filter(identifier=identifier_text).first()):
        identifier = Identifier.objects.create(identifier=identifier_text, safe=True, userms=user.userms)
    if identifier.userms and identifier.userms.parent != user:
        return HttpResponseForbidden()
    identifier.userms = user.userms
    identifier.save()
    if identifier_text not in user.userms.identifiers:
        user.userms.identifiers.append(identifier_text)
        user.userms.save()
    logger.info(f'管理员 #{request.user.id} 为用户 {user.realname}#{user.id} 添加标识 "{identifier_text}"')
    video_list = VideoModel.objects.filter(player=user, video__identifier=identifier_text, state=MS_TextChoices.State.IDENTIFIER)
    for video in video_list:
        update_state(video, MS_TextChoices.State.OFFICIAL)
    logger.info(f'修改了 {len(video_list)} 个录像状态')
    return HttpResponse()


# 管理员删除标识
@require_POST
@staff_required
def staff_del_identifier(request):
    identifier_text = request.POST.get('identifier')
    if not identifier_text:
        return HttpResponseBadRequest()
    identifier = Identifier.objects.filter(identifier=identifier_text).first()
    if not identifier:
        return HttpResponseNotFound()
    videos = VideoModel.objects.filter(video__identifier=identifier_text, state=MS_TextChoices.State.OFFICIAL)
    if not videos:
        identifier.delete()
        logger.info(f'管理员 #{request.user.id} 删除标识 "{identifier_text}"')
    else:
        userms = identifier.userms
        if userms and identifier_text in userms.identifiers:
            userms.identifiers.remove(identifier_text)
            userms.save()
        identifier.userms = None
        identifier.save()
        logger.info(f'管理员 #{request.user.id} 解绑标识 "{identifier_text}"')
        for video in videos:
            update_state(video, MS_TextChoices.State.IDENTIFIER)
        logger.info(f'修改了 {len(videos)} 个录像状态')
    return HttpResponse()


# 管理员过审标识
@require_POST
@staff_required
def staff_approve_identifier(request):
    identifier_text = request.POST.get('identifier')
    if not identifier_text:
        return HttpResponseBadRequest()
    identifier = Identifier.objects.filter(identifier=identifier_text).first()
    if not identifier:
        return HttpResponseNotFound()
    identifier.safe = True
    identifier.save()
    logger.info(f'管理员 #{request.user.id} 过审标识 "{identifier_text}"')
    return HttpResponse()


# 管理员查询标识
@require_GET
def staff_get_identifier(request):
    identifier_text = request.GET.get('identifier')
    if not identifier_text:
        return HttpResponseBadRequest()
    identifier = Identifier.objects.filter(identifier=identifier_text).first()
    if not identifier:
        return HttpResponseNotFound()
    if identifier.userms:
        userid = identifier.userms.parent.id
    else:
        userid = None
    return JsonResponse({'user': userid, 'safe': identifier.safe})
