
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpRequest
from userprofile.decorators import banned_blocked, staff_required, login_required_error
from .models import Tournament, TournamentParticipant, GSCTournament
from .forms import TournamentForm
from utils import verify_text
from config.text_choices import Tournament_TextChoices
from datetime import datetime
from config.tournaments import GSC_Defaults, TournamentWeights
from utils.response import HttpResponseConflict
from userprofile.models import UserProfile

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
def cancel_tournament(request: HttpRequest):
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
def get_tournament_list(request: HttpRequest):
    tournament_list = Tournament.objects.all().select_subclasses()
    return JsonResponse({
        'type': 'success',
        'data': [{
            'id': tournament.id,
            'series': tournament.series,
            'name': tournament.name,
            'start_time': tournament.start_time,
            'end_time': tournament.end_time,
            'state': tournament.state,
            'host_id': tournament.host.id,
            'host_realname': tournament.host.realname,
        } for tournament in tournament_list],
    })

@require_GET
def get_tournament(request):
    id = request.GET.get('id')
    if not id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.select_subclasses().filter(id=id).first()
    if not tournament:
        return HttpResponseNotFound()
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
    pass


@require_POST
def new_GSC_tournament(request: HttpRequest):
    if request.user.id != GSC_Defaults.HOST_ID:
        return HttpResponseForbidden()
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    
    if not start_time or not end_time:
        state = Tournament_TextChoices.State.PENDING
    elif datetime.now() < start_time:
        state = Tournament_TextChoices.State.PREPARING
    else:
        return JsonResponse({'type': 'error', 'msg': 'invalid_start_time'})
    
    order = request.POST.get('id')
    if GSCTournament.objects.filter(order=order).exists():
        return HttpResponseConflict()
    
    new_GSC = GSCTournament.objects.create(
        start_time=start_time,
        end_time=end_time,
        state=state,
        host=request.user,
        weight=TournamentWeights.GSC,
        order=order,
        token='',
    )

    return JsonResponse({'type': 'success', 'data': new_GSC})

@require_POST
def set_tournament(request: HttpRequest):
    """
    比赛的主办方可以修改比赛信息。目前仅支持修改部分信息，参见下文。

    request应包含POST数据：
        - tournament_id: 要更新的比赛ID
        - start_time (可选): 比赛开始时间
        - end_time (可选): 比赛结束时间
        - order (可选, 仅GSC比赛): 届数
        - token (可选, 仅GSC比赛): 比赛标识
    """
    if not (tournament_id := request.POST.get('tournament_id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if tournament.host != request.user:
        return HttpResponseForbidden()
    
    if start_time := request.POST.get('start_time'):
        tournament.start_time = start_time
    if end_time := request.POST.get('end_time'):
        tournament.end_time = end_time

    if isinstance(tournament, GSCTournament):
        if order := request.POST.get('order'):
            if GSCTournament.objects.filter(order=order).exists():
                return HttpResponseConflict()
            tournament.order = order
        if token := request.POST.get('token'):
            tournament.token = token

    tournament.save()
    return JsonResponse({'type': 'success', 'data': tournament})

@require_POST
@staff_required
def set_tournament_staff(request: HttpRequest):
    """
    管理员可以修改比赛权重和比赛主办方。

    request应包含POST数据：
        - tournament_id: 要更新的比赛ID
        - weight (可选): 比赛权重
        - host_id (可选): 主办方用户ID
    """
    if not (tournament_id := request.POST.get('tournament_id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    
    if (weight := request.POST.get('weight')):
        tournament.weight = weight
    if (host_id := request.POST.get('host_id')):
        if not (host := UserProfile.objects.filter(id=host_id).first()):
            return HttpResponseNotFound()
        tournament.host = host
    
    tournament.save()
    return JsonResponse({'type': 'success', 'data': tournament})