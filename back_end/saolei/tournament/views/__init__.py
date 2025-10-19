from datetime import datetime, timezone

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit

from config.text_choices import Tournament_TextChoices
from userprofile.decorators import banned_blocked, login_required_error, staff_required
from userprofile.models import UserProfile
from utils import verify_text
from utils.response import HttpResponseConflict
from videomanager.view_utils import generate_file_stream
from ..forms import TournamentForm
from ..models import GSCTournament, Tournament, TournamentParticipant
from ..utils import participant_videos


@require_POST
@banned_blocked
@login_required_error
def create_tournament(request: HttpRequest):
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
        state=Tournament_TextChoices.State.PENDING,
    )
    return HttpResponse()


@require_POST
@staff_required
def allow_tournament(request: HttpRequest):
    tournament_id = request.POST.get('id')
    if not id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=tournament_id).first()
    if not tournament:
        return HttpResponseNotFound()
    if datetime.now(tz=timezone.utc) > tournament.start_time:
        tournament.state = Tournament_TextChoices.State.CANCELLED
        return JsonResponse({'type': 'error', 'object': 'tournament', 'category': 'missed_start_time'})
    tournament.state = Tournament_TextChoices.State.PREPARING
    tournament.save()
    return HttpResponse()


@require_POST
@login_required_error
def cancel_tournament(request: HttpRequest):
    tournament_id = request.POST.get('id')
    if not tournament_id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=tournament_id).first()
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
    data = []
    for tournament in tournament_list:
        tournament.refresh_state()
        data.append({
            'id': tournament.id,
            'series': tournament.series,
            'name': tournament.name,
            'start_time': tournament.start_time,
            'end_time': tournament.end_time,
            'state': tournament.state,
            'host_id': tournament.host.id,
            'host_realname': tournament.host.realname,
        })
    return JsonResponse({
        'type': 'success',
        'data': data,
    })


@require_GET
def get_tournament(request):
    tournament_id = request.GET.get('id')
    if not tournament_id:
        return HttpResponseBadRequest()
    tournament: Tournament = Tournament.objects.select_subclasses().filter(id=tournament_id).first()
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
        'state': tournament.state,
    }
    return JsonResponse({'type': 'success', 'data': data})


@require_POST
@banned_blocked
def tournament_checkin(request):
    tournament_id = request.POST.get('id')
    if not tournament_id:
        return HttpResponseBadRequest()
    tournament = Tournament.objects.filter(id=tournament_id).first()
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
def set_tournament(request: HttpRequest):
    """
    比赛的主办方可以修改比赛信息。目前仅支持修改部分信息，参见下文。

    request应包含POST数据：
        - id: 要更新的比赛ID
        - start_time (可选): 比赛开始时间。比赛开始后不可修改
        - end_time (可选): 比赛结束时间。比赛开始后不可修改
        - order (可选, 仅GSC比赛): 届数
        - token (可选, 仅GSC比赛): 比赛标识，不能与其他存在的比赛标识冲突
    """
    if not (tournament_id := request.POST.get('id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.select_subclasses().filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if tournament.host != request.user:
        return HttpResponseForbidden()

    if start_time := request.POST.get('start_time'):
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        tournament.start_time = start_time
    if end_time := request.POST.get('end_time'):
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        tournament.end_time = end_time

    if isinstance(tournament, GSCTournament):
        if order := request.POST.get('order'):
            if GSCTournament.objects.filter(order=order).exists():
                return HttpResponseConflict()
            tournament.order = order
        if token := request.POST.get('token'):
            if GSCTournament.objects.filter(token=token).first():
                return HttpResponseConflict()
            if TournamentParticipant.objects.filter(token=token).first():
                return HttpResponseConflict()
            tournament.token = token

    tournament.save()
    tournament.refresh_state()
    return HttpResponse()


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


@require_POST
@staff_required
def validate_tournament(request: HttpRequest):
    if not (tournament_id := request.POST.get('id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    valid = request.POST.get('valid')
    if valid == 'true':
        tournament.validate()
        return HttpResponse()
    elif valid == 'false':
        tournament.invalidate()
        return HttpResponse()
    return HttpResponseBadRequest()


@require_GET
def get_participant_list(request: HttpRequest):
    if not (tournament_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    return JsonResponse({'type': 'success', 'data': list(tournament.participants.values('id', 'user__id', 'user__realname'))})


@require_GET
def get_participant_videos(request: HttpRequest):
    if not (tournament_id := request.GET.get('tournament_id')):
        return HttpResponseBadRequest()
    print(tournament_id)
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if not (user_id := request.GET.get('user_id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    if tournament.state == Tournament_TextChoices.State.ONGOING and request.user != user:
        return HttpResponseForbidden()
    participant = TournamentParticipant.objects.filter(user=user, tournament=tournament).first()
    if not participant:
        return HttpResponseNotFound()
    return JsonResponse({'type': 'success', 'data': participant_videos(participant)})


@require_GET
def get_tournament_news(request: HttpRequest):
    preparing_tournaments = Tournament.objects.filter(state=Tournament_TextChoices.State.PREPARING)
    ongoing_tournaments = Tournament.objects.filter(state=Tournament_TextChoices.State.ONGOING)
    return JsonResponse({
        'type': 'success',
        'preparing': list(preparing_tournaments.values('id', 'start_time')),
        'ongoing': list(ongoing_tournaments.values('id', 'end_time')),
    })


@require_GET
@ratelimit(key='ip', rate='1/h')
def download_all_videos(request: HttpRequest):
    if not (tournament_id := request.GET.get('tournament_id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if tournament.state not in [Tournament_TextChoices.State.FINISHED, Tournament_TextChoices.State.AWARDED]:
        return HttpResponseForbidden()
    response = StreamingHttpResponse(generate_file_stream(tournament.videos.all()), content_type="application/octet-stream")
    response["Content-Disposition"] = 'attachment; filename="all_files_stream.bin"'
    return response


@require_GET
@ratelimit(key='ip', rate='1/m')
def download_videos_participant(request: HttpRequest):
    if not (tournament_id := request.GET.get('tournament_id')):
        return HttpResponseBadRequest()
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if not (user_id := request.GET.get('user_id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    if tournament.state == Tournament_TextChoices.State.ONGOING and request.user != user:
        return HttpResponseForbidden()
    response = StreamingHttpResponse(generate_file_stream(tournament.videos.filter(player=user)), content_type="application/octet-stream")
    response["Content-Disposition"] = 'attachment; filename="all_files_stream.bin"'
    return response
