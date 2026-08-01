from django.utils import timezone

from config.text_choices import MS_TextChoices
from tournament.services import checkin_with_arbiter, checkin_with_token
from videomanager.models import VideoModel
from .models import Tournament, TournamentParticipant


def participant_videos(participant: TournamentParticipant):
    return list(participant.videos.values('id', 'upload_time', 'level', 'mode', 'timems', 'bv', 'state', 'software', 'cl', 'ce', 'file_size', 'end_time', 'path'))


def add_video_to_checked_tournaments(video: VideoModel):
    for tournament in getattr(video, '_checked_in_tournaments', []):
        tournament.videos.add(video)


def tournament_accepts_checkin(tournament: Tournament):
    now = timezone.now()
    return (
        tournament.start_time is not None
        and tournament.end_time is not None
        and tournament.start_time <= now < tournament.end_time
    )


def tournament_has_ended(tournament: Tournament):
    return tournament.end_time is not None and timezone.now() >= tournament.end_time


def video_checkin(video: VideoModel, tournament_identifiers: list[str]):
    if video.upload_time is None:
        video.upload_time = timezone.now()

    checked_in_tournaments = []
    if video.software == MS_TextChoices.Software.AVF:
        checked_in_tournaments.extend(checkin_with_arbiter(video, video.video.identifier))
    else:
        tournament_tokens = tournament_identifiers
        checked_in_tournaments.extend(checkin_with_token(video, tournament_tokens))
    video._checked_in_tournaments = checked_in_tournaments
    if video.pk is not None:
        add_video_to_checked_tournaments(video)
