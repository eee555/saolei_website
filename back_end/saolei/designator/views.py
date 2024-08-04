from msuser.models import UserMS
from models import Designator
from userprofile.models import UserProfile
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound
from .utils import add_designator_aftermath

# 请求修改自己的标识
def add_designator(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    user = UserProfile.objects.filter(id=request.user.id).first()
    if user == None:
        return HttpResponseForbidden()
    designator = request.POST.get('designator', None)
    if designator == None:
        return HttpResponseBadRequest()
    collision = Designator.objects.filter(designator=designator).first()
    if collision != None:
        collision_user = collision.userms.parent
        if collision_user.id == user.id:
            return HttpResponse() # 本人已有该标识
        return JsonResponse(collision_user.id) # 返回标识冲突的用户
    Designator.objects.create(designator=designator, userms=user.userms) # 新标识
    # TODO: 日志
    add_designator_aftermath(user, designator)
    user.userms.designators.append(designator)
    user.userms.save()
    return HttpResponse()

# 请求删除自己的标识
def del_designator(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    user = UserProfile.objects.filter(id=request.user.id).first()
    if user == None:
        return HttpResponseForbidden()
    designator = request.POST.get('designator', None)
    if designator == None:
        return HttpResponseBadRequest()
    object = Designator.objects.filter(designator=designator).first()
    if not object:
        return HttpResponseNotFound()
    object.delete()
    # TODO: 日志
    user.userms.designators.remove(designator)
    user.userms.save()
    return HttpResponse()

# 管理员添加标识
def staff_add_designator(request):
    # TODO
    return HttpResponse()

# 管理员删除标识
def staff_del_designator(request):
    # TODO
    return HttpResponse()