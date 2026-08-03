from datetime import datetime, timezone
from typing import Literal

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.text_choices import Tournament_TextChoices
from tournament.cache import TournamentCache
from tournament.models import GSCTournament, Tournament, TournamentParticipant
from userprofile.decorators import login_required_error, staff_required
from userprofile.models import UserProfile
from utils.response import HttpResponseConflict
from videomanager.schema import VideoBaseOut
from videomanager.view_utils import generate_file_stream

router = Router()
cache = TournamentCache()


class TournamentIdIn(Schema):
    id: int


class TournamentValidationIn(TournamentIdIn):
    valid: bool


class TournamentStaffSetIn(Schema):
    tournament_id: int
    weight: int | None = None
    host_id: int | None = None


class TournamentSetIn(TournamentIdIn):
    start_time: datetime | None = None
    end_time: datetime | None = None
    order: int | None = None
    token: str | None = None


class ParticipantListIn(Schema):
    tournament_id: int
    user_id: int


TournamentOut = create_schema(
    Tournament,
    fields=['id', 'start_time', 'end_time', 'state'],
    custom_fields=[
        ('name', dict[str, str] | str, ''),
        ('description', dict[str, str] | str, ''),
        ('series', str, ''),
        ('host_id', int | None, None),
    ],
)

TournamentParticipantOut = create_schema(
    TournamentParticipant,
    fields=['id'],
    custom_fields=[
        ('user_id', int | None, None),
    ],
)


class TournamentNewsItemOut(Schema):
    id: int
    start_time: datetime | None = None
    end_time: datetime | None = None


class TournamentNewsOut(Schema):
    preparing: list[TournamentNewsItemOut]
    ongoing: list[TournamentNewsItemOut]


@router.get('/get_list', response=list[TournamentOut])
def get_tournament_list(
    request: HttpRequest,
    category: Literal['normal', 'awarded', 'other', 'all'] = 'all',
):
    queryset = Tournament.objects.all()
    if category == 'normal':
        queryset = queryset.filter(state=Tournament_TextChoices.State.NORMAL)
    elif category == 'awarded':
        queryset = queryset.filter(state=Tournament_TextChoices.State.AWARDED)
    elif category == 'other':
        queryset = queryset.exclude(state__in=[
            Tournament_TextChoices.State.NORMAL,
            Tournament_TextChoices.State.AWARDED,
        ])

    return list(queryset.select_subclasses())


@router.get('/get', response=TournamentOut)
def get_tournament(request: HttpRequest, tournament_id: int):
    return get_object_or_404(Tournament, id=tournament_id).select_subclass()


@router.post('/set')
@decorate_view(login_required_error)
def set_tournament(request: HttpRequest, data: TournamentSetIn = Form(...)):  # noqa: B008
    tournament = get_object_or_404(Tournament, id=data.id).select_subclass()
    if tournament.host != request.user:
        return HttpResponseForbidden()

    update_fields = []
    if data.start_time is not None:
        tournament.start_time = data.start_time
        update_fields.append('start_time')
    if data.end_time is not None:
        tournament.end_time = data.end_time
        update_fields.append('end_time')

    if isinstance(tournament, GSCTournament):
        if data.order is not None:
            if GSCTournament.objects.exclude(order=tournament.order).filter(order=data.order).exists():
                return HttpResponseConflict()
            tournament.order = data.order
            update_fields.append('order')
        if data.token is not None:
            if GSCTournament.objects.exclude(order=tournament.order).filter(_token=data.token).exists():
                return HttpResponseConflict()
            if TournamentParticipant.objects.filter(token=data.token).exists():
                return HttpResponseConflict()
            tournament._token = data.token
            update_fields.append('_token')

    if update_fields:
        tournament.save(update_fields=update_fields)
    return HttpResponse()


@router.post('/validate')
@decorate_view(staff_required)
def validate_tournament(request: HttpRequest, data: TournamentValidationIn = Form(...)):  # noqa: B008
    tournament = get_object_or_404(Tournament, id=data.id).select_subclass()
    if not data.valid:
        tournament.invalidate()
        return HttpResponse()
    if not tournament.can_validate():
        return {'type': 'error', 'object': 'tournament', 'category': 'invalid_time'}

    update_fields = tournament.validate()
    if update_fields:
        tournament.save(update_fields=update_fields)
    return HttpResponse()


