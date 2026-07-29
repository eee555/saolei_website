from datetime import datetime, timezone

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view

from config.text_choices import Tournament_TextChoices
from config.tournaments import GSC_Defaults, TournamentWeights
from identifier.models import Identifier
from identifier.services import bind_identifier
from identifier.utils import verify_identifier
from tournament.decorators import GSC_admin_required
from tournament.models import GSCParticipant, GSCTournament, Tournament
from userprofile.decorators import login_required_error
from utils.response import HttpResponseConflict
from .services import get_gsc_scores, refresh_gsc_participant_score
from .tasks import task_gsc_finish, task_gsc_refresh

router = Router()


class NewGSCTournamentIn(Schema):
    id: int
    start_time: datetime | None = None
    end_time: datetime | None = None


class RegisterGSCParticipantIn(Schema):
    identifier: str
    order: int


class GSCOrderIn(Schema):
    order: int


class GSCParticipantRefreshIn(Schema):
    id: int


def can_manage_GSC(request: HttpRequest):
    return request.user.is_authenticated and (request.user.is_staff or request.user.id == GSC_Defaults.HOST_ID)


def _aware_datetime(value: datetime | None):
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=timezone.utc)


def task_response(enqueued_task):
    return {
        'type': 'success',
        'data': {
            'task_id': str(enqueued_task.db_result.id),
        },
    }


@router.post('/new')
@decorate_view(GSC_admin_required)
def new_GSC_tournament(request: HttpRequest, data: NewGSCTournamentIn = Form(...)):  # noqa: B008
    start_time = _aware_datetime(data.start_time)
    end_time = _aware_datetime(data.end_time)

    if start_time is None or end_time is None:
        state = Tournament_TextChoices.State.PENDING
    elif datetime.now(tz=timezone.utc) < start_time:
        state = Tournament_TextChoices.State.PREPARING
    else:
        return {'type': 'error', 'msg': 'invalid_start_time'}

    if GSCTournament.objects.filter(order=data.id).exists():
        return HttpResponseConflict()

    GSCTournament.objects.create(
        start_time=start_time,
        end_time=end_time,
        state=state,
        host=request.user,
        weight=TournamentWeights.GSC,
        order=data.id,
    )

    return HttpResponse()


@router.get('/admin-info')
def get_GSC_tournament(request: HttpRequest, id: int):
    tournament = GSCTournament.objects.filter(order=id).first()
    if not tournament:
        return {'type': 'error'}
    return {
        'type': 'success',
        'data': {
            'id': tournament.id,
            'start_time': tournament.start_time,
            'end_time': tournament.end_time,
            'state': tournament.state,
            'token': tournament.token,
        },
    }


@router.get('/info')
def get_gscinfo(request: HttpRequest, id: int | None = None, order: int | None = None):
    if id is None and order is None:
        return HttpResponseBadRequest()

    if id is not None:
        tournament = Tournament.objects.select_subclasses().filter(id=id).first()
        if not isinstance(tournament, GSCTournament):
            return HttpResponseNotFound()
        order = tournament.order
    else:
        tournament = GSCTournament.objects.filter(order=order).first()

    if not tournament:
        return HttpResponseNotFound()

    tournament.refresh_state()
    results = None
    if tournament.state in [Tournament_TextChoices.State.FINISHED, Tournament_TextChoices.State.AWARDED]:
        results = list(get_gsc_scores(tournament))
        identifier = None
    elif request.user.is_authenticated:
        participant = GSCParticipant.objects.filter(tournament=tournament, user=request.user).first()
        identifier = participant.arbiter_identifier.identifier if participant and participant.arbiter_identifier else None
    else:
        identifier = None

    return {
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
    }


@router.post('/register')
@decorate_view(login_required_error)
def register_GSCParticipant(request: HttpRequest, data: RegisterGSCParticipantIn = Form(...)):  # noqa: B008
    user = request.user
    userms = user.userms
    if not (tournament := GSCTournament.objects.filter(order=data.order).first()):
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.ONGOING:
        return HttpResponseForbidden()
    if not data.identifier.endswith(tournament.token):
        return {'type': 'error', 'object': 'identifier', 'category': 'suffix'}

    if not verify_identifier(data.identifier):
        return {'type': 'error', 'object': 'identifier', 'category': 'invalid'}
    identifier = Identifier.objects.filter(identifier=data.identifier).first()
    if identifier.userms and identifier.userms != userms:
        return {'type': 'error', 'object': 'identifier', 'category': 'collision'}
    if participant := GSCParticipant.objects.filter(tournament=tournament, user=request.user).first():
        if participant.arbiter_identifier:
            return {'type': 'error', 'object': 'participant', 'category': 'registered'}
        participant.arbiter_identifier = identifier
        participant.save(update_fields=['arbiter_identifier'])
    else:
        GSCParticipant.objects.create(tournament=tournament, user=user, arbiter_identifier=identifier)
    if not identifier.userms:
        bind_identifier(identifier, userms)
    return {'type': 'success'}


@router.get('/participants')
def get_participant_list(request: HttpRequest, order: int):
    if not (tournament := GSCTournament.objects.filter(order=order).first()):
        return HttpResponseNotFound()
    participants = GSCParticipant.objects.filter(tournament=tournament).values(
        'id',
        'user__id',
        'user__realname',
        'bt1st', 'bt20th', 'bt20sum',
        'it1st', 'it12th', 'it12sum',
        'et1st', 'et5th', 'et5sum',
        't37',
    )
    return {'type': 'success', 'data': list(participants)}


@router.post('/participant/refresh')
@decorate_view(login_required_error)
def refresh_GSCParticipant(request: HttpRequest, data: GSCParticipantRefreshIn = Form(...)):  # noqa: B008
    if not can_manage_GSC(request):
        return HttpResponseForbidden()
    participant = GSCParticipant.objects.filter(tournamentparticipant_ptr_id=data.id).first()
    if not participant:
        return HttpResponseNotFound()
    refresh_gsc_participant_score(participant)
    return {
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
    }


@router.post('/refreshscore')
@decorate_view(login_required_error)
def refresh_GSC_score(request: HttpRequest, data: GSCOrderIn = Form(...)):  # noqa: B008
    if not can_manage_GSC(request):
        return HttpResponseForbidden()
    if not GSCTournament.objects.filter(order=data.order).exists():
        return HttpResponseNotFound()
    return task_response(task_gsc_refresh.enqueue(data.order))


@router.post('/award')
@decorate_view(login_required_error)
def award_GSC(request: HttpRequest, data: GSCOrderIn = Form(...)):  # noqa: B008
    if not can_manage_GSC(request):
        return HttpResponseForbidden()
    if not (tournament := GSCTournament.objects.filter(order=data.order).first()):
        return HttpResponseNotFound()
    if tournament.state not in [Tournament_TextChoices.State.FINISHED, Tournament_TextChoices.State.AWARDED]:
        return HttpResponseForbidden()

    return task_response(task_gsc_finish.enqueue(data.order))
