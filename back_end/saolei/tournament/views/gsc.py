from datetime import datetime, timezone

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from config.text_choices import Tournament_TextChoices
from config.tournaments import TournamentWeights
from identifier.models import Identifier
from identifier.utils import verify_identifier
from userprofile.decorators import login_required_error
from utils.response import HttpResponseConflict
from ..decorators import GSC_admin_required
from ..models import GSCParticipant, GSCTournament, Tournament


@require_POST
@GSC_admin_required
def new_GSC_tournament(request: HttpRequest):
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
        tournament_id = tournament.tournament_ptr_id
    else:
        tournament: GSCTournament = Tournament.objects.select_subclasses().filter(id=tournament_id).first()
        order = tournament.order
    if not tournament:
        return HttpResponseNotFound()
    tournament.refresh_state()
    results = None
    if tournament.state == Tournament_TextChoices.State.FINISHED or tournament.state == Tournament_TextChoices.State.AWARDED:
        results = list(tournament.get_scores())
        identifier = None
    elif request.user.is_authenticated:
        participant = GSCParticipant.objects.filter(tournament=tournament, user=request.user).first()
        if not participant:
            identifier = None
        else:
            arbiter_identifier = participant.arbiter_identifier
            if arbiter_identifier:
                identifier = arbiter_identifier.identifier
            else:
                identifier = None
    else:
        identifier = None
    return JsonResponse({
        'type': 'success',
        'data': {
            'id': tournament.tournament_ptr_id,
            'start_time': tournament.start_time,
            'end_time': tournament.end_time,
            'state': tournament.state,
            'order': order,
            'token': tournament.token,
        },
        'results': results,
        'identifier': identifier,
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
    if not identifier_text.endswith(tournament.token):  # 检查尾号
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'suffix'})

    if not verify_identifier(identifier_text):  # 审查标识
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'invalid'})
    identifier = Identifier.objects.filter(identifier=identifier_text).first()
    if identifier.userms and identifier.userms != userms:  # 检查标识是否被占用
        return JsonResponse({'type': 'error', 'object': 'identifier', 'category': 'collision'})
    if participant := GSCParticipant.objects.filter(tournament=tournament, user=request.user).first():
        if participant.arbiter_identifier:
            return JsonResponse({'type': 'error', 'object': 'participant', 'category': 'registered'})
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
def get_participant_list(request: HttpRequest):
    if not (order := request.GET.get('order')):
        return HttpResponseBadRequest()
    if not (tournament := GSCTournament.objects.filter(order=order).first()):
        return HttpResponseNotFound()
    return JsonResponse({'type': 'success', 'data': list(tournament.participants.values('id', 'user__id', 'user__realname'))})


@require_POST
@GSC_admin_required
def refresh_GSCParticipant(request: HttpRequest):
    if not (participant_id := request.POST.get('id')):
        return HttpResponseBadRequest()
    participant = GSCParticipant.objects.filter(tournamentparticipant_ptr_id=participant_id).first()
    if not participant:
        return HttpResponseNotFound()
    participant.refresh()
    return JsonResponse({
        'id': participant.id,
        'user__id': participant.user.id,
        'user__realname': participant.user.realname,
        'bt1st': participant.bt1st,
        'bt20th': participant.bt20th,
        'bt20sum': participant.bt20sum,
        'it1st': participant.it1st,
        'it12th': participant.it12th,
        'it12sum': participant.it12sum,
        'et1st': participant.et1st,
        'et5th': participant.et5th,
        'et5sum': participant.et5sum,
        't37': participant.t37,
    })


@require_POST
def award_GSC(request: HttpRequest):
    if not (order := request.POST.get('order')):
        return HttpResponseBadRequest()
    if not (tournament := GSCTournament.objects.filter(order=order).first()):
        return HttpResponseNotFound()
    if tournament.state not in [Tournament_TextChoices.State.FINISHED, Tournament_TextChoices.State.AWARDED]:
        return HttpResponseForbidden()
    tournament.refresh_rank()
    tournament.state = Tournament_TextChoices.State.AWARDED
    tournament.save()
    return HttpResponse()
