
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from userprofile.decorators import banned_blocked, staff_required, login_required_error
from .models import Tournament, TournamentParticipant
from .forms import TournamentForm
from .utils import refresh_tournament
from utils import verify_text
from config.text_choices import Tournament_TextChoices
from datetime import datetime

@require_POST
@banned_blocked
@login_required_error
def create_tournament(request):
    # 处理创建比赛的逻辑
    create_form = TournamentForm(data=request.POST)
    if not create_form.is_valid():
        return HttpResponseBadRequest()
    is_valid = verify_text(create_form.cleaned_data['name'] + create_form.cleaned_data['description'])
    if not is_valid:
        return JsonResponse({'type': 'error', 'object': 'tournament', 'category': 'invalid_name_or_description'})
    Tournament.objects.create(
        name=create_form.cleaned_data['name'],
        description=create_form.cleaned_data['description'],
        start_time=create_form.cleaned_data['start_time'],
        end_time=create_form.cleaned_data['end_time'],
        series=create_form.cleaned_data['series'],
        host=request.user,
        state=Tournament_TextChoices.State.PENDING
    )
    return HttpResponse()

@require_POST
@staff_required
def allow_tournament(request):
    id = request.POST.get('id')
    if not id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=id).first()
    if not tournament:
        return HttpResponseNotFound()
    if datetime.now() > tournament.start_time:
        tournament.state = Tournament_TextChoices.State.CANCELLED
        return JsonResponse({'type': 'error', 'object': 'tournament', 'category': 'missed_start_time'})
    tournament.state = Tournament_TextChoices.State.PREPARING
    tournament.save()
    return HttpResponse()

@require_POST
@login_required_error
def cancel_tournament(request):
    id = request.POST.get('id')
    if not id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=id).first()
    if not tournament:
        return HttpResponseNotFound()
    if not request.user.is_staff and tournament.host != request.user:
        return HttpResponseForbidden()
    tournament.state = Tournament_TextChoices.State.CANCELLED
    tournament.save()
    return HttpResponse()

@require_GET
def get_tournament_list(request):
    tournament_list = Tournament.objects.all()
    for tournament in tournament_list:
        refresh_tournament(tournament)
    return JsonResponse({'type': 'success', 'data': tournament_list.values('id', 'name', 'description', 'start_time', 'end_time', 'series', 'host__id', 'host__realname', 'state')})

@require_GET
def get_tournament(request):
    id = request.GET.get('id')
    if not id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=id).first()
    if not tournament:
        return HttpResponseNotFound()
    refresh_tournament(tournament)
    data = {
        'id': tournament.id,
        'name': tournament.name,
        'description': tournament.description,
        'start_time': tournament.start_time,
        'end_time': tournament.end_time,
        'series': tournament.series,
        'host_id': tournament.host.id,
        'host_realname': tournament.host.realname,
        'state': tournament.state
    }
    return JsonResponse({'type': 'success', 'data': data})

@require_POST
@banned_blocked
def tournament_checkin(request):
    id = request.POST.get('id')
    if not id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=id).first()
    refresh_tournament(tournament)
    if not tournament:
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.ONGOING:
        return JsonResponse({'type': 'error', 'object': 'tournament', 'msg': 'not_ongoing'})
    participant = TournamentParticipant.objects.filter(tournament=tournament, user=request.user).first()
    if participant:
        return JsonResponse({'type': 'warning', 'object': 'tournament', 'msg': 'already_checked_in'})
    participant = TournamentParticipant.objects.create(tournament=tournament, user=request.user)
    return JsonResponse({'type': 'success', 'object': 'tournament', 'data': participant})

def download_tournament(request):
    