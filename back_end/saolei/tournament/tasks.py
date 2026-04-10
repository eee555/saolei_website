from django.tasks import task

from config.text_choices import Tournament_TextChoices
from tournament.models import GSCTournament
from tournament.services import tournament_videos_reveal


@task
def task_gsc_finish(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    tournament.refresh_score()
    tournament.refresh_rank()
    tournament_videos_reveal(tournament)
    tournament.state = Tournament_TextChoices.State.AWARDED
    tournament.save(update_fields=['state'])
