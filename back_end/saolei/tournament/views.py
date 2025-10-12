from datetime import datetime, timezone

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from config.text_choices import Tournament_TextChoices
from config.tournaments import GSC_Defaults, TournamentWeights
from identifier.models import Identifier
from identifier.utils import verify_identifier
from msuser.models import UserMS
from userprofile.decorators import banned_blocked, login_required_error, staff_required
from userprofile.models import UserProfile
from utils import verify_text
from utils.response import HttpResponseConflict
from .forms import TournamentForm
from .models import GSCParticipant, GSCTournament, Tournament, TournamentParticipant


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
def new_GSC_tournament(request: HttpRequest):
    if request.user.id != GSC_Defaults.HOST_ID:
        return HttpResponseForbidden()
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')

    if not start_time or not end_time:
        state = Tournament_TextChoices.State.PENDING
    elif datetime.now(tz=timezone.utc) < start_time:
        state = Tournament_TextChoices.State.PREPARING
    else:
        return JsonResponse({'type': 'error', 'msg': 'invalid_start_time'})

    order = request.POST.get('id')
    if GSCTournament.objects.filter(order=order).exists():
        return HttpResponseConflict()

    GSCTournament.objects.create(
        start_time=start_time,
        end_time=end_time,
        state=state,
        host=request.user,
        weight=TournamentWeights.GSC,
        order=order,
    )

    return HttpResponse()


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


@require_GET
def get_GSC_tournament(request: HttpRequest):
    if not (gsc_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    tournament = GSCTournament.objects.filter(order=gsc_id).first()
    if not tournament:
        return JsonResponse({'type': 'error'})
    return JsonResponse({'type': 'success', 'data': {
        'id': tournament.id,
        'start_time': tournament.start_time,
        'end_time': tournament.end_time,
        'state': tournament.state,
        'token': tournament.token,
    }})


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
def get_gscinfo(request: HttpRequest):
    """
    获取GSC比赛信息。

    根据请求参数中的id或order获取比赛信息，并返回比赛详情和比赛结果。

    request应包含GET数据：
        - id（可选）: 比赛ID
        - order（可选）: GSC届数，优先级低于id
        - 二者至少包含其一，否则返回 400 Bad Request

    返回包含以下结构的JSON响应：
        {
            'type': 'success',
            'data': 比赛数据,
            'results': 比赛结果。若未颁奖则为空
        }
    """
    if not (tournament_id := request.GET.get('id')):
        if not (order := request.GET.get('order')):
            return HttpResponseBadRequest()
        tournament = GSCTournament.objects.filter(order=order).first()
    else:
        tournament: GSCTournament = Tournament.objects.select_subclasses().filter(id=tournament_id).first()
    if not tournament:
        return HttpResponseNotFound()
    tournament.refresh_state()
    if tournament.state == Tournament_TextChoices.State.FINISHED or tournament.state == Tournament_TextChoices.State.AWARDED:
        results = list(GSCParticipant.objects.filter(tournament=tournament).values(
            'user__id', 'user__realname',
            'start_time', 'end_time',
            'rank', 'rank_score',
            'bt1st', 'bt20th', 'bt20sum',
            'it1st', 'it12th', 'it12sum',
            'et1st', 'et5th', 'et5sum',
        ))
    elif request.user.is_authenticated:
        participant = GSCParticipant.objects.filter(tournament=tournament, user=request.user).first()
        if not participant:
            results = None
        else:
            participant.refresh()
            identifier = participant.arbiter_identifier
            results = {
                'token': participant.token,
                'arbiter_identifier': identifier.identifier if identifier else '',
                'bt1st': participant.bt1st,
                'bt20th': participant.bt20th,
                'bt20sum': participant.bt20sum,
                'it1st': participant.it1st,
                'it12th': participant.it12th,
                'it12sum': participant.it12sum,
                'et1st': participant.et1st,
                'et5th': participant.et5th,
                'et5sum': participant.et5sum,
            }
    else:
        results = []
    return JsonResponse({
        'type': 'success',
        'data': {
            'id': tournament.id,
            'start_time': tournament.start_time,
            'end_time': tournament.end_time,
            'state': tournament.state,
            'order': tournament.order,
            'token': tournament.token,
        },
        'results': results,
    })


@require_POST
@login_required_error
def register_GSCParticipant(request: HttpRequest):
    """
    该函数用于处理用户注册GSC比赛的阿比特标识的请求。它会验证请求参数、比赛状态、用户注册状态以及标识符的有效性，
    在所有条件满足后为用户关联相应的标识。若有需要，将用户注册为比赛参与者。

    Args:
        request (HttpRequest): HTTP请求对象，包含以下POST参数：
            - identifier (str): 阿比特标识
            - order (str): 比赛届数

    Returns:
        JsonResponse: 包含注册结果的JSON响应。可能的返回值：
            - 成功：{'type': 'success'}
            - 错误：{'type': 'error', 'object': str, 'category': str}
            - HTTP错误响应：
                * 400 Bad Request：缺少必要参数
                * 404 Not Found：比赛不存在
                * 403 Forbidden：比赛未进行中
                * 409 Conflict：用户已注册

    错误类型说明：
        - object: 'identifier' - 表示错误与标识符相关
        - category:
            * 'suffix' - 标识符后缀不匹配
            * 'invalid' - 标识符无效
            * 'collision' - 标识符已被其他用户占用
    """
    # 不应由正常的前端产生的错误
    user = request.user
    userms = user.userms
    if not (identifier_text := request.POST.get('identifier')):
        return HttpResponseBadRequest()
    if not (order := request.POST.get('order')):
        return HttpResponseBadRequest()
    if not (tournament := GSCTournament.objects.filter(order=order).first()):
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.ONGOING:  # 比赛必须是进行中
        return HttpResponseForbidden()
    if (GSCParticipant.objects.filter(tournament=tournament, user=request.user)):  # 用户必须未注册
        return HttpResponseConflict()
    if not identifier_text.endswith(tournament.token):  # 检查尾号
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'suffix'})

    if not verify_identifier(identifier_text):  # 审查标识
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'invalid'})
    identifier = Identifier.objects.filter(identifier=identifier_text).first()
    if identifier.userms and identifier.userms != userms:  # 检查标识是否被占用
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'collision'})
    if participant := GSCParticipant.objects.filter(tournament=tournament, user=request.user).first():
        participant.arbiter_identifier = identifier
        participant.save()
    else:
        GSCParticipant.objects.create(tournament=tournament, user=user, arbiter_identifier=identifier)
    if not identifier.userms:
        identifier.userms = userms
        userms.identifiers.append(identifier_text)
        identifier.save()
        userms.save()
    return JsonResponse({'type': 'success'})


@require_GET
def get_tournament_news(request: HttpRequest):
    preparing_tournaments = Tournament.objects.filter(state=Tournament_TextChoices.State.PREPARING)
    ongoing_tournaments = Tournament.objects.filter(state=Tournament_TextChoices.State.ONGOING)
    return JsonResponse({
        'type': 'success',
        'preparing': list(preparing_tournaments.values('id', 'start_time')),
        'ongoing': list(ongoing_tournaments.values('id', 'end_time')),
    })
