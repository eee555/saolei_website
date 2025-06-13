
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.views.decorators.http import require_GET, require_POST
from userprofile.decorators import banned_blocked, login_required_error
from .models import GSCParticipant, GSC


@require_GET
@banned_blocked
@login_required_error
def get_my_games(request):
    gscid = request.GET.get('gscid')
    if not gscid:
        return HttpResponseBadRequest()
    participant = GSCParticipant.objects.filter(gsc__id=gscid, user=request.user).first()
    if not participant:
        return HttpResponseNotFound()
    

@require_POST
@login_required_error
def set_gsc_field(request):
    # 只向郭锦洋开放
    if request.user.id != 48:
        return HttpResponseForbidden()
    gscid = request.POST.get('id')
    field = request.POST.get('field')
    value = request.POST.get('value')
    if not gscid or not field or not value:
        return HttpResponseBadRequest()
    gsc = GSC.objects.filter(id=gscid).first()
    if not gsc:
        return HttpResponseNotFound()
    if field == 'start_time':
        gsc.update(start_time=value)
    elif field == 'end_time':
        gsc.update(end_time=value)
    elif field == 'token':
        gsc.update(token=value)
    else:
        return HttpResponseBadRequest()
    return HttpResponse()

@require_GET
def get_gsc_info(request):
    gscid = request.GET.get('gscid')
    if not gscid:
        return HttpResponseBadRequest()
    gsc = GSC.objects.filter(id=gscid).first()
    if not gsc:
        return HttpResponseNotFound()
    data = {
        'start_time': gsc.start_time,
        'end_time': gsc.end_time,
        'token': gsc.token
    }
    return JsonResponse(data)