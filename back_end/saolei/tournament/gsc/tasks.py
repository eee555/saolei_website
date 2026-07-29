from django.tasks import task

from tournament.models import GSCTournament
from .services import finish_gsc_tournament, refresh_gsc_scores_and_ranks


@task
def task_gsc_refresh(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    return refresh_gsc_scores_and_ranks(tournament)


@task
def task_gsc_finish(gsc_order: int):
    tournament = GSCTournament.objects.get(order=gsc_order)
    return finish_gsc_tournament(tournament)
