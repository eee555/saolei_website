from msuser.models import UserMS
from models import Designator
from userprofile.models import UserProfile
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse

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
    # TODO: 扫描标识未通过的录像
    return HttpResponse()