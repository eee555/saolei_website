from config.text_choices import MS_TextChoices, Tournament_TextChoices
from videomanager.models import VideoModel
from .models import GSCParticipant, GSCTournament, TournamentParticipant


def participant_videos(participant: TournamentParticipant):
    return list(participant.videos.values('id', 'upload_time', 'level', 'mode', 'timems', 'bv', 'state', 'software', 'cl', 'ce', 'file_size', 'end_time', 'path'))


def add_video_to_checked_tournaments(video: VideoModel):
    for tournament in getattr(video, '_checked_in_tournaments', []):
        tournament.videos.add(video)


def video_checkin(video: VideoModel, tournament_identifiers: list[str]):
    user = video.player
    checked_in_tournaments = []
    if video.software == MS_TextChoices.Software.AVF:
        if participant := TournamentParticipant.objects.filter(user=user, arbiter_identifier__identifier=video.video.identifier).first():
            tournament = participant.tournament
            tournament.refresh_state()
            if tournament.state == Tournament_TextChoices.State.ONGOING:
                video.ongoing_tournament = True
                checked_in_tournaments.append(tournament)
    elif video.software == MS_TextChoices.Software.EVF:
        tournament_tokens = tournament_identifiers
        for token in tournament_tokens:
            if token == '':
                continue
            gsc_tournament = GSCTournament.objects.filter(token=token).first()
            if not gsc_tournament:  # 暂时只支持gsc
                continue
            participant = TournamentParticipant.objects.filter(user=user, tournament=gsc_tournament).first()
            gsc_tournament.refresh_state()
            if gsc_tournament.state == Tournament_TextChoices.State.ONGOING:
                video.ongoing_tournament = True
                checked_in_tournaments.append(gsc_tournament)
                if not participant:
                    GSCParticipant.objects.create(user=user, tournament=gsc_tournament, token=token)
    video._checked_in_tournaments = checked_in_tournaments
    if video.pk is not None:
        add_video_to_checked_tournaments(video)
