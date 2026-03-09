from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from django_tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult

from userprofile.decorators import banned_blocked, login_required_error
from utils.exceptions import ExceptionToResponse
from .forms import UploadVideoForm
from .utils import new_video_by_file


@require_POST
@login_required_error
@banned_blocked
@ratelimit(key='ip', rate='5/s')
def video_upload(request: HttpRequest):
    if request.user.userms.video_num_total >= request.user.userms.video_num_limit:
        return HttpResponse(status=402)  # 录像仓库已满
    if not request.user.has_realname():
        return JsonResponse({'type': 'error', 'obj': 'userprofile', 'category': 'realname_required'})
    video_form = UploadVideoForm(data=request.POST, files=request.FILES)
    if not video_form.is_valid():
        return HttpResponseBadRequest(video_form.errors)
    try:
        video = new_video_by_file(request.user, video_form.cleaned_data["file"])
    except ExceptionToResponse as e:
        return e.response()
    return JsonResponse({'type': 'success', 'object': 'videomodel', 'category': 'upload', 'data': {'id': video.id, 'state': video.state}})


@require_GET
@ratelimit(key='ip', rate='1/5s')
def view_task_summary(request: HttpRequest):
    total = DBTaskResult.objects.count()
    ready = DBTaskResult.objects.filter(status=TaskResultStatus.READY).count()
    running = DBTaskResult.objects.filter(status=TaskResultStatus.RUNNING).count()
    successful = DBTaskResult.objects.filter(status=TaskResultStatus.SUCCESSFUL).count()
    failed = DBTaskResult.objects.filter(status=TaskResultStatus.FAILED).count()
    return JsonResponse({'total': total, 'ready': ready, 'running': running, 'successful': successful, 'failed': failed})
