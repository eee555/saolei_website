from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit
from django_tasks_db.models import DBTaskResult

from userprofile.decorators import banned_blocked, login_required_error, staff_required
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
        video = new_video_by_file(request.user, video_form.cleaned_data['file'])
    except ExceptionToResponse as e:
        return e.response()
    return JsonResponse({'type': 'success', 'object': 'videomodel', 'category': 'upload', 'data': {'id': video.id, 'state': video.state}})


@require_GET
@staff_required
def view_task_detail(request: HttpRequest):
    return JsonResponse(list(DBTaskResult.objects.all().values()), safe=False)


@require_POST
@staff_required
def view_delete_task(request: HttpRequest):
    task_id = request.POST.get('task_id')
    if not task_id:
        return HttpResponseBadRequest()

    db_task = DBTaskResult.objects.filter(id=task_id).first()
    if not db_task:
        return HttpResponseNotFound()

    db_task.delete()
    return HttpResponse()
