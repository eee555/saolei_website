from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
import requests

from config.text_choices import Saolei_TextChoices
from userprofile.decorators import login_required_error, staff_required
from userprofile.models import UserProfile
from utils.response import HttpResponseConflict
from utils.exceptions import ExceptionToResponse
from .models import AccountLinkQueue, Platform, PLATFORM_CONFIG, VideoSaolei, AccountSaolei
from .services import update_account
from .utils import delete_account, link_account

private_platforms = ["q"]  # 私人账号平台


# 为自己绑定账号，需要指定平台和ID
@require_POST
@login_required_error
@ratelimit(key='user', rate='10/d')
def add_link(request: HttpRequest):
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    if AccountLinkQueue.objects.filter(platform=platform, userprofile=request.user).first():
        return HttpResponseConflict()  # 每个平台只能绑一个账号
    AccountLinkQueue.objects.create(platform=platform, identifier=request.POST.get('identifier'), userprofile=request.user)
    return HttpResponse()


# 解绑自己的账号，只需要指定平台
@require_POST
@login_required_error
def delete_link(request):
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    if accountlink := AccountLinkQueue.objects.filter(platform=platform, userprofile=request.user).first():
        if accountlink.verified:
            delete_account(request.user, platform)
        accountlink.delete()
        return HttpResponse()
    return HttpResponseNotFound()


# 二合一接口
# 仅提供id，则返回该id的所有link的id
# 提供id+platform，返回对应账号的详情
@require_GET
def get_link(request):
    if not (userid := request.GET.get("id")):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound()
    if platform := request.GET.get("platform"):
        if platform in private_platforms and not request.user.is_staff and user != request.user:
            return HttpResponseForbidden()
        account = getattr(user, PLATFORM_CONFIG[platform]['related_name'])
        data = model_to_dict(account)
        if platform != Platform.QQ:
            data['update_time'] = account.update_time
        return JsonResponse(data)
    else:
        if request.user.is_staff or user == request.user:  # 管理员或用户本人可以获得全部数据
            accountlink = AccountLinkQueue.objects.filter(userprofile=user).values("platform", "identifier", "verified")
        else:  # 其他人不能获得未绑定账号与私人账号数据
            accountlink = AccountLinkQueue.objects.filter(userprofile=user, verified=True).exclude(platform__in=private_platforms).values("platform", "identifier")
        return JsonResponse(list(accountlink), safe=False)


@require_POST
@staff_required
def verify_link(request):
    userid = request.POST.get("id")
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound()
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    if not (identifier := request.POST.get('identifier')):
        return HttpResponseBadRequest()
    collision = AccountLinkQueue.objects.filter(platform=platform, identifier=identifier, verified=True).first()
    if collision:  # 该平台该ID已被绑定
        if collision.userprofile == user:
            return HttpResponse()
        else:
            return HttpResponseConflict()
    accountlink = AccountLinkQueue.objects.filter(platform=platform, identifier=identifier).first()
    if not accountlink:
        return HttpResponseNotFound()
    link_account(platform, identifier, user)
    accountlink.verified = True
    accountlink.save()
    update_account(platform, user, 0)
    return HttpResponse()


@require_POST
@staff_required
def unverify_link(request):
    userid = request.GET.get("id")
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound()
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    if not (identifier := request.POST.get('identifier')):
        return HttpResponseBadRequest()
    accountlink = AccountLinkQueue.objects.filter(userprofile=user, platform=platform, identifier=identifier).first()
    if not accountlink:
        return HttpResponseNotFound()
    delete_account(user, platform)
    accountlink.verified = False
    accountlink.save()
    return HttpResponse()


@require_POST
@login_required_error
def update_link(request):
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    status = update_account(platform, request.user)
    if status == '':
        return JsonResponse({'type': 'success'})
    elif status == 'unsupported':
        return HttpResponseBadRequest()
    return JsonResponse({'type': 'error', 'category': status})


@require_POST
@login_required_error
def import_saolei_videolist(request: HttpRequest):
    """
    请求参数:
        user_id (str, optional): 管理员可指定用户ID来导入其他用户的录像。若未指定则导入当前登录用户的录像
        page (str): 页码，将该页未加入队列的录像加入队列，并返回加入的录像。如果页码为0则返回队列中所有未导入的录像
        
    异常处理:
        - 用户不存在返回404
        - 用户没有绑定扫雷网账号返回403
        - 连接错误返回错误JSON响应
    """
    if request.user.is_staff:
        if user_id := request.POST.get('user_id'):
            if not (user := UserProfile.objects.filter(id=user_id).first()):
                return HttpResponseNotFound()
        else:
            user = request.user
    else:
        user = request.user

    try:
        account = user.account_saolei
    except UserProfile.account_saolei.RelatedObjectDoesNotExist:
        return JsonResponse({'type': 'error', 'obj': 'saolei', 'category': 'not_linked'})

    try:
        page = int(request.POST.get('page'))
    except:
        return HttpResponseBadRequest()

    if page == 0:
        video_list = list(account.videos.exclude(import_state=Saolei_TextChoices.SaoleiVideoImportState.IMPORTED).values('id', 'upload_time', 'level', 'bv', 'timems', 'nf', 'import_state', 'import_video'))
    else:
        try:
            video_list = [v.dict() for v in account.import_video_list(page)]
        except ExceptionToResponse as e:
            return e.response()
        except requests.exceptions.ConnectionError:
            return JsonResponse({'type': 'error', 'obj': 'saolei', 'category': 'connection'})

    return JsonResponse({'type': 'success', 'data': video_list}, safe=False)


@require_GET
def get_saolei_videolist(request: HttpRequest):
    if not (saolei_id := request.GET.get('saolei_id')):
        return HttpResponseBadRequest()
    if not (saolei_account := AccountSaolei.objects.filter(id=saolei_id).first()):
        return HttpResponseNotFound()
    
    return JsonResponse(list(saolei_account.videos.values('id', 'upload_time', 'level', 'bv', 'timems', 'nf', 'import_state', 'import_video')), safe=False)


@require_POST
@login_required_error
def import_saolei_video(request: HttpRequest):
    if not (video_id := request.POST.get('video_id')):
        return HttpResponseBadRequest()
    if not (video := VideoSaolei.objects.filter(id=video_id).first()):
        return HttpResponseNotFound()
    if not request.user.is_staff and video.user.parent != request.user:
        return HttpResponseForbidden()

    try:
        video.run_import()
    except ExceptionToResponse as e:
        return e.response()

    return JsonResponse({'type': 'success', 'data': {
        'id': video.id,
        'upload_time': video.upload_time,
        'level': video.level,
        'bv': video.bv,
        'timems': video.timems,
        'nf': video.nf,
        'import_state': video.import_state,
        'import_video': video.import_video.id,
    }})
