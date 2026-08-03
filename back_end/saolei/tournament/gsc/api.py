from datetime import datetime
from uuid import UUID

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.text_choices import Tournament_TextChoices
from config.tournaments import TournamentWeights
from identifier.models import Identifier
from identifier.services import bind_identifier
from identifier.utils import verify_identifier
from tournament.gsc.decorators import GSC_admin_required
from tournament.models import GSCParticipant, GSCTournament, Tournament
from userprofile.decorators import login_required_error
from utils.response import HttpResponseConflict
from tournament.utils import tournament_accepts_checkin, tournament_has_ended
from .services import get_gsc_scores
from .tasks import helper_gsc_finish_tournament

router = Router()


class NewGSCTournamentIn(Schema):
    id: int
    start_time: datetime | None = None
    end_time: datetime | None = None


class RegisterGSCParticipantIn(Schema):
    identifier: str
    order: int


class GSCParticipantIn(Schema):
    order: int


class GSCOrderIn(Schema):
    order: int


class GSCTaskOut(Schema):
    id: UUID
    status: str
    enqueued_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    return_value: object | None
    exception_class_path: str
    traceback: str


GSCInfoOut = create_schema(
    GSCTournament,
    fields=['id', 'order', 'start_time', 'end_time', 'state'],
    custom_fields=[
        ('token', str, ''),
    ],
)
GSCScoreOut = create_schema(
    GSCParticipant,
    fields=[
        'id',
        'start_time', 'end_time',
        'rank', 'rank_score',
        'bt1st', 'bt20th', 'bt20sum',
        'it1st', 'it12th', 'it12sum',
        'et1st', 'et5th', 'et5sum',
    ],
    custom_fields=[
        ('user__id', int | None, None),
        ('user__realname', str | None, None),
    ],
)


class GSCDetailOut(Schema):
    data: GSCInfoOut
    results: list[GSCScoreOut] | None
    participant: bool
    identifier: str | None


def task_response(task):
    return {
        'type': 'success',
        'data': {
            'task_id': str(task.id),
        },
    }


def task_out(task):
    if task is None:
        return None
    return {
        'id': task.id,
        'status': task.status,
        'enqueued_at': task.enqueued_at,
        'started_at': task.started_at,
        'finished_at': task.finished_at,
        'return_value': task.return_value,
        'exception_class_path': task.exception_class_path,
        'traceback': task.traceback,
    }


@router.post('/new')
@decorate_view(GSC_admin_required)
def new_GSC_tournament(request: HttpRequest, data: NewGSCTournamentIn = Form(...)):  # noqa: B008
    if GSCTournament.objects.filter(order=data.id).exists():
        return HttpResponseConflict()

    GSCTournament.objects.create(
        start_time=data.start_time,
        end_time=data.end_time,
        state=Tournament_TextChoices.State.PENDING,
        host=request.user,
        weight=TournamentWeights.GSC,
        order=data.id,
    )

    return HttpResponse()


@router.get('/admin-info', response=GSCInfoOut)
def get_GSC_tournament(request: HttpRequest, order: int):
    return get_object_or_404(GSCTournament, order=order)


@router.get('/info', response=GSCDetailOut)
def get_gscinfo(request: HttpRequest, id: int | None = None, order: int | None = None):
    if id is None and order is None:
        return HttpResponseBadRequest()

    if id is not None:
        tournament = get_object_or_404(Tournament, id=id)
        tournament = get_object_or_404(GSCTournament, tournament_ptr=tournament)
        order = tournament.order
    else:
        tournament = get_object_or_404(GSCTournament, order=order)

    if tournament.state == Tournament_TextChoices.State.AWARDED:
        results = list(get_gsc_scores(tournament))
        participant_exists = False
        identifier = None
    elif request.user.is_authenticated:
        results = None
        participant = GSCParticipant.objects.filter(tournament=tournament, user=request.user).first()
        participant_exists = participant is not None
        identifier = participant.arbiter_identifier.identifier if participant and participant.arbiter_identifier else None
    else:
        results = None
        participant_exists = False
        identifier = None

    return {
        'data': tournament,
        'results': results,
        'participant': participant_exists,
        'identifier': identifier,
    }


@router.post('/participant')
@decorate_view(login_required_error)
def create_gsc_participant(request: HttpRequest, data: GSCParticipantIn = Form(...)):  # noqa: B008
    user = request.user
    if not (tournament := GSCTournament.objects.filter(order=data.order).first()):
        return HttpResponseNotFound()
    if not tournament_accepts_checkin(tournament):
        return HttpResponseForbidden()
    if not tournament.token:
        return HttpResponseForbidden()

    GSCParticipant.objects.get_or_create(
        tournament=tournament,
        user=user,
        defaults={
            'token': tournament._token,
            'start_time': tournament.start_time,
            'end_time': tournament.end_time,
        },
    )
    return {'type': 'success'}


@router.post('/participant/identifier')
@decorate_view(login_required_error)
def register_gsc_participant_identifier(request: HttpRequest, data: RegisterGSCParticipantIn = Form(...)):  # noqa: B008
    user = request.user
    userms = user.userms
    if not (tournament := GSCTournament.objects.filter(order=data.order).first()):
        return HttpResponseNotFound()
    if not tournament_accepts_checkin(tournament):
        return HttpResponseForbidden()
    if not tournament.token:
        return HttpResponseForbidden()
    if not (participant := GSCParticipant.objects.filter(tournament=tournament, user=user).first()):
        return HttpResponseNotFound()
    if not data.identifier.endswith(tournament.token):
        return {'type': 'error', 'object': 'identifier', 'category': 'suffix'}

    if not verify_identifier(data.identifier):
        return {'type': 'error', 'object': 'identifier', 'category': 'invalid'}
    identifier = Identifier.objects.get(identifier=data.identifier)
    if identifier.userms and identifier.userms != userms:
        return {'type': 'error', 'object': 'identifier', 'category': 'collision'}
    if participant.arbiter_identifier:
        return {'type': 'error', 'object': 'participant', 'category': 'registered'}
    participant.arbiter_identifier = identifier
    participant.save(update_fields=['arbiter_identifier'])
    if not identifier.userms:
        bind_identifier(identifier, userms)
    return {'type': 'success'}


@router.get('/task', response=GSCTaskOut | None)
@decorate_view(GSC_admin_required)
def get_gsc_task(request: HttpRequest, order: int):
    tournament = get_object_or_404(GSCTournament, order=order)
    return task_out(tournament.task)


@router.post('/task/finish')
@decorate_view(GSC_admin_required)
def finish_gsc_task(request: HttpRequest, data: GSCOrderIn = Form(...)):  # noqa: B008
    if not (tournament := GSCTournament.objects.filter(order=data.order).first()):
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.AWARDED and not tournament_has_ended(tournament):
        return HttpResponseForbidden()

    return task_response(helper_gsc_finish_tournament(tournament))
