from .models import TournamentParticipant, GSCTournament, GSCParticipant
from videomanager.models import VideoModel
from config.text_choices import MS_TextChoices, Tournament_TextChoices


def participant_videos(participant: TournamentParticipant):
    return list(participant.videos.values('id', 'upload_time', "level", "mode", "timems", "bv", "state", "software", "cl", "ce", "file_size", "end_time", 'path'))

def video_checkin(video: VideoModel, tournament_identifiers: list[str]):
    user = video.player
    if video.software == MS_TextChoices.Software.AVF:
        if participant := TournamentParticipant.objects.filter(user=user, arbiter_identifier__identifier=video.video.identifier).first():
            tournament = participant.tournament
            tournament.refresh_state()
            if tournament.state == Tournament_TextChoices.State.ONGOING:
                video.ongoing_tournament = True
                tournament.videos.add(video)
    elif video.software == MS_TextChoices.Software.EVF:
        tournament_tokens = tournament_identifiers
        for token in tournament_tokens:
            if token == '':
                continue
            gsc_tournament = GSCTournament.objects.filter(token=token).first()
            participant = TournamentParticipant.objects.filter(user=user, tournament=gsc_tournament).first()
            if not gsc_tournament:  # 暂时只支持gsc
                continue
            gsc_tournament.refresh_state()
            if gsc_tournament.state == Tournament_TextChoices.State.ONGOING:
                video.ongoing_tournament = True
                gsc_tournament.videos.add(video)
                if not participant:
                    GSCParticipant.objects.create(user=user, tournament=gsc_tournament, token=token)