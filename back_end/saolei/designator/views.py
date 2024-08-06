from msuser.models import UserMS
from .models import Designator
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
    designator_text = request.POST.get('designator')
    if designator_text == None:
        return HttpResponseBadRequest()
    
    designator = Designator.objects.filter(designator=designator_text).first()
    if not designator or not designator.safe:
        return JsonResponse({'type': 'error', 'object': 'designator', 'category': 'notFound'})
    if designator.userms:
        designator_user = designator.userms.parent
        if designator_user.id == user.id:
            return HttpResponseConflict() # 本人已有该标识
        return JsonResponse({'type': 'error', 'object': 'designator', 'category': 'conflict', 'value': designator_user.id}) # 返回标识冲突的用户
    video_list = VideoModel.objects.filter(player=user, video__designator=designator)
    if not video_list:
        return JsonResponse({'type': 'error', 'object': 'designator', 'category': 'notFound'})
    for video in video_list:
        if video.state == VideoModel.State.DESIGNATOR:
            update_state(video, VideoModel.State.OFFICIAL)
    designator.userms = user.userms
    designator.save()
    user.userms.designators.append(designator_text)
    user.userms.save()
    # TODO: 日志
    return JsonResponse({'type': 'success', 'object': 'designator', 'category': 'add', 'value': len(video_list)})

# 请求删除自己的标识
@require_POST
def del_designator(request):
    user = UserProfile.objects.filter(id=request.user.id).first()
    if user == None:
        return HttpResponseForbidden()
    designator_text = request.POST.get('designator', None)
    if designator_text == None:
        return HttpResponseBadRequest()
    designator = Designator.objects.filter(designator=designator_text).first()
    if not designator:
        return HttpResponseNotFound()
    if designator.userms.parent.id != user.id:
        return HttpResponseForbidden()
    designator.msuser = None
    designator.save()
    user.userms.designators.remove(designator_text)
    user.userms.save()
    # TODO: 日志
    video_list = VideoModel.objects.filter(player=user, video__designator=designator_text)
    for video in video_list:
        if video.state == VideoModel.State.OFFICIAL:
            update_state(video, VideoModel.State.DESIGNATOR, update_ranking=False)
    if video_list:
        update_personal_record_stock(user)
    return JsonResponse({'type': 'success', 'object': 'designator', 'category': 'add', 'value': len(video_list)})

# 管理员添加标识
def staff_add_designator(request):
    # TODO
    return HttpResponse()

# 管理员删除标识
def staff_del_designator(request):
    # TODO
    return HttpResponse()