from .models import AccountLinkQueue
from .utils import update_account, delete_account
from userprofile.models import UserProfile
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound
from utils.response import HttpResponseConflict
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from userprofile.decorators import login_required_error, staff_required

private_platforms = [""] # 私人账号平台

# 为自己绑定账号，需要指定平台和ID
@ratelimit(key='user', rate='10/d')
@require_POST
@login_required_error
def add_link(request):
    user = UserProfile.objects.filter(id=request.user.id).first()
    platform = request.POST.get('platform')
    if platform == None:
        return HttpResponseBadRequest()
    accountlink = AccountLinkQueue.objects.filter(platform=platform, userprofile=user).first()
    if accountlink:
        return HttpResponseConflict() # 每个平台只能绑一个账号
    accountlink = AccountLinkQueue.objects.create(platform=platform, identifier=request.POST.get('identifier'), userprofile=user)
    return HttpResponse()

# 解绑自己的账号，只需要指定平台
@require_POST
@login_required_error
def delete_link(request):
    user = UserProfile.objects.filter(id=request.user.id).first()
    platform = request.POST.get('platform')
    if platform == None:
        return HttpResponseBadRequest()
    accountlink = AccountLinkQueue.objects.filter(platform=platform, userprofile=user).first()
    if accountlink:
        if accountlink.verified:
            delete_account(user, platform)
        accountlink.delete()
        return HttpResponse()
    return HttpResponseNotFound()

@require_GET
def get_link(request):
    userid = request.GET.get("id")
    user = UserProfile.objects.filter(id=userid).first()
    if request.user.is_staff or user == request.user: # 管理员或用户本人可以获得全部数据
        accountlink = AccountLinkQueue.objects.filter(userprofile=user).values("platform","identifier","verified")
    else: # 其他人不能获得未绑定账号与私人账号数据
        accountlink = AccountLinkQueue.objects.filter(userprofile=user,verified=True).exclude(platform__in=private_platforms).values("platform","identifier")
    return JsonResponse(list(accountlink), safe=False)

@require_POST
@staff_required
def verify_link(request):
    userid = request.POST.get("id")
    user = UserProfile.objects.filter(id=userid).first()
    if user == None:
        return HttpResponseNotFound()
    platform = request.POST.get('platform')
    if platform == None:
        return HttpResponseBadRequest()
    identifier = request.POST.get('identifier')
    if identifier == None:
        return HttpResponseBadRequest()
    collision = AccountLinkQueue.objects.filter(platform=platform,identifier=identifier,verified=True).first()
    if collision: # 该平台该ID已被绑定
        if collision.userprofile == user:
            return HttpResponse()
        else:
            return HttpResponseConflict()
    accountlink = AccountLinkQueue.objects.filter(platform=platform,identifier=identifier).first()
    if not accountlink:
        return HttpResponseNotFound()
    update_account(platform, identifier, user)
    accountlink.verified = True
    accountlink.save()
    return HttpResponse()

@require_POST
@staff_required
def unverify_link(request):
    userid = request.GET.get("id")
    user = UserProfile.objects.filter(id=userid).first()
    if not user:
        return HttpResponseNotFound()
    platform = request.POST.get('platform')
    identifier = request.POST.get('identifier')
    accountlink = AccountLinkQueue.objects.filter(userprofile=user,platform=platform,identifier=identifier).first()
    if not accountlink:
        return HttpResponseNotFound()
    delete_account(user, platform)
    accountlink.verified = False
    accountlink.save()
    return HttpResponse()
    