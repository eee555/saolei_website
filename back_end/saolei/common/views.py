from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpRequest
from django.views.decorators.http import require_POST
from .forms import UploadVideoForm
from .utils import new_video_by_file
from userprofile.decorators import login_required_error, banned_blocked
from django_ratelimit.decorators import ratelimit
from utils.exceptions import ExceptionToResponse


@require_POST
@login_required_error
@banned_blocked
@ratelimit(key='ip', rate='5/s')
def video_upload(request: HttpRequest):
    if request.user.userms.video_num_total >= request.user.userms.video_num_limit:
        return HttpResponse(status=402)  # 录像仓库已满
    video_form = UploadVideoForm(data=request.POST, files=request.FILES)
    if not video_form.is_valid():
        return HttpResponseBadRequest(video_form.errors)
    try:
        video = new_video_by_file(request.user, video_form.cleaned_data["file"])
    except ExceptionToResponse as e:
        return e.response()
    return JsonResponse({'type': 'success', 'object': 'videomodel', 'category': 'upload', 'data': {'id': video.id, 'state': video.state}})
