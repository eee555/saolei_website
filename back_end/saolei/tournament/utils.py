from django.utils import timezone

from config.text_choices import MS_TextChoices
from videomanager.models import VideoModel
from .cache import (
    get_normal_gsc_tournament_by_token,
    get_normal_participant_info_by_arbiter_identifier,
    get_normal_participant_info_by_tournament,
)
from .models import GSCParticipant, Tournament, TournamentParticipant


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
    user = video.player
    checked_in_tournaments = []
    if video.software == MS_TextChoices.Software.AVF:
        participant_info = get_normal_participant_info_by_arbiter_identifier(user.id, video.video.identifier)
        if participant_info is not None:
            tournament = Tournament.objects.filter(id=participant_info['tournament']).first()
        else:
            tournament = None
        if tournament is not None:
            if tournament_accepts_checkin(tournament):
                video.ongoing_tournament = True
                checked_in_tournaments.append(tournament)
    elif video.software == MS_TextChoices.Software.EVF:
        tournament_tokens = tournament_identifiers
        for token in tournament_tokens:
            if token == '':
                continue
            gsc_tournament = get_normal_gsc_tournament_by_token(token)
            if not gsc_tournament:  # 暂时只支持gsc
                continue
            participant_info = get_normal_participant_info_by_tournament(user.id, gsc_tournament.id)
            participant_exists = participant_info is not None
            if tournament_accepts_checkin(gsc_tournament):
                video.ongoing_tournament = True
                checked_in_tournaments.append(gsc_tournament)
                if not participant_exists:
                    GSCParticipant.objects.create(user=user, tournament=gsc_tournament, token=token)
    video._checked_in_tournaments = checked_in_tournaments
    if video.pk is not None:
        add_video_to_checked_tournaments(video)
