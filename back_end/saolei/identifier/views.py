from msuser.models import UserMS
from .models import Identifier
from userprofile.models import UserProfile
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET, require_POST
from utils.response import HttpResponseConflict
from videomanager.models import VideoModel
from videomanager.view_utils import update_state, update_personal_record_stock

# 请求修改自己的标识
@require_POST
def add_designator(request):
    user = UserProfile.objects.filter(id=request.user.id).first()
    if user == None:
        return HttpResponseForbidden()
    designator_text = request.POST.get('identifier')
    if designator_text == None:
        return HttpResponseBadRequest()
    
    identifier = Identifier.objects.filter(identifier=designator_text).first()
    if not identifier or not identifier.safe:
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'notFound'})
    if identifier.userms:
        designator_user = identifier.userms.parent
        if designator_user.id == user.id:
            return HttpResponseConflict() # 本人已有该标识
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'conflict', 'value': designator_user.id}) # 返回标识冲突的用户
    video_list = VideoModel.objects.filter(player=user, video__designator=designator_text)
    if not video_list:
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'notFound'})
    for video in video_list:
        if video.state == VideoModel.State.IDENTIFIER:
            update_state(video, VideoModel.State.OFFICIAL)
    identifier.userms = user.userms
    identifier.save()
    user.userms.designators.append(designator_text)
    user.userms.save()
    # TODO: 日志
    return JsonResponse({'type': 'success', 'object': 'identifier', 'category': 'add', 'value': len(video_list)})

# 请求删除自己的标识
@require_POST
def del_designator(request):
    user = UserProfile.objects.filter(id=request.user.id).first()
    if user == None:
        return HttpResponseForbidden()
    designator_text = request.POST.get('identifier', None)
    if designator_text == None:
        return HttpResponseBadRequest()
    identifier = Identifier.objects.filter(identifier=designator_text).first()
    if not identifier:
        return HttpResponseNotFound()
    if identifier.userms.parent.id != user.id:
        return HttpResponseForbidden()
    identifier.userms = None
    identifier.save()
    user.userms.designators.remove(designator_text)
    user.userms.save()
    # TODO: 日志
    video_list = VideoModel.objects.filter(player=user, video__designator=designator_text)
    for video in video_list:
        if video.state == VideoModel.State.OFFICIAL:
            update_state(video, VideoModel.State.IDENTIFIER, update_ranking=False)
    if video_list:
        update_personal_record_stock(user)
    return JsonResponse({'type': 'success', 'object': 'identifier', 'category': 'add', 'value': len(video_list)})

# 管理员添加标识
def staff_add_designator(request):
    # TODO
    return HttpResponse()

# 管理员删除标识
def staff_del_designator(request):
    # TODO
    return HttpResponse()