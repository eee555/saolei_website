from .models import AccountLinkQueue
from userprofile.models import UserProfile
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound
from utils.response import HttpResponseConflict
from django.views.decorators.http import require_GET, require_POST

private_platforms = [""] # 私人账号平台

@require_POST
def add_link(request):
    user = UserProfile.objects.filter(id=request.user.id).first()
    if user == None:
        return HttpResponseForbidden()
    platform = request.POST.get('platform')
    if platform == None:
        return HttpResponseBadRequest()
    accountlink = AccountLinkQueue.objects.filter(platform=platform, userprofile=user).first()
    if accountlink:
        return HttpResponseConflict()
    accountlink = AccountLinkQueue.objects.create(platform=platform, identifier=request.POST.get('identifier'), userprofile=user)
    return HttpResponse()

@require_GET
def get_link(request):
    userid = request.POST.get("id")
    user = UserProfile.objects.filter(id=userid).first()
    accountlink = AccountLinkQueue.objects.filter(userprofile=user)
    print(accountlink)
    if not request.user.is_staff and request.user != user:
        accountlink = accountlink.exclude(platform__in=private_platforms).values("platform","identifier","verified") # 非管理员不能查其他人的私人账号
    return JsonResponse(list(accountlink), safe=False)

