
from datetime import datetime, time, timedelta

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.text_choices import Tournament_TextChoices
from config.tournaments import TournamentWeights
from tournament.models import WeeklyParticipant, WeeklyTournament
from userprofile.decorators import login_required_error, staff_required
from utils.response import HttpResponseConflict
from utils.schema import IdIn

router = Router()


class NewWeeklyTournamentIn(Schema):
    tournament_format: str = Tournament_TextChoices.WeeklyFormat.CLASSIC


class WeeklySetIn(IdIn):
    state: str


WeeklyInfoOut = create_schema(
    WeeklyTournament,
    fields=['id', 'year', 'week', 'start_time', 'end_time', 'state', 'tournament_format'],
)

WeeklyScoreOut = create_schema(
    WeeklyParticipant,
    fields=['id', 'start_time', 'end_time', 'rank', 'rank_score', 'classic_et', 'classic_it', 'classic_score'],
    custom_fields=[('user_id', int | None, None)],
)


class WeeklyDetailOut(Schema):
    data: WeeklyInfoOut
    results: list[WeeklyScoreOut] | None
    token: str | None


def get_next_week_window():
    today = timezone.localdate()
    next_monday = today + timedelta(days=7 - today.weekday())
    start_time = timezone.make_aware(
        datetime.combine(next_monday, time.min),
        timezone.get_current_timezone(),
    )
    end_time = start_time + timedelta(days=7)
    year, week, _ = start_time.isocalendar()
    return year, week, start_time, end_time


@router.post('/new')
@decorate_view(staff_required)
def new_weekly_tournament(request: HttpRequest, data: NewWeeklyTournamentIn = Form(...)):  # noqa: B008
    year, week, start_time, end_time = get_next_week_window()
    if WeeklyTournament.objects.filter(year=year, week=week).exists():
        return HttpResponseConflict()

    tournament = WeeklyTournament.objects.create(
        year=year,
        week=week,
        start_time=start_time,
        end_time=end_time,
        state=Tournament_TextChoices.State.PENDING,
        subclass=Tournament_TextChoices.Subclass.WEEKLY,
        host=request.user,
        weight=TournamentWeights.WEEKLY,
        tournament_format=data.tournament_format,
    )
    update_fields = tournament.validate()
    if update_fields:
        tournament.save(update_fields=update_fields)
    return HttpResponse()


@router.post('/set')
@decorate_view(login_required_error)
def set_weekly_tournament(request: HttpRequest, data: WeeklySetIn = Form(...)):  # noqa: B008
    tournament = get_object_or_404(WeeklyTournament, id=data.id)
    if not request.user.is_staff and tournament.host != request.user:
        return HttpResponseForbidden()
    if data.state not in Tournament_TextChoices.State.values:
        return HttpResponseBadRequest()

    if data.state == Tournament_TextChoices.State.NORMAL:
        if not tournament.can_validate():
            return HttpResponseBadRequest()
        update_fields = tournament.validate()
    else:
        tournament.state = data.state
        update_fields = ['state']

    if update_fields:
        tournament.save(update_fields=update_fields)
    return HttpResponse()


@router.get('/info', response=WeeklyDetailOut)
def get_weeklyinfo(request: HttpRequest, tournament_id: int):

    tournament = get_object_or_404(WeeklyTournament, tournament_ptr_id=tournament_id)

    if tournament.state == Tournament_TextChoices.State.AWARDED:
        return {
            'data': tournament,
            'results': WeeklyParticipant.objects.filter(tournament=tournament),
            'token': None,
        }

    if not request.user.is_authenticated:
        return {
            'data': tournament,
            'results': None,
            'token': None,
        }

    participant = WeeklyParticipant.objects.filter(tournament=tournament, user=request.user).first()
    if participant is None:
        return {
            'data': tournament,
            'results': None,
            'token': None,
        }
    return {
        'data': tournament,
        'results': None,
        'token': participant.token,
    }


@router.post('/participant')
@decorate_view(login_required_error)
def create_weekly_participant(request: HttpRequest, data: IdIn = Form(...)):  # noqa: B008
    user = request.user
    tournament = get_object_or_404(WeeklyTournament, id=data.id)
    if not tournament.accept_checkin():
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
