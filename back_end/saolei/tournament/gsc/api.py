from datetime import datetime

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from ninja import Field, Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.text_choices import Tournament_TextChoices
from config.tournaments import TournamentWeights
from identifier.models import Identifier
from identifier.services import bind_identifier
from identifier.utils import verify_identifier
from tournament.gsc.decorators import GSC_admin_required
from tournament.models import GSCParticipant, GSCTournament
from userprofile.decorators import login_required_error
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from utils.response import HttpResponseConflict
from utils.schema import DBTaskOut
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


class GSCOrderIn(Schema):
    order: int


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
        ('user__id', int | None, Field(None, alias='user.id')),
        ('user__realname', str | None, Field(None, alias='user.realname')),
    ],
)


def task_response(task):
    return {
        'type': 'success',
        'data': {
            'task_id': str(task.id),
        },
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


@router.get('/results', response=list[GSCScoreOut])
def get_results(request: HttpRequest, tournament_id: int):
    tournament = get_object_or_404(GSCTournament, tournament_ptr_id=tournament_id)
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        return HttpResponseForbidden()
    return list(get_gsc_scores(tournament))


@router.post('/participant')
@decorate_view(login_required_error)
def create_gsc_participant(request: HttpRequest, data: GSCOrderIn = Form(...)):  # noqa: B008
    user = request.user
    tournament = get_object_or_404(GSCTournament, order=data.order)
    if not tournament.accept_checkin():
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
    user: UserProfile = request.user
    tournament = get_object_or_404(GSCTournament, order=data.order)
    if not tournament.accept_checkin():
        return HttpResponseForbidden()
    if not tournament.token:
        return HttpResponseForbidden()
    participant = get_object_or_404(GSCParticipant, tournament=tournament, user=user)
    if not data.identifier.endswith(tournament.token):
        raise ExceptionToResponse('identifier', 'suffix')

    if not verify_identifier(data.identifier):
        raise ExceptionToResponse('identifier', 'invalid')
    identifier = Identifier.objects.get(identifier=data.identifier)
    if identifier.userms_id and identifier.userms_id != user.userms_id:
        raise ExceptionToResponse('identifier', 'collision')
    if participant.arbiter_identifier:
        raise ExceptionToResponse('participant', 'registered')
    participant.arbiter_identifier = identifier
    participant.save(update_fields=['arbiter_identifier'])
    if not identifier.userms:
        bind_identifier(identifier, user.userms)
    return {'type': 'success'}


@router.get('/task', response=DBTaskOut | None)
@decorate_view(GSC_admin_required)
def get_gsc_task(request: HttpRequest, order: int):
    return get_object_or_404(GSCTournament, order=order).task


@router.post('/task/finish')
@decorate_view(GSC_admin_required)
def finish_gsc_task(request: HttpRequest, data: GSCOrderIn = Form(...)):  # noqa: B008
    tournament = get_object_or_404(GSCTournament, order=data.order)
    if not tournament.is_ended():
        return HttpResponseForbidden()

    return task_response(helper_gsc_finish_tournament(tournament))
