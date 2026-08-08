
from datetime import timedelta

from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.text_choices import Tournament_TextChoices
from tournament.models import WeeklyParticipant, WeeklyTournament
from tournament.schema import TournamentIdIn
from userprofile.decorators import login_required_error

router = Router()

WeeklyInfoOut = create_schema(
    WeeklyTournament,
    fields=['id', 'year', 'week', 'start_time', 'end_time', 'state', 'tournament_format'],
)

WeeklyScoreOut = create_schema(
    WeeklyParticipant,
    fields=['id', 'start_time', 'end_time', 'rank', 'rank_score', 'classic_et', 'classic_it', 'classic_score'],
    custom_fields=[('user_id', int | None, None)]
)


class WeeklyDetailOut(Schema):
    data: WeeklyInfoOut
    results: list[WeeklyScoreOut] | None
    participant: bool
    token: str


@router.get('/info', response=WeeklyDetailOut)
def get_weeklyinfo(request: HttpRequest, tournament_id: int | None = None, order: int | None = None):
    if tournament_id is None and order is None:
        return HttpResponseBadRequest()
    if tournament_id is not None and order is not None:
        return HttpResponseBadRequest()

    if tournament_id is not None:
        tournament = get_object_or_404(WeeklyTournament, tournament_ptr_id=tournament_id)
        order = tournament.order
    else:
        tournament = get_object_or_404(WeeklyTournament, order=order)

    if tournament.state == Tournament_TextChoices.State.AWARDED:
        return {
            'data': tournament,
            'results': WeeklyParticipant.objects.filter(tournament=tournament),
            'participant': False,
            'token': None,
        }

    if not request.user.is_authenticated:
        return {
            'data': tournament,
            'results': None,
            'participant': False,
            'token': None,
        }

    participant = WeeklyParticipant.objects.filter(tournament=tournament, user=request.user).first()
    if participant is None:
        return {
            'data': tournament,
            'results': None,
            'participant': False,
            'token': None,
        }
    return {
        'data': tournament,
        'results': None,
        'participant': True,
        'token': participant.token,
    }


@router.post('/participant')
@decorate_view(login_required_error)
def create_weekly_participant(request: HttpRequest, data: TournamentIdIn = Form(...)):  # noqa: B008
    user = request.user
    tournament = get_object_or_404(WeeklyTournament, order=data.order)
    if not tournament.accept_checkin():
        return HttpResponseForbidden()
    if not tournament.token:
        return HttpResponseForbidden()

    now = timezone.now()
    participant = WeeklyParticipant.objects.get_or_create(
        tournament=tournament,
        user=user,
        defaults={
            'start_time': now,
            'end_time': now + timedelta(hours=2),
        },
    )
    return {'type': 'success', 'token': participant[0].token}
