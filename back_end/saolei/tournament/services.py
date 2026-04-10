from config.text_choices import Tournament_TextChoices
from .models import Tournament


def tournament_videos_reveal(tournament: Tournament):
    for video in tournament.videos.all():
        ongoing_tournaments = video.tournaments.filter(state=Tournament_TextChoices.State.ONGOING)
        if not ongoing_tournaments.exists():
            video.ongoing_tournament = False
            video.save(update_fields=['ongoing_tournament'])
