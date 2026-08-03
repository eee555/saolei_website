from datetime import datetime, timezone

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from ninja import Form, Router, Schema
from ninja.decorators import decorate_view

from config.text_choices import Tournament_TextChoices
from tournament.cache import TournamentCache
from tournament.models import GSCTournament, Tournament, TournamentParticipant
from tournament.utils import participant_videos
from userprofile.decorators import login_required_error, staff_required
from userprofile.models import UserProfile
from utils.response import HttpResponseConflict
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


class TournamentOut(Schema):
    id: int
    name: dict[str, str]
    description: dict[str, str] | str
    start_time: datetime | None
    end_time: datetime | None
    series: str
    host_id: int | None
    state: str


class TournamentParticipantOut(Schema):
    id: int
    user__id: int | None


class TournamentNewsItemOut(Schema):
    id: int
    start_time: datetime | None = None
    end_time: datetime | None = None


class TournamentNewsOut(Schema):
    preparing: list[TournamentNewsItemOut]
    ongoing: list[TournamentNewsItemOut]


def tournament_out(tournament: Tournament) -> dict:
    return {
        'id': tournament.id,
        'name': tournament.name,
        'description': tournament.description,
        'start_time': tournament.start_time,
        'end_time': tournament.end_time,
        'series': tournament.series,
        'host_id': tournament.host_id,
        'state': tournament.state,
    }


@router.get('/get_list', response=list[TournamentOut])
def get_tournament_list(request: HttpRequest):
    return [
        tournament_out(tournament)
        for tournament in (item.select_subclass() for item in Tournament.objects.all())
        if tournament is not None
    ]


@router.get('/get', response=TournamentOut)
def get_tournament(request: HttpRequest, id: int):
    tournament = get_object_or_404(Tournament, id=id).select_subclass()
    return tournament_out(tournament)


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
        if not (host := UserProfile.objects.filter(id=data.host_id).first()):
            return HttpResponseNotFound()
        tournament.host = host
        update_fields.append('host')
    if update_fields:
        tournament.save(update_fields=update_fields)
    return tournament_out(tournament)


@router.get('/participants', response=list[TournamentParticipantOut])
def get_participant_list(request: HttpRequest, id: int):
    if not (tournament := Tournament.objects.filter(id=id).first()):
        return HttpResponseNotFound()
    return tournament.participants.values('id', 'user__id')


@router.get('/get_videos/participant')
def get_participant_videos(request: HttpRequest, tournament_id: int, user_id: int):
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.AWARDED and request.user != user:
        return HttpResponseForbidden()
    participant = TournamentParticipant.objects.filter(user=user, tournament=tournament).first()
    return participant_videos(participant) if participant else []


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
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.AWARDED:
        return HttpResponseForbidden()
    response = StreamingHttpResponse(generate_file_stream(tournament.videos.all()), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="all_files_stream.bin"'
    return response


@router.get('/download/participant')
@decorate_view(ratelimit(key='ip', rate='1/m'))
def download_videos_participant(request: HttpRequest, tournament_id: int, user_id: int):
    if not (tournament := Tournament.objects.filter(id=tournament_id).first()):
        return HttpResponseNotFound()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    if tournament.state != Tournament_TextChoices.State.AWARDED and request.user != user:
        return HttpResponseForbidden()
    response = StreamingHttpResponse(generate_file_stream(tournament.videos.filter(player=user)), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="all_files_stream.bin"'
    return response
