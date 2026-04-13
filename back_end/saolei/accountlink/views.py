import logging

from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from django_tasks import TaskResultStatus

from userprofile.decorators import login_required_error, staff_required
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from utils.response import HttpResponseConflict
from .models import AccountLinkQueue, AccountSaolei, Platform, PLATFORM_CONFIG, VideoSaolei
from .services import saolei_video_import_one, update_account
from .tasks import helper_saolei_video_import_bulk
from .utils import delete_account, link_account

logger = logging.getLogger('accountlink')
private_platforms = ['q']  # 私人账号平台


# 为自己绑定账号，需要指定平台和ID
@require_POST
@login_required_error
@ratelimit(key='user', rate='10/d')
def add_link(request: HttpRequest):
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    if not (identifier := request.POST.get('identifier')):
        return HttpResponseBadRequest()
    if AccountLinkQueue.objects.filter(platform=platform, userprofile=request.user).first():
        return HttpResponseConflict()  # 每个平台只能绑一个账号
    AccountLinkQueue.objects.create(platform=platform, identifier=identifier, userprofile=request.user)
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
    if not (userid := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=userid).first()):
        return HttpResponseNotFound()
    if platform := request.GET.get('platform'):
        if platform in private_platforms and not request.user.is_staff and user != request.user:
            return HttpResponseForbidden()
        account = getattr(user, PLATFORM_CONFIG[platform]['related_name'])
        data = model_to_dict(account)
        if platform != Platform.QQ:
            data['update_time'] = account.update_time
        return JsonResponse(data)
    else:
        if request.user.is_staff or user == request.user:  # 管理员或用户本人可以获得全部数据
            accountlink = AccountLinkQueue.objects.filter(userprofile=user).values('platform', 'identifier', 'verified')
        else:  # 其他人不能获得未绑定账号与私人账号数据
            accountlink = AccountLinkQueue.objects.filter(userprofile=user, verified=True).exclude(platform__in=private_platforms).values('platform', 'identifier', 'verified')
        return JsonResponse(list(accountlink), safe=False)


@require_POST
@staff_required
def verify_link(request):
    userid = request.POST.get('id')
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
    update_account(platform, user)
    return HttpResponse()


@require_POST
@staff_required
def unverify_link(request):
    userid = request.GET.get('id')
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
@ratelimit(key='user', rate='6/h')
def update_link(request):
    if not (platform := request.POST.get('platform')):
        return HttpResponseBadRequest()
    try:
        update_account(platform, request.user)
    except ExceptionToResponse as e:
        return e.response()
    return JsonResponse({'type': 'success'})


@require_POST
@login_required_error
def view_saolei_import_one_video(request):
    if not (video_id := request.POST.get('video_id')):
        return HttpResponseBadRequest()
    video = VideoSaolei.objects.filter(id=video_id).first()
    if not video:
        return HttpResponseNotFound()
    if video.user != request.user.account_saolei:
        return HttpResponseForbidden()
    import_task = video.import_task
    if import_task:
        status = import_task.status
        if status in [TaskResultStatus.READY, TaskResultStatus.RUNNING]:
            return HttpResponseConflict()
        import_task.delete()

    try:
        saolei_video_import_one(video)
    except ExceptionToResponse as e:
        return e.response()

    video.refresh_from_db()
    return JsonResponse({'type': 'success', 'import_video__id': video.import_video.id})


@require_POST
@login_required_error
def view_saolei_import_videos(request):
    """
    处理扫雷网录像导入请求的视图函数。函数尝试创建一个任务。

    前提：
        1. 请求类型为POST。
        2. 用户已登录，否则返回HttpResponseForbidden。

    参数:
        mode (str): 导入模式，必须为'all'或'new'，分别表示导入所有录像或仅导入新录像。

    返回:
        HttpResponseForbidden: 如果用户没有关联的saolei账号。
        HttpResponseBadRequest: 如果请求中缺少mode参数或mode参数无效。
        HttpResponseConflict: 如果已有排队中或进行中的任务。
        HttpResponse: 成功创建导入任务后返回空响应。
    """
    if not (saolei_account := request.user.account_saolei):
        return HttpResponseForbidden()
    if not (mode := request.POST.get('mode')):
        return HttpResponseBadRequest()
    if mode not in ['all', 'new']:
        return HttpResponseBadRequest()

    import_task = saolei_account.video_import_task
    if import_task and import_task.status in [TaskResultStatus.READY, TaskResultStatus.RUNNING]:
        logger.warning(f'用户#{request.user.id} 已有一个扫雷网录像同步任务在进行中，无法创建新任务，模式：{mode}')
        return HttpResponseConflict()
    else:
        logger.info(f'用户#{request.user.id} 开始创建扫雷网录像同步任务，模式：{mode}')
        helper_saolei_video_import_bulk(saolei_account, mode)
        return HttpResponse()


@require_GET
@ratelimit(key='ip', rate='1/s')
def view_saolei_get_import_list(request: HttpRequest):
    videos = VideoSaolei.objects.all()
    user_id = request.GET.get('user_id')
    saolei_id = request.GET.get('saolei_id')
    if user_id and saolei_id:
        return HttpResponseBadRequest()
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
        if not user:
            return HttpResponseNotFound()
        videos = videos.filter(user=user.account_saolei)
    if saolei_id:
        account = AccountSaolei.objects.filter(id=saolei_id).first()
        if not account:
            return HttpResponseNotFound()
        videos = videos.filter(user=account)

    data = videos.values('id', 'user__id', 'upload_time', 'level', 'bv', 'timems', 'nf', 'state', 'import_video__id', 'import_task__status')
    return JsonResponse(list(data), safe=False)


@require_GET
def view_saolei_get_import_summary(request: HttpRequest):
    if not (saolei_id := request.GET.get('saolei_id')):
        return HttpResponseBadRequest
    if not (saolei_account := AccountSaolei.objects.filter(id=saolei_id).first()):
        return HttpResponseNotFound()

    bulk_task = saolei_account.video_import_task
    bulk_task_status = bulk_task.status if bulk_task else None

    videos = VideoSaolei.objects.filter(user=saolei_account)
    imported_videos = videos.filter(import_video__isnull=False)
    data = {
        'bulk_task_status': bulk_task_status,
        'total': videos.count(),
        'old_imported': imported_videos.filter(import_task__isnull=True).count(),
        'new_total': videos.filter(import_task__isnull=False).count(),
        'new_ready': videos.filter(import_task__status=TaskResultStatus.READY).count(),
        'new_success': imported_videos.filter(import_task__isnull=False).count(),
        'new_failed': imported_videos.filter(import_task__status=TaskResultStatus.FAILED).count(),
        'new_connection': videos.filter(import_video__isnull=True, import_task__status=TaskResultStatus.SUCCESSFUL).count(),
    }

    return JsonResponse(data)
