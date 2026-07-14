from django.tasks import task

from config.text_choices import Tournament_TextChoices
from .models import GSCTournament
from .services import reveal_videos_for_tournament


@task
def task_gsc_finish(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    tournament.refresh_score()
    tournament.refresh_rank()
    reveal_videos_for_tournament(tournament)
    tournament.state = Tournament_TextChoices.State.AWARDED
    tournament.save(update_fields=['state'])