@router.post('/allow')
@decorate_view(staff_required)
def allow_tournament(request: HttpRequest, data: TournamentIdIn = Form(...)):  # noqa: B008
    tournament = get_object_or_404(Tournament, id=data.id).select_subclass()
    if not tournament.can_validate():
        return {'type': 'error', 'object': 'tournament', 'category': 'invalid_time'}
    if datetime.now(tz=timezone.utc) > tournament.start_time:
        tournament.state = Tournament_TextChoices.State.CANCELLED
        tournament.save(update_fields=['state'])
        return {'type': 'error', 'object': 'tournament', 'category': 'missed_start_time'}

    update_fields = tournament.validate()
    if update_fields:
        tournament.save(update_fields=update_fields)
    return HttpResponse()


@router.post('/cancel')
@decorate_view(login_required_error)
def cancel_tournament(request: HttpRequest, data: TournamentIdIn = Form(...)):  # noqa: B008
    if not (tournament := Tournament.objects.filter(id=data.id).first()):
        return HttpResponseNotFound()
    if not request.user.is_staff and tournament.host != request.user:
        return HttpResponseForbidden()
    tournament.state = Tournament_TextChoices.State.CANCELLED
    tournament.save(update_fields=['state'])
    return HttpResponse()


@router.post('/set_staff', response=TournamentOut)
@decorate_view(staff_required)
def set_tournament_staff(request: HttpRequest, data: TournamentStaffSetIn = Form(...)):  # noqa: B008
    tournament = get_object_or_404(Tournament, id=data.tournament_id).select_subclass()

    update_fields = []
    if data.weight is not None:
        tournament.weight = data.weight
        update_fields.append('weight')
    if data.host_id is not None:
        tournament.host = get_object_or_404(UserProfile, id=data.host_id)
        update_fields.append('host')
    if update_fields:
        tournament.save(update_fields=update_fields)
    return tournament


@router.get('/participants', response=list[TournamentParticipantOut])
def get_participant_list(request: HttpRequest, tournament_id: int):
    return get_object_or_404(Tournament, id=tournament_id).participants


@router.get('/get_videos/participant', response=list[VideoBaseOut])
def get_participant_videos(request: HttpRequest, tournament_id: int, user_id: int):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = get_object_or_404(UserProfile, id=user_id)
    if tournament.state != Tournament_TextChoices.State.AWARDED and request.user != user:
        return HttpResponseForbidden()
    participant = TournamentParticipant.objects.filter(user=user, tournament=tournament).first()
    return participant.videos if participant else []


@router.get('/get_news', response=TournamentNewsOut)
def get_tournament_news(request: HttpRequest):
    now = datetime.now(tz=timezone.utc)
    normal_tournaments = cache.get_tournament_all()
    return {
        'preparing': [
            {'id': tournament.id, 'start_time': tournament.start_time}
            for tournament in normal_tournaments
            if tournament.start_time is not None and tournament.start_time > now
        ],
        'ongoing': [
            {'id': tournament.id, 'end_time': tournament.end_time}
            for tournament in normal_tournaments
            if tournament.start_time is not None
            and tournament.end_time is not None
            and tournament.start_time <= now < tournament.end_time
        ],
    }


@router.get('/download')
@decorate_view(ratelimit(key='ip', rate='1/h'))
def download_all_videos(request: HttpRequest, tournament_id: int):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        return HttpResponseForbidden()
    response = StreamingHttpResponse(generate_file_stream(tournament.videos.all()), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="all_files_stream.bin"'
    return response


@router.get('/download/participant')
@decorate_view(ratelimit(key='ip', rate='1/m'))
def download_videos_participant(request: HttpRequest, tournament_id: int, user_id: int):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = get_object_or_404(UserProfile, id=user_id)
    if tournament.state != Tournament_TextChoices.State.AWARDED and request.user != user:
        return HttpResponseForbidden()
    response = StreamingHttpResponse(generate_file_stream(tournament.videos.filter(player=user)), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="all_files_stream.bin"'
    return response
